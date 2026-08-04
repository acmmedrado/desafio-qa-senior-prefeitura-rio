# Avaliacao da Estrategia de QA

Este documento resume as principais escolhas da suite e responde aos criterios que eu usaria para avaliar a entrega em um desafio de QA Senior.

## A cobertura vai alem dos happy paths?

Sim. A suite cobre fluxos felizes, mas tambem valida riscos de contrato, seguranca, borda, usabilidade da API, resiliencia e isolamento de dados.

Exemplos de cenarios fora do happy path:

- token ausente, token invalido e esquema de autorizacao malformado;
- servico inexistente;
- variacoes adversariais de ID inexistente, incluindo entrada SQL-like, unicode parecido, string enorme e whitespace;
- JSON malformado;
- content-type nao JSON;
- query ausente, vazia ou em branco;
- paginacao com valores negativos, zero, nao numericos e pagina fora do intervalo;
- webhook sem assinatura, com assinatura invalida, assinatura gerada com segredo incorreto e assinatura de outro payload;
- payload grande de webhook;
- query longa com caracteres Unicode;
- metodo HTTP nao suportado;
- busca sem resultado;
- busca com acento, espacos extras e termos comuns de usuario.
- consistencia entre listagem e detalhe para todos os servicos;
- ids, tags e `view_count` consistentes para todo o catalogo observado.

Essa abordagem mostra que a suite nao valida apenas se a API funciona quando tudo esta correto. Ela tambem verifica se a API falha de forma previsivel, segura e facil de consumir.

## Os testes de performance sao realistas?

Os testes de performance atuais sao realistas como smoke/load test de regressao, mas nao devem ser interpretados como prova final de capacidade de producao.

Thresholds atuais:

- `http_req_failed < 1%`
- `p95 < 300ms`
- `p99 < 750ms`
- `checks > 99%`

Esses limites fazem sentido como primeira barra para uma API simples de catalogo publico, pois respostas de busca, listagem e detalhe precisam continuar rapidas mesmo sob acesso concorrente. O cenario de CI sobe ate 50 usuarios virtuais para detectar regressao sem tornar o pipeline lento.

Para justificar a ordem de grandeza: se o catalogo tiver 20 mil acessos por dia e 20% deles acontecerem em uma janela de pico de 2 horas, isso representa cerca de 33 requisicoes por minuto. Considerando usuarios navegando por alguns segundos entre busca, detalhe e recomendacao, 50 VUs e uma carga conservadora para smoke. O projeto tambem inclui `performance/spike.k6.js`, que sobe ate 150 VUs para execucao manual de pico.

Limite importante: a API do desafio roda em memoria, sem banco, rede real, cache externo ou infraestrutura de producao. Por isso, os tempos locais em microssegundos nao provam capacidade final. Para producao, eu adicionaria endurance test, capacity test em ambiente semelhante ao real e monitoramento de saturacao.

## Os bugs estao reproduziveis?

Sim. Os bugs estao documentados em `docs/BUGS.md` com impacto, severidade, comportamento esperado, comportamento atual e evidencia. Alem disso, cada bug relevante possui um teste automatizado marcado como `known_bug`.

Qualquer pessoa do time consegue reproduzir sem ajuda:

```bash
make release-gate
make test-known-bugs-diagnostic
```

O `release-gate` mostra os bugs criticos ou de seguranca que deveriam bloquear release. A suite diagnostica mostra bugs medios, baixos e riscos de usabilidade que devem continuar visiveis sem bloquear todo desenvolvimento.

## O CI falha quando deveria e passa quando deveria?

Sim. O CI foi desenhado para separar comportamento aceito de defeitos conhecidos.

- `make test` roda `pytest -m "not known_bug"` e deve passar.
- `make release-gate` roda `known_bug_high or security` e deve falhar localmente enquanto houver bugs criticos sem waiver.
- `make test-known-bugs-diagnostic` roda bugs conhecidos nao criticos como diagnostico.
- o GitHub Actions publica HTML, JUnit XML e `quality-summary.md`, mantendo os bugs conhecidos visiveis sem transformar a existencia deles em falha inesperada do pipeline.

Esse desenho evita uma interpretacao perigosa de "CI verde significa sem bugs". O quality gate principal fica verde para comportamentos aceitos, enquanto o resumo do CI continua apontando que o release esta bloqueado pelos bugs criticos documentados.

## As ferramentas escolhidas tem justificativa?

Sim. As ferramentas foram escolhidas pela simplicidade, legibilidade e compatibilidade com automacao de API.

| Ferramenta | Justificativa |
|---|---|
| `pytest` | Suite legivel, suporte a fixtures, markers e boa organizacao por dominio. |
| `requests` | Cliente HTTP simples e direto para testes funcionais de API. |
| `jsonschema` | Validacao formal das respostas contra o contrato observado em `openapi.yaml`. |
| `pytest-html` | Relatorios HTML consumiveis por pessoas do time e avaliadores. |
| JUnit XML | Formato padrao para CI, dashboards e sumarizacao automatica. |
| `ruff` | Lint e formatacao rapidos para manter qualidade do codigo de teste. |
| `k6` | Testes de performance com cenarios e thresholds declarativos; no CI roda via imagem Docker oficial para evitar dependencia de action arquivada. |
| GitHub Actions | Execucao automatica, artefatos, agendamento e resumo visivel no pull request ou push. |

## Conclusao

A cobertura e suficiente para o contexto do desafio e esta acima de uma entrega minima. Ela demonstra maturidade por cobrir riscos alem do happy path, documentar bugs de forma executavel, separar gates por severidade, justificar performance com limites claros, explorar entradas adversariais e manter o codigo de teste organizado.

Ela ainda nao substitui uma estrategia completa de producao. Com mais tempo, eu adicionaria testes gerados por contrato com Schemathesis, property-based testing com Hypothesis, simulacao controlada de timeouts/falhas de rede e testes de endurance em ambiente mais parecido com producao.
