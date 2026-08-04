# Desafio QA Senior - Automacao

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
docs/BUGS.md                 Bugs encontrados, impacto e reproducao
.github/workflows/quality.yml CI de qualidade
```

## Estrategia de cobertura

Os testes foram separados por dominio para facilitar manutencao:

- `test_health.py`: disponibilidade e metadados operacionais.
- `test_services.py`: listagem, paginacao e detalhe de servico.
- `test_search.py`: busca por texto e validacoes de entrada.
- `test_auth_and_recommendations.py`: autorizacao, favoritos e recomendacoes.
- `test_webhook.py`: contrato do webhook e assinatura HMAC.

Usei `pytest` porque e simples, legivel, adequado para testes HTTP e gera artefatos consumiveis pelo CI. Usei `k6` para performance porque permite thresholds declarativos e cenarios de carga reproduziveis sem acoplar a suite funcional a metricas temporais.

## Performance

Os thresholds atuais foram definidos como uma primeira barra de producao para um catalogo municipal de alta consulta e baixa complexidade computacional:

- `http_req_failed < 1%`
- `p95 < 300ms`
- `p99 < 750ms`
- `checks > 99%`

O cenario sobe ate 50 usuarios virtuais por ser um teste smoke de CI. Em uma etapa pre-producao, eu adicionaria cenarios mais longos, ramp-up com centenas de usuarios, teste de pico e teste de endurance.

## CI

O workflow `.github/workflows/quality.yml`:

1. Sobe a API com Docker Compose.
2. Instala dependencias Python.
3. Executa o quality gate funcional, excluindo bugs conhecidos.
4. Executa os testes de bugs conhecidos como diagnostico nao bloqueante.
5. Publica os relatorios como artefato.
6. Executa o smoke de performance com k6.
7. Derruba a API ao final.

Como a API atual tem defeitos de severidade media a critica, a suite completa deve falhar ate que eles sejam corrigidos. O gate principal, porem, fica verde para os comportamentos que ja estao corretos.

## O que faria com mais tempo

- Criaria um OpenAPI inicial a partir do comportamento esperado e adicionaria contract testing formal.
- Separaria testes bloqueantes de release e testes exploratorios/diagnosticos com marcadores de severidade.
- Adicionaria testes de resiliencia para timeouts, reinicio da API e payloads grandes.
- Integraria relatorio consolidado de qualidade no CI com sumario de bugs conhecidos.
- Evoluiria test data management para uma API com estado persistente, evitando dependencia de dados globais fixos.
