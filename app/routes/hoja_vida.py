from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    send_file,
    session,
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


def cargar_datos_base():
    """Carga los datos base requeridos para las vistas."""
    return {
        "docentes": get_docentes(),
        "inspectores_piso": get_inspectores_piso(),
        "psicologos": get_psicologos(),
        "materias": get_materias(),
        "cursos": get_cursos(),
        "jornadas": get_jornadas(),
    }


def validar_formulario(form_data):
    """Valida los datos del formulario."""
    import re

    errores = []
    # Lista de campos obligatorios
    campos_obligatorios = [
        "cedula",
        "nombres",
        "apellidos",
        "direccion",
        "telefono",
        "email",
    ]

    # Validación de campos obligatorios
    for campo in campos_obligatorios:
        if not form_data.get(campo):
            errores.append(f"El campo {campo.capitalize()} es obligatorio.")

    # Validación de cédula
    cedula = form_data.get("cedula", "")
    if len(cedula) != 10 or not cedula.isdigit():
        errores.append("La cédula debe tener exactamente 10 dígitos numéricos.")

    # Validación de teléfono
    telefono = form_data.get("telefono", "")
    if len(telefono) < 7 or not telefono.isdigit():
        errores.append("El teléfono debe ser numérico y tener al menos 7 dígitos.")

    # Validación de correo electrónico
    email = form_data.get("email", "")
    email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"  # Patrón para validar formato de email
    if not re.match(email_regex, email):
        errores.append(
            "El correo electrónico debe contener un '@' y al menos un punto ('.') en el dominio."
        )
        
    # Validación de nombres
    nombres = form_data.get("nombres", "")
    if not nombres.replace(" ", "").isalpha():
        errores.append("El campo 'nombres' solo puede contener letras y espacios.")
        
    # Validación de nombres
    apellidos = form_data.get("apellidos", "")
    if not apellidos.replace(" ", "").isalpha():
        errores.append("El campo 'apellidos' solo puede contener letras y espacios.")

    return errores


