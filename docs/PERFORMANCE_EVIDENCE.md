# Evidencia de Performance

Esta evidencia foi gerada localmente com a API em `http://localhost:8080` e serve como registro resumido dos testes de performance. Os relatorios brutos de k6 nao sao versionados para evitar ruido no repositorio; o CI executa o mesmo smoke automaticamente.

## Smoke test

Comando:

```bash
make perf
```

Resultado observado:

```text
http_req_failed: 0.00%
checks: 100.00%
dropped_iterations: 0
http_reqs: 35.10 req/s
p95 global: 601 us
p99 global: 1.14 ms
```

Interpretacao:

- todos os thresholds passaram;
- nao houve falhas HTTP;
- nao houve iteracoes descartadas;
- a latencia local ficou muito abaixo dos limites definidos.

## Thresholds

| Metrica | Threshold | Justificativa |
|---|---:|---|
| `http_req_failed` | `< 1%` | Um servico publico de consulta deve tolerar pouquissimas falhas sob carga curta. |
| `checks` | `> 99%` | Garante que as respostas continuem corretas, nao apenas rapidas. |
| `dropped_iterations` | `0` | Indica que a carga configurada foi atendida sem saturacao evidente. |
| `p95` global | `< 300ms` | Barra inicial para manter busca/listagem perceptivelmente rapidas. |
| `p99` global | `< 750ms` | Limite para cauda de latencia em smoke de CI. |

## Escala municipal

Para uma estimativa simples: se o catalogo tiver 20 mil acessos por dia e 20% deles ocorrerem em uma janela de pico de 2 horas, isso representa cerca de 33 requisicoes por minuto. O smoke atual roda por 45 segundos com cenarios constantes cobrindo health, listagem, detalhe, busca, recomendacoes e webhook, chegando a cerca de 35 requisicoes por segundo localmente.

Isso nao prova capacidade final de producao, porque a API do desafio roda em memoria e sem infraestrutura real. O objetivo e detectar regressao de latencia, erro e saturacao no pipeline.

## Spike manual

Comando:

```bash
make perf-spike
```

Uso:

- rodar fora do CI de pull request;
- observar comportamento sob aumento repentino de demanda;
- complementar o smoke automatizado sem deixar o pipeline lento.
