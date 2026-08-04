# Desafio QA Senior - Automacao

[![quality](https://github.com/acmmedrado/desafio-qa-senior-prefeitura-rio/actions/workflows/quality.yml/badge.svg)](https://github.com/acmmedrado/desafio-qa-senior-prefeitura-rio/actions/workflows/quality.yml)

Esta entrega monta uma camada de qualidade para o Catalogo de Servicos Publicos. O foco foi validar comportamento de API, seguranca basica, erros, bordas, performance e capacidade de execucao automatica em CI.

## Como executar

Suba a API:

```bash
cd api
docker compose up -d --build
```

Instale as dependencias e rode os testes funcionais:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
```

Tambem ha atalhos via `make`:

```bash
make install
make api
make test
make release-gate
make test-known-bugs
make perf
```

Para rodar apenas o quality gate bloqueante, excluindo bugs ja documentados:

```bash
pytest -m "not known_bug"
```

Para rodar somente os testes que documentam bugs conhecidos:

```bash
pytest -m known_bug
```

Para gerar relatorios locais:

```bash
mkdir -p reports
pytest --junitxml=reports/pytest-junit.xml --html=reports/pytest-report.html --self-contained-html
```

Para rodar performance:

```bash
k6 run performance/catalog-api.k6.js
```

Variaveis suportadas:

- `BASE_URL`: URL da API. Padrao: `http://localhost:8080`
- `AUTH_TOKEN`: token usado pelo k6. Padrao: `qa-challenge-token`
- `WEBHOOK_SECRET`: segredo HMAC usado pelo k6. Padrao: `webhook-secret-2024`

## O que foi priorizado

Priorizei riscos que impediriam colocar a API em producao com confianca:

- Integridade de contrato: formato de resposta, paginacao e consistencia de metadados.
- Tratamento de erro: IDs inexistentes, JSON invalido, entradas vazias e parametros fora do intervalo.
- Autenticacao e autorizacao: endpoint protegido, token invalido, ausencia de token e recomendacoes.
- Seguranca de integracao: validacao HMAC do webhook.
- Performance operacional: smoke/load test com thresholds para latencia e taxa de erro.

O conjunto atual separa dois usos: o quality gate executa `pytest -m "not known_bug"` e deve passar; os testes marcados como `known_bug` documentam defeitos encontrados e devem falhar enquanto os bugs descritos em `docs/BUGS.md` nao forem corrigidos.

## Estrutura

```text
api/                         API fornecida no desafio
tests/                       Testes funcionais e de contrato com pytest
performance/catalog-api.k6.js Teste de carga/smoke com k6
performance/spike.k6.js       Teste manual de pico/stress
docs/BUGS.md                 Bugs encontrados, impacto e reproducao
docs/EXECUTION.md            Resultado de uma execucao local real
docs/RISK_TRACEABILITY.md     Risco, requisito, teste e evidencia
docs/RELEASE_WAIVERS.md       Politica de waiver para bugs bloqueantes
docs/UX_QUALITY.md           Avaliacao da API pela lente de usabilidade
.github/workflows/quality.yml CI de qualidade
```

## Estrategia de cobertura

Os testes foram separados por dominio para facilitar manutencao:

- `test_health.py`: disponibilidade e metadados operacionais.
- `test_services.py`: listagem, paginacao e detalhe de servico.
- `test_search.py`: busca por texto e validacoes de entrada.
- `test_auth_and_recommendations.py`: autorizacao, favoritos e recomendacoes.
- `test_webhook.py`: contrato do webhook e assinatura HMAC.

Usei `pytest` porque e simples, legivel, adequado para testes HTTP e gera artefatos consumiveis pelo CI. Usei `k6` para performance porque permite thresholds declarativos e cenarios de carga reproduziveis sem acoplar a suite funcional a metricas temporais. O contrato observado esta em `openapi.yaml` e algumas respostas sao validadas contra JSON Schema.

## Matriz de cobertura

| Endpoint | Happy path | Erros e bordas | Auth/seguranca | Contrato | Performance |
|---|---:|---:|---:|---:|---:|
| `GET /health` | Sim | N/A | N/A | Sim | Sim |
| `GET /api/v1/services` | Sim | Sim | N/A | Sim | Sim |
| `GET /api/v1/services/:id` | Sim | Sim | N/A | Sim | Sim |
| `POST /api/v1/services/search` | Sim | Sim | N/A | Sim | Sim |
| `GET /api/v1/services/:id/recommendations` | Sim | Sim | Sim | Sim | Sim |
| `POST /api/v1/services/:id/favorite` | Sim | Sim | Sim | Sim | Nao |
| `POST /api/v1/webhooks/catalog` | Sim | Sim | Sim | Sim | Sim |

## Qualidade orientada a experiencia

Alem de validar status code e contrato, esta entrega avalia se a API sustenta uma experiencia publica encontravel, previsivel e inclusiva. A analise completa esta em `docs/UX_QUALITY.md`.

Foram adicionados testes para:

- jornada real de busca, detalhe e recomendacao;
- clareza minima do conteudo dos servicos;
- estabilidade das categorias para consumo no front-end;
- busca por linguagem de necessidade;
- ordenacao por relevancia;
- normalizacao de termos comuns digitados por usuarios.

## Politica de release gate

Os bugs conhecidos sao separados por risco:

- `known_bug_high` e `security`: bloqueiam release e rodam em `make release-gate`.
- demais `known_bug`: rodam como diagnostico em `make test-known-bugs-diagnostic`.

Isso significa que o CI pode ficar vermelho enquanto existirem bugs criticos sem waiver. A politica e os waivers estao documentados em `docs/RISK_TRACEABILITY.md` e `docs/RELEASE_WAIVERS.md`.

## Resultados locais

Uma execucao local real esta registrada em `docs/EXECUTION.md`. Os resultados abaixo foram resumidos em texto para evitar screenshots com usuario, nome da maquina, caminhos locais ou stack traces extensos.

Com a API rodando localmente em `http://localhost:8080`:

| Comando | Resultado esperado | Interpretacao |
|---|---:|---|
| `make lint` | passou | Codigo de testes e scripts formatado/validado com `ruff` |
| `make test` | 34 passed | Quality gate funcional verde |
| `make release-gate` | 5 failed | Bugs criticos/seguranca bloqueando release |
| `make test-known-bugs-diagnostic` | 12 failed | Bugs medios/baixos e riscos de UX documentados |
| `make perf` | passou | Smoke de performance com `0.00%` de falhas HTTP |

Resumo do relatorio consolidado:

```text
Quality gate: 34 passed, 0 failed
Release-blocking known bugs: 5 failed
Non-blocking known bug diagnostics: 12 failed
Performance smoke: 0.00% HTTP failures, dropped_iterations=0
```

## Performance

Os thresholds atuais foram definidos como uma primeira barra de producao para um catalogo municipal de alta consulta e baixa complexidade computacional:

- `http_req_failed < 1%`
- `p95 < 300ms`
- `p99 < 750ms`
- `checks > 99%`

O cenario de CI sobe ate 50 usuarios virtuais por ser um smoke test. Uma forma de justificar esse numero: se o catalogo tiver 20 mil acessos/dia e 20% deles ocorrerem em uma janela de pico de 2 horas, isso representa cerca de 33 requisicoes/minuto. Com usuarios navegando por alguns segundos entre busca, detalhe e recomendacao, 50 VUs e uma carga conservadora para detectar regressao sem deixar o CI lento.

Os tempos observados localmente em microssegundos refletem uma API Go em memoria, sem banco, rede real, cache externo, observabilidade ou infraestrutura de producao. Por isso, os testes de performance aqui servem como smoke/regressao e nao como prova de capacidade final de producao.

Tambem existe um cenario manual de spike/stress:

```bash
make perf-spike
```

Ele sobe ate 150 VUs e usa thresholds menos estritos para observar comportamento sob aumento subido de demanda.

## CI

O workflow `.github/workflows/quality.yml`:

1. Sobe a API com Docker Compose.
2. Instala dependencias Python.
3. Executa lint/format dos testes com `ruff`.
4. Executa o quality gate funcional, excluindo bugs conhecidos.
5. Executa o release gate bloqueante para bugs criticos/seguranca.
6. Executa os testes de bugs conhecidos nao criticos como diagnostico.
7. Gera um resumo consolidado no GitHub Step Summary.
8. Publica os relatorios como artefato.
9. Executa o smoke de performance com k6.
10. Derruba a API ao final.

Como a API atual tem defeitos de severidade media a critica, a suite completa deve falhar ate que eles sejam corrigidos. O gate principal, porem, fica verde para os comportamentos que ja estao corretos.

## O que faria com mais tempo

- Expandiria contract testing com Schemathesis gerando casos automaticamente a partir do `openapi.yaml`.
- Adicionaria property-based testing com Hypothesis para busca, paginacao e payloads.
- Criaria cenarios de resiliencia com falhas de rede/controladas por proxy, como timeout e conexao recusada.
- Separaria uma suite de endurance para execucao agendada mais longa fora do CI de pull request.
- Evoluiria test data management para uma API com estado persistente, evitando dependencia de dados globais fixos.
