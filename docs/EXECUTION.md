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
49 passed, 23 deselected
```

Release gate bloqueante:

```bash
pytest -m "known_bug and (known_bug_high or security)"
```

Resultado observado:

```text
10 failed, 62 deselected
```

Suite diagnostica de bugs conhecidos:

```bash
pytest -m "known_bug and not (known_bug_high or security)"
```

Resultado observado:

```text
13 failed, 59 deselected
```

As 10 falhas do release gate devem bloquear release enquanto nao forem corrigidas ou formalmente justificadas em `docs/RELEASE_WAIVERS.md`. As 13 falhas diagnosticas representam bugs medios/baixos e riscos de usabilidade documentados em `docs/BUGS.md`.

## Performance

Comando executado:

```bash
k6 run performance/catalog-api.k6.js
```

Resultado observado:

```text
http_req_failed: 0.00%
http_reqs: 35.10/s
dropped_iterations: 0
http_req_duration p(95): 601us
http_req_duration p(99): 1.14ms
checks: 100.00%
```

Todos os thresholds definidos no script passaram.
