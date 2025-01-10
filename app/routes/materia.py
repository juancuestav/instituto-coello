from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for, session
from ..database import Database

materia_bp = Blueprint("materia", __name__)


@materia_bp.route("/<int:id>", methods=["GET"])
def get_materia(id):
    return jsonify({"message": f"Detalle de la materia con ID {id}"})


# Página principal: muestra el formulario y el listado de materias
@materia_bp.route("/", methods=["GET", "POST"])
def index():
    if "user_id" not in session:
        flash("Por favor, inicia sesión para acceder a esta página.", "warning")
        return redirect(url_for("auth.login"))
    
    if request.method == "POST":
        nombre_materia = request.form.get("nombre_materia")
        if nombre_materia:
            try:
                conn = Database.get_connection()
                with conn.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO materias (nombre_materia) VALUES (%s)", (nombre_materia,)
                    )
                conn.commit()
                flash("Curso guardado exitosamente.", "success")
            except Exception as e:
                flash(f"Error al guardar el curso: {str(e)}", "danger")
            finally:
                conn.close()
        else:
            flash("El campo de curso no puede estar vacío.", "warning")
        return redirect(url_for("materia.index"))

    # Consulta todos los materias existentes
    try:
        conn = Database.get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, nombre_materia FROM materias")
            materias_data = cursor.fetchall()
    except Exception as e:
        flash(f"Error al obtener los materias: {str(e)}", "danger")
        materias_data = []
    finally:
        conn.close()
    return render_template("materia/index.html", materias=materias_data)


# Editar un curso
@materia_bp.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    if request.method == "POST":
        nuevo_nombre = request.form.get("nombre_materia")
        if nuevo_nombre:
            try:
                conn = Database.get_connection()
                with conn.cursor() as cursor:
                    cursor.execute(
                        "UPDATE materias SET nombre_materia = %s WHERE id = %s",
                        (nuevo_nombre, id),
                    )
                conn.commit()
                flash("Curso actualizado exitosamente.", "success")
            except Exception as e:
                flash(f"Error al actualizar el curso: {str(e)}", "danger")
            finally:
                conn.close()
            return redirect(url_for("materia.index"))

    # Recupera el curso actual
    try:
        conn = Database.get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, nombre_materia FROM materias WHERE id = %s", (id,)
            )
            materia = cursor.fetchone()
    except Exception as e:
        flash(f"Error al obtener el curso: {str(e)}", "danger")
        materia = None
    finally:
        conn.close()
    return render_template("materia/update.html", materia=materia)


# Eliminar un curso
@materia_bp.route("/eliminar/<int:id>", methods=["POST"])
def eliminar(id):
    try:
        conn = Database.get_connection()
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM materias WHERE id = %s", (id,))
        conn.commit()
        flash("Materia eliminada exitosamente.", "success")
    except Exception as e:
        error_message = str(e)
        # Diccionario de mensajes para llaves foráneas
        foreign_key_messages = {
            "FK_logros_academicos_hojas_vida": "No se puede eliminar la materia porque está asociado a una hoja de vida. Por favor, primero cambie la materia a la hoja de vida.",
            "FK_faltas_hojas_vida": "No se puede eliminar la materia porque está asociado a una hoja de vida. Por favor, primero cambie la materia a la hoja de vida.",
        }

        # Verificar si el error está relacionado con una llave foránea conocida
        for key, message in foreign_key_messages.items():
            if key in error_message:
                flash(message, "danger")
                break
        else:
            # Mensaje genérico para errores no específicos
            flash(f"Error al eliminar la materia: {error_message}", "danger")
    finally:
        conn.close()
    return redirect(url_for("materia.index"))
