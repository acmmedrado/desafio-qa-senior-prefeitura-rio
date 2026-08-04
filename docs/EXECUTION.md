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
34 passed, 17 deselected
```

Release gate bloqueante:

```bash
pytest -m "known_bug_high or security"
```

Resultado observado:

```text
5 failed, 46 deselected
```

Suite diagnostica de bugs conhecidos:

```bash
pytest -m "known_bug and not (known_bug_high or security)"
```

Resultado observado:

```text
12 failed, 39 deselected
```

As 5 falhas do release gate devem bloquear release enquanto nao forem corrigidas ou formalmente justificadas em `docs/RELEASE_WAIVERS.md`. As 12 falhas diagnosticas representam bugs medios/baixos e riscos de usabilidade documentados em `docs/BUGS.md`.

## Performance

Comando executado:

```bash
k6 run performance/catalog-api.k6.js
```

Resultado observado:

```text
http_req_failed: 0.00%
http_reqs: 35.13/s
dropped_iterations: 0
http_req_duration p(95): 710us
http_req_duration p(99): 1.41ms
checks: 100.00%
```

Todos os thresholds definidos no script passaram.
