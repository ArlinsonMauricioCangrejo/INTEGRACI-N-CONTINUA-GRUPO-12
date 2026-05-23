"""
Pruebas automatizadas del Sistema de Gestión de Tickets.

Estas pruebas se ejecutarán automáticamente por Jenkins en la Semana 5
sobre cada cambio publicado en GitHub, garantizando que el contrato de
la API se mantenga estable a lo largo del módulo.
"""
import pytest

from app.main import app, storage


@pytest.fixture
def client():
    storage.clear()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_health_endpoint(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "ok"
    assert data["service"] == "ticket-system"


def test_create_ticket_basic(client):
    res = client.post("/api/tickets", json={"title": "Servidor caído", "priority": "alta"})
    assert res.status_code == 201
    data = res.get_json()
    assert data["id"] == 1
    assert data["title"] == "Servidor caído"
    assert data["priority"] == "alta"
    assert data["status"] == "abierto"


def test_create_ticket_without_title_fails(client):
    res = client.post("/api/tickets", json={"description": "sin titulo"})
    assert res.status_code == 400
    assert "title" in res.get_json()["error"].lower()


def test_create_ticket_with_invalid_priority_fails(client):
    res = client.post("/api/tickets", json={"title": "test", "priority": "urgentisima"})
    assert res.status_code == 400


def test_list_tickets_empty(client):
    res = client.get("/api/tickets")
    assert res.status_code == 200
    assert res.get_json() == []


def test_list_multiple_tickets(client):
    client.post("/api/tickets", json={"title": "T1"})
    client.post("/api/tickets", json={"title": "T2", "priority": "alta"})
    res = client.get("/api/tickets")
    assert res.status_code == 200
    data = res.get_json()
    assert len(data) == 2
    assert data[0]["id"] == 1
    assert data[1]["id"] == 2


def test_get_ticket_by_id(client):
    client.post("/api/tickets", json={"title": "Buscado"})
    res = client.get("/api/tickets/1")
    assert res.status_code == 200
    assert res.get_json()["title"] == "Buscado"


def test_get_nonexistent_ticket_returns_404(client):
    res = client.get("/api/tickets/999")
    assert res.status_code == 404


def test_update_ticket_status(client):
    client.post("/api/tickets", json={"title": "Para procesar"})
    res = client.put("/api/tickets/1", json={"status": "en_progreso"})
    assert res.status_code == 200
    assert res.get_json()["status"] == "en_progreso"


def test_update_ticket_invalid_status_fails(client):
    client.post("/api/tickets", json={"title": "Test"})
    res = client.put("/api/tickets/1", json={"status": "no_existe"})
    assert res.status_code == 400


def test_delete_ticket(client):
    client.post("/api/tickets", json={"title": "Eliminar"})
    res = client.delete("/api/tickets/1")
    assert res.status_code == 204
    assert client.get("/api/tickets/1").status_code == 404


def test_delete_nonexistent_ticket_returns_404(client):
    res = client.delete("/api/tickets/999")
    assert res.status_code == 404


def test_index_page_renders(client):
    res = client.get("/")
    assert res.status_code == 200
    assert b"Sistema de Gesti" in res.data
