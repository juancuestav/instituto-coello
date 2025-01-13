from mysql.connector import Error
from .database import Database

ADMIN = 1
DOCENTE = 2
INSPECTOR_PISO = 3
PSICOLOGO = 4


# Funciones de consulta
def get_docentes():
    query = f"SELECT id, nombre FROM usuarios u INNER JOIN usuario_rol ur ON u.id = ur.usuario_id WHERE ur.rol_id = {DOCENTE} ORDER BY nombre ASC"
    try:
        # Obtén la conexión del pool
        conn = Database.get_connection()
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(query)  # Ejecuta la consulta
            data = cursor.fetchall()  # Recupera los resultados
        return data
    except Error as e:
        print(f"Error al obtener docentes: {e}")
        return []
    finally:
        # Asegúrate de cerrar la conexión después de usarla
        if conn.is_connected():
            conn.close()


def get_inspectores_piso():
    query = f"SELECT id, nombre FROM usuarios u INNER JOIN usuario_rol ur ON u.id = ur.usuario_id WHERE ur.rol_id = {INSPECTOR_PISO} ORDER BY nombre ASC"
    try:
        # Obtén la conexión del pool
        conn = Database.get_connection()
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(query)  # Ejecuta la consulta
            data = cursor.fetchall()  # Recupera los resultados
        return data
    except Error as e:
        print(f"Error al obtener docentes: {e}")
        return []
    finally:
        # Asegúrate de cerrar la conexión después de usarla
        if conn.is_connected():
            conn.close()
            
def get_psicologos():
    query = f"SELECT id, nombre FROM usuarios u INNER JOIN usuario_rol ur ON u.id = ur.usuario_id WHERE ur.rol_id = {PSICOLOGO} ORDER BY nombre ASC"
    try:
        # Obtén la conexión del pool
        conn = Database.get_connection()
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(query)  # Ejecuta la consulta
            data = cursor.fetchall()  # Recupera los resultados
        return data
    except Error as e:
        print(f"Error al obtener docentes: {e}")
        return []
    finally:
        # Asegúrate de cerrar la conexión después de usarla
        if conn.is_connected():
            conn.close()


def get_materias():
    query = "SELECT id, nombre_materia FROM materias ORDER BY nombre_materia ASC"
    try:
        # Obtén la conexión del pool
        conn = Database.get_connection()
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(query)  # Ejecuta la consulta
            data = cursor.fetchall()  # Recupera los resultados
        return data
    except Error as e:
        print(f"Error al obtener materias: {e}")
        return []
    finally:
        # Asegúrate de cerrar la conexión después de usarla
        if conn.is_connected():
            conn.close()


def get_cursos():
    query = "SELECT id, nombre_curso FROM cursos ORDER BY id ASC"
    try:
        # Obtén la conexión del pool
        conn = Database.get_connection()
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(query)  # Ejecuta la consulta
            data = cursor.fetchall()  # Recupera los resultados
        return data
    except Error as e:
        print(f"Error al obtener cursos: {e}")
        return []
    finally:
        # Asegúrate de cerrar la conexión después de usarla
        if conn.is_connected():
            conn.close()


def get_jornadas():
    query = "SELECT id, nombre_jornada FROM jornadas ORDER BY id ASC"
    try:
        # Obtén la conexión del pool
        conn = Database.get_connection()
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(query)  # Ejecuta la consulta
            data = cursor.fetchall()  # Recupera los resultados
        return data
    except Error as e:
        print(f"Error al obtener jornadas: {e}")
        return []
    finally:
        # Asegúrate de cerrar la conexión después de usarla
        if conn.is_connected():
            conn.close()


def get_roles():
    query = "SELECT id, nombre FROM roles ORDER BY id ASC"
    try:
        # Obtén la conexión del pool
        conn = Database.get_connection()
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(query)  # Ejecuta la consulta
            data = cursor.fetchall()  # Recupera los resultados
        return data
    except Error as e:
        print(f"Error al obtener roles: {e}")
        return []
    finally:
        # Asegúrate de cerrar la conexión después de usarla
        if conn.is_connected():
            conn.close()


def get_hojas_vida():
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
            m.nombre_materia AS materia
        FROM hojas_vida hv
        INNER JOIN materias m ON hv.materia_id = m.id
        LEFT JOIN usuarios d ON hv.docente_id = d.id
        LEFT JOIN usuarios i ON hv.inspector_piso_id = i.id
        LEFT JOIN usuarios p ON hv.psicologo_id = p.id
        ORDER BY hv.id ASC
    """
    try:
        # Obtén la conexión del pool
        conn = Database.get_connection()
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(query)  # Ejecuta la consulta
            data = cursor.fetchall()  # Recupera los resultados
        return data
    except Error as e:
        print(f"Error al obtener hojas de vida: {e}")
        return []
    finally:
        # Asegúrate de cerrar la conexión después de usarla
        if conn.is_connected():
            conn.close()

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