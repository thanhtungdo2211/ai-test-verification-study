# Reproduction scripts

## Mutation testing

After a candidate and the required tests have been frozen:

```bash
uv run python scripts/run_mutation.py --candidate run-01 --suite ai-only
uv run python scripts/run_mutation.py --candidate run-01 --suite full
```

The wrapper runs each configuration in a fresh temporary directory and writes immutable evidence below:

- `results/mutation-ai-only/run-XX/`
- `results/mutation-independent/run-XX/`

It refuses to overwrite an existing non-empty evidence directory. Move an invalid run aside with a documented reason instead of deleting or silently replacing it.

