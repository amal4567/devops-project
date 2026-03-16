from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

tasks = []
next_id = 1


@app.route("/")
def home():
    return render_template("todo.html")


@app.route("/tasks", methods=["GET"])
def get_tasks():
    return jsonify(tasks)


@app.route("/tasks", methods=["POST"])
def add_task():
    global next_id

    data = request.get_json()
    if not data:
        return jsonify({"error": "Aucune donnée reçue"}), 400

    text = (data.get("text") or "").strip()
    prio = data.get("prio", "moyenne")
    cat = data.get("cat", "Perso")
    date = data.get("date", "")

    if not text:
        return jsonify({"error": "Tâche vide"}), 400

    new_task = {
        "id": next_id,
        "text": text,
        "done": False,
        "prio": prio,
        "cat": cat,
        "date": date
    }

    tasks.insert(0, new_task)
    next_id += 1
    return jsonify(new_task), 201


@app.route("/tasks/<int:task_id>/toggle", methods=["POST"])
def toggle_task(task_id):
    for task in tasks:
        if task["id"] == task_id:
            task["done"] = not task["done"]
            return jsonify(task)

    return jsonify({"error": "Tâche introuvable"}), 404


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    global tasks

    before = len(tasks)
    tasks = [task for task in tasks if task["id"] != task_id]

    if len(tasks) == before:
        return jsonify({"error": "Tâche introuvable"}), 404

    return jsonify({"message": "Tâche supprimée"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
