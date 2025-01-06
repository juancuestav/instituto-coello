from flask import Flask
from .routes import register_blueprints
from .database import Database

def create_app():
    # Crear la instancia de la aplicación Flask
    app = Flask(__name__)
    
    # Cargar configuración
    app.config.from_object("instance.config.Config")
    
    # Configuración de la base de datos
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'sistema',
    }
    
    # Inicializar el pool de conexiones
    Database.initialize_connection_pool(db_config)

    # Importar y registrar las rutas después de crear la app
    with app.app_context():
        # Registrar todos los Blueprints
        register_blueprints(app)

    return app
