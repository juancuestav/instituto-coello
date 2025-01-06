import mysql.connector
from mysql.connector import Error

try:
    # Conexión a la base de datos
    connection = mysql.connector.connect(
        host="localhost", user="root", password="", database="sistema"
    )

    if connection.is_connected():
        cursor = connection.cursor()

        # Insertar roles
        roles = [
            ("Admin", "Administrador del sistema."),
            ("Docente", "Usuarios con rol de docente."),
            ("Inspector de piso", "Usuarios con rol de inspector de piso."),
            ("Psicologo", "Usuarios con rol de psicologo."),
        ]
        cursor.executemany(
            "INSERT INTO roles (nombre, descripcion) VALUES (%s, %s)", roles
        )

        # Insertar usuarios
        usuarios = [
            ("Gabriel Martinez", "admin@example.com", "123456"),
            ("Ana López", "ana@example.com", "123456"),
            ("Ximena Duarte", "ximena@example.com", "123456"),
            ("Paula Andrade", "paula@example.com", "123456"),
        ]
        cursor.executemany(
            "INSERT INTO usuarios (nombre, email, password) VALUES (%s, %s, %s)",
            usuarios,
        )

        # Obtener IDs de roles y usuarios - Administrador
        cursor.execute("SELECT id FROM roles WHERE nombre = 'Admin'")
        rol_administrador_id = cursor.fetchone()[0]

        cursor.execute("SELECT id FROM usuarios WHERE email = 'admin@example.com'")
        usuario1_id = cursor.fetchone()[0]
        
        # Obtener IDs de roles y usuarios - Docente
        cursor.execute("SELECT id FROM roles WHERE nombre = 'Docente'")
        rol_docente_id = cursor.fetchone()[0]

        cursor.execute("SELECT id FROM usuarios WHERE email = 'ana@example.com'")
        usuario2_id = cursor.fetchone()[0]
        
        # Obtener IDs de roles y usuarios - Inspector de piso
        cursor.execute("SELECT id FROM roles WHERE nombre = 'Inspector de piso'")
        rol_inspector_piso_id = cursor.fetchone()[0]

        cursor.execute("SELECT id FROM usuarios WHERE email = 'ximena@example.com'")
        usuario3_id = cursor.fetchone()[0]
        
        # Obtener IDs de roles y usuarios - Psicologo
        cursor.execute("SELECT id FROM roles WHERE nombre = 'Psicologo'")
        rol_psicologo_id = cursor.fetchone()[0]

        cursor.execute("SELECT id FROM usuarios WHERE email = 'paula@example.com'")
        usuario4_id = cursor.fetchone()[0]

        # Asociar roles a usuarios
        relaciones = [
            (usuario1_id, rol_administrador_id),
            (usuario2_id, rol_docente_id),
            (usuario3_id, rol_inspector_piso_id),
            (usuario4_id, rol_psicologo_id),
        ]
        cursor.executemany(
            "INSERT INTO usuario_rol (usuario_id, rol_id) VALUES (%s, %s)", relaciones
        )

        # Insertar cursos (debe ser una lista de tuplas)
        cursos = [
            ("Octavo",),
            ("Noveno",),
            ("Décimo",),
            ("Primero de bachillerato",),
            ("Segundo de bachillerato",),
            ("Tercero de bachillerato",),
        ]
        cursor.executemany("INSERT INTO cursos (nombre_curso) VALUES (%s)", cursos)

        # Insertar jornadas (debe ser una lista de tuplas)
        jornadas = [
            ("Matutina",),
            ("Vespertina",),
            ("Nocturna",),
        ]
        cursor.executemany(
            "INSERT INTO jornadas (nombre_jornada) VALUES (%s)", jornadas
        )

        # Insertar materias (debe ser una lista de tuplas)
        materias = [
            ("Matemáticas",),
            ("Lengua y Literatura",),
            ("Ciencias Naturales",),
            ("Historia",),
            ("Geografía",),
            ("Educación Cívica",),
            ("Inglés (u otro idioma extranjero)",),
            ("Arte",),
            ("Educación Física",),
            ("Tecnología",),
        ]

        cursor.executemany(
            "INSERT INTO materias (nombre_materia) VALUES (%s)", materias
        )

        # Confirmar cambios
        connection.commit()
        print("Datos iniciales insertados con éxito.")

except Error as e:
    print(f"Error al conectar a la base de datos: {e}")

finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("Conexión cerrada.")
