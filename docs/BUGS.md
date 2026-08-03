# Relatorio de Bugs

Ambiente validado: API local via `docker compose up -d`, porta `8080`.

## BUG-001 - Servico inexistente retorna 500 em vez de 404

Severidade: Alta

Impacto: consumidores da API recebem erro interno para uma entrada esperada de usuario. Isso prejudica observabilidade, mascara erro de negocio como incidente e pode acionar alertas falsos em producao.

Como reproduzir:

```bash
curl -i http://localhost:8080/api/v1/services/s999
```

Resultado atual: `500 Internal Server Error`.

Resultado esperado: `404 Not Found` com corpo consistente, por exemplo `{"error":"service not found"}`.

Teste automatizado: `tests/test_services.py::test_get_unknown_service_returns_404_instead_of_server_error`.

## BUG-002 - Busca com query vazia retorna todos os servicos

Severidade: Media

Impacto: uma busca vazia pode gerar carga desnecessaria e comportamento confuso para o usuario. Em bases maiores, esse padrao aumenta risco de resposta lenta e consumo indevido.

Como reproduzir:

```bash
curl -i -X POST http://localhost:8080/api/v1/services/search \
  -H 'Content-Type: application/json' \
  -d '{"query":""}'
```

Resultado atual: `200 OK` com todos os servicos.

Resultado esperado: `400 Bad Request` com mensagem indicando que `query` e obrigatoria e nao pode ser vazia.

Testes automatizados:

- `tests/test_search.py::test_search_rejects_empty_query`
- `tests/test_search.py::test_search_rejects_blank_query`

## BUG-003 - `total_pages` usa arredondamento para baixo

Severidade: Media

Impacto: clientes podem esconder paginas existentes. Com 11 servicos e `per_page=10`, a API informa 1 pagina, embora exista uma segunda pagina com resultado.

Como reproduzir:

```bash
curl -s 'http://localhost:8080/api/v1/services?page=1&per_page=10'
```

Resultado atual: `total_pages` igual a `1`.

Resultado esperado: `total_pages` igual a `2`.

Teste automatizado: `tests/test_services.py::test_list_services_default_pagination_contract`.

## BUG-004 - Webhook aceita payload sem assinatura HMAC valida

Severidade: Critica

Impacto: sistemas externos poderiam enviar atualizacoes falsas para o catalogo. Para um servico publico, isso e risco de integridade de dados e seguranca.

Como reproduzir:

```bash
curl -i -X POST http://localhost:8080/api/v1/webhooks/catalog \
  -H 'Content-Type: application/json' \
  -d '{"event":"service.deleted","id":"s002"}'
```

Resultado atual: `200 OK`.

Resultado esperado: `401 Unauthorized` para assinatura ausente ou invalida.

Testes automatizados:

- `tests/test_webhook.py::test_webhook_rejects_missing_signature`
- `tests/test_webhook.py::test_webhook_rejects_invalid_signature`

## BUG-005 - Recomendacoes sao acessiveis sem autenticacao

Severidade: Alta

Impacto: o endpoint foi descrito como dado personalizado no codigo da API e deveria estar protegido. Expor recomendacoes sem token quebra a politica de autorizacao esperada.

Como reproduzir:

```bash
curl -i http://localhost:8080/api/v1/services/s002/recommendations
```

Resultado atual: `200 OK`.

Resultado esperado: `401 Unauthorized` sem `Authorization: Bearer qa-challenge-token`.

Teste automatizado: `tests/test_auth_and_recommendations.py::test_recommendations_requires_authorization`.
