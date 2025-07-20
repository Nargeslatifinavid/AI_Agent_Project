# AI‑Agent Project

## Prerequisites
* Docker ≥ 24
* Docker Compose (comes with Docker Desktop)

## Quick start

```bash
# 1 – create your local .env
cp .env.example .env
# edit .env and set POSTGRES_PASSWORD (and optionally LLM_MODEL)

# 2 – build & run the stack
docker-compose up -d --build

# 3 – verify services
docker-compose ps        # both `db` and `app` should be "Up"

# 4 – run unit tests
docker-compose exec app pytest -q
