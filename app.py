from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import calendar
from datetime import datetime

from functions import login_required, error, recortar_semana, generar_horas, convertir_dias

app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

#conecto con la db
db = SQL("sqlite:///turnos.db")

#ruta del index
@app.route("/")
@login_required
def index():
    user_id = session.get("user_id")
    user = db.execute("SELECT * FROM users WHERE id = ?",user_id)
    fecha_actual  = datetime.now()
    dt_string = fecha_actual.strftime("%d/%m/%Y %H:%M")
    return render_template("index.html",user = user[0],fecha_actual = dt_string)

#ruta del login
@app.route("/login",methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "POST":
     # Ensure username was submitted
        if not request.form.get("username"):
            return error("must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return error("must provide password")

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return error("invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

#ruta del logout
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

#ruta del register
@app.route("/register",methods=["GET", "POST"])
def register():
    if request.method == "POST":
        #traigo el username,password,confirmation y verifico que no sean nulas
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if not username:
            return error("Usuario en blanco")
        if not password:
            return error("Clave en blanco")
        if not confirmation:
            return error("Confirmacion en blanco")

        #verifico que la password sea igual que confirmation
        if password != confirmation:
            return error("La clave es distinta en de la confirmacion")

        #verifico si el nombre ya esta en la db
        rows = db.execute("SELECT * FROM users WHERE username = ?",username)
        if len(rows) >= 1:
            return error("El nombre ya esta usado")
        else:
            #guardo el usuario en la db
            db.execute("INSERT INTO users (username,hash)  VALUES (?,?)",username,generate_password_hash(password))
            # guardo el numero de sesion del usuario
            user_id = db.execute("SELECT id FROM users WHERE username = ?", username)[0][
                "id"
            ]
            session["user_id"] = user_id
        return redirect("/")
    else:
        return render_template("register.html")

@app.route("/horarios", methods=["GET","POST"])
@login_required
def horarios():
    if request.method == "POST":
        #traigo todos los datos del form y confirmo que no esten en blanco
        p_dia = request.form.get("p_dia")
        if not p_dia:
            return error("Primer dia en blanco")

        f_dia = request.form.get("f_dia")
        if not f_dia:
            return error("Ultimo dia en blanco")

        p_hora = request.form.get("p_hora")
        if not p_hora:
            return error("Primer hora en blanco")

        f_hora = request.form.get("f_hora")
        if not f_hora:
            return error("Ultima hora en blanco")

        #compruebo que las horas no sean las mismas

        if p_hora == f_hora:
            return error("Misma hora de comienzo que de final")

        intervalo = int(request.form.get("intervalo"))
        if not intervalo:
            return error("Intervalo en blanco")

        #compruebo que los intervalos esten correctos(utlize chat bing para saber lo del split)
        primera_hora = int(p_hora.split(':')[0]) * 60 + int(p_hora.split(':')[1])
        ultima_hora = int(f_hora.split(':')[0]) * 60 + int(f_hora.split(':')[1])

        if ((ultima_hora - primera_hora) % intervalo) != 0:
            return error("Intervalo inválido")

        #cargo los datos a la db
        user_id = session.get("user_id")
        db.execute("INSERT INTO horarios (user_id,p_dia,f_dia,p_hora,f_hora,intervalo) VALUES(?,?,?,?,?,?) ",user_id,p_dia,f_dia,p_hora,f_hora,intervalo)
        return redirect("/")
    else:
        return render_template("horarios.html")

@app.route("/perfil",methods=["GET","POST"])
@login_required
def perfil():
    if request.method == "POST":

        user_id = session.get("user_id")
        # traigo los datos del form
        rubro = request.form.get("rubro")
        nombre_negocio = request.form.get("nombre_negocio")
        #guardo los datos en la db
        db.execute("INSERT INTO negocio (user_id,rubro,nombre_negocio) VALUES (?,?,?)",user_id,rubro,nombre_negocio)

        return redirect("/")
    else:
        user_id = session.get("user_id")
        #trago los datos de user
        user = db.execute("SELECT * FROM users WHERE id = ?",user_id)
        horarios = db.execute("SELECT * FROM horarios WHERE user_id = ?",user_id)
        return render_template("perfil.html",user=user[0],horarios= horarios[0])


@app.route("/turnos/<int:id_user>", methods=["GET", "POST"])
def turnos(id_user):
    id_user = int(id_user)

    # Aquí buscarías en la base de datos la información del usuario
    user = db.execute("SELECT * FROM users WHERE id = ?",id_user)
    if len(user) < 1:
         return error("Proveedor de servicios invalido")

    # Coloco titulo a la pagina
    negocio = db.execute("SELECT * FROM negocio WHERE user_id = ?",id_user)

    # traigo los horarios de la db  y los guardo en variables
    horarios = db.execute("SELECT * FROM horarios WHERE user_id = ?",id_user)
    # compruebo que los hoarios no sean nulos
    if len(horarios) < 1:
         return error("Horarios del proveedor invalidos")

    p_dia = horarios[0]['p_dia']
    f_dia = horarios[0]['f_dia']
    p_hora = horarios[0]['p_hora']
    f_hora = horarios[0]['f_hora']
    intervalo = horarios[0]['intervalo']
    semana =["lunes","martes","miercoles","jueves","viernes","sabado","domingo"]

    semana = recortar_semana(semana,p_dia,f_dia)
    horas = generar_horas(p_hora,f_hora,intervalo)

    if request.method == "GET":

        #convierto el p_dia y el f_dia en num y luego itero sobre la base de datos para crear los turnos
        primer_dia = convertir_dias(p_dia)
        ultimo_dia = convertir_dias(f_dia)

        # Obtengo el mes actual
        ahora = datetime.now()
        mes = ahora.month

        _, num_dias = calendar.monthrange(2024, mes)

        #verifico si existen la primer y ultima fecha del turno si es asi no creo nada
        min_fecha = db.execute("SELECT MIN(fecha) FROM turnos WHERE user_id = ?", id_user)[0]["MIN(fecha)"]
        max_fecha = db.execute("SELECT MAX(fecha) FROM turnos WHERE user_id = ?", id_user)[0]["MAX(fecha)"]

        if min_fecha is None and max_fecha is None:
            #itero en cada dia del mes acutual y creo un turno en ese dia
            for dia in range(1,num_dias+1):
                fecha = datetime(2024, mes, dia)
                if fecha.weekday() not in range(primer_dia, ultimo_dia+1):
                    continue
                fecha_str = fecha.strftime('%Y-%m-%d')

                # Verifico si el turno ya existe en la base de datos
                turno_existente = db.execute("SELECT * FROM turnos WHERE user_id = ? AND fecha = ?", id_user, fecha_str)
                if len(turno_existente) == 0:
                # Si el turno no existe, lo creo
                    db.execute("INSERT INTO turnos (user_id,fecha,estado) VALUES (?,?,?)",id_user,fecha_str,False)

            #agrego las horas a los turnos
            turnos = db.execute("SELECT * FROM turnos WHERE user_id = ?",id_user)
            for turno in turnos:
                for hora in horas:
                    #convierto a hora en un obejto de tipo time
                    hora = datetime.strptime(hora, '%H:%M').time()
                    # Verifica si el horario ya existe en la base de datos
                    hora_existente = db.execute("SELECT * FROM turnos WHERE user_id = ? AND fecha = ? AND hora = ?",id_user, turno['fecha'], hora)
                    if len(hora_existente) == 0:
                        # Si el horario no existe, lo crea
                        db.execute("INSERT INTO turnos (user_id,fecha,hora,estado) VALUES (?,?,?,?)",id_user,turno['fecha'],hora,False)
            #encuentro el dia mas chico y mas grande
            min_fecha = db.execute("SELECT MIN(fecha) FROM turnos WHERE user_id = ?",id_user)
            max_fecha = db.execute("SELECT MAX(fecha) FROM turnos WHERE user_id = ?",id_user)
        else:
            min_fecha = min_fecha
            max_fecha = max_fecha
        return render_template('turnos.html',id_user = id_user, semanas=semana, tiempo=horas,negocio = negocio[0],min_fecha = min_fecha,max_fecha = max_fecha,p_dia = primer_dia,f_dia = ultimo_dia)

    elif request.method == "POST":
        nombre = request.form.get("nombre")
        cel = request.form.get("numero_cel")
        dia_form = request.form.get("dia")
        hora_form = request.form.get("hora")

        #convierto los dias y las hora para que coincidadn con la db
        dia_f = datetime.strptime(dia_form, "%Y-%m-%d").date()
        hora_f= datetime.strptime(hora_form, "%H:%M").time()

        # verifico si el turno esta tomado sino lo pongo en true
        turno = db.execute("SELECT * FROM turnos WHERE user_id = ? AND fecha = ? AND hora = ? ",id_user,dia_f,hora_f)
        if len(turno) == 0:
            return error("No se encontró el turno")
        if turno[0]["estado"] == 1:
            return error("turno ya tomado")
        else:
            db.execute("UPDATE turnos SET estado = ? WHERE user_id = ? AND fecha = ? AND hora = ?",1,id_user,dia_f,hora_f)
            #guardo el nombre y el celu
            db.execute("INSERT INTO clientes (id_turno,nom_cliente,num_cliente) VALUES (?,?,?)",turno[0]["id_turno"],nombre,cel)
        return redirect("/")

@app.route("/ver_turnos")
@login_required
def ver_turnos():
    user_id = session.get("user_id")
    #traigo los turnos del user
    turnos= db.execute("SELECT * FROM turnos JOIN clientes on turnos.id_turno = clientes.id_turno WHERE turnos.user_id = ? AND turnos.  estado = ? ",user_id,True)
    print(turnos)
    return render_template("ver_turnos.html",turnos = turnos)

@app.route("/clientes")
@login_required
def clientes():
    user_id = session.get("user_id")
    clientes = db.execute("SELECT * FROM clientes JOIN turnos on clientes.id_turno = turnos.id_turno WHERE turnos.user_id = ? AND turnos.estado = ?",user_id,True)
    return render_template("clientes.html", clientes = clientes)
