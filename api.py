from flask import Flask, request, jsonify, abort
import redis
from waitress import serve

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Configuración de KeyDB
keydb = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

# === API REST ===
@app.route("/api/recetas", methods=["GET"])
def obtener_recetas():
    """Obtener todas las recetas."""
    try:
        claves = keydb.keys()
        recetas = [{"nombre": clave} for clave in claves]
        return jsonify(recetas)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/recetas/<nombre>", methods=["GET"])
def obtener_receta(nombre):
    """Obtener los detalles de una receta."""
    if not keydb.exists(nombre):
        abort(404, description="Receta no encontrada")
    receta = keydb.hgetall(nombre)
    return jsonify(receta)


@app.route("/api/recetas", methods=["POST"])
def agregar_receta():
    """Agregar una nueva receta."""
    data = request.json
    nombre = data.get("nombre")
    ingredientes = data.get("ingredientes")
    pasos = data.get("pasos")

    if not nombre or not ingredientes or not pasos:
        abort(400, description="Faltan datos requeridos")

    if keydb.exists(nombre):
        abort(400, description="La receta ya existe")

    keydb.hset(nombre, mapping={"ingredientes": ingredientes, "pasos": pasos})
    return jsonify({"message": "Receta creada exitosamente"}), 201


@app.route("/api/recetas/<nombre>", methods=["PUT"])
def actualizar_receta(nombre):
    """Actualizar una receta existente."""
    if not keydb.exists(nombre):
        abort(404, description="Receta no encontrada")

    data = request.json
    ingredientes = data.get("ingredientes")
    pasos = data.get("pasos")

    if not ingredientes or not pasos:
        abort(400, description="Faltan datos requeridos")

    keydb.hset(nombre, mapping={"ingredientes": ingredientes, "pasos": pasos})
    return jsonify({"message": "Receta actualizada exitosamente"})


@app.route("/api/recetas/<nombre>", methods=["DELETE"])
def eliminar_receta(nombre):
    """Eliminar una receta."""
    if not keydb.exists(nombre):
        abort(404, description="Receta no encontrada")

    keydb.delete(nombre)
    return jsonify({"message": "Receta eliminada exitosamente"})


# Iniciar la aplicación
if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=5000)
