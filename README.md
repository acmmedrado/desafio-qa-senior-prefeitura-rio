# Desafio Técnico — Engenheiro(a) de Qualidade (QA) Sênior — Automação

## Contexto

Nossa equipe de back-end entregou o Catálogo de Serviços Públicos: uma API que lista e serve serviços municipais para os cariocas, como informações de vacinação, matrícula escolar, regularização de imóvel, benefícios sociais. A API está rodando. O que ainda não existe é uma entidade que verifique se a qualidade está a altura de um serviço desse porte.

Seu trabalho é sanar essa necessidade do zero. Partimos do princípio de que o código pode ter problemas, você vai testar para descobrir.

## A API

```bash
cd api/
docker compose up -d
# disponível em http://localhost:8080
```

| Endpoint | Descrição |
|----------|-----------|
| `GET /health` | Status da API |
| `GET /api/v1/services` | Lista serviços (suporta paginação com `page` e `per_page`) |
| `GET /api/v1/services/:id` | Detalhe de um serviço |
| `POST /api/v1/services/search` | Busca por texto — body: `{"query": "..."}` |
| `GET /api/v1/services/:id/recommendations` | Serviços relacionados |
| `POST /api/v1/webhooks/catalog` | Recebe atualizações de sistemas externos |
| `POST /api/v1/services/:id/favorite` | Marca serviço como favorito |

Autenticação: `Authorization: Bearer qa-challenge-token`

Webhook: o sistema externo assina com HMAC-SHA256. O header é `X-Signature-256: sha256=<hmac>`, o secret é `webhook-secret-2024`.

Não há documentação formal além da informada acima, parte do trabalho é explorar e entender o comportamento da API.

## O que entregar

Um repositório com um conjunto que dê confiança real para colocar essa API em produção. Ferramentas, estrutura e estratégia de cobertura são escolhas suas.

Esperamos encontrar testes que cubram mais do que os caminhos felizes, como: autenticação, erros, validações, comportamentos de borda. Esperamos testes de performance com thresholds que façam sentido para um serviço público de alta demanda. Esperamos um CI rodando os testes automaticamente. E esperamos um documento com os problemas que você encontrou: o que acontece, o que deveria acontecer, como reproduzir e qual o impacto.

O README deve explicar o que você priorizou testar, por que, e o que faria com mais tempo.

## O que olhamos

A cobertura vai além dos happy paths? Os testes de performance são realistas, ou seja, os thresholds fazem sentido para a escala de um app municipal (milhares de pessoas acessando diariamente)? Os bugs estão documentados de forma que qualquer pessoa do time consiga reproduzir sem ajuda? O CI falha quando deveria e passa quando deveria? As escolhas de ferramentas têm justificativa?

## Diferenciais

- Contract testing
- Testes de acessibilidade
- Testes de resiliência (timeouts, falhas intermitentes)
- Relatório de qualidade gerado automaticamente no CI
- Test data management sem estado compartilhado entre testes

---

Dúvidas: **selecao.pcrj@gmail.com**
