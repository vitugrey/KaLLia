FROM python:3.11-slim

# Instala dependências do sistema necessárias para compilar pacotes C (como tgcrypto)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Instala o uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Instala dependências
COPY pyproject.toml ./
RUN uv pip install --system pyrogram tgcrypto httpx loguru

# Copia o código
COPY bot.py ./

CMD ["python", "bot.py"]

