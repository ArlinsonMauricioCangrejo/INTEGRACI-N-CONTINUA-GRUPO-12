"""
Sistema de Gestión de Tickets de Soporte.

Aplicación Flask que expone una API REST y una interfaz web mínima para
crear, listar, actualizar y eliminar tickets. Este es el punto de entrada
único del contenedor Backend; el contenedor Frontend de la Semana 3 podrá
seguir consumiendo esta misma API.

Endpoints expuestos:
    GET    /                      Interfaz web
    GET    /api/health            Verificación de salud del servicio
    GET    /api/tickets           Listar tickets
    POST   /api/tickets           Crear ticket
    GET    /api/tickets/<id>      Consultar ticket
    PUT    /api/tickets/<id>      Actualizar ticket
    DELETE /api/tickets/<id>      Eliminar ticket
"""
from flask import Flask, jsonify, render_template, request

from app.models import Ticket
from app.storage import TicketStorage

VERSION = "0.1.0"

app = Flask(__name__)
storage = TicketStorage()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "ticket-system", "version": VERSION})


@app.route("/api/tickets", methods=["GET"])
def list_tickets():
    return jsonify([t.to_dict() for t in storage.all()])


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
    storage.add(ticket)
    return jsonify(ticket.to_dict()), 201


@app.route("/api/tickets/<int:ticket_id>", methods=["GET"])
def get_ticket(ticket_id: int):
    ticket = storage.get(ticket_id)
    if ticket is None:
        return jsonify({"error": "Ticket no encontrado"}), 404
    return jsonify(ticket.to_dict())


@app.route("/api/tickets/<int:ticket_id>", methods=["PUT"])
def update_ticket(ticket_id: int):
    ticket = storage.get(ticket_id)
    if ticket is None:
        return jsonify({"error": "Ticket no encontrado"}), 404
    data = request.get_json(silent=True) or {}
    try:
        ticket.update(
            status=data.get("status"),
            priority=data.get("priority"),
            description=data.get("description"),
            title=data.get("title"),
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(ticket.to_dict())


@app.route("/api/tickets/<int:ticket_id>", methods=["DELETE"])
def delete_ticket(ticket_id: int):
    if storage.delete(ticket_id):
        return "", 204
    return jsonify({"error": "Ticket no encontrado"}), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
