from flask import Blueprint, request, render_template, flash, redirect, url_for, jsonify, send_file, session
from ..database import Database
from ..listados import get_hojas_vida, get_materias, recuperarId
from xhtml2pdf import pisa
import io
import re

falta_bp = Blueprint("falta", __name__)

# Página principal: muestra el formulario y el listado de logro academico
@falta_bp.route("/", methods=["GET", "POST"])
def index():
    if "user_id" not in session:
        flash("Por favor, inicia sesión para acceder a esta página.", "warning")
        return redirect(url_for("auth.login"))
    
    hojas_vida = get_hojas_vida()
    materias = get_materias()

    if request.method == "POST":
        descripcion_falta = request.form.get("descripcion_falta")
        observacion = request.form.get("observacion")
        hoja_vida = request.form.get("hoja_vida")
        materia = request.form.get("materia")

        if descripcion_falta:
            try:
                conn = Database.get_connection()
                with conn.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO faltas (descripcion_falta, observacion, hoja_vida_id, fecha, materia_id) VALUES (%s, %s, %s, NOW(), %s)",
                        (
                            descripcion_falta,
                            observacion,
                            hoja_vida,
                            materia,
                        ),
                    )
                conn.commit()
                flash("Registro de falta guardado exitosamente.", "success")
            except Exception as e:
                flash(f"Error al guardar el registro de falta: {str(e)}", "danger")
            finally:
                conn.close()
        else:
            flash("El campo descripción de falta no puede estar vacío.", "warning")
        return redirect(url_for("falta.index"))

    # Consulta todos los logros existentes
    try:
        conn = Database.get_connection()
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(
                "SELECT o.id, descripcion_falta, observacion, fecha, CONCAT(m.nombre_materia, ' | ', hv.nombres, ' ' , hv.apellidos) as hoja_vida FROM faltas o INNER JOIN hojas_vida hv ON o.hoja_vida_id = hv.id INNER JOIN materias m ON o.materia_id = m.id"
            )
            faltas = cursor.fetchall()
    except Exception as e:
        flash(f"Error al obtener los logros académicos: {str(e)}", "danger")
        faltas = []
    finally:
        conn.close()
    return render_template(
        "falta/index.html", faltas=faltas, hojas_vida=hojas_vida, materias=materias
    )


# Editar una falta
@falta_bp.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    hojas_vida = get_hojas_vida()
    materias = get_materias()

    if request.method == "POST":
        descripcion_falta = request.form.get("descripcion_falta")
        observacion = request.form.get("observacion")
        hoja_vida = request.form.get("hoja_vida")
        materia = request.form.get("materia")

        if descripcion_falta:
            try:
                conn = Database.get_connection()
                with conn.cursor() as cursor:
                    cursor.execute(
                        "UPDATE faltas SET descripcion_falta = %s, observacion = %s, hoja_vida_id = %s, materia_id = %s WHERE id = %s",
                        (descripcion_falta, observacion, hoja_vida, materia, id),
                    )
                conn.commit()
                flash("Registro de falta actualizado exitosamente.", "success")
            except Exception as e:
                flash(f"Error al actualizar el registro de falta: {str(e)}", "danger")
            finally:
                conn.close()
            return redirect(url_for("falta.index"))

    # Recupera la falta actual
    try:
        conn = Database.get_connection()
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM faltas WHERE id = %s", (id,))
            falta = cursor.fetchone()
    except Exception as e:
        flash(f"Error al obtener el registro de falta: {str(e)}", "danger")
        falta = None
    finally:
        conn.close()
    return render_template(
        "falta/update.html", falta=falta, hojas_vida=hojas_vida, materias=materias
    )


# Eliminar un logro academico
@falta_bp.route("/eliminar/<int:id>", methods=["POST"])
def eliminar(id):
    try:
        conn = Database.get_connection()
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM faltas WHERE id = %s", (id,))
        conn.commit()
        flash("Registro de falta eliminado exitosamente.", "success")
    except Exception as e:
        flash(f"Error al eliminar el registro de falta: {str(e)}", "danger")
    finally:
        conn.close()
    return redirect(url_for("falta.index"))

