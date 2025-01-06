from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for
from ..database import Database

curso_bp = Blueprint("curso", __name__)

# Página principal: muestra el formulario y el listado de cursos
@curso_bp.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        curso = request.form.get("curso")
        if curso:
            try:
                conn = Database.get_connection()
                with conn.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO cursos (nombre_curso) VALUES (%s)", (curso,)
                    )
                conn.commit()
                flash("Curso guardado exitosamente.", "success")
            except Exception as e:
                flash(f"Error al guardar el curso: {str(e)}", "danger")
            finally:
                conn.close()
        else:
            flash("El campo de curso no puede estar vacío.", "warning")
        return redirect(url_for("curso.index"))

    # Consulta todos los cursos existentes
    try:
        conn = Database.get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, nombre_curso FROM cursos")
            cursos_data = cursor.fetchall()
    except Exception as e:
        flash(f"Error al obtener los cursos: {str(e)}", "danger")
        cursos_data = []
    finally:
        conn.close()
    return render_template("curso/index.html", cursos=cursos_data)


# Editar un curso
@curso_bp.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    if request.method == "POST":
        nuevo_nombre = request.form.get("curso")
        if nuevo_nombre:
            try:
                conn = Database.get_connection()
                with conn.cursor() as cursor:
                    cursor.execute(
                        "UPDATE cursos SET nombre_curso = %s WHERE id = %s",
                        (nuevo_nombre, id),
                    )
                conn.commit()
                flash("Curso actualizado exitosamente.", "success")
            except Exception as e:
                flash(f"Error al actualizar el curso: {str(e)}", "danger")
            finally:
                conn.close()
            return redirect(url_for("curso.index"))

    # Recupera el curso actual
    try:
        conn = Database.get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, nombre_curso FROM cursos WHERE id = %s", (id,))
            curso = cursor.fetchone()
    except Exception as e:
        flash(f"Error al obtener el curso: {str(e)}", "danger")
        curso = None
    finally:
        conn.close()
    return render_template("curso/update.html", curso=curso)


# Eliminar un curso
@curso_bp.route("/eliminar/<int:id>", methods=["POST"])
def eliminar(id):
    try:
        conn = Database.get_connection()
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM cursos WHERE id = %s", (id,))
        conn.commit()
        flash("Curso eliminado exitosamente.", "success")
    except Exception as e:
        flash(f"Error al eliminar el curso: {str(e)}", "danger")
    finally:
        conn.close()
    return redirect(url_for("curso.index"))
