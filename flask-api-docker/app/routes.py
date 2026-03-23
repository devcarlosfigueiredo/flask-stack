"""
Rotas da API, organizadas em dois blueprints: health e tasks.
"""

import logging
from flask import Blueprint, jsonify, request
from app.main import db
from app.models import Task

logger = logging.getLogger(__name__)

# Health check — consultado pelo Docker e por ferramentas de monitoramento.
health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
def health():
    """Retorna o status da aplicação e da conexão com o banco."""
    try:
        db.session.execute(db.text("SELECT 1"))
        db_status = "ok"
    except Exception as exc:  # noqa: BLE001
        logger.warning("Database health check failed: %s", exc)
        db_status = "unavailable"

    return jsonify({"status": "ok", "database": db_status}), 200


tasks_bp = Blueprint("tasks", __name__)


@tasks_bp.get("/tasks")
def list_tasks():
    tasks = Task.query.order_by(Task.created_at.desc()).all()
    return jsonify({"tasks": [t.to_dict() for t in tasks], "total": len(tasks)}), 200


@tasks_bp.post("/tasks")
def create_task():
    data = request.get_json(silent=True) or {}

    title = data.get("title", "").strip()
    if not title:
        return jsonify({"error": "O campo 'title' é obrigatório."}), 400

    task = Task(title=title, description=data.get("description", ""))
    db.session.add(task)
    db.session.commit()
    logger.info("task criada: id=%s title=%s", task.id, task.title)
    return jsonify(task.to_dict()), 201


@tasks_bp.get("/tasks/<int:task_id>")
def get_task(task_id: int):
    task = Task.query.get_or_404(task_id)
    return jsonify(task.to_dict()), 200


@tasks_bp.put("/tasks/<int:task_id>")
def update_task(task_id: int):
    task = Task.query.get_or_404(task_id)
    data = request.get_json(silent=True) or {}

    if "title" in data:
        task.title = data["title"].strip() or task.title
    if "description" in data:
        task.description = data["description"]
    if "done" in data:
        task.done = bool(data["done"])

    db.session.commit()
    logger.info("task atualizada: id=%s", task.id)
    return jsonify(task.to_dict()), 200


@tasks_bp.delete("/tasks/<int:task_id>")
def delete_task(task_id: int):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    logger.info("task removida: id=%s", task_id)
    return jsonify({"message": f"Task {task_id} removida com sucesso."}), 200
