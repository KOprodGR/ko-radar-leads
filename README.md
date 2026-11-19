# KO Radar · Leads

Buscador de **negócios locais sem site**, usando a **API oficial do Google Places**. Você informa cidade, bairro e nichos, e ele gera um CSV de leads qualificados: negócios abertos, com telefone, que **não têm site** cadastrado no Google Maps.

Pensado para quem oferece **site, vídeo curto ou automação** a pequenos negócios e quer uma lista organizada para abordar **à mão**.

> **Status:** a etapa 1 (busca) está pronta e testada. A geração de mensagens e de links `wa.me` ainda **não foi implementada** (veja o [Roteiro](#roteiro)).

## O que ele faz

1. **`buscar_leads.py`**: para cada nicho, faz uma busca de texto (`"<nicho> em <bairro>, <cidade>"`) e salva em `leads.csv` os negócios que:
   - estão em operação (`OPERATIONAL`);
   - têm telefone;
   - **não têm site** (`websiteUri` vazio);
   - ainda não estão no CSV (sem duplicar, pelo `place_id`).
2. **`detalhes_leads.py`**: para os leads com status `novo`, busca detalhes adicionais (tipo do negócio, horário de funcionamento) e salva em `detalhes.json`, para você personalizar a abordagem.

Só usa a **biblioteca padrão do Python**. Não há nada para instalar.

## Estrutura

```
ko-radar-leads/
├── README.md
├── buscar_leads.py        # etapa 1: busca e gera o leads.csv
├── detalhes_leads.py      # detalhes dos leads novos -> detalhes.json
├── .env.example           # modelo do arquivo de chave
├── .gitignore
└── exemplo/
    └── leads.exemplo.csv  # exemplo do formato (dados fictícios)
```

## Requisitos

- **Python 3.8 ou maior** (testado no 3.12).
- Uma **chave da Google Places API (New)**.

## Configuração

1. No [Google Cloud Console](https://console.cloud.google.com), crie um projeto **separado** para este radar e ative a **Places API (New)**.
2. Crie uma **chave de API** e **restrinja** à Places API (New). Configure também um **alerta de orçamento** no projeto.
3. Copie o modelo e coloque a chave:

   ```bash
   cp .env.example .env      # no Windows (PowerShell): copy .env.example .env
   ```

   Edite o `.env` e preencha `GOOGLE_PLACES_API_KEY`. O arquivo `.env` está no `.gitignore`: **nunca o envie para o GitHub**.

## Uso

Teste primeiro sem gastar nada. O `--dry-run` só mostra o plano:

```bash
python buscar_leads.py --dry-run
```

Busca de verdade (padrão: São Paulo, Ipiranga, 10 leads):

```bash
python buscar_leads.py
python buscar_leads.py --cidade "Campinas" --bairro "Cambuí" --nichos adega,moda --meta 10
```

| Opção | Padrão | O que faz |
|---|---|---|
| `--cidade` | `São Paulo` | Cidade |
| `--bairro` | `Ipiranga` | Bairro |
| `--nichos` | `moda,contabilidade,adega,restaurante` | Nichos, separados por vírgula |
| `--meta` | `10` | Para quando atingir esse número de leads sem site |
| `--saida` | `leads.csv` | Arquivo de saída |
| `--dry-run` | (desligado) | Mostra o plano e não chama a API |

Depois, os detalhes dos leads novos (1 chamada por lead):

```bash
python detalhes_leads.py --dry-run     # lista quem seria detalhado
python detalhes_leads.py
```

Rodar de novo **acrescenta** só leads novos ao CSV e só detalha quem ainda não está no `detalhes.json`.

## Formato do `leads.csv`

Colunas: `status`, `nome`, `nicho`, `telefone`, `nota`, `avaliacoes`, `endereco`, `maps`, `place_id`, `data_busca`. O arquivo é gravado em `utf-8-sig`, então abre direto no Excel. Há um exemplo em [`exemplo/leads.exemplo.csv`](exemplo/leads.exemplo.csv).

**Status dos leads:** `novo`, `contatado`, `respondeu`, `fechado`, `não quer` e `descartado`. Você atualiza o status à mão no CSV. O `detalhes_leads.py` só processa quem está como `novo`.

## Custo

Os campos de telefone e de site entram na faixa **Enterprise** da Places API, que é mais cara. Em um teste com 3 buscas, o gasto foi de cerca de **US$ 0,10**. Os preços mudam e dependem do seu plano, então consulte a [tabela oficial](https://developers.google.com/maps/billing-and-pricing/pricing) e use o `--dry-run` e o alerta de orçamento.

## Limitações conhecidas

- O script lê só a **primeira página** de cada busca (até 20 resultados), sem paginação.
- Nos testes, o `detalhes_leads.py` retornou apenas **tipo do negócio e horário**. Avaliações e fotos vieram vazias para os negócios testados, apesar de estarem no `FieldMask`.
- Negócio sem site **no Google Maps** pode ter site ou Instagram em outro lugar. **Confira cada lead** antes de abordar.
- Os dados vêm do Google e podem estar desatualizados.

## Uso responsável

- Use **só a API oficial**. Não raspe o Google Maps.
- **Não envie mensagens em massa de forma automática.** O fluxo previsto é gerar a mensagem e **você enviar manualmente**, em volume pequeno e de um número separado.
- Toda mensagem deve trazer uma **frase de saída** (por exemplo, "se não quiser receber, é só me avisar") e você deve **respeitar quem pedir para parar**.
- Telefones de empresas continuam sendo dados que exigem cuidado. Observe a **LGPD** e as regras do WhatsApp. **Não publique o seu `leads.csv`** nem o `detalhes.json`: ambos estão no `.gitignore`.

## Roteiro

- [x] Etapa 1: buscador de leads (CSV).
- [x] Detalhes dos leads (tipo e horário).
- [ ] Mensagem personalizada por lead, citando algo real do negócio.
- [ ] Gerador de link `wa.me` com a mensagem pronta e a frase de saída.
- [ ] Painel simples de status dos leads (e exportação para o Google Sheets).

## Licença

Defina a licença antes de publicar (por exemplo, MIT) e adicione um arquivo `LICENSE`.
