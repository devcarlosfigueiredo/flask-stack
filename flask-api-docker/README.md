# Docker Flask API — Task Manager

API REST para gerenciamento de tarefas, containerizada com Docker. O projeto cobre os principais conceitos de containerização: multi-stage build, orquestração com Docker Compose, reverse proxy com Nginx e banco de dados PostgreSQL com persistência de dados.

---

## Arquitetura

```
                        ┌─────────────────────────────────────────┐
                        │           Docker Network (bridge)        │
                        │                                         │
  Cliente HTTP  ──────► │  [Nginx :80]  ──►  [Flask API :5000]   │
                        │                          │              │
                        │                          ▼              │
                        │                   [PostgreSQL :5432]    │
                        │                          │              │
                        │                   [Volume: pg_data]     │
                        └─────────────────────────────────────────┘
```

| Serviço | Imagem base          | Função                                      |
|---------|----------------------|---------------------------------------------|
| nginx   | nginx:1.27-alpine    | Reverse proxy, ponto de entrada público     |
| api     | python:3.12-slim     | Flask + Gunicorn, lógica de negócio (REST)  |
| db      | postgres:16-alpine   | Banco relacional com persistência em volume |

---

## Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/) >= 24
- [Docker Compose](https://docs.docker.com/compose/) >= 2.20 (incluso no Docker Desktop)

---

## Subindo com Docker Compose

Esta é a forma recomendada de rodar o projeto, pois sobe todos os serviços de uma vez.

**1. Clone o repositório**

```bash
git clone https://github.com/seu-usuario/docker-flask-api.git
cd docker-flask-api
```

**2. Configure as variáveis de ambiente**

```bash
cp .env.example .env
nano .env
```

Preencha ao menos `POSTGRES_PASSWORD` e `SECRET_KEY` antes de continuar.

**3. Suba os serviços**

```bash
docker compose up -d
```

**4. Verifique o status**

```bash
docker compose ps
docker compose logs -f api
```

**5. Acesse a API**

```
http://localhost/health
http://localhost/api/v1/tasks
```

---

## Build e execução manual da imagem

Caso queira rodar apenas o container da API, sem banco de dados:

```bash
# Build da imagem
docker build -t flask-task-api:1.0.0 .

# Rodar o container
docker run -d \
  --name task-api \
  -p 5000:5000 \
  -e SECRET_KEY="sua-chave-secreta" \
  flask-task-api:1.0.0

# Acompanhar os logs
docker logs -f task-api

# Parar e remover
docker stop task-api && docker rm task-api
```

---

## Endpoints

| Método | Rota                 | Descrição                 |
|--------|----------------------|---------------------------|
| GET    | /health              | Health check da aplicação |
| GET    | /api/v1/tasks        | Lista todas as tarefas    |
| POST   | /api/v1/tasks        | Cria uma nova tarefa      |
| GET    | /api/v1/tasks/{id}   | Retorna uma tarefa        |
| PUT    | /api/v1/tasks/{id}   | Atualiza uma tarefa       |
| DELETE | /api/v1/tasks/{id}   | Remove uma tarefa         |

### Exemplos com cURL

```bash
# Listar tarefas
curl http://localhost/api/v1/tasks

# Criar tarefa
curl -X POST http://localhost/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Aprender Kubernetes", "description": "Próximo passo após Docker"}'

# Marcar como concluída
curl -X PUT http://localhost/api/v1/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"done": true}'

# Remover
curl -X DELETE http://localhost/api/v1/tasks/1
```

---

## Gerenciamento dos containers

```bash
# Ver status dos serviços
docker compose ps

# Logs de um serviço específico
docker compose logs -f api
docker compose logs -f db

# Parar os serviços (mantém volumes)
docker compose stop

# Parar e remover os containers (mantém volumes)
docker compose down

# Parar, remover containers e volumes — apaga todos os dados
docker compose down -v

# Rebuild após mudanças no código
docker compose up -d --build api
```

---

## Estrutura do projeto

```
docker-flask-api/
├── app/
│   ├── __init__.py        # pacote Python
│   ├── main.py            # app factory (create_app)
│   ├── models.py          # modelos SQLAlchemy
│   └── routes.py          # blueprints e rotas
├── nginx/
│   └── nginx.conf         # configuração do reverse proxy
├── postgres/
│   └── init.sql           # script de inicialização do banco
├── .dockerignore          # arquivos excluídos do contexto de build
├── .env.example           # template de variáveis de ambiente
├── .gitignore
├── docker-compose.yml     # orquestração multi-container
├── Dockerfile             # multi-stage build
├── requirements.txt       # dependências Python
├── wsgi.py                # entrypoint do Gunicorn
└── README.md
```

---

## Decisões de implementação

### Dockerfile

O build usa dois stages. O primeiro (`builder`) instala o gcc e compila as extensões C do psycopg2. O segundo (`runtime`) copia apenas os pacotes já compilados, sem carregar as ferramentas de build na imagem final. Isso reduz o tamanho da imagem e diminui a superfície de ataque.

A aplicação roda com um usuário sem privilégios de root. A instrução `COPY requirements.txt` fica separada do restante do código para que o Docker reaproveite o cache da layer de dependências enquanto só o código da aplicação muda.

### Docker Compose

O `depends_on` com `condition: service_healthy` garante que o Postgres esteja aceitando conexões antes de a API tentar inicializar. Variáveis marcadas com `:?` no Compose falham imediatamente se não estiverem definidas no `.env`, evitando que a stack suba com configuração incompleta.

A porta 5000 da API não é exposta ao host. Todo o tráfego passa pelo Nginx, que é o único serviço com porta pública.

### Segurança

Credenciais são lidas exclusivamente de variáveis de ambiente. O `.dockerignore` exclui o `.env` do contexto de build para que ele não vaze para dentro da imagem. O Nginx desabilita o header de versão (`server_tokens off`) e adiciona os headers básicos de segurança.

---

## Contribuindo

1. Faça um fork do projeto
2. Crie uma branch: `git checkout -b feature/minha-feature`
3. Commit: `git commit -m 'feat: adiciona minha feature'`
4. Push: `git push origin feature/minha-feature`
5. Abra um Pull Request

---

## Licença

Distribuído sob a licença MIT. Veja `LICENSE` para mais informações.
