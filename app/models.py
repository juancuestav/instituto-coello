class Usuario:
    def __init__(self, id, nombre, email, password, roles=None):
        self.id = id
        self.nombre = nombre
        self.email = email
        self.password = password
        self.roles = roles if roles else []

    def __repr__(self):
        return f"<Usuario {self.nombre}>"


class Rol:
    def __init__(self, id, nombre, descripcion):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion

    def __repr__(self):
        return f"<Rol {self.nombre}>"


class Docente:
    def __init__(self, id, nombres, apellidos, email, cedula, telefono=None):
        self.id = id
        self.nombres = nombres
        self.apellidos = apellidos
        self.email = email
        self.cedula = cedula
        self.telefono = telefono

    def __repr__(self):
        return f"<Docente {self.nombres} {self.apellidos}>"


class Materia:
    def __init__(self, id, nombre_materia):
        self.id = id
        self.nombre_materia = nombre_materia

    def __repr__(self):
        return f"<Materia {self.nombre_materia}>"


class Curso:
    def __init__(self, id, nombre_curso):
        self.id = id
        self.nombre_curso = nombre_curso

    def __repr__(self):
        return f"<Curso {self.nombre_curso}>"


class Jornada:
    def __init__(self, id, nombre_jornada):
        self.id = id
        self.nombre_jornada = nombre_jornada

    def __repr__(self):
        return f"<Jornada {self.nombre_jornada}>"


class HojaVida:
    def __init__(self, id, nombres, apellidos, email, cedula, telefono, direccion, jornada_id, curso_id, docente_id, materia_id, observaciones=None):
        self.id = id
        self.nombres = nombres
        self.apellidos = apellidos
        self.email = email
        self.cedula = cedula
        self.telefono = telefono
        self.direccion = direccion
        self.jornada_id = jornada_id
        self.curso_id = curso_id
        self.docente_id = docente_id
        self.materia_id = materia_id
        self.observaciones = observaciones if observaciones else []

    def __repr__(self):
        return f"<HojaVida {self.nombres} {self.apellidos}>"


class Observacion:
    def __init__(self, id, detalle_observacion, hoja_vida_id):
        self.id = id
        self.detalle_observacion = detalle_observacion
        self.hoja_vida_id = hoja_vida_id

    def __repr__(self):
        return f"<Observacion {self.id}>"
