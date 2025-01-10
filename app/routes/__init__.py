from flask import Blueprint

# Importar Blueprints de cada archivo
from .materia import materia_bp
from .auth import auth_bp
from .curso import curso_bp
from .jornada import jornada_bp
from .hoja_vida import hoja_vida_bp
from .usuario import usuario_bp
from .observacion import observacion_bp
from .logro_academico import logro_academico_bp
from .falta import falta_bp

def register_blueprints(app):
    """Registrar todos los Blueprints en la aplicación Flask."""
    app.register_blueprint(auth_bp)
    app.register_blueprint(materia_bp, url_prefix='/materias')
    app.register_blueprint(curso_bp, url_prefix='/cursos')
    app.register_blueprint(jornada_bp, url_prefix='/jornadas')
    app.register_blueprint(hoja_vida_bp, url_prefix='/hoja_vida')
    app.register_blueprint(usuario_bp, url_prefix='/usuarios')
    app.register_blueprint(observacion_bp, url_prefix='/observaciones')
    app.register_blueprint(logro_academico_bp, url_prefix='/logros-academicos')
    app.register_blueprint(falta_bp, url_prefix='/faltas')