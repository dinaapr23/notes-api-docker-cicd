import pytest
from app import create_app, db


@pytest.fixture
def client():
    app = create_app({"TESTING": True})
    db.reset_db()
    with app.test_client() as client:
        yield client
    db.reset_db()


def test_health_check(client):
    """Quality gate: health endpoint must report healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "healthy"}


def test_list_notes_empty(client):
    response = client.get("/notes")
    assert response.status_code == 200
    assert response.get_json() == []


def test_create_note(client):
    response = client.post("/notes", json={
        "title": "Belajar Docker",
        "content": "Mencoba integrasi Docker, Compose, dan CI/CD",
    })
    assert response.status_code == 201
    body = response.get_json()
    assert body["title"] == "Belajar Docker"
    assert "id" in body


def test_create_note_missing_field(client):
    response = client.post("/notes", json={"title": "Tanpa konten"})
    assert response.status_code == 400


def test_get_note_not_found(client):
    response = client.get("/notes/999")
    assert response.status_code == 404


def test_get_note_after_create(client):
    create_res = client.post("/notes", json={
        "title": "Judul",
        "content": "Isi catatan",
    })
    note_id = create_res.get_json()["id"]

    get_res = client.get(f"/notes/{note_id}")
    assert get_res.status_code == 200
    assert get_res.get_json()["title"] == "Judul"


def test_delete_note(client):
    create_res = client.post("/notes", json={
        "title": "Hapus saya",
        "content": "isi",
    })
    note_id = create_res.get_json()["id"]

    delete_res = client.delete(f"/notes/{note_id}")
    assert delete_res.status_code == 200

    get_res = client.get(f"/notes/{note_id}")
    assert get_res.status_code == 404

def test_simulasi_gagal():
    assert False
