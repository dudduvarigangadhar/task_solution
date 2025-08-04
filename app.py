import os
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from init_db import get_db, close_db, init_db  
from dotenv import load_dotenv

load_dotenv()


def create_app():
    app = Flask(__name__)
    app.teardown_appcontext(close_db)

    
    with app.app_context():
        init_db()


    @app.route("/")
    def home():
        return jsonify({"message": "User Management System"})

    @app.route("/users", methods=["GET"])
    def get_all_users():
        db = get_db()
        cursor = db.execute("SELECT id, name, email, created_at FROM users")
        users = [dict(row) for row in cursor.fetchall()]
        return jsonify(users)

    @app.route("/user/<int:user_id>", methods=["GET"])
    def get_user(user_id):
        db = get_db()
        cursor = db.execute(
            "SELECT id, name, email, created_at FROM users WHERE id = ?", (user_id,)
        )
        user = cursor.fetchone()
        if not user:
            return jsonify({"error": "User not found"}), 404
        return jsonify(dict(user))

    @app.route("/users", methods=["POST"])
    def create_user():
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400

        name = data.get("name", "").strip()
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")

        if not name or not email or not password:
            return jsonify({"error": "name, email, and password are required"}), 400

        hashed = generate_password_hash(password)
        db = get_db()
        try:
            db.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                (name, email, hashed),
            )
            db.commit()
        except Exception as e:
            if "UNIQUE constraint failed: users.email" in str(e):
                return jsonify({"error": "Email already registered"}), 409
            return jsonify({"error": "Database error"}), 500

        return jsonify({"message": "User created successfully"}), 201

    @app.route("/user/<int:user_id>", methods=["PUT"])
    def update_user(user_id):
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400

        name = data.get("name", "").strip()
        email = data.get("email", "").strip().lower()

        if not name or not email:
            return jsonify({"error": "Both name and email required"}), 400

        db = get_db()
        try:
            cursor = db.execute(
                "UPDATE users SET name = ?, email = ? WHERE id = ?",
                (name, email, user_id),
            )
            db.commit()
            if cursor.rowcount == 0:
                return jsonify({"error": "User not found"}), 404
        except Exception as e:
            if "UNIQUE constraint failed: users.email" in str(e):
                return jsonify({"error": "Email already in use"}), 409
            return jsonify({"error": "Database error"}), 500

        return jsonify({"message": "User updated"})

    @app.route("/user/<int:user_id>", methods=["DELETE"])
    def delete_user(user_id):
        db = get_db()
        cursor = db.execute("DELETE FROM users WHERE id = ?", (user_id,))
        db.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "User not found"}), 404
        return jsonify({"message": f"User {user_id} deleted"})

    @app.route("/search", methods=["GET"])
    def search_users():
        name = request.args.get("name", "").strip()
        if not name:
            return jsonify({"error": "Provide name to search"}), 400
        pattern = f"%{name}%"
        db = get_db()
        cursor = db.execute(
            "SELECT id, name, email, created_at FROM users WHERE name LIKE ?", (pattern,)
        )
        users = [dict(row) for row in cursor.fetchall()]
        return jsonify(users)

    @app.route("/login", methods=["POST"])
    def login():
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400

        email = data.get("email", "").strip().lower()
        password = data.get("password", "")

        if not email or not password:
            return jsonify({"error": "Email and password required"}), 400

        db = get_db()
        cursor = db.execute("SELECT id, password FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        if user and check_password_hash(user["password"], password):
            return jsonify({"status": "success", "user_id": user["id"]})
        return jsonify({"status": "failed"}), 401

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 5009))
    app.run(host="0.0.0.0", port=port, debug=True)
