# Resumo de Execucao

Ambiente local usado para validacao:

- macOS
- Go `1.26.5`
- k6 `2.1.0`
- Python `3.9.6`
- API executada com `PORT=8080 go run .`

## Testes funcionais

Quality gate bloqueante:

```bash
pytest -m "not known_bug"
```

Resultado observado:

```text
17 passed, 13 deselected
```

Suite de bugs conhecidos:

```bash
pytest -m known_bug
```

Resultado observado:

```text
13 failed, 17 deselected
```

As falhas sao esperadas enquanto os bugs descritos em `docs/BUGS.md` nao forem corrigidos.

## Performance

Comando executado:

```bash
k6 run performance/catalog-api.k6.js
```

Resultado observado:

```text
http_req_failed: 0.00%
http_req_duration p(95): 664.39us
http_req_duration p(99): 938.95us
checks: 100.00%
```

Todos os thresholds definidos no script passaram.
