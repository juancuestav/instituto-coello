from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from ..database import Database

# Crear el Blueprint
auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/", methods=["GET"])
def home():
    return render_template("auth/login.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Obtener datos del formulario
        email = request.form.get("email")
        password = request.form.get("password")

        try:
            # Conexión a la base de datos
            connection = Database.get_connection()
            cursor = connection.cursor(dictionary=True)

            # Buscar usuario por email
            cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
            user = cursor.fetchone()

            cursor.close()
            connection.close()

            # Validar usuario y contraseña
            if user and check_password_hash(user['password'], password):
                # Guardar usuario en sesión
                session['user_id'] = user['id']
                session['user_email'] = user['email']
                flash("Inicio de sesión exitoso.", "success")
                return redirect(url_for("materia.index"))  # Redirigir a otra parte de la app
            else:
                flash("Correo o contraseña incorrectos.", "danger")
        except Exception as e:
            print(f"Error: {e}")
            flash("Error al iniciar sesión.", "danger")

    return render_template("auth/login.html")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Obtener datos del formulario
        nombre = request.form.get("nombre")
        email = request.form.get("email")
        password = request.form.get("password")

        try:
            # Conexión a la base de datos
            connection = Database.get_connection()
            cursor = connection.cursor()

            # Verificar si el correo ya está registrado
            cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
            existing_user = cursor.fetchone()

            if existing_user:
                flash("El correo ya está registrado.", "danger")
                return redirect(url_for("auth.register"))

            # Insertar nuevo usuario
            hashed_password = generate_password_hash(password)
            cursor.execute(
                "INSERT INTO usuarios (nombre, email, password) VALUES (%s, %s, %s)",
                (nombre, email, hashed_password),
            )
            connection.commit()

            cursor.close()
            connection.close()

            flash("Registro exitoso. Ahora puedes iniciar sesión.", "success")
            return redirect(url_for("auth.login"))

        except Exception as e:
            print(f"Error: {e}")
            flash("Error al registrar usuario.", "danger")

    return render_template("auth/register.html")

@auth_bp.route("/logout")
def logout():
    # Limpiar sesión
    session.clear()
    flash("Sesión cerrada correctamente.", "success")
    return redirect(url_for("auth.login"))
