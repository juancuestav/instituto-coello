from flask import Blueprint, request, render_template, flash, redirect, url_for, session
from ..database import Database
from ..listados import get_hojas_vida

observacion_bp = Blueprint("observacion", __name__)


# Página principal: muestra el formulario y el listado de observacions
@observacion_bp.route("/", methods=["GET", "POST"])
def index():
    if "user_id" not in session:
        flash("Por favor, inicia sesión para acceder a esta página.", "warning")
        return redirect(url_for("auth.login"))
    
    hojas_vida = get_hojas_vida()

    if request.method == "POST":
        observacion = request.form.get("observacion")
        hoja_vida = request.form.get("hoja_vida")

        if observacion:
            try:
                conn = Database.get_connection()
                with conn.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO observaciones (detalle_observacion, hoja_vida_id, fecha) VALUES (%s, %s, NOW())",
                        (
                            observacion,
                            hoja_vida,
                        ),
                    )
                conn.commit()
                flash("Observación guardada exitosamente.", "success")
            except Exception as e:
                flash(f"Error al guardar el observación: {str(e)}", "danger")
            finally:
                conn.close()
        else:
            flash("El campo de observación no puede estar vacío.", "warning")
        return redirect(url_for("observacion.index"))

    # Consulta todos los observaciones existentes
    try:
        conn = Database.get_connection()
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(
                "SELECT o.id, detalle_observacion, fecha, CONCAT(m.nombre_materia, ' | ', hv.nombres, ' ' , hv.apellidos) as hoja_vida FROM observaciones o INNER JOIN hojas_vida hv ON o.hoja_vida_id = hv.id INNER JOIN materias m ON hv.materia_id = m.id"
            )
            observaciones = cursor.fetchall()
    except Exception as e:
        flash(f"Error al obtener los observaciones: {str(e)}", "danger")
        observaciones = []
    finally:
        conn.close()
    return render_template(
        "observacion/index.html", observaciones=observaciones, hojas_vida=hojas_vida
    )


# Editar un observacion
@observacion_bp.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    hojas_vida = get_hojas_vida()

    if request.method == "POST":
        nuevo_nombre = request.form.get("observacion")
        hoja_vida = request.form.get("hoja_vida")

        if nuevo_nombre:
            try:
                conn = Database.get_connection()
                with conn.cursor() as cursor:
                    cursor.execute(
                        "UPDATE observaciones SET detalle_observacion = %s, hoja_vida_id = %s WHERE id = %s",
                        (nuevo_nombre, hoja_vida, id),
                    )
                conn.commit()
                flash("Observación actualizada exitosamente.", "success")
            except Exception as e:
                flash(f"Error al actualizar el observación: {str(e)}", "danger")
            finally:
                conn.close()
            return redirect(url_for("observacion.index"))

    # Recupera el observacion actual
    try:
        conn = Database.get_connection()
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM observaciones WHERE id = %s", (id,))
            observacion = cursor.fetchone()
    except Exception as e:
        flash(f"Error al obtener el observacion: {str(e)}", "danger")
        observacion = None
    finally:
        conn.close()
    return render_template(
        "observacion/update.html", observacion=observacion, hojas_vida=hojas_vida
    )


# Eliminar un observacion
@observacion_bp.route("/eliminar/<int:id>", methods=["POST"])
def eliminar(id):
    try:
        conn = Database.get_connection()
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM observaciones WHERE id = %s", (id,))
        conn.commit()
        flash("Observación eliminada exitosamente.", "success")
    except Exception as e:
        flash(f"Error al eliminar el observacion: {str(e)}", "danger")
    finally:
        conn.close()
    return redirect(url_for("observacion.index"))
