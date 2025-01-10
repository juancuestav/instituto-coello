from functools import wraps
from flask import session, redirect, url_for, request, make_response

def redirect_if_authenticated(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "user_id" in session:
            return redirect(url_for("hoja_vida.index"))
        
        # Añadir cabeceras para deshabilitar la caché
        response = make_response(func(*args, **kwargs))
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    return wrapper
