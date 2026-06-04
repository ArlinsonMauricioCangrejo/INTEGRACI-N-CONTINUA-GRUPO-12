"""
Sistema de Gestión de Tickets de Soporte — Contenedor Backend.

API REST en Flask que expone los endpoints de gestión de tickets.
A partir de la Entrega 1 (Semana 3) el backend deja de servir la
interfaz web: la interfaz queda alojada en su propio contenedor
(Frontend) y consume esta API a través del proxy reverso de Nginx,
materializando la separación de responsabilidades exigida por la
arquitectura de contenedores.
"""
import os

from flask import Flask, jsonify, request

from app.database import init_db
from app.models import Ticket
from app.storage import TicketStorage

VERSION = "1.0.0"

app = Flask(__name__)
storage = TicketStorage()

# Crea las tablas en PostgreSQL la primera vez que el contenedor arranca.
init_db()


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "service": "ticket-system-backend",
        "version": VERSION,
        "database": os.environ.get("DATABASE_URL", "sqlite (local)").split("@")[-1],
    })


@app.route("/api/tickets", methods=["GET"])
def list_tickets():
    return jsonify(storage.all())


@app.route("/api/tickets", methods=["POST"])
def create_ticket():
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    if not title:
        return jsonify({"error": "El campo 'title' es obligatorio"}), 400
    try:
        ticket = Ticket.new(
            title=title,
            description=data.get("description", ""),
            priority=data.get("priority", "media"),
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(storage.add(ticket)), 201


@app.route("/api/tickets/<int:ticket_id>", methods=["GET"])
def get_ticket(ticket_id: int):
    ticket = storage.get(ticket_id)
    if ticket is None:
        return jsonify({"error": "Ticket no encontrado"}), 404
    return jsonify(ticket)


@app.route("/api/tickets/<int:ticket_id>", methods=["PUT"])
def update_ticket(ticket_id: int):
    data = request.get_json(silent=True) or {}
    try:
        updated = storage.update(
            ticket_id,
            status=data.get("status"),
            priority=data.get("priority"),
            description=data.get("description"),
            title=data.get("title"),
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    if updated is None:
        return jsonify({"error": "Ticket no encontrado"}), 404
    return jsonify(updated)


@app.route("/api/tickets/<int:ticket_id>", methods=["DELETE"])
def delete_ticket(ticket_id: int):
    if storage.delete(ticket_id):
        return "", 204
    return jsonify({"error": "Ticket no encontrado"}), 404


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV", "production") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)
