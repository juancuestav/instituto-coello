from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for, session
from ..database import Database

jornada_bp = Blueprint("jornada", __name__)


@jornada_bp.route("/<int:id>", methods=["GET"])
def get_jornada(id):
    return jsonify({"message": f"Detalle de la jornada con ID {id}"})


# Página principal: muestra el formulario y el listado de jornadas
@jornada_bp.route("/", methods=["GET", "POST"])
def index():
    if "user_id" not in session:
        flash("Por favor, inicia sesión para acceder a esta página.", "warning")
        return redirect(url_for("auth.login"))
    
    if request.method == "POST":
        nombre_jornada = request.form.get("nombre_jornada").strip()
        if nombre_jornada:
            try:
                conn = Database.get_connection()
                with conn.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO jornadas (nombre_jornada) VALUES (%s)", (nombre_jornada,)
                    )
                conn.commit()
                flash("Curso guardado exitosamente.", "success")
            except Exception as e:
                flash(f"Error al guardar el curso: {str(e)}", "danger")
            finally:
                conn.close()
        else:
            flash("El campo de nombre de jornada no puede estar vacío.", "warning")
        return redirect(url_for("jornada.index"))

    # Consulta todos los jornadas existentes
    try:
        conn = Database.get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, nombre_jornada FROM jornadas")
            jornadas_data = cursor.fetchall()
    except Exception as e:
        flash(f"Error al obtener los jornadas: {str(e)}", "danger")
        jornadas_data = []
    finally:
        conn.close()
    return render_template("jornada/index.html", jornadas=jornadas_data)


# Editar un curso
@jornada_bp.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    if request.method == "POST":
        nuevo_nombre = request.form.get("nombre_jornada").strip()
        if nuevo_nombre:
            try:
                conn = Database.get_connection()
                with conn.cursor() as cursor:
                    cursor.execute(
                        "UPDATE jornadas SET nombre_jornada = %s WHERE id = %s",
                        (nuevo_nombre, id),
                    )
                conn.commit()
                flash("Curso actualizado exitosamente.", "success")
            except Exception as e:
                flash(f"Error al actualizar el curso: {str(e)}", "danger")
            finally:
                conn.close()
            return redirect(url_for("jornada.index"))
        else:
            flash("El campo de nombre de jornada no puede estar vacío.", "warning")

    # Recupera el curso actual
    try:
        conn = Database.get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, nombre_jornada FROM jornadas WHERE id = %s", (id,)
            )
            jornada = cursor.fetchone()
    except Exception as e:
        flash(f"Error al obtener el curso: {str(e)}", "danger")
        jornada = None
    finally:
        conn.close()
    return render_template("jornada/update.html", jornada=jornada)


# Eliminar un curso
@jornada_bp.route("/eliminar/<int:id>", methods=["POST"])
def eliminar(id):
    try:
        conn = Database.get_connection()
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM jornadas WHERE id = %s", (id,))
        conn.commit()
        flash("Curso eliminado exitosamente.", "success")
    except Exception as e:
        flash(f"Error al eliminar el curso: {str(e)}", "danger")
    finally:
        conn.close()
    return redirect(url_for("jornada.index"))
