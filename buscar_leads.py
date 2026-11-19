"""Etapa 1 do KO Radar: busca negocios locais no Google Places (API oficial)
e salva em CSV os que NAO tem site.

Uso:
  python buscar_leads.py --dry-run          (nao chama a API, so mostra o plano)
  python buscar_leads.py                    (busca de verdade, gera leads.csv)
  python buscar_leads.py --nichos adega,moda --bairro Ipiranga --meta 10

Usa so a biblioteca padrao do Python (nada para instalar).
"""
import argparse
import csv
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import date

URL = "https://places.googleapis.com/v1/places:searchText"
# Campos pedidos. websiteUri e telefone entram na faixa "Enterprise" (mais cara).
CAMPOS = ",".join([
    "places.id", "places.displayName", "places.formattedAddress",
    "places.nationalPhoneNumber", "places.websiteUri", "places.rating",
    "places.userRatingCount", "places.googleMapsUri", "places.businessStatus",
])
COLUNAS = ["status", "nome", "nicho", "telefone", "nota", "avaliacoes",
           "endereco", "maps", "place_id", "data_busca"]


def carregar_env(caminho):
    if not os.path.exists(caminho):
        return
    with open(caminho, encoding="utf-8") as f:
        for linha in f:
            linha = linha.strip()
            if linha and not linha.startswith("#") and "=" in linha:
                k, v = linha.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def buscar(chave, consulta):
    corpo = json.dumps({"textQuery": consulta, "languageCode": "pt-BR",
                        "regionCode": "BR", "pageSize": 20}).encode("utf-8")
    req = urllib.request.Request(URL, data=corpo, method="POST", headers={
        "Content-Type": "application/json",
        "X-Goog-Api-Key": chave,
        "X-Goog-FieldMask": CAMPOS,
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode("utf-8")).get("places", [])
    except urllib.error.HTTPError as e:
        # Nao mostra a chave; so o motivo devolvido pelo Google.
        print(f"ERRO {e.code} do Google: {e.read().decode('utf-8')[:400]}")
        sys.exit(1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cidade", default="São Paulo")
    ap.add_argument("--bairro", default="Ipiranga")
    ap.add_argument("--nichos", default="moda,contabilidade,adega,restaurante")
    ap.add_argument("--meta", type=int, default=10, help="leads sem site para parar")
    ap.add_argument("--saida", default="leads.csv")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    pasta = os.path.dirname(os.path.abspath(__file__))
    carregar_env(os.path.join(pasta, ".env"))
    nichos = [n.strip() for n in a.nichos.split(",") if n.strip()]
    consultas = [(n, f"{n} em {a.bairro}, {a.cidade}") for n in nichos]

    print(f"Plano: {len(consultas)} buscas (1 chamada cada), meta {a.meta} leads sem site.")
    for _, c in consultas:
        print("  -", c)
    if a.dry_run:
        print("Dry-run: nenhuma chamada feita, nada gasto.")
        return

    chave = os.environ.get("GOOGLE_PLACES_API_KEY", "")
    if not chave:
        sys.exit("Chave nao encontrada: preencha GOOGLE_PLACES_API_KEY no .env")

    # Leads ja salvos (evita duplicar entre execucoes)
    saida = os.path.join(pasta, a.saida)
    vistos = set()
    if os.path.exists(saida):
        with open(saida, encoding="utf-8-sig", newline="") as f:
            vistos = {l["place_id"] for l in csv.DictReader(f)}

    novos = []
    for nicho, consulta in consultas:
        if len(novos) >= a.meta:
            break
        lugares = buscar(chave, consulta)
        sem_site = 0
        for p in lugares:
            if p.get("websiteUri") or p.get("id") in vistos:
                continue
            if p.get("businessStatus", "OPERATIONAL") != "OPERATIONAL":
                continue
            if not p.get("nationalPhoneNumber"):
                continue  # sem telefone nao da para abordar
            vistos.add(p["id"])
            sem_site += 1
            novos.append({
                "status": "novo",
                "nome": p.get("displayName", {}).get("text", ""),
                "nicho": nicho,
                "telefone": p["nationalPhoneNumber"],
                "nota": p.get("rating", ""),
                "avaliacoes": p.get("userRatingCount", ""),
                "endereco": p.get("formattedAddress", ""),
                "maps": p.get("googleMapsUri", ""),
                "place_id": p["id"],
                "data_busca": date.today().isoformat(),
            })
            if len(novos) >= a.meta:
                break
        print(f"{consulta}: {len(lugares)} resultados, {sem_site} leads sem site")

    novo_arquivo = not os.path.exists(saida)
    with open(saida, "a", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUNAS)
        if novo_arquivo:
            w.writeheader()
        w.writerows(novos)
    print(f"Salvos {len(novos)} leads em {saida}")


if __name__ == "__main__":
    main()
