import mysql.connector

# Configuración de la conexión
connection = mysql.connector.connect(
    host="localhost",
    user="root",  # Cambia esto por tu usuario
    password="",  # Cambia esto por tu contraseña
    database="sistema",  # Cambia esto por tu base de datos
)
cursor = connection.cursor()

# Crear tablas
tables = {
    "usuario": """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            email VARCHAR(120) UNIQUE NOT NULL,
            password VARCHAR(128) NOT NULL
        );
    """,
    "rol": """
        CREATE TABLE IF NOT EXISTS roles (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(50) UNIQUE NOT NULL,
            descripcion TEXT
        );
    """,
    "usuario_rol": """
        CREATE TABLE IF NOT EXISTS usuario_rol (
            usuario_id INT NOT NULL,
            rol_id INT NOT NULL,
            PRIMARY KEY (usuario_id, rol_id),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
            FOREIGN KEY (rol_id) REFERENCES roles(id) ON DELETE CASCADE
        );
    """,
    "materia": """
        CREATE TABLE IF NOT EXISTS materias (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre_materia VARCHAR(100) NOT NULL
        );
    """,
    "curso": """
        CREATE TABLE IF NOT EXISTS cursos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre_curso VARCHAR(100) NOT NULL
        );
    """,
    "jornada": """
        CREATE TABLE IF NOT EXISTS jornadas (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre_jornada VARCHAR(100) NOT NULL
        );
    """,
    "hoja_vida": """
        CREATE TABLE IF NOT EXISTS hojas_vida (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombres VARCHAR(100) NOT NULL,
            apellidos VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            cedula VARCHAR(10) UNIQUE NOT NULL,
            telefono VARCHAR(10),
            direccion VARCHAR(255) NOT NULL,
            jornada_id INT NOT NULL,
            curso_id INT NOT NULL,
            docente_id INT DEFAULT NULL,
            inspector_piso_id INT DEFAULT NULL,
            psicologo_id INT DEFAULT NULL,
            materia_id INT NOT NULL,
            FOREIGN KEY (jornada_id) REFERENCES jornadas(id) ON DELETE CASCADE,
            FOREIGN KEY (curso_id) REFERENCES cursos(id) ON DELETE CASCADE,
            FOREIGN KEY (docente_id) REFERENCES usuarios(id) ON DELETE CASCADE,
            FOREIGN KEY (inspector_piso_id) REFERENCES usuarios(id) ON DELETE CASCADE,
            FOREIGN KEY (psicologo_id) REFERENCES usuarios(id) ON DELETE CASCADE,
            FOREIGN KEY (materia_id) REFERENCES materias(id) ON DELETE CASCADE
        );
    """,
    "observacion": """
        CREATE TABLE IF NOT EXISTS observaciones (
            id INT AUTO_INCREMENT PRIMARY KEY,
            detalle_observacion TEXT NOT NULL,
            hoja_vida_id INT NOT NULL,
            fecha DATE NOT NULL,
            FOREIGN KEY (hoja_vida_id) REFERENCES hojas_vida(id) ON DELETE CASCADE
        );
    """,
    "logros_academicos": """
        CREATE TABLE `logros_academicos` (
        	`id` BIGINT(20) UNSIGNED AUTO_INCREMENT NOT NULL DEFAULT '0',
        	`logro` VARCHAR(255) NOT NULL DEFAULT '' COLLATE 'utf8mb4_0900_ai_ci',
        	`observacion` VARCHAR(255) NULL DEFAULT NULL COLLATE 'utf8mb4_0900_ai_ci',
        	`fecha` DATE NULL DEFAULT NULL,
        	`hoja_vida_id` INT(10) NULL DEFAULT NULL,
        	PRIMARY KEY (`id`) USING BTREE,
        	INDEX `FK_logros_academicos_hojas_vida` (`hoja_vida_id`) USING BTREE,
        	CONSTRAINT `FK_logros_academicos_hojas_vida` FOREIGN KEY (`hoja_vida_id`) REFERENCES `hojas_vida` (`id`) ON UPDATE NO ACTION ON DELETE NO ACTION
        )
    """,
}

# Ejecutar las sentencias SQL
for table_name, ddl in tables.items():
    try:
        cursor.execute(ddl)
        print(f"Tabla {table_name} creada o ya existe.")
    except mysql.connector.Error as err:
        print(f"Error creando la tabla {table_name}: {err}")

# Cerrar la conexión
cursor.close()
connection.close()
