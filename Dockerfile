FROM python:3.10-slim
WORKDIR /app

# libpq + tool
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl gnupg2 \
 && echo "deb http://apt.postgresql.org/pub/repos/apt bookworm-pgdg main" \
      > /etc/apt/sources.list.d/pgdg.list \
 && curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - \
 && apt-get update \
 && apt-get install -y --no-install-recommends libpq5 libpq-dev \
 && rm -rf /var/lib/apt/lists/*



ENV PIP_NO_CACHE_DIR=1 \
    PIP_DEFAULT_TIMEOUT=600 \
    PYTHONUNBUFFERED=1 \
    PIP_EXTRA_INDEX_URL="https://download.pytorch.org/whl/cpu"
# --------------------------------------- #

COPY requirements.txt .
RUN pip install --upgrade "psycopg2-binary>=2.9.10" \
 && pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
