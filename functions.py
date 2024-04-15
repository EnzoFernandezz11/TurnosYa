
from flask import redirect, render_template, session
from functools import wraps
from datetime import datetime, timedelta

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

def error(mesage):
    return render_template("error.html",mesage = mesage)

def recortar_semana(semana, p_dia, f_dia):
    inicio = semana.index(p_dia)
    fin = semana.index(f_dia)
    return semana[inicio:fin+1]

#me ayude de chatbing para crear esta funcion

def generar_horas(p_hora, f_hora, intervalo):
    formato = "%H:%M"
    p_hora = datetime.strptime(p_hora, formato)
    f_hora = datetime.strptime(f_hora, formato)
    intervalo = timedelta(minutes=intervalo)

    horas = []
    hora_actual = p_hora
    while hora_actual <= f_hora:
        horas.append(hora_actual.time().strftime(formato))
        hora_actual += intervalo
    return horas

def convertir_dias(dia):
    if dia == "lunes":
        return 0
    elif dia == "martes":
        return 1
    elif dia == "miercoles":
        return 2
    elif dia == "jueves":
        return 3
    elif dia == "viernes":
        return 4
    elif dia == "sabado":
        return 5
    elif dia =="domingo":
        return 6



