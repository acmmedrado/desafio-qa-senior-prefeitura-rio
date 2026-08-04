# Desafio QA Senior - Automacao

[![quality](https://github.com/acmmedrado/desafio-qa-senior-prefeitura-rio/actions/workflows/quality.yml/badge.svg)](https://github.com/acmmedrado/desafio-qa-senior-prefeitura-rio/actions/workflows/quality.yml)

Camada de qualidade para o **Catalogo de Servicos Publicos** da Prefeitura do Rio. A entrega valida comportamento de API, contrato, seguranca, bordas, UX da busca, resiliencia, performance e execucao automatica em CI.

## Visao Geral

| Area | Status | Evidencia |
|---|---|---|
| Quality gate funcional | OK | `49/49` testes passando |
| Release gate | Bloqueado | `10` bugs criticos/seguranca documentados |
| Diagnostico de bugs | Mapeado | `13` falhas conhecidas de media/baixa severidade e UX |
| Performance smoke | OK | `0.00%` falhas HTTP, `p95=601us`, `p99=1.14ms` |
| CI | OK | Lint, testes, relatorios e k6 no GitHub Actions |

**Leitura importante:** CI verde significa que a automacao executou corretamente. Nao significa liberacao automatica: o release segue bloqueado enquanto os bugs criticos/seguranca nao forem corrigidos ou formalmente aceitos em waiver.

## Sumario

- [Como Rodar](#como-rodar)
- [Resultados Locais](#resultados-locais)
- [Cobertura](#cobertura)
- [Bugs Encontrados](#bugs-encontrados)
- [Diferenciais do Desafio](#diferenciais-do-desafio)
- [Arquitetura dos Testes](#arquitetura-dos-testes)
- [Performance](#performance)
- [CI e Relatorios](#ci-e-relatorios)
- [O Que Faria Com Mais Tempo](#o-que-faria-com-mais-tempo)

## Como Rodar

### 1. Subir a API

```bash
cd api
docker compose up -d --build
```

A API fica disponivel em `http://localhost:8080`.

### 2. Instalar dependencias

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Ou, pelo Makefile:

```bash
make install
```

### 3. Executar a suite principal

```bash
make test
```

Esse comando roda o quality gate funcional, excluindo bugs ja conhecidos:

```bash
pytest -m "not known_bug"
```

### Comandos uteis

| Comando | O que faz | Quando usar |
|---|---|---|
| `make lint` | Roda `ruff check` e `ruff format --check` | Antes de commit/CI |
| `make test` | Roda o quality gate funcional | Validar comportamento aceito |
| `make release-gate` | Roda bugs criticos/seguranca conhecidos | Decisao de release |
| `make test-known-bugs-diagnostic` | Roda bugs medios/baixos e UX | Diagnostico e acompanhamento |
| `make reports` | Gera HTML, JUnit XML e resumo consolidado | Evidencia local |
| `make perf` | Roda smoke de performance com k6 | Regressao de carga |
| `make perf-spike` | Roda spike/stress manual | Pico fora do CI |
| `make clean` | Remove caches e relatorios locais | Limpeza do workspace |

Variaveis suportadas:

| Variavel | Padrao | Uso |
|---|---|---|
| `BASE_URL` | `http://localhost:8080` | URL da API testada |
| `AUTH_TOKEN` | `qa-challenge-token` | Token usado pelo k6 |
| `WEBHOOK_SECRET` | `webhook-secret-2024` | Secret HMAC do webhook |

## Resultados Locais

Execucao local registrada em [docs/EXECUTION.md](docs/EXECUTION.md), com API em `http://localhost:8080`.

| Gate | Comando | Resultado | Interpretacao |
|---|---|---:|---|
| Lint | `make lint` | passou | Codigo de testes e scripts consistente |
| Quality gate | `make test` | `49 passed` | Comportamentos aceitos estao verdes |
| Release gate | `make release-gate` | `10 failed` | Bugs criticos/seguranca bloqueiam release |
| Diagnostico | `make test-known-bugs-diagnostic` | `13 failed` | Bugs conhecidos seguem reproduziveis |
| Performance | `make perf` | passou | Sem falhas HTTP e sem saturacao no smoke |

Resumo consolidado gerado por `make reports`:

```text
Quality gate: 49 passed, 0 failed
Release-blocking known bugs: 10 failed
Non-blocking known bug diagnostics: 13 failed
Performance smoke: 0.00% HTTP failures, dropped_iterations=0
```

## Cobertura

### Matriz por endpoint

| Endpoint | Happy path | Erros e bordas | Auth/seguranca | Contrato | Performance |
|---|---:|---:|---:|---:|---:|
| `GET /health` | Sim | N/A | N/A | Sim | Sim |
| `GET /api/v1/services` | Sim | Sim | N/A | Sim | Sim |
| `GET /api/v1/services/:id` | Sim | Sim | N/A | Sim | Sim |
| `POST /api/v1/services/search` | Sim | Sim | N/A | Sim | Sim |
| `GET /api/v1/services/:id/recommendations` | Sim | Sim | Sim | Sim | Sim |
| `POST /api/v1/services/:id/favorite` | Sim | Sim | Sim | Sim | Nao |
| `POST /api/v1/webhooks/catalog` | Sim | Sim | Sim | Sim | Sim |

### Lentes de qualidade

| Lente | Testes mapeados | O que cobre |
|---|---:|---|
| API contract and schema | 40 | OpenAPI, JSON Schema, consistencia de payloads |
| Negative and edge cases | 25 | Entradas invalidas, bordas, IDs adversariais |
| Security and authorization | 12 | Token, injection, vazamento de erro, esquemas invalidos e HMAC |
| Test data management | 4 | Snapshot isolado e ausencia de estado mutavel compartilhado |
| UX and API usability | 6 | Encontrabilidade, linguagem de usuario e relevancia |
| Resilience | 5 | Burst curto, payload grande, conexao e metodos invalidos |

### Prioridades de teste

| Prioridade | Por que importa |
|---|---|
| Contrato | Consumidores precisam de respostas previsiveis e colecoes consistentes. |
| Tratamento de erro | Erros esperados nao podem virar `500` nem stack trace operacional. |
| Autorizacao | Endpoints protegidos devem rejeitar ausencia, token invalido e esquema malformado. |
| Webhook HMAC | Integracoes externas nao podem alterar catalogo sem assinatura valida. |
| UX da API | Busca publica precisa tolerar necessidade real de usuario, nao so nome oficial. |
| Performance | Um catalogo municipal deve responder rapido sob acesso concorrente. |

## Bugs Encontrados

A lista completa esta em [docs/BUGS.md](docs/BUGS.md). Cada bug tem impacto, reproducao, resultado atual, resultado esperado e teste automatizado.

| ID | Severidade | Area | Resumo |
|---|---|---|---|
| BUG-001 | Alta | Erro/contrato | Servico inexistente ou ID adversarial retorna `500` em vez de `404`. |
| BUG-002 | Media | Validacao | Busca vazia ou sem `query` retorna sucesso. |
| BUG-003 | Media | Paginacao | `total_pages` usa arredondamento para baixo. |
| BUG-004 | Critica | Seguranca | Webhook aceita assinatura ausente, invalida, com secret errado ou algoritmo incorreto. |
| BUG-005 | Alta | Autorizacao | Recomendacoes aceitam ausencia/token invalido. |
| BUG-006 | Baixa | Contrato/UX | Busca sem resultado retorna `results: null` em vez de `[]`. |
| BUG-007 | Media | UX | Busca nao normaliza acentos, espacos e tags comuns. |
| BUG-008 | Media | UX | Busca nao entende linguagem de necessidade nem prioriza relevancia. |

## Diferenciais do Desafio

| Diferencial | Implementacao |
|---|---|
| Contract testing | `openapi.yaml`, `jsonschema` e validacoes em `tests/test_contract.py` |
| Acessibilidade | Avaliacao pela lente de API usability em [docs/UX_QUALITY.md](docs/UX_QUALITY.md) |
| Security testing | `tests/test_security.py` cobre injection, auth abusiva, HMAC malformado e information disclosure |
| Resiliencia | `tests/test_resilience.py`, payload grande, burst concorrente e conexao fechada |
| Relatorio no CI | `scripts/quality_summary.py` gera `quality-summary.md` e Step Summary |
| Test data management | Fixtures isoladas, `tests/data.py`, snapshots frescos e client por teste |
| Performance | k6 com thresholds, smoke no CI e spike manual |
| Qualidade do codigo de teste | `ruff`, client HTTP de dominio e helpers de webhook |

## Arquitetura dos Testes

### Fluxo da automacao

```text
GitHub Actions / make
        |
        v
pytest markers
quality gate | release gate | diagnostic bugs
        |
        v
CatalogApiClient
base_url | timeout | paths | headers
        |
        v
Catalogo de Servicos Publicos API
        |
        v
JUnit XML + HTML + quality-summary.md
```

### Camadas

| Camada | Arquivos | Responsabilidade |
|---|---|---|
| Orquestracao | `Makefile`, `.github/workflows/quality.yml` | Rodar lint, gates, relatorios e performance localmente ou no CI. |
| Test runners | `pytest.ini`, markers `contract`, `negative`, `security`, `known_bug` | Separar comportamentos aceitos, bugs bloqueantes e diagnosticos. |
| Testes de API | `tests/test_*.py` | Validar contrato, erro, auth, busca, webhook, UX, resiliencia e seguranca. |
| Client de dominio | `tests/client.py` | Centralizar URL base, timeout, paths e sessao HTTP. |
| Dados de teste | `tests/data.py`, fixtures em `conftest.py` | Evitar IDs e termos espalhados, criar snapshots isolados por teste. |
| Helpers | `tests/helpers.py` | Montar payload assinado e assinatura HMAC de forma reutilizavel. |
| Contrato | `openapi.yaml`, `tests/test_contract.py` | Formalizar comportamento observado e validar respostas com JSON Schema. |
| Performance | `performance/catalog-api.k6.js`, `performance/spike.k6.js` | Medir regressao de latencia, erro, saturacao e pico manual. |
| Evidencia | `reports/`, `scripts/quality_summary.py`, `docs/` | Gerar artefatos legiveis, bugs reproduziveis e rastreabilidade. |

### Mapa da suite

| Suite | Lente principal | Exemplos de cobertura |
|---|---|---|
| `test_health.py` | Operacional | Health check e metadados basicos. |
| `test_services.py` | Catalogo | Listagem, paginacao, detalhe e IDs inexistentes. |
| `test_search.py` | Busca | Termos validos, query vazia, JSON invalido e content-type. |
| `test_auth_and_recommendations.py` | Autorizacao | Favoritos, token invalido, recomendacoes protegidas. |
| `test_webhook.py` | Integracao segura | HMAC ausente, invalido, secret errado e payload divergente. |
| `test_security.py` | Abuso defensivo | Injection, path traversal, token gigante e vazamento de informacao. |
| `test_contract.py` | Contrato formal | OpenAPI, JSON Schema, IDs, tags, view count e consistencia. |
| `test_data_management.py` | Estado de teste | Snapshot isolado e ausencia de mutacao compartilhada. |
| `test_ux_quality.py` | Usabilidade da API | Encontrabilidade, linguagem de necessidade e relevancia. |
| `test_resilience.py` | Robustez | Burst concorrente, payload grande, metodo invalido e conexao fechada. |

### Decisoes de clean code

| Decisao | Ganho |
|---|---|
| Client HTTP explicito | Testes leem intencao de negocio, nao montagem repetida de URL. |
| Dados centralizados | Mudanca no seed da API exige ajuste em um lugar so. |
| Fixtures com teardown | Cada teste fecha sua sessao HTTP e reduz vazamento entre cenarios. |
| Markers estritos | O CI separa qualidade, bug conhecido, seguranca e diagnostico sem ambiguidade. |
| Helpers de HMAC | Assinatura de webhook fica correta e reutilizavel. |
| Relatorio consolidado | Quem avalia entende status geral sem abrir cada HTML individualmente. |

### Test data management

A API do desafio nao possui endpoints de criacao/remocao de servicos, entao a suite evita depender de estado mutavel compartilhado:

- cada teste recebe um `CatalogApiClient` proprio, com sessao HTTP fechada ao final;
- `catalog_snapshot` busca um snapshot fresco do catalogo por teste;
- `tests/data.py` centraliza IDs, titulos, categorias e termos;
- seletores como `catalog.by_title(...)`, `catalog.by_category(...)` e `catalog.unknown_id()` evitam strings espalhadas;
- testes de favoritos e webhook verificam que essas operacoes nao alteram o catalogo base;
- mutacoes locais no snapshot de um teste nao vazam para outro.

## Qualidade Orientada a Experiencia

A API foi avaliada como base de uma experiencia publica: encontravel, previsivel e inclusiva. A analise completa esta em [docs/UX_QUALITY.md](docs/UX_QUALITY.md).

Foram testados:

- jornada real de busca, detalhe e recomendacao;
- clareza minima do conteudo dos servicos;
- estabilidade das categorias para consumo no front-end;
- busca por linguagem de necessidade;
- ordenacao por relevancia;
- normalizacao de termos comuns digitados por usuarios.

## Performance

Os thresholds atuais sao uma primeira barra de producao para uma API municipal de consulta:

| Metrica | Threshold | Motivo |
|---|---:|---|
| `http_req_failed` | `< 1%` | Falhas devem ser raras em servico publico de consulta. |
| `checks` | `> 99%` | Resposta precisa ser correta, nao so rapida. |
| `dropped_iterations` | `0` | Indica que a carga configurada foi atendida. |
| `p95` global | `< 300ms` | Mantem listagem/busca perceptivelmente rapidas. |
| `p99` global | `< 750ms` | Controla cauda de latencia no smoke. |

O smoke de CI roda por 45 segundos cobrindo health, listagem, detalhe, busca, recomendacoes e webhook. A estimativa usada: se o catalogo tiver 20 mil acessos/dia e 20% ocorrerem em uma janela de pico de 2 horas, isso representa cerca de 33 requisicoes/minuto. Com usuarios navegando por alguns segundos entre telas, 50 VUs e uma carga conservadora para detectar regressao sem deixar o CI lento.

Limite da evidencia: a API roda em memoria, sem banco, rede real, cache externo ou infraestrutura de producao. Por isso, os numeros locais servem como smoke/regressao, nao como prova final de capacidade.

Evidencia detalhada: [docs/PERFORMANCE_EVIDENCE.md](docs/PERFORMANCE_EVIDENCE.md).

## CI e Relatorios

O workflow `.github/workflows/quality.yml`:

| Etapa | Objetivo |
|---|---|
| Start API | Sobe a API com Docker Compose |
| Install | Instala dependencias Python |
| Lint | Executa `ruff check` e `ruff format --check` |
| Quality gate | Roda `pytest -m "not known_bug"` |
| Release evidence | Coleta bugs criticos/seguranca conhecidos |
| Diagnostic evidence | Coleta bugs medios/baixos e UX |
| Summary | Gera resumo consolidado no GitHub Step Summary |
| Artifacts | Publica HTML, JUnit XML e `quality-summary.md` |
| k6 smoke | Executa performance com imagem Docker oficial do k6 |

### Exemplos de relatorios gerados localmente

Os exemplos abaixo foram gerados com `make reports` e resumidos em texto para evitar expor usuario da maquina, caminhos locais ou stack traces completos.

| Relatorio | Resultado | Leitura |
|---|---|---|
| `reports/quality-summary.md` | `72` testes nos gates | Visao geral para CI e decisao de release |
| `reports/pytest-report.html` | `49 passed, 23 deselected` | Quality gate funcional verde |
| `reports/release-gate-report.html` | `10 failed, 62 deselected` | Bugs criticos/seguranca reproduziveis |
| `reports/known-bugs-report.html` | `13 failed, 59 deselected` | Bugs diagnosticos e UX reproduziveis |

Exemplo do `quality-summary.md`:

```text
Quality gate funcional: 49/49 passed
Release blockers conhecidos: 10
Bugs diagnosticos conhecidos: 13

Quality Lenses:
- API contract and schema: 40 tests mapped
- Negative and edge cases: 25 tests mapped
- Security and authorization: 12 tests mapped
- Test data management: 4 tests mapped
- UX and API usability: 6 tests mapped
- Resilience: 5 tests mapped
```

## Documentacao Complementar

| Documento | Conteudo |
|---|---|
| [docs/BUGS.md](docs/BUGS.md) | Bugs, impacto e reproducao |
| [docs/EXECUTION.md](docs/EXECUTION.md) | Resultado de execucao local real |
| [docs/PERFORMANCE_EVIDENCE.md](docs/PERFORMANCE_EVIDENCE.md) | Evidencia e justificativa de performance |
| [docs/RISK_TRACEABILITY.md](docs/RISK_TRACEABILITY.md) | Risco, requisito, teste e evidencia |
| [docs/RELEASE_WAIVERS.md](docs/RELEASE_WAIVERS.md) | Politica de waiver para release |
| [docs/UX_QUALITY.md](docs/UX_QUALITY.md) | Analise de usabilidade da API |
| [docs/QA_EVALUATION.md](docs/QA_EVALUATION.md) | Resposta aos criterios do desafio |

## O Que Faria Com Mais Tempo

- Expandiria contract testing com Schemathesis gerando casos automaticamente a partir do `openapi.yaml`.
- Adicionaria property-based testing com Hypothesis para busca, paginacao e payloads.
- Criaria cenarios de resiliencia com falhas de rede controladas por proxy, como timeout e conexao recusada.
- Separaria uma suite de endurance para execucao agendada mais longa fora do CI de pull request.
- Evoluiria test data management para uma API com estado persistente, usando setup/teardown ou factories.