@falta_bp.route("/imprimir/<int:id>", methods=["GET"])
def imprimir(id):
    try:
        # Obtener observaciones y hoja de vida de la base de datos
        conn = Database.get_connection()
        cursor = conn.cursor(dictionary=True)

        # Obtener faltas
        query = """
            SELECT 
            la.*,
            m.nombre_materia as materia,
            u.nombre as docente
            FROM faltas la 
            INNER JOIN hojas_vida hv ON la.hoja_vida_id = hv.id 
            INNER JOIN materias m ON la.materia_id = m.id 
            INNER JOIN usuarios u ON hv.docente_id = u.id 
            WHERE hoja_vida_id = %s
        """
        cursor.execute(
            query,
            (id,),
        )
        faltas = cursor.fetchall()  # fetchall devuelve una lista de diccionarios

        # Obtener hoja de vida
        query = """
            SELECT 
                hv.id,
                hv.cedula,
                hv.nombres,
                hv.apellidos,
                hv.direccion,
                hv.telefono,
                hv.email,
                hv.representante,
                d.nombre AS docente,
                i.nombre AS inspector_piso,
                p.nombre AS psicologo,
                m.nombre_materia AS materia,
                c.nombre_curso AS curso,
                j.nombre_jornada AS jornada
                FROM hojas_vida hv
                INNER JOIN materias m ON hv.materia_id = m.id
                INNER JOIN cursos c ON hv.curso_id = c.id
                INNER JOIN jornadas j ON hv.jornada_id = j.id
                LEFT JOIN usuarios d ON hv.docente_id = d.id
                LEFT JOIN usuarios i ON hv.inspector_piso_id = i.id
                LEFT JOIN usuarios p ON hv.psicologo_id = p.id
                WHERE hv.id = %s
        """
        cursor.execute(query, (id,))
        hoja_vida = cursor.fetchone()

    except Exception as e:
        return jsonify({"error": f"Error al acceder a la base de datos: {str(e)}"}), 500

    finally:
        # Cerrar conexión y cursor de forma segura
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    # Validar datos obtenidos
    if not faltas:        
        flash("No se encontraron registros de falta para esta hoja de vida.", "warning")
        return redirect(url_for("hoja_vida.index"))

    if not hoja_vida:
        flash("No se encontró la hoja de vida especificada.", "warning")
        return redirect(url_for("hoja_vida.index"))

    # Renderizar la plantilla HTML
    try:
        rendered_html = render_template(
            "reportes/falta.html",
            faltas=faltas,
            hoja_id=id,
            hoja_vida=hoja_vida,
        )
    except Exception as e:
        return jsonify({"error": f"Error al renderizar la plantilla: {str(e)}"}), 500

    # Crear el PDF en memoria
    pdf_buffer = io.BytesIO()
    pisa_status = pisa.CreatePDF(src=rendered_html, dest=pdf_buffer)

    if pisa_status.err:
        return jsonify({"error": "No se pudo generar el PDF"}), 500

    # Retornar el PDF generado
    pdf_buffer.seek(0)
    return send_file(
        pdf_buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"hoja_vida_{id}_faltas.pdf",
    )
    
def extraer_valores(frase):
    # Buscar el patrón de cédula
    descripcion_falta_match = re.search(r"falta (\w+)", frase)
    descripcion_falta = descripcion_falta_match.group(1) if descripcion_falta_match else None 
    
    observacion_match = re.search(r"observación (\w+)", frase)
    observacion = observacion_match.group(1) if observacion_match else None 
    
    hoja_vida_match = re.search(r"hoja de vida ([\w\s]+)", frase)
    hoja_vida = hoja_vida_match.group(1) if hoja_vida_match else None 
    
    materia_match = re.search(r"materia ([\w\s]+)", frase)
    materia = materia_match.group(1) if materia_match else None 

    return (
        descripcion_falta,
        observacion,
        hoja_vida,
        materia,
    )


# Crear la consulta SQL
def generar_consulta_sql(
    descripcion_falta,
    observacion,
    hoja_vida,
    materia,
):
    condiciones = []
    if descripcion_falta:
        condiciones.append(f"LOWER(descripcion_falta) LIKE LOWER('%{descripcion_falta}%')")
    if observacion:
        condiciones.append(f"LOWER(observacion) LIKE LOWER('%{observacion}%')")
    if hoja_vida:
        hoja_vida_id = recuperarId("hojas_vida", "nombres", hoja_vida)
        condiciones.append(f"hoja_vida_id = '{hoja_vida_id}'")
    if materia:
        materia_id = recuperarId("materias", "nombre_materia", materia)
        condiciones.append(f"o.materia_id = '{materia_id}'")

    if condiciones:
        where_clause = " AND ".join(condiciones)
        return f"""
                SELECT o.id, descripcion_falta, observacion, fecha, CONCAT(m.nombre_materia, ' | ', hv.nombres, ' ' , hv.apellidos) as hoja_vida FROM faltas o INNER JOIN hojas_vida hv ON o.hoja_vida_id = hv.id INNER JOIN materias m ON o.materia_id = m.id
                WHERE {where_clause};
                """
    else:
        return "SELECT * FROM faltas where id = -1;"


@falta_bp.route("/buscar", methods=["GET"])
def buscar():
    hojas_vida = get_hojas_vida()
    materias = get_materias()

    frase = request.args.get("frase")

    # Extraer valores de la frase
    (
        descripcion_falta,
        observacion,
        hoja_vida,
        materia,
    ) = extraer_valores(frase)

    query = generar_consulta_sql(
        descripcion_falta, observacion, hoja_vida, materia
    )

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
        "falta/index.html",
        faltas=row,
        materias=materias,
        hojas_vida=hojas_vida,
    )