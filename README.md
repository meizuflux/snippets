# Snippets


# dev notes: ignore
https://learn.microsoft.com/en-us/windows/wsl/tutorials/wsl-database#install-postgresql


# commands
## dev
```fish
uv run sanic app:app_factory --factory --host=localhost --port=8000 --dev --reload --reload-dir=templates/
```

```fish
docker run --name snippets-postgres -p 5432:5432 -h localhost -e POSTGRES_PASS
WORD=test -e POSTGRES_DB=snippets -d postgres
```

```fish
uv run scripts/sql.py -f sql/schema.sql
```

```
curl -X GET http://localhost:8000/api/v1/auth/about \
     -H "X-API-KEY: "
```