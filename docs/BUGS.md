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

Testes automatizados:

- `tests/test_services.py::test_get_unknown_service_returns_404_instead_of_server_error`
- `tests/test_services.py::test_get_unknown_service_handles_adversarial_ids_without_server_error`

Observacao adicional: o mesmo comportamento foi observado com variacoes adversariais de ID inexistente, como entrada SQL-like, unicode parecido, string muito longa e whitespace. Isso indica que o problema nao esta restrito a um ID inexistente simples.

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
- `tests/test_search.py::test_search_rejects_missing_query_field`

## BUG-003 - `total_pages` usa arredondamento para baixo

Severidade: Media

Impacto: clientes podem esconder paginas existentes. Com 11 servicos e `per_page=10`, a API informa 1 pagina, embora exista uma segunda pagina com resultado.

Como reproduzir:

```bash
curl -s 'http://localhost:8080/api/v1/services?page=1&per_page=10'
```

Resultado atual: `total_pages` igual a `1`.

Resultado esperado: `total_pages` igual a `2`.

Testes automatizados:

- `tests/test_services.py::test_list_services_default_pagination_contract`
- `tests/test_services.py::test_list_services_total_pages_uses_ceiling_for_smaller_page_size`

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
- `tests/test_webhook.py::test_webhook_rejects_signature_created_with_wrong_secret`
- `tests/test_webhook.py::test_webhook_rejects_signature_from_different_payload`

## BUG-005 - Recomendacoes sao acessiveis sem autenticacao

Severidade: Alta

Impacto: o endpoint foi descrito como dado personalizado no codigo da API e deveria estar protegido. Expor recomendacoes sem token quebra a politica de autorizacao esperada.

Como reproduzir:

```bash
curl -i http://localhost:8080/api/v1/services/s002/recommendations
```

Resultado atual: `200 OK`.

Resultado esperado: `401 Unauthorized` sem `Authorization: Bearer qa-challenge-token` ou com token/esquema invalido.

Testes automatizados:

- `tests/test_auth_and_recommendations.py::test_recommendations_requires_authorization`
- `tests/test_auth_and_recommendations.py::test_recommendations_rejects_invalid_authorization_variants`

## BUG-006 - Busca sem resultados retorna `null` em vez de lista vazia

Severidade: Baixa

Impacto: clientes precisam tratar dois tipos possiveis para `results`: lista quando ha resultados e `null` quando nao ha. Isso aumenta complexidade no front-end e pode causar erro em consumidores que esperam sempre uma colecao iteravel.

Como reproduzir:

```bash
curl -i -X POST http://localhost:8080/api/v1/services/search \
  -H 'Content-Type: application/json' \
  -d '{"query":"termo-sem-correspondencia"}'
```

Resultado atual: `200 OK` com `"results": null`.

Resultado esperado: `200 OK` com `"results": []`.

Teste automatizado: `tests/test_search.py::test_search_returns_empty_result_set_when_no_service_matches`.

## BUG-007 - Busca nao tolera acentos, espacos e termos de tags

Severidade: Media

Impacto: usuarios reais tendem a digitar termos sem acento, com espacos acidentais ou palavras comuns que aparecem como tags. A busca atual pode retornar zero resultados para servicos existentes, criando falsa indisponibilidade do servico.

Exemplos de reproducao:

```bash
curl -i -X POST http://localhost:8080/api/v1/services/search \
  -H 'Content-Type: application/json' \
  -d '{"query":"vacinacao"}'
```

```bash
curl -i -X POST http://localhost:8080/api/v1/services/search \
  -H 'Content-Type: application/json' \
  -d '{"query":"  saude  "}'
```

```bash
curl -i -X POST http://localhost:8080/api/v1/services/search \
  -H 'Content-Type: application/json' \
  -d '{"query":"onibus"}'
```

Resultado atual: a API retorna zero resultados ou `results: null` para termos que deveriam encontrar servicos relevantes.

Resultado esperado: busca normalizada por acento/espaco e considerando `tags`, retornando servicos como `s002`, `s010` e `s006` nos exemplos acima.

Testes automatizados:

- `tests/test_search.py::test_search_is_accent_insensitive_for_user_typed_text`
- `tests/test_search.py::test_search_trims_surrounding_spaces`
- `tests/test_search.py::test_search_matches_tags_for_common_user_terms`

## BUG-008 - Busca nao atende linguagem de necessidade e ordenacao por relevancia

Severidade: Media

Impacto: usuarios de servicos publicos costumam buscar pela necessidade que possuem, nao pelo nome oficial do servico. Se a API nao entende termos como `matricular filho` ou `abrir comercio`, o front-end pode exibir zero resultados para uma necessidade atendida pelo catalogo. Alem disso, sem criterio de relevancia, um resultado menos adequado pode aparecer antes do servico mais provavel.

Exemplos de reproducao:

```bash
curl -i -X POST http://localhost:8080/api/v1/services/search \
  -H 'Content-Type: application/json' \
  -d '{"query":"matricular filho"}'
```

```bash
curl -i -X POST http://localhost:8080/api/v1/services/search \
  -H 'Content-Type: application/json' \
  -d '{"query":"abrir comercio"}'
```

```bash
curl -i -X POST http://localhost:8080/api/v1/services/search \
  -H 'Content-Type: application/json' \
  -d '{"query":"familia"}'
```

Resultado atual: buscas por necessidade podem retornar zero resultados, e a ordenacao nao prioriza necessariamente o servico cujo titulo e mais relevante.

Resultado esperado: a busca deveria considerar sinonimos/termos populares e ordenar por relevancia, priorizando match em titulo e tags antes de descricao.

Testes automatizados:

- `tests/test_ux_quality.py::test_search_supports_need_based_language_for_school_enrollment`
- `tests/test_ux_quality.py::test_search_supports_need_based_language_for_opening_a_business`
- `tests/test_ux_quality.py::test_search_prioritizes_title_matches_over_description_matches`
