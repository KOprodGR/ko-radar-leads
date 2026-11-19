"""Etapa 2 (parte 1): puxa detalhes de cada lead com status "novo" do leads.csv
(site, resumo, horario, ultimas avaliacoes) e salva em detalhes.json.
Pula leads ja detalhados e leads com outro status (ex.: descartado).

Uso: python detalhes_leads.py [--dry-run]
"""
import csv
import json
import os
import sys
import urllib.error
import urllib.request

PASTA = os.path.dirname(os.path.abspath(__file__))
CAMPOS = ",".join([
    "id", "displayName", "websiteUri", "primaryTypeDisplayName",
    "editorialSummary", "regularOpeningHours.weekdayDescriptions",
    "reviews.rating", "reviews.text", "reviews.relativePublishTimeDescription",
    "photos.name",
])


def carregar_env():
    p = os.path.join(PASTA, ".env")
    if os.path.exists(p):
        for l in open(p, encoding="utf-8"):
            l = l.strip()
            if l and not l.startswith("#") and "=" in l:
                k, v = l.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def detalhe(chave, place_id):
    req = urllib.request.Request(
        f"https://places.googleapis.com/v1/places/{place_id}?languageCode=pt-BR",
        headers={"X-Goog-Api-Key": chave, "X-Goog-FieldMask": CAMPOS})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"ERRO {e.code}: {e.read().decode('utf-8')[:300]}")
        return None


def main():
    carregar_env()
    with open(os.path.join(PASTA, "leads.csv"), encoding="utf-8-sig", newline="") as f:
        leads = [l for l in csv.DictReader(f) if l["status"] == "novo"]
    arq = os.path.join(PASTA, "detalhes.json")
    dados = json.load(open(arq, encoding="utf-8")) if os.path.exists(arq) else {}
    pend = [l for l in leads if l["place_id"] not in dados]
    print(f"{len(pend)} leads para detalhar (1 chamada cada).")
    if "--dry-run" in sys.argv:
        for l in pend:
            print(" -", l["nome"])
        return
    chave = os.environ.get("GOOGLE_PLACES_API_KEY", "")
    if not chave:
        sys.exit("Chave nao encontrada no .env")
    for l in pend:
        d = detalhe(chave, l["place_id"])
        if d is None:
            continue
        dados[l["place_id"]] = d
        print(f"{l['nome']}: site={d.get('websiteUri', '-')}, "
              f"{len(d.get('reviews', []))} avaliacoes, {len(d.get('photos', []))} fotos")
    json.dump(dados, open(arq, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
