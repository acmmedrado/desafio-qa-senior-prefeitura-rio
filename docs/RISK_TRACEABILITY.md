# Matriz de Rastreabilidade

| Requisito/Risco | Tipo | Testes | Evidencia/Bug |
|---|---|---|---|
| API deve estar operacional | Funcional | `test_health_returns_operational_metadata`, `test_health_matches_openapi_contract` | Quality gate |
| Listagem deve ser paginada corretamente | Contrato | `test_list_services_default_pagination_contract`, `test_list_services_total_pages_uses_ceiling_for_smaller_page_size` | BUG-003 |
| Detalhe inexistente deve permitir recuperacao | Funcional/erro | `test_get_unknown_service_returns_404_instead_of_server_error` | BUG-001 |
| Busca nao deve aceitar entrada vazia | Validacao | `test_search_rejects_empty_query`, `test_search_rejects_blank_query` | BUG-002 |
| Busca deve retornar colecoes previsiveis | Contrato/UX | `test_empty_search_response_matches_openapi_contract`, `test_search_returns_empty_result_set_when_no_service_matches` | BUG-006 |
| Busca deve apoiar encontrabilidade | UX | `test_search_is_accent_insensitive_for_user_typed_text`, `test_search_matches_tags_for_common_user_terms`, `test_search_supports_need_based_language_for_school_enrollment` | BUG-007, BUG-008 |
| Endpoints protegidos devem exigir token | Seguranca | `test_favorite_requires_authorization`, `test_recommendations_requires_authorization` | BUG-005 |
| Webhook deve validar integridade do payload | Seguranca | `test_webhook_rejects_missing_signature`, `test_webhook_rejects_invalid_signature`, `test_webhook_rejects_signature_from_different_payload` | BUG-004 |
| Respostas devem cumprir contrato formal | Contrato | `tests/test_contract.py` | OpenAPI + JSON Schema |
| API deve lidar com carga curta | Performance | `performance/catalog-api.k6.js` | CI smoke |
| API deve lidar com pico manual | Performance | `performance/spike.k6.js` | Execucao manual |
| API deve resistir a entradas extremas | Resiliencia | `tests/test_resilience.py`, payload grande de webhook | Quality gate |
| Testes nao devem compartilhar estado mutavel | Test data management | `tests/test_data_management.py`, fixtures `catalog_snapshot` e `catalog` | Quality gate |

## Politica de Gate

- `make test`: valida comportamentos corretos e deve ficar verde.
- `make release-gate`: executa bugs conhecidos de alta severidade ou seguranca e deve bloquear release enquanto falhar localmente.
- `make test-known-bugs-diagnostic`: executa riscos medios/baixos e UX como diagnostico nao bloqueante.
- `make reports`: gera JUnit, HTML e resumo consolidado.

No CI, os bugs conhecidos sao coletados como evidencia e publicados no resumo consolidado. O workflow deve falhar apenas quando o quality gate de comportamentos aceitos falhar.

Estado atual validado localmente:

- Quality gate: 38 testes passando.
- Release gate: 5 falhas bloqueantes.
- Diagnostico nao bloqueante: 12 falhas conhecidas.

## Criterio de Waiver

Um bug em `release-gate` so deveria ser aceito temporariamente com:

- responsavel nomeado;
- justificativa de negocio;
- impacto conhecido;
- mitigacao temporaria;
- data de expiracao;
- plano de correcao.
