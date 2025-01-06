from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    send_file,
)
from ..listados import (
    get_docentes,
    get_materias,
    get_cursos,
    get_jornadas,
    get_hojas_vida,
    get_inspectores_piso,
    get_psicologos,
)
from xhtml2pdf import pisa
import io
import re
from ..database import Database

# Crear el Blueprint para hojas de vida
hoja_vida_bp = Blueprint("hoja_vida", __name__)


# Ruta principal para gestionar hojas de vida
@hoja_vida_bp.route("/", methods=["GET", "POST"])
def index():
    # Cargar datos iniciales
    hojas_vida = get_hojas_vida()
    docentes = get_docentes()
    inspectores_piso = get_inspectores_piso()
    psicologos = get_psicologos()
    materias = get_materias()
    cursos = get_cursos()
    jornadas = get_jornadas()

    if request.method == "POST":
        form_data = {
            "cedula": request.form.get("cedula", ""),
            "nombres": request.form.get("nombres", ""),
            "apellidos": request.form.get("apellidos", ""),
            "direccion": request.form.get("direccion", ""),
            "telefono": request.form.get("telefono", ""),
            "email": request.form.get("email", ""),
            "docente": request.form.get("docente"),
            "inspector_piso": request.form.get("inspector_piso"),
            "psicologo": request.form.get("psicologo"),
            "materia": request.form.get("materia"),
            "curso": request.form.get("curso"),
            "jornada": request.form.get("jornada"),
        }

        # Validaciones
        required_fields = [
            "cedula",
            "nombres",
            "apellidos",
            "direccion",
            "telefono",
            "email",
        ]
        for field in required_fields:
            if not form_data[field]:
                flash(f"El campo {field.capitalize()} es obligatorio.", "danger")
                return render_template(
                    "hoja_vida/index.html",
                    hojas_vida=hojas_vida,
                    docentes=docentes,
                    inspectores_piso=inspectores_piso,
                    psicologos=psicologos,
                    materias=materias,
                    cursos=cursos,
                    jornadas=jornadas,
                )

        if len(form_data["cedula"]) != 10 or not form_data["cedula"].isdigit():
            flash("La cédula debe tener 10 dígitos y ser numérica.", "danger")
            return render_template(
                "hoja_vida/index.html",
                hojas_vida=hojas_vida,
                docentes=docentes,
                inspectores_piso=inspectores_piso,
                psicologos=psicologos,
                materias=materias,
                cursos=cursos,
                jornadas=jornadas,
            )

        if len(form_data["telefono"]) < 7 or not form_data["telefono"].isdigit():
            flash("El teléfono debe ser numérico y tener al menos 7 dígitos.", "danger")
            return render_template(
                "hoja_vida/index.html",
                hojas_vida=hojas_vida,
                docentes=docentes,
                inspectores_piso=inspectores_piso,
                psicologos=psicologos,
                materias=materias,
                cursos=cursos,
                jornadas=jornadas,
            )

        if "@" not in form_data["email"]:
            flash("El correo electrónico es inválido.", "danger")
            return render_template(
                "hoja_vida/index.html",
                hojas_vida=hojas_vida,
                docentes=docentes,
                inspectores_piso=inspectores_piso,
                psicologos=psicologos,
                materias=materias,
                cursos=cursos,
                jornadas=jornadas,
            )

        # Guardar en la base de datos
        query = """
            INSERT INTO hojas_vida (
                cedula, nombres, apellidos, direccion, telefono, email,
                docente_id, inspector_piso_id, psicologo_id, materia_id, curso_id, jornada_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        try:
            conn = Database.get_connection()
            with conn.cursor() as cursor:
                cursor.execute(
                    query,
                    (
                        form_data["cedula"],
                        form_data["nombres"],
                        form_data["apellidos"],
                        form_data["direccion"],
                        form_data["telefono"],
                        form_data["email"],
                        form_data["docente"],
                        form_data["inspector_piso"],
                        form_data["psicologo"],
                        form_data["materia"],
                        form_data["curso"],
                        form_data["jornada"],
                    ),
                )
            conn.commit()
            flash("Hoja de vida guardada exitosamente.", "success")
            return redirect(url_for("hoja_vida.index"))
        except Exception as e:
            flash(f"Error al guardar la hoja de vida: {str(e)}", "danger")
        finally:
            conn.close()

    return render_template(
        "hoja_vida/index.html",
        hojas_vida=hojas_vida,
        docentes=docentes,
        inspectores_piso=inspectores_piso,
        psicologos=psicologos,
        materias=materias,
        cursos=cursos,
        jornadas=jornadas,
    )


# Ruta para editar una hoja de vida
@hoja_vida_bp.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    docentes = get_docentes()
    inspectores_piso = get_inspectores_piso()
    psicologos = get_psicologos()
    materias = get_materias()
    cursos = get_cursos()
    jornadas = get_jornadas()

    if request.method == "POST":
        form_data = {
            "cedula": request.form.get("cedula", ""),
            "nombres": request.form.get("nombres", ""),
            "apellidos": request.form.get("apellidos", ""),
            "direccion": request.form.get("direccion", ""),
            "telefono": request.form.get("telefono", ""),
            "email": request.form.get("email", ""),
            "docente": request.form.get("docente"),
            "inspector_piso": request.form.get("inspector_piso"),
            "psicologo": request.form.get("psicologo"),
            "materia": request.form.get("materia"),
            "curso": request.form.get("curso"),
            "jornada": request.form.get("jornada"),
        }

        # Validaciones
        required_fields = [
            "cedula",
            "nombres",
            "apellidos",
            "direccion",
            "telefono",
            "email",
        ]
        for field in required_fields:
            if not form_data[field]:
                flash(f"El campo {field.capitalize()} es obligatorio.", "danger")
                return render_template(
                    "hoja_vida/update.html",
                    hoja_vida=form_data,
                    docentes=docentes,
                    inspectores_piso=inspectores_piso,
                    psicologos=psicologos,
                    materias=materias,
                    cursos=cursos,
                    jornadas=jornadas,
                )

        if len(form_data["cedula"]) != 10 or not form_data["cedula"].isdigit():
            flash("La cédula debe tener 10 dígitos y ser numérica.", "danger")
            return render_template(
                "hoja_vida/update.html",
                hoja_vida=form_data,
                docentes=docentes,
                inspectores_piso=inspectores_piso,
                psicologos=psicologos,
                materias=materias,
                cursos=cursos,
                jornadas=jornadas,
            )

        if len(form_data["telefono"]) < 7 or not form_data["telefono"].isdigit():
            flash("El teléfono debe ser numérico y tener al menos 7 dígitos.", "danger")
            return render_template(
                "hoja_vida/update.html",
                hoja_vida=form_data,
                docentes=docentes,
                inspectores_piso=inspectores_piso,
                psicologos=psicologos,
                materias=materias,
                cursos=cursos,
                jornadas=jornadas,
            )

        if "@" not in form_data["email"]:
            flash("El correo electrónico es inválido.", "danger")
            return render_template(
                "hoja_vida/update.html",
                hoja_vida=form_data,
                docentes=docentes,
                inspectores_piso=inspectores_piso,
                psicologos=psicologos,
                materias=materias,
                cursos=cursos,
                jornadas=jornadas,
            )

        # Actualizar en la base de datos
        try:
            conn = Database.get_connection()
            with conn.cursor() as cursor:
                query = """
                    UPDATE hojas_vida
                    SET cedula = %s, nombres = %s, apellidos = %s, direccion = %s,
                        telefono = %s, email = %s, docente_id = %s, inspector_piso_id = %s,
                        psicologo_id = %s, materia_id = %s, curso_id = %s, jornada_id = %s
                    WHERE id = %s
                """
                cursor.execute(
                    query,
                    (
                        form_data["cedula"],
                        form_data["nombres"],
                        form_data["apellidos"],
                        form_data["direccion"],
                        form_data["telefono"],
                        form_data["email"],
                        form_data["docente"],
                        form_data["inspector_piso"],
                        form_data["psicologo"],
                        form_data["materia"],
                        form_data["curso"],
                        form_data["jornada"],
                        id,
                    ),
                )
                conn.commit()
                flash("Hoja de vida actualizada exitosamente.", "success")
                return redirect(url_for("hoja_vida.index"))
        except Exception as e:
            flash(f"Error al actualizar la hoja de vida: {str(e)}", "danger")
        finally:
            conn.close()

    # Recuperar la hoja de vida
    try:
        conn = Database.get_connection()
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM hojas_vida WHERE id = %s", (id,))
            hoja_vida = cursor.fetchone()
            if not hoja_vida:
                flash("La hoja de vida no existe.", "danger")
                return redirect(url_for("hoja_vida.index"))
    except Exception as e:
        flash(f"Error al obtener la hoja de vida: {str(e)}", "danger")
        return redirect(url_for("hoja_vida.index"))
    finally:
        conn.close()

    return render_template(
        "hoja_vida/update.html",
        hoja_vida=hoja_vida,
        docentes=docentes,
        inspectores_piso=inspectores_piso,
        psicologos=psicologos,
        materias=materias,
        cursos=cursos,
        jornadas=jornadas,
    )


# Ruta para eliminar una hoja de vida
@hoja_vida_bp.route("/eliminar/<int:id>", methods=["POST"])
def eliminar(id):
    try:
        query = "DELETE FROM hojas_vida WHERE id = %s"
        conn = Database.get_connection()
        with conn.cursor() as cursor:
            cursor.execute(query, (id,))
        conn.commit()
        flash(f"Hoja de vida con id {id} eliminada exitosamente.", "success")
    except Exception as e:
        flash(f"Error al eliminar la hoja de vida: {str(e)}", "danger")
    finally:
        if conn:
            conn.close()

    return redirect(url_for("hoja_vida.index"))


@hoja_vida_bp.route("/imprimir/<int:id>", methods=["GET"])
def imprimir(id):
    try:
        # Obtener observaciones y hoja de vida de la base de datos
        conn = Database.get_connection()
        cursor = conn.cursor(dictionary=True)

        # Obtener observaciones
        query = """
            SELECT 
            o.*,
            m.nombre_materia as materia,
            u.nombre as docente,
            u2.nombre as psicologo
            FROM observaciones o 
            INNER JOIN hojas_vida hv ON o.hoja_vida_id = hv.id 
            INNER JOIN materias m ON hv.materia_id = m.id 
            INNER JOIN usuarios u ON hv.docente_id = u.id 
            INNER JOIN usuarios u2 ON hv.psicologo_id = u2.id 
            WHERE hoja_vida_id = %s
        """
        cursor.execute(
            query,
            (id,),
        )
        observaciones = cursor.fetchall()  # fetchall devuelve una lista de diccionarios

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
                c.nombre_curso AS curso
                FROM hojas_vida hv
                INNER JOIN materias m ON hv.materia_id = m.id
                INNER JOIN cursos c ON hv.curso_id = c.id
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
    if not observaciones:
        return (
            jsonify(
                {"error": "No se encontraron observaciones para esta hoja de vida."}
            ),
            404,
        )

    if not hoja_vida:
        return jsonify({"error": "No se encontró la hoja de vida especificada."}), 404

    # Renderizar la plantilla HTML
    try:
        rendered_html = render_template(
            "reportes/hoja_vida.html",
            observaciones=observaciones,
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
        download_name=f"hoja_vida_{id}_observaciones.pdf",
    )

def extraer_valores(frase):
    # Buscar el patrón de cédula
    cedula_match = re.search(r"cedula (\d+)", frase)
    cedula = cedula_match.group(1) if cedula_match else None

    # Buscar el patrón de nombre
    nombre_match = re.search(r"nombres (\w+)", frase)
    nombre = nombre_match.group(1) if nombre_match else None

    # Buscar el patrón de dirección
    direccion_match = re.search(r"direccion ([\w\s]+?)(,| y|$)", frase)
    direccion = direccion_match.group(1).strip() if direccion_match else None

    # Buscar el patrón de teléfono
    telefono_match = re.search(r"telefono (\d+)", frase)
    telefono = telefono_match.group(1) if telefono_match else None

    # Buscar el patrón de email
    email_match = re.search(r"email ([\w._%+-]+@[\w.-]+\.[a-zA-Z]{2,})", frase)
    email = email_match.group(1) if email_match else None

    # Buscar el patrón de jornada
    jornada_match = re.search(r"jornada (\w+)", frase)
    jornada = jornada_match.group(1) if jornada_match else None

    # Buscar el patrón de curso
    curso_match = re.search(r"curso ([\w\s]+)", frase)
    curso = curso_match.group(1).strip() if curso_match else None

    return cedula, nombre, direccion, telefono, email, jornada, curso


# Crear la consulta SQL
def generar_consulta_sql(cedula, nombre, direccion, telefono, email, jornada, curso):
    condiciones = []
    if cedula:
        condiciones.append(f"LOWER(cedula) LIKE LOWER('%{cedula}%')")
    if nombre:
        condiciones.append(f"LOWER(nombres) LIKE LOWER('%{nombre}%')")
    if direccion:
        condiciones.append(f"LOWER(direccion) LIKE LOWER('%{direccion}%')")
    if telefono:
        condiciones.append(f"LOWER(telefono) LIKE LOWER('%{telefono}%')")
    if email:
        condiciones.append(f"LOWER(email) LIKE LOWER('%{email}%')")
    if jornada:
        condiciones.append(f"LOWER(jornada) LIKE LOWER('%{jornada}%')")
    if curso:
        condiciones.append(f"LOWER(curso) LIKE LOWER('%{curso}%')")

    if condiciones:
        where_clause = " AND ".join(condiciones)
        return f"SELECT * FROM hojas_vida WHERE {where_clause};"
    else:
        return "SELECT * FROM hojas_vida;"
    
# "Busca hoja de vida con cedula 0705570679, nombre Juan, direccion Quito, telefono 0987654321, email juan@example.com, jornada matutina y curso matematicas"
@hoja_vida_bp.route("/buscar", methods=["GET"])
def buscar():
    frase = request.args.get("frase")
    print(frase)
    # Cargar datos iniciales
    docentes = get_docentes()
    inspectores_piso = get_inspectores_piso()
    psicologos = get_psicologos()
    materias = get_materias()
    cursos = get_cursos()
    jornadas = get_jornadas()
    
    conn = Database.get_connection()
    cursor = conn.cursor(dictionary=True)

    # Extraer valores de la frase
    cedula, nombre, direccion, telefono, email, jornada, curso = extraer_valores(frase)

    query = generar_consulta_sql(
        cedula, nombre, direccion, telefono, email, jornada, curso
    )

    cursor.execute(query)
    row = cursor.fetchall()
    conn.close()
    
    return render_template(
        "hoja_vida/index.html",
        hojas_vida=row,
        docentes=docentes,
        inspectores_piso=inspectores_piso,
        psicologos=psicologos,
        materias=materias,
        cursos=cursos,
        jornadas=jornadas,
    )
    
# Ruta para buscar hojas de vida
""" @hoja_vida_bp.route("/buscar", methods=["GET"])
def buscar():
    query = request.args.get("query")
    "cedula": request.form.get("cedula", ""),
    # Simular resultados
    resultados = [
        {
            "cedula": "0745874125",
            "nombres": "Pedro Andres",
            "direccion": "Av. Menendez",
            "telefono": "0897654321",
            "email": "pedro@gmail.com",
        }
    ]
    return render_template("hoja_vida/index.html", hojas_de_vida=resultados) """