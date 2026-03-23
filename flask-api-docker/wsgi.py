"""
Entrypoint para o Gunicorn.

Em produção (dentro do container), o Gunicorn importa este módulo e
serve o objeto `application`. Para rodar localmente sem Docker, basta
executar este arquivo diretamente.

    # produção
    gunicorn wsgi:application

    # desenvolvimento local
    python wsgi.py
"""

from app.main import create_app, db

application = create_app()


@application.cli.command("init-db")
def init_db():
    """Cria as tabelas no banco de dados."""
    with application.app_context():
        db.create_all()
        print("Banco de dados inicializado.")


if __name__ == "__main__":
    application.run(host="0.0.0.0", port=5000, debug=True)
