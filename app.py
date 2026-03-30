from flask import Flask, render_template, request, jsonify, session
from functools import wraps
import hashlib
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# ---------- DONNÉES EN MÉMOIRE ----------
# users: { username: hashed_password }
users = {}
# tasks: { username: [ {id, text, done, prio, cat, date}, ... ] }
user_tasks = {}
# next_id par user
user_next_id = {}


def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

# ---------- DÉCORATEUR AUTH ----------


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "username" not in session:
            return jsonify({"error": "Non authentifié"}), 401
        return f(*args, **kwargs)
    return decorated

# ---------- ROUTES HTML ----------


@app.route("/")
def home():
    return render_template("todo.html")

# ---------- AUTH ----------


@app.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json()
    username = (data.get("username") or "").strip().lower()
    password = (data.get("password") or "").strip()

    if not username or not password:
        return jsonify({"error": "Champs requis"}), 400
    if len(username) < 3:
        return jsonify({"error": "Pseudo trop court (min 3 caractères)"}), 400
    if len(password) < 4:
        return jsonify({"error": "Mot de passe trop court (min 4 caractères)"}), 400
    if username in users:
        return jsonify({"error": "Ce pseudo est déjà pris"}), 409

    users[username] = hash_pw(password)
    user_tasks[username] = []
    user_next_id[username] = 1
    session["username"] = username
    return jsonify({"username": username}), 201


@app.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    username = (data.get("username") or "").strip().lower()
    password = (data.get("password") or "").strip()

    if not username or not password:
        return jsonify({"error": "Champs requis"}), 400
    if username not in users or users[username] != hash_pw(password):
        return jsonify({"error": "Pseudo ou mot de passe incorrect"}), 401

    session["username"] = username
    return jsonify({"username": username}), 200


@app.route("/auth/logout", methods=["POST"])
def logout():
    session.pop("username", None)
    return jsonify({"message": "Déconnecté"}), 200


@app.route("/auth/me", methods=["GET"])
def me():
    if "username" in session:
        return jsonify({"username": session["username"]}), 200
    return jsonify({"username": None}), 200

# ---------- TÂCHES ----------


@app.route("/tasks", methods=["GET"])
@login_required
def get_tasks():
    u = session["username"]
    return jsonify(user_tasks.get(u, []))


@app.route("/tasks", methods=["POST"])
@login_required
def add_task():
    u = session["username"]
    data = request.get_json()
    if not data:
        return jsonify({"error": "Aucune donnée reçue"}), 400

    text = (data.get("text") or "").strip()
    prio = data.get("prio", "moyenne")
    cat = data.get("cat",  "Perso")
    date = data.get("date", "")

    if not text:
        return jsonify({"error": "Tâche vide"}), 400

    nid = user_next_id.get(u, 1)
    new_task = {"id": nid, "text": text, "done": False,
                "prio": prio, "cat": cat, "date": date}
    user_tasks[u].insert(0, new_task)
    user_next_id[u] = nid + 1
    return jsonify(new_task), 201


@app.route("/tasks/<int:task_id>/toggle", methods=["POST"])
@login_required
def toggle_task(task_id):
    u = session["username"]
    for task in user_tasks.get(u, []):
        if task["id"] == task_id:
            task["done"] = not task["done"]
            return jsonify(task)
    return jsonify({"error": "Tâche introuvable"}), 404


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
@login_required
def delete_task(task_id):
    u = session["username"]
    before = len(user_tasks.get(u, []))
    user_tasks[u] = [t for t in user_tasks[u] if t["id"] != task_id]
    if len(user_tasks[u]) == before:
        return jsonify({"error": "Tâche introuvable"}), 404
    return jsonify({"message": "Tâche supprimée"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
