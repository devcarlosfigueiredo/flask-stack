-- init.sql
-- Executado pelo PostgreSQL na primeira inicialização do container.
-- Cria a estrutura do banco e insere alguns registros de exemplo.

\connect taskmanager;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS tasks (
    id          SERIAL PRIMARY KEY,
    title       VARCHAR(120) NOT NULL,
    description TEXT,
    done        BOOLEAN NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tasks_done ON tasks (done);

-- Mantém updated_at sincronizado automaticamente a cada UPDATE.
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS set_updated_at ON tasks;
CREATE TRIGGER set_updated_at
    BEFORE UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

INSERT INTO tasks (title, description, done) VALUES
    ('Estudar Docker',         'Aprender Dockerfile, volumes e redes',    FALSE),
    ('Configurar CI/CD',       'Pipeline com GitHub Actions',             FALSE),
    ('Ler documentação Flask', 'Blueprints, contexto de app e extensões', TRUE)
ON CONFLICT DO NOTHING;
