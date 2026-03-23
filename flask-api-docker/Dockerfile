# Dockerfile — Flask Task Manager API
# Build em dois stages: o primeiro compila as dependências, o segundo
# monta a imagem final sem carregar as ferramentas de compilação.

# Stage 1: builder
# Precisa do gcc para compilar o driver do PostgreSQL (psycopg2).
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia o requirements antes do restante do código para que o Docker
# reaproveite o cache desta layer enquanto só o código mudar.
COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install --prefix=/install --no-cache-dir -r requirements.txt


# Stage 2: runtime
# Parte do mesmo python:3.12-slim limpo, sem gcc nem libpq-dev.
FROM python:3.12-slim AS runtime

LABEL maintainer="seu-nome <voce@email.com>" \
      version="1.0.0" \
      description="Flask Task Manager API"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    PORT=5000

# Apenas a biblioteca de runtime do PostgreSQL, sem ferramentas de compilação.
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 \
    && rm -rf /var/lib/apt/lists/*

# A aplicação roda com um usuário sem privilégios de root.
RUN groupadd --system appgroup && useradd --system --gid appgroup appuser

WORKDIR /app

# Traz os pacotes instalados no stage anterior.
COPY --from=builder /install /usr/local

COPY --chown=appuser:appgroup . .

USER appuser

# EXPOSE é documentação — não publica a porta automaticamente.
EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" \
    || exit 1

# 3 workers cobre bem a maioria dos cenários para uma API simples.
# Ajuste conforme o número de CPUs disponíveis no host.
CMD ["gunicorn", \
     "--bind", "0.0.0.0:5000", \
     "--workers", "3", \
     "--timeout", "60", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "wsgi:application"]
