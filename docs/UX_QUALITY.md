# Qualidade Orientada a Experiencia

Esta avaliacao olha para a API como parte da experiencia do cidadao. Mesmo sem interface grafica, a API define se o front-end consegue oferecer uma busca compreensivel, previsivel e inclusiva.

## Heuristicas aplicadas

### Encontrabilidade

Pergunta: a pessoa consegue encontrar o servico certo sem conhecer o nome oficial?

Riscos observados:

- A busca nao considera `tags`.
- A busca nao normaliza acentos.
- A busca nao remove espacos acidentais.
- A busca nao cobre linguagem de necessidade, como `matricular filho` ou `abrir comercio`.
- Os resultados parecem seguir a ordem do array, nao uma ordenacao por relevancia.

Testes relacionados:

- `test_search_is_accent_insensitive_for_user_typed_text`
- `test_search_trims_surrounding_spaces`
- `test_search_matches_tags_for_common_user_terms`
- `test_search_supports_need_based_language_for_school_enrollment`
- `test_search_supports_need_based_language_for_opening_a_business`
- `test_search_prioritizes_title_matches_over_description_matches`

### Compreensibilidade

Pergunta: os dados retornados ajudam o front-end a explicar o servico?

O que foi validado:

- Todos os servicos ativos possuem titulo.
- Descricoes possuem tamanho minimo para apoiar entendimento.
- Categorias e orgaos estao preenchidos.
- Tags existem em quantidade minima.

Teste relacionado:

- `test_service_content_supports_public_service_comprehension`

### Previsibilidade

Pergunta: a API retorna estruturas consistentes para o front-end?

Riscos observados:

- Busca sem resultado retorna `results: null`, mas deveria retornar `results: []`.
- Paginacao informa `total_pages` incorreto.
- Servico inexistente retorna erro interno em vez de `404`.

Testes relacionados:

- `test_search_returns_empty_result_set_when_no_service_matches`
- `test_list_services_default_pagination_contract`
- `test_get_unknown_service_returns_404_instead_of_server_error`

### Recuperacao de erro

Pergunta: quando algo falha, o front-end consegue orientar a pessoa?

Riscos observados:

- Busca vazia retorna todos os servicos em vez de orientar a pessoa a digitar um termo.
- Falhas de autorizacao e HMAC precisam ser previsiveis para evitar estados ambiguos.

Testes relacionados:

- `test_search_rejects_empty_query`
- `test_search_rejects_blank_query`
- `test_favorite_requires_authorization`
- `test_webhook_rejects_missing_signature`

### Jornada

Pergunta: uma jornada real funciona de ponta a ponta?

Foi validado um fluxo curto:

1. Buscar `vacina`.
2. Encontrar `Vacinação Gratuita`.
3. Abrir o detalhe do servico.
4. Ver recomendacoes relacionadas da mesma categoria.

Teste relacionado:

- `test_user_can_complete_search_to_detail_to_recommendation_journey`

## Recomendacoes de produto/API

- Normalizar busca removendo acentos e espacos laterais.
- Considerar `title`, `description`, `category` e `tags` no indice de busca.
- Adicionar sinonimos e termos populares para servicos publicos.
- Ordenar resultados por relevancia: titulo, tag, descricao, popularidade.
- Retornar colecoes vazias como `[]`, nunca `null`.
- Documentar o contrato de erro para facilitar microcopy no front-end.
- Separar `category` machine-readable de um eventual `category_label` amigavel para exibicao.

## Por que isso importa

Em servico publico, usabilidade nao e apenas conveniencia. Se a busca falha para linguagem comum, a pessoa pode concluir que o servico nao existe. A API precisa sustentar uma experiencia inclusiva para usuarios que nao conhecem siglas, nomes oficiais ou termos administrativos.
