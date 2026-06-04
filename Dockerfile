# Use a imagem base oficial do Python (slim para ser mais leve no Raspberry)
FROM python:3.13-slim

# Instala o gerenciador de pacotes uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Define o diretório de trabalho no container
WORKDIR /app

# Copia os arquivos de dependência do projeto
COPY pyproject.toml uv.lock ./

# Sincroniza as dependências do projeto usando uv (sem fazer cache para reduzir o tamanho da imagem)
RUN uv sync --frozen --no-cache

# Copia o código fonte do projeto
COPY src/ ./src/
COPY main.py config.toml ./

# Cria a pasta data para a persistência do banco SQLite
RUN mkdir -p data

# Expõe a porta em que o FastAPI roda
EXPOSE 1904

# Executa a aplicação usando o ambiente virtual criado pelo uv
CMD ["uv", "run", "python", "main.py"]
