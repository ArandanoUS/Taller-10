from flask import Flask, render_template, request, redirect, url_for, flash
import requests

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Configuración de la API REST
API_URL = "http://localhost:5000/api/recetas"

@app.route("/")
def index():
    """Página principal que muestra el listado de recetas."""
    response = requests.get(API_URL)
    if response.status_code != 200:
        flash("❌ No se pudieron cargar las recetas.")
        recetas = []
    else:
        recetas = response.json()
    return render_template("index.html", recetas=recetas)


@app.route("/receta/<nombre>")
def ver_receta(nombre):
    """Ver los detalles de una receta."""
    response = requests.get(f"{API_URL}/{nombre}")
    if response.status_code == 404:
        flash("❌ La receta no existe.")
        return redirect(url_for("index"))

    receta = response.json()
    return render_template("receta.html", nombre=nombre, receta=receta)


@app.route("/agregar", methods=["GET", "POST"])
def agregar_receta():
    """Agregar una nueva receta."""
    if request.method == "POST":
        data = {
            "nombre": request.form["nombre"],
            "ingredientes": request.form["ingredientes"],
            "pasos": request.form["pasos"],
        }
        response = requests.post(API_URL, json=data)
        if response.status_code == 201:
            flash("✅ Receta agregada exitosamente.")
            return redirect(url_for("index"))
        else:
            flash(response.json().get("description", "❌ Error al agregar receta."))
            return redirect(url_for("agregar_receta"))

    return render_template("agregar.html")


@app.route("/editar/<nombre>", methods=["GET", "POST"])
def editar_receta(nombre):
    """Editar una receta existente."""
    if request.method == "POST":
        data = {
            "ingredientes": request.form["ingredientes"],
            "pasos": request.form["pasos"],
        }
        response = requests.put(f"{API_URL}/{nombre}", json=data)
        if response.status_code == 200:
            flash("✅ Receta actualizada exitosamente.")
            return redirect(url_for("ver_receta", nombre=nombre))
        else:
            flash(response.json().get("description", "❌ Error al actualizar receta."))
            return redirect(url_for("editar_receta", nombre=nombre))

    response = requests.get(f"{API_URL}/{nombre}")
    if response.status_code == 404:
        flash("❌ La receta no existe.")
        return redirect(url_for("index"))

    receta = response.json()
    return render_template("editar.html", nombre=nombre, receta=receta)


@app.route("/eliminar/<nombre>", methods=["POST"])
def eliminar_receta(nombre):
    """Eliminar una receta existente."""
    response = requests.delete(f"{API_URL}/{nombre}")
    if response.status_code == 200:
        flash("✅ Receta eliminada exitosamente.")
    else:
        flash(response.json().get("description", "❌ Error al eliminar receta."))

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True, port=8000)
