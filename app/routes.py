from flask import Blueprint, jsonify, request
from app.db import db_cursor

bp = Blueprint("notes", __name__)


def _row_to_dict(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "content": row["content"],
        "created_at": row["created_at"],
    }


@bp.route("/health", methods=["GET"])
def health():
    """Health check endpoint used by Docker Compose healthcheck and CI."""
    return jsonify({"status": "healthy"}), 200


@bp.route("/notes", methods=["GET"])
def list_notes():
    with db_cursor() as cur:
        cur.execute("SELECT * FROM notes ORDER BY id ASC")
        rows = cur.fetchall()
    return jsonify([_row_to_dict(r) for r in rows]), 200


@bp.route("/notes", methods=["POST"])
def create_note():
    data = request.get_json(silent=True) or {}
    title = data.get("title")
    content = data.get("content")

    if not title or not content:
        return jsonify({"error": "title and content are required"}), 400

    with db_cursor() as cur:
        cur.execute(
            "INSERT INTO notes (title, content) VALUES (?, ?)", (title, content)
        )
        note_id = cur.lastrowid
        cur.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
        row = cur.fetchone()

    return jsonify(_row_to_dict(row)), 201


@bp.route("/notes/<int:note_id>", methods=["GET"])
def get_note(note_id):
    with db_cursor() as cur:
        cur.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
        row = cur.fetchone()

    if not row:
        return jsonify({"error": "note not found"}), 404
    return jsonify(_row_to_dict(row)), 200


@bp.route("/notes/<int:note_id>", methods=["DELETE"])
def delete_note(note_id):
    with db_cursor() as cur:
        cur.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
        row = cur.fetchone()
        if not row:
            return jsonify({"error": "note not found"}), 404
        cur.execute("DELETE FROM notes WHERE id = ?", (note_id,))

    return jsonify({"message": "deleted"}), 200