@hoja_vida_bp.route("/", methods=["GET", "POST"])
def index():
    if "user_id" not in session:
        flash("Por favor, inicia sesión para acceder a esta página.", "warning")
        return redirect(url_for("auth.login"))

    datos_base = cargar_datos_base()
    hojas_vida = get_hojas_vida()

    if request.method == "POST":
        form_data = {
            key: request.form.get(key, "")
            for key in [
                "cedula",
                "nombres",
                "apellidos",
                "direccion",
                "telefono",
                "email",
                "docente",
                "inspector_piso",
                "psicologo",
                "materia",
                "curso",
                "jornada",
                "representante",
            ]
        }
        errores = validar_formulario(form_data)

        if errores:
            for error in errores:
                flash(error, "danger")
            return render_template(
                "hoja_vida/index.html", hojas_vida=hojas_vida, **datos_base
            )

        try:
            query = """
                INSERT INTO hojas_vida (
                    cedula, nombres, apellidos, direccion, telefono, email,
                    docente_id, inspector_piso_id, psicologo_id, materia_id, curso_id, jornada_id, representante
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            with Database.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Verificar si el correo ya está registrado
                    cursor.execute("SELECT id FROM hojas_vida WHERE email = %s", (form_data["email"],))
                    existing_user = cursor.fetchone()

                    if existing_user:
                        flash("El correo ya está registrado.", "danger")
                        return redirect(url_for("hoja_vida.index"))
            
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
                            form_data["representante"],
                        ),
                    )
                conn.commit()
            flash("Hoja de vida guardada exitosamente.", "success")
            return redirect(url_for("hoja_vida.index"))
        except Exception as e:
            flash(f"Error al guardar la hoja de vida: {e}", "danger")

    return render_template("hoja_vida/index.html", hojas_vida=hojas_vida, **datos_base)


@hoja_vida_bp.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    datos_base = cargar_datos_base()
    hoja_vida = None

    try:
        with Database.get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM hojas_vida WHERE id = %s", (id,))
                hoja_vida = cursor.fetchone()
        if not hoja_vida:
            flash("La hoja de vida no existe.", "danger")
            return redirect(url_for("hoja_vida.index"))
    except Exception as e:
        flash(f"Error al obtener la hoja de vida: {e}", "danger")
        return redirect(url_for("hoja_vida.index"))

    if request.method == "POST":
        form_data = {
            key: request.form.get(key, "")
            for key in [
                "cedula",
                "nombres",
                "apellidos",
                "direccion",
                "telefono",
                "email",
                "docente",
                "inspector_piso",
                "psicologo",
                "materia",
                "curso",
                "jornada",
                "representante",
            ]
        }
        errores = validar_formulario(form_data)

        if errores:
            for error in errores:
                flash(error, "danger")
            return render_template(
                "hoja_vida/update.html", hoja_vida=hoja_vida, **datos_base
            )

        try:
            query = """
                UPDATE hojas_vida
                SET cedula = %s, nombres = %s, apellidos = %s, direccion = %s,
                    telefono = %s, email = %s, docente_id = %s, inspector_piso_id = %s,
                    psicologo_id = %s, materia_id = %s, curso_id = %s, jornada_id = %s, representante = %s
                WHERE id = %s
            """
            with Database.get_connection() as conn:
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
                            form_data["representante"],
                            id,
                        ),
                    )
                conn.commit()
            flash("Hoja de vida actualizada exitosamente.", "success")
            return redirect(url_for("hoja_vida.index"))
        except Exception as e:
            flash(f"Error al actualizar la hoja de vida: {e}", "danger")

    return render_template("hoja_vida/update.html", hoja_vida=hoja_vida, **datos_base)


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
        error_message = str(e)
        # Diccionario de mensajes para llaves foráneas
        foreign_key_messages = {
            "FK_faltas_hojas_vida": "No se puede eliminar la hoja de vida porque tiene faltas asociadas. Por favor, elimine primero las faltas relacionadas.",
            "FK_logros_academicos_hojas_vida": "No se puede eliminar la hoja de vida porque tiene logros académicos asociados. Por favor, elimine primero los logros relacionados.",
            "FK_observaciones_hojas_vida": "No se puede eliminar la hoja de vida porque tiene observaciones asociadas. Por favor, elimine primero las observaciones relacionadas.",
        }

        # Verificar si el error está relacionado con una llave foránea conocida
        for key, message in foreign_key_messages.items():
            if key in error_message:
                flash(message, "danger")
                break
        else:
            # Mensaje genérico para errores no específicos
            flash(f"Error al eliminar la hoja de vida: {error_message}", "danger")
    finally:
        if conn:
            conn.close()

    return redirect(url_for("hoja_vida.index"))


# Ruta para eliminar una hoja de vida
""" @hoja_vida_bp.route("/eliminar/<int:id>", methods=["POST"])
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

    return redirect(url_for("hoja_vida.index")) """


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
            u2.nombre as psicologo,
            hv.representante
            FROM observaciones o 
            INNER JOIN hojas_vida hv ON o.hoja_vida_id = hv.id 
            INNER JOIN materias m ON o.materia_id = m.id 
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
                hv.representante,
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
        flash("No se encontraron observaciones para esta hoja de vida.", "warning")
        return redirect(url_for("hoja_vida.index"))

    if not hoja_vida:
        flash("No se encontró la hoja de vida especificada.", "warning")
        return redirect(url_for("hoja_vida.index"))

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

    # Buscar el patrón de nombres
    nombres_match = re.search(r"nombres (\w+)", frase)
    nombres = nombres_match.group(1) if nombres_match else None

    # Buscar el patrón de apellidos
    apellidos_match = re.search(r"apellidos (\w+)", frase)
    apellidos = apellidos_match.group(1) if apellidos_match else None

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

    # Buscar el patrón de docente
    docente_match = re.search(r"docente ([\w\s]+)", frase)
    docente = docente_match.group(1).strip() if docente_match else None

    # Buscar el patrón de materia
    materia_match = re.search(r"materia ([\w\s]+)", frase)
    materia = materia_match.group(1).strip() if materia_match else None

    # Buscar el patrón de inspector de piso
    inspector_piso_match = re.search(r"inspector de piso ([\w\s]+)", frase)
    inspector_piso = (
        inspector_piso_match.group(1).strip() if inspector_piso_match else None
    )

    # Buscar el patrón de psicologo
    psicologo_match = re.search(r"psicologo ([\w\s]+)", frase)
    psicologo = psicologo_match.group(1).strip() if psicologo_match else None

    return (
        cedula,
        nombres,
        apellidos,
        direccion,
        telefono,
        email,
        jornada,
        curso,
        docente,
        materia,
        inspector_piso,
        psicologo,
    )


# Crear la consulta SQL
def generar_consulta_sql(
    cedula,
    nombres,
    apellidos,
    direccion,
    telefono,
    email,
    jornada,
    curso,
    docente,
    materia,
    inspector_piso,
    psicologo,
):
    condiciones = []
    if cedula:
        condiciones.append(f"LOWER(cedula) LIKE LOWER('%{cedula}%')")
    if nombres:
        condiciones.append(f"LOWER(nombres) LIKE LOWER('%{nombres}%')")
    if apellidos:
        condiciones.append(f"LOWER(apellidos) LIKE LOWER('%{apellidos}%')")
    if direccion:
        condiciones.append(f"LOWER(direccion) LIKE LOWER('%{direccion}%')")
    if telefono:
        condiciones.append(f"LOWER(telefono) LIKE LOWER('%{telefono}%')")
    if email:
        condiciones.append(f"LOWER(email) LIKE LOWER('%{email}%')")
    if jornada:
        jornada_id = recuperarId("jornadas", "nombre_jornada", jornada)
        condiciones.append(f"jornada_id = '{jornada_id}'")
    if curso:
        curso_id = recuperarId("cursos", "nombre_curso", curso)
        condiciones.append(f"curso_id = '{curso_id}'")
    if docente:
        docente_id = recuperarId("usuarios", "nombre", docente)
        condiciones.append(f"docente_id = '{docente_id}'")
    if materia:
        materia_id = recuperarId("materias", "nombre_materia", materia)
        condiciones.append(f"materia_id = '{materia_id}'")
    if inspector_piso:
        inspector_piso_id = recuperarId("usuarios", "nombre", inspector_piso)
        condiciones.append(f"inspector_piso_id = '{inspector_piso_id}'")
    if psicologo:
        psicologo_id = recuperarId("usuarios", "nombre", psicologo)
        condiciones.append(f"psicologo_id = '{psicologo_id}'")

    if condiciones:
        where_clause = " AND ".join(condiciones)
        return f"""SELECT 
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
                WHERE {where_clause};"""
    else:
        return "SELECT * FROM hojas_vida where id = -1;"


# "Busca hoja de vida con cedula 0705570679, nombre Juan, direccion Quito, telefono 0987654321, email juan@example.com, jornada matutina y curso matematicas"
# @hoja_vida_bp.route("/buscar", methods=["POST"])
@hoja_vida_bp.route("/buscar", methods=["GET"])
def buscar():
    frase = request.args.get("frase")
    # Cargar datos iniciales
    docentes = get_docentes()
    inspectores_piso = get_inspectores_piso()
    psicologos = get_psicologos()
    materias = get_materias()
    cursos = get_cursos()
    jornadas = get_jornadas()

    # Extraer valores de la frase
    (
        cedula,
        nombres,
        apellidos,
        direccion,
        telefono,
        email,
        jornada,
        curso,
        docente,
        materia,
        inspector_piso,
        psicologo,
    ) = extraer_valores(frase)

    query = generar_consulta_sql(
        cedula,
        nombres,
        apellidos,
        direccion,
        telefono,
        email,
        jornada,
        curso,
        docente,
        materia,
        inspector_piso,
        psicologo,
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
        "hoja_vida/index.html",
        hojas_vida=row,
        docentes=docentes,
        inspectores_piso=inspectores_piso,
        psicologos=psicologos,
        materias=materias,
        cursos=cursos,
        jornadas=jornadas,
    )


def recuperarId(tabla, campo_a_buscar, texto_a_buscar):
    try:
        # Validar nombres de tabla y columna
        if not tabla.isidentifier() or not campo_a_buscar.isidentifier():
            raise ValueError("Nombre de tabla o columna inválido.")

        # Conexión a la base de datos
        conn = Database.get_connection()

        with conn.cursor(dictionary=True) as cursor:
            # Consulta con LIMIT 1
            query = f"""
                SELECT id FROM {tabla}
                WHERE LOWER({campo_a_buscar}) LIKE LOWER(%s)
                LIMIT 1
            """
            cursor.execute(query, ("%" + texto_a_buscar + "%",))
            fila = cursor.fetchone()

            if fila:
                return fila["id"]
            else:
                return -1

    except Exception as e:
        print(f"Error: {e}")
        return -1

    finally:
        # Garantizar el cierre de conexión
        if conn and conn.is_connected():
            conn.close()

    try:
        conn = Database.get_connection()
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(
                "SELECT * FROM "
                + tabla
                + " WHERE LOWER("
                + campo_a_buscar
                + ") LIKE LOWER(%s)",
                ("%" + texto_a_buscar + "%",),
            )
            fila = cursor.fetchone()
            cursor.close()
            conn.close()

            if not fila:
                return -1
            else:
                return fila["id"]
    except Exception as e:
        return -1
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
