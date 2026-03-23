"""
Task Manager API — módulo principal.

Usa o padrão app factory (create_app) para facilitar testes e evitar
importações circulares entre os módulos da aplicação.
"""

import os
import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)

db = SQLAlchemy()
migrate = Migrate()


def create_app() -> Flask:
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL",
        "sqlite:///tasks.db",  # fallback para rodar localmente sem Docker
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")

    db.init_app(app)
    migrate.init_app(app, db)

    from app.routes import tasks_bp, health_bp
    app.register_blueprint(health_bp)
    app.register_blueprint(tasks_bp, url_prefix="/api/v1")

    return app
