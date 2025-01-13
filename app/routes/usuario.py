from flask import Blueprint, request, render_template, flash, redirect, url_for, session
from werkzeug.security import generate_password_hash
from ..database import Database
from ..listados import get_roles

usuario_bp = Blueprint("usuario", __name__)


# Página principal: muestra el formulario y el listado de cursos
@usuario_bp.route("/", methods=["GET", "POST"])
def index():
    if "user_id" not in session:
        flash("Por favor, inicia sesión para acceder a esta página.", "warning")
        return redirect(url_for("auth.login"))

    roles = get_roles()  # Obtener la lista de roles para el formulario

    if request.method == "POST":
        # Obtener datos del formulario
        nombre = request.form.get("nombre").strip()
        email = request.form.get("email").strip()
        password = request.form.get("password")
        rol = request.form.get("rol")  # ID del rol seleccionado

        # Validación de campos obligatorios
        if not nombre:
            flash("El campo nombre es obligtorio.", "warning")
            return redirect(url_for("usuario.index"))

        try:
            # Conexión a la base de datos
            connection = Database.get_connection()
            cursor = connection.cursor()

            # Verificar si el correo ya está registrado
            cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
            existing_user = cursor.fetchone()

            if existing_user:
                flash("El correo ya está registrado.", "danger")
                return redirect(url_for("usuario.index"))

            # Insertar nuevo usuario
            hashed_password = generate_password_hash(password)
            cursor.execute(
                "INSERT INTO usuarios (nombre, email, password) VALUES (%s, %s, %s)",
                (nombre, email, hashed_password),
            )
            connection.commit()

            # Obtener el ID del usuario recién creado
            usuario_id = cursor.lastrowid

            # Insertar el rol del usuario en la tabla usuario_rol
            if rol:
                cursor.execute(
                    "INSERT INTO usuario_rol (usuario_id, rol_id) VALUES (%s, %s)",
                    (usuario_id, rol),
                )
                connection.commit()

            cursor.close()
            connection.close()

            flash(
                "Registro exitoso. Ahora puedes iniciar sesión con esta nueva cuenta de usuario.",
                "success",
            )
            return redirect(url_for("usuario.index"))

        except Exception as e:
            print(f"Error: {e}")
            flash("Error al registrar usuario.", "danger")

    # Consulta todos los usuarios existentes junto con su rol
    try:
        conn = Database.get_connection()
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(
                """
                SELECT u.id, u.nombre, u.email, r.nombre AS rol
                FROM usuarios u
                LEFT JOIN usuario_rol ur ON u.id = ur.usuario_id
                LEFT JOIN roles r ON ur.rol_id = r.id
                """
            )
            usuarios = cursor.fetchall()
    except Exception as e:
        flash(f"Error al obtener los usuarios: {str(e)}", "danger")
        usuarios = []
    finally:
        conn.close()
    return render_template("usuario/index.html", usuarios=usuarios, roles=roles)


# Editar un curso
@usuario_bp.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    # Obtener roles disponibles
    roles = get_roles()

    try:
        # Obtener datos del usuario actual
        conn = Database.get_connection()
        with conn.cursor(dictionary=True) as cursor:
            # Obtener usuario
            cursor.execute(
                "SELECT id, nombre, email FROM usuarios WHERE id = %s", (id,)
            )
            usuario = cursor.fetchone()

            if not usuario:
                flash("Usuario no encontrado.", "danger")
                return redirect(url_for("usuario.index"))

            # Obtener rol actual del usuario
            cursor.execute(
                "SELECT rol_id FROM usuario_rol WHERE usuario_id = %s", (id,)
            )
            rol_actual = cursor.fetchone()
            usuario["rol_id"] = rol_actual["rol_id"] if rol_actual else None

    except Exception as e:
        flash(f"Error al obtener datos del usuario: {str(e)}", "danger")
        return redirect(url_for("usuario.index"))
    finally:
        conn.close()

    if request.method == "POST":
        # Obtener datos del formulario
        nombre = request.form.get("nombre")
        email = request.form.get("email")
        password = request.form.get("password")
        rol = request.form.get("rol")

        try:
            conn = Database.get_connection()
            with conn.cursor() as cursor:
                # Actualizar datos del usuario
                if password:
                    hashed_password = generate_password_hash(password)
                    cursor.execute(
                        "UPDATE usuarios SET nombre = %s, email = %s, password = %s WHERE id = %s",
                        (nombre, email, hashed_password, id),
                    )
                else:
                    cursor.execute(
                        "UPDATE usuarios SET nombre = %s, email = %s WHERE id = %s",
                        (nombre, email, id),
                    )

                # Actualizar el rol del usuario
                cursor.execute("DELETE FROM usuario_rol WHERE usuario_id = %s", (id,))
                if rol:
                    cursor.execute(
                        "INSERT INTO usuario_rol (usuario_id, rol_id) VALUES (%s, %s)",
                        (id, rol),
                    )

                conn.commit()

            flash("Usuario actualizado exitosamente.", "success")
            return redirect(url_for("usuario.index"))

        except Exception as e:
            flash(f"Error al actualizar usuario: {str(e)}", "danger")
        finally:
            conn.close()

    return render_template("usuario/update.html", usuario=usuario, roles=roles)


# Eliminar un curso
@usuario_bp.route("/eliminar/<int:id>", methods=["POST"])
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
