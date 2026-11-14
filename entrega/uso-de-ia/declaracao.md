# Declaração de uso de IA

## Ferramenta e modelo

**Claude Code** (terminal) com **Claude Opus 5.5 (high effort)**. Sessões exportadas:

- `sessao-01.txt`: correções, busca de defeitos, revisão dos testes e do repositório;
- `sessao-02.txt`: revisão e enxugamento do `README-ENTREGA.md` e desta declaração.

Eu nunca tinha programado em Python antes deste desafio, então usei a IA bastante, tanto para encontrar os
problemas quanto para entender cada correção.

## O que a IA fez

- Achou a causa do ranking invertido e **aplicou a correção** em `services/report_builder.py` (`-valor` na
  chave de ordenação), explicando por que não usar `reverse=True`.
- A meu pedido, procurou defeitos não cobertos pelos testes e achou o corte de 200 linhas. Removeu o corte e
  comparou o relatório real com um script independente que aplica as regras do README no CSV. Essa remoção
  não chegou ao commit (ver abaixo).
- Analisou o CSV para confirmar que os dados estavam consistentes.
- Revisou meu `tests/test_extras.py` e apontou os erros: nome do arquivo (`teste_extras.py`, que o pytest
  ignora), funções com recuo a mais dentro de outro teste, `tmp_path` faltando, nome de campo errado e uma
  função sem o prefixo `test_`.
- Revisou o repositório antes da entrega.
- Na `sessao-02`, enxugou o `README-ENTREGA.md` e esta declaração, e corrigiu inconsistências (nome do
  arquivo da sessão, número de ferramentas).

## O que eu fiz

- Criei o repositório com um primeiro commit do código original, antes de qualquer alteração.
- Instalei o Python 3.11 e configurei o ambiente virtual.
- Apliquei com as minhas próprias mãos as correções de noites, câmbio e status, uma por commit, rodando `pytest -q` a cada uma.
  Errei no caminho: nas noites, editei primeiro a assinatura da função em vez do `return`; no câmbio, mantive
  o `float` até entender a regra do `Decimal`; e ajustei a ordem dos imports apontada pelo `ruff`.
- Revisei e commitei a correção do ranking feita pela IA (`64b031d`).
- Escrevi os testes adicionais e corrigi os erros apontados na revisão. Com eles rodando, o teste das 200
  linhas mostrou que o corte ainda estava no código; removi e commitei (`c88e7c5`).
- Decidi implementar a melhoria da moeda sem taxa (código 2) e escrevi o teste dela.
- Deixei os testes independentes da pasta de execução do `pytest` (`326ceb6`).
- Rodei a validação com a amostra e com o arquivo real e conferi o `output/report.json`.
- Revisei o texto do `README-ENTREGA.md` e desta declaração.
