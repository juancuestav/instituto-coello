from flask import Blueprint, request, render_template, flash, redirect, url_for, jsonify, send_file, session
from ..database import Database
from ..listados import get_hojas_vida, get_materias
from xhtml2pdf import pisa
import io

logro_academico_bp = Blueprint("logro_academico", __name__)

# Página principal: muestra el formulario y el listado de logro academico
@logro_academico_bp.route("/", methods=["GET", "POST"])
def index():
    if "user_id" not in session:
        flash("Por favor, inicia sesión para acceder a esta página.", "warning")
        return redirect(url_for("auth.login"))
    
    hojas_vida = get_hojas_vida()
    materias = get_materias()

    if request.method == "POST":
        logro = request.form.get("logro")
        observacion = request.form.get("observacion")
        hoja_vida = request.form.get("hoja_vida")
        materia = request.form.get("materia")

        if logro:
            try:
                conn = Database.get_connection()
                with conn.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO logros_academicos (logro, observacion, hoja_vida_id, fecha, materia_id) VALUES (%s, %s, %s, NOW(), %s)",
                        (
                            logro,
                            observacion,
                            hoja_vida,
                            materia,
                        ),
                    )
                conn.commit()
                flash("Logro académico guardado exitosamente.", "success")
            except Exception as e:
                flash(f"Error al guardar el logro académico: {str(e)}", "danger")
            finally:
                conn.close()
        else:
            flash("El campo de logro no puede estar vacío.", "warning")
        return redirect(url_for("logro_academico.index"))

    # Consulta todos los logros existentes
    try:
        conn = Database.get_connection()
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(
                "SELECT o.id, logro, observacion, fecha, CONCAT(m.nombre_materia, ' | ', hv.nombres, ' ' , hv.apellidos) as hoja_vida FROM logros_academicos o INNER JOIN hojas_vida hv ON o.hoja_vida_id = hv.id INNER JOIN materias m ON o.materia_id = m.id"
            )
            logros_academicos = cursor.fetchall()
    except Exception as e:
        flash(f"Error al obtener los logros académicos: {str(e)}", "danger")
        logros_academicos = []
    finally:
        conn.close()
    return render_template(
        "logro_academico/index.html", logros_academicos=logros_academicos, hojas_vida=hojas_vida, materias=materias
    )


# Editar un logro academico
@logro_academico_bp.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    hojas_vida = get_hojas_vida()
    materias = get_materias()

    if request.method == "POST":
        logro = request.form.get("logro")
        observacion = request.form.get("observacion")
        hoja_vida = request.form.get("hoja_vida")
        materia = request.form.get("materia")

        if logro:
            try:
                conn = Database.get_connection()
                with conn.cursor() as cursor:
                    cursor.execute(
                        "UPDATE logros_academicos SET logro = %s, observacion = %s, hoja_vida_id = %s, materia_id = %s WHERE id = %s",
                        (logro, observacion, hoja_vida, materia, id),
                    )
                conn.commit()
                flash("Logro académico actualizado exitosamente.", "success")
            except Exception as e:
                flash(f"Error al actualizar el logro académico: {str(e)}", "danger")
            finally:
                conn.close()
            return redirect(url_for("logro_academico.index"))

    # Recupera el logro academico actual
    try:
        conn = Database.get_connection()
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM logros_academicos WHERE id = %s", (id,))
            logro_academico = cursor.fetchone()
    except Exception as e:
        flash(f"Error al obtener el logro académico: {str(e)}", "danger")
        logro_academico = None
    finally:
        conn.close()
    return render_template(
        "logro_academico/update.html", logro_academico=logro_academico, hojas_vida=hojas_vida, materias=materias
    )


# Eliminar un logro academico
@logro_academico_bp.route("/eliminar/<int:id>", methods=["POST"])
def eliminar(id):
    try:
        conn = Database.get_connection()
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM logros_academicos WHERE id = %s", (id,))
        conn.commit()
        flash("Logro académico eliminada exitosamente.", "success")
    except Exception as e:
        flash(f"Error al eliminar el logro académico: {str(e)}", "danger")
    finally:
        conn.close()
    return redirect(url_for("logro_academico.index"))

@logro_academico_bp.route("/imprimir/<int:id>", methods=["GET"])
def imprimir(id):
    try:
        # Obtener observaciones y hoja de vida de la base de datos
        conn = Database.get_connection()
        cursor = conn.cursor(dictionary=True)

        # Obtener logros academicos
        query = """
            SELECT 
            la.*,
            m.nombre_materia as materia,
            u.nombre as docente
            FROM logros_academicos la 
            INNER JOIN hojas_vida hv ON la.hoja_vida_id = hv.id 
            INNER JOIN materias m ON hv.materia_id = m.id 
            INNER JOIN usuarios u ON hv.docente_id = u.id 
            WHERE hoja_vida_id = %s
        """
        cursor.execute(
            query,
            (id,),
        )
        logros_academicos = cursor.fetchall()  # fetchall devuelve una lista de diccionarios

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
    if not logros_academicos:
        flash("No se encontraron logros académicos para esta hoja de vida.", "warning")
        return redirect(url_for("hoja_vida.index"))

    if not hoja_vida:
        flash("No se encontró la hoja de vida especificada.", "warning")
        return redirect(url_for("hoja_vida.index"))

    # Renderizar la plantilla HTML
    try:
        rendered_html = render_template(
            "reportes/logro_academico.html",
            logros_academicos=logros_academicos,
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
        download_name=f"hoja_vida_{id}_logros.pdf",
    )