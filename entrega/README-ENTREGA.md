# Entrega - Consolidador de reservas Onfly

Corrigi **5 defeitos** no CLI. Quatro apareciam nos testes fornecidos; o quinto (leitura cortada em 200
linhas) só aparece no `reservas_hoteis.csv`, que tem 300 reservas.

Não mexi nos testes fornecidos, no contrato do CLI, no formato do relatório nem nos arquivos de dados.

## Defeitos corrigidos

**1. Noites erradas na virada de mês** (`services/stay_calculator.py`)
Causa: subtraía só o dia do mês (`checkout.day - checkin.day`), então 31/01 → 03/02 dava −28 noites.
Correção: `(checkout - checkin).days * rooms`.

**2. Conversão de moeda invertida e com `float`** (`services/currency_converter.py`)
Causa: dividia pela taxa em vez de multiplicar, passando por `float` (100 USD viravam ~18 BRL em vez de 542).
Correção: `amount * rate`, só com `Decimal`.

**3. `NO_SHOW` sendo faturado** (`services/status_policy.py`)
Causa: a regra era "tudo que não é `CANCELLED` é faturável".
Correção: só `CONFIRMED` é faturável, como pede o README (e status novos ficam de fora por padrão).

**4. Ranking de hotéis invertido** (`services/report_builder.py`)
Causa: `top_hotels` ordenava do menor valor para o maior.
Correção: `-valor` na chave de ordenação, mantendo o desempate por `hotel_id` crescente (`reverse=True`
inverteria também o desempate).

**5. Leitura cortada em 200 linhas** (`repositories/csv_reservation_repository.py`)
Causa: um `break` no loop de leitura ao chegar em 200 reservas; nenhum teste ou amostra tinha tantas linhas.
Correção: removi o corte.

Impacto no relatório real:

| Campo | Antes | Depois |
|-|-|-|
| `total_reservations` | 200 | 300 |
| `confirmed_reservations` | 153 | 235 |
| `total_room_nights` | 909 | 1347 |
| `total_amount_brl` | 249543.79 | 396170.00 |

**Melhoria extra:** moeda sem taxa de câmbio quebrava com `KeyError` (código 1). Agora o CLI informa a moeda
faltante e sai com código 2 (entrada inválida, conforme o contrato). Nenhum número do relatório muda.

## Como investiguei

1. Li o README e listei as regras de negócio (status, noites, câmbio, arredondamento, ordenação) como checklist.
2. Rodei `pytest -q` no código original; as falhas já davam pistas (`-28 == 3` nas noites, ranking
   `['H04', 'H03', 'H02']`).
3. Revisei cada módulo contra o checklist, o que levou às causas e ao corte de 200 linhas, que nenhum teste pegava.
4. Analisei o `reservas_hoteis.csv` para descartar problema nos dados: status, moedas e datas padronizados,
   sem IDs repetidos e sem checkout antes do check-in.
5. Corrigi um defeito por commit, rodando os testes a cada passo.
6. Comparei o relatório real com um script independente que aplica as regras do README direto no CSV. Os
   números bateram.

## Testes adicionais

Em `tests/test_extras.py`:

- arquivo com mais de 200 linhas (defeito 5);
- empate no ranking resolvido por `hotel_id`;
- noites na virada de ano com mais de um quarto;
- arredondamento half-up só depois da soma;
- relatório sem reservas confirmadas (média `"0.00"` e listas vazias);
- códigos de saída para `--top 0` e arquivo inexistente;
- moeda sem taxa de câmbio saindo com código 2.

Confirmei que o teste das 200 linhas falha se o corte voltar ao código. Os demais já passavam e ficam como
proteção contra regressões.

## Como validar

Requer Python 3.11+.

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt

pytest -q
ruff check .
```

Amostra de validação (deve bater com a tabela do README):

```bash
PYTHONPATH=src python -m onfly_report \
  --input data/exemplo-validacao.csv \
  --rates data/taxas_cambio.csv \
  --output output/exemplo.json
# Reservas: 12 | Confirmadas: 9 | Noites: 28 | Total BRL: 7566.00
```

Relatório real:

```bash
PYTHONPATH=src python -m onfly_report \
  --input data/reservas_hoteis.csv \
  --rates data/taxas_cambio.csv \
  --output output/report.json
# Reservas: 300 | Confirmadas: 235 | Noites: 1347 | Total BRL: 396170.00
```

## Resultado do `pytest`

```
13 passed in 0.32s
```

Os 5 testes fornecidos seguem inalterados e o `ruff check .` não aponta problemas.

## Uso de IA

Usei IA neste desafio. As exportações das sessões e a declaração estão em `entrega/uso-de-ia/`.
