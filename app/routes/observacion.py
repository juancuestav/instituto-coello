from flask import Blueprint, request, render_template, flash, redirect, url_for, session
from ..database import Database
from ..listados import get_hojas_vida, get_materias, recuperarId
import re

observacion_bp = Blueprint("observacion", __name__)


# Página principal: muestra el formulario y el listado de observacions
@observacion_bp.route("/", methods=["GET", "POST"])
def index():
    if "user_id" not in session:
        flash("Por favor, inicia sesión para acceder a esta página.", "warning")
        return redirect(url_for("auth.login"))

    hojas_vida = get_hojas_vida()
    materias = get_materias()

    if request.method == "POST":
        observacion = request.form.get("observacion")
        hoja_vida = request.form.get("hoja_vida")
        materia = request.form.get("materia")

        if observacion:
            try:
                conn = Database.get_connection()
                with conn.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO observaciones (detalle_observacion, hoja_vida_id, fecha, materia_id) VALUES (%s, %s, NOW(), %s)",
                        (
                            observacion,
                            hoja_vida,
                            materia,
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
                "SELECT o.id, detalle_observacion, fecha, CONCAT(m.nombre_materia, ' | ', hv.nombres, ' ' , hv.apellidos) as hoja_vida FROM observaciones o INNER JOIN hojas_vida hv ON o.hoja_vida_id = hv.id INNER JOIN materias m ON o.materia_id = m.id"
            )
            observaciones = cursor.fetchall()
    except Exception as e:
        flash(f"Error al obtener los observaciones: {str(e)}", "danger")
        observaciones = []
    finally:
        conn.close()
    return render_template(
        "observacion/index.html",
        observaciones=observaciones,
        hojas_vida=hojas_vida,
        materias=materias,
    )


# Editar un observacion
@observacion_bp.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    hojas_vida = get_hojas_vida()
    materias = get_materias()

    if request.method == "POST":
        nuevo_nombre = request.form.get("observacion")
        hoja_vida = request.form.get("hoja_vida")
        materia = request.form.get("materia")

        if nuevo_nombre:
            try:
                conn = Database.get_connection()
                with conn.cursor() as cursor:
                    cursor.execute(
                        "UPDATE observaciones SET detalle_observacion = %s, hoja_vida_id = %s, materia_id = %s WHERE id = %s",
                        (nuevo_nombre, hoja_vida, materia, id),
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
        "observacion/update.html",
        observacion=observacion,
        hojas_vida=hojas_vida,
        materias=materias,
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


def extraer_valores(frase):
    # Buscar el patrón de cédula
    observacion_match = re.search(r"observación (\w+)", frase)
    observacion = observacion_match.group(1) if observacion_match else None 
    
    hoja_vida_match = re.search(r"hoja de vida ([\w\s]+)", frase)
    hoja_vida = hoja_vida_match.group(1) if hoja_vida_match else None 
    
    materia_match = re.search(r"materia ([\w\s]+)", frase)
    materia = materia_match.group(1) if materia_match else None 

    return (
        observacion,
        hoja_vida,
        materia,
    )


# Crear la consulta SQL
def generar_consulta_sql(
    observacion,
    hoja_vida,
    materia,
):
    condiciones = []
    if observacion:
        condiciones.append(f"LOWER(detalle_observacion) LIKE LOWER('%{observacion}%')")
    if hoja_vida:
        hoja_vida_id = recuperarId("hojas_vida", "nombres", hoja_vida)
        condiciones.append(f"hoja_vida_id = '{hoja_vida_id}'")
    if materia:
        materia_id = recuperarId("materias", "nombre_materia", materia)
        condiciones.append(f"o.materia_id = '{materia_id}'")

    print("Condiciones")
    print(condiciones)

    if condiciones:
        where_clause = " AND ".join(condiciones)
        return f"""
                SELECT o.id, detalle_observacion, fecha, CONCAT(m.nombre_materia, ' | ', hv.nombres, ' ' , hv.apellidos) as hoja_vida FROM observaciones o INNER JOIN hojas_vida hv ON o.hoja_vida_id = hv.id INNER JOIN materias m ON o.materia_id = m.id
                WHERE {where_clause};
                """
    else:
        return "SELECT * FROM observaciones where id = -1;"


@observacion_bp.route("/buscar", methods=["GET"])
def buscar():
    hojas_vida = get_hojas_vida()
    materias = get_materias()

    frase = request.args.get("frase")

    # Extraer valores de la frase
    (
        observacion,
        hoja_vida,
        materia,
    ) = extraer_valores(frase)
    
    print("Valores...")
    print(observacion)
    print(hoja_vida)
    print(materia)

    query = generar_consulta_sql(
        observacion, hoja_vida, materia
    )
    
    print('Voy a buscar...')
    print(query)

    conn = Database.get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query)
    row = cursor.fetchall()
    # conn.close()
    if cursor:
        cursor.close()
    if conn:
        conn.close()

    return render_template(
        "observacion/index.html",
        observaciones=row,
        materias=materias,
        hojas_vida=hojas_vida,
    )
