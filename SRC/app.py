from flask import Flask, flash, render_template, request, redirect, url_for, session
from flask import make_response
from functools import wraps
import pymysql.cursors
from dotenv import load_dotenv
import os
import pymysql
from datetime import datetime
from flask_bcrypt import Bcrypt

load_dotenv()
app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = "chaveSegurança"

def nocache(view):
    @wraps(view)
    def no_cache_view(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    return no_cache_view

@app.context_processor
def inject_user():
    # Verifica se o usuário está realmente logado na sessão
    if 'user_id' in session and session.get('user_name') and session.get('user_role') is not None:
        return {
            "user_name": session.get("user_name"),
            "user_role": session.get("user_role")
        }
    else:
        # Se não estiver logado, limpa qualquer dado inconsistente da sessão
        session.clear()
        return {
            "user_name": None,
            "user_role": None
        }

def get_db_connection():
    connection = pymysql.connect(
        host = os.getenv("DB_HOST"),
        user = os.getenv("DB_USER"),
        password = os.getenv("DB_PASSWORD"),
        db = os.getenv("DB_NAME"),
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection

@app.route("/", methods=["GET", "POST"])
@nocache
def index():
    if request.method == "POST":
        entry = request.form.get("entry")
        password = request.form.get("password")
        
        if not entry or not password:
            error_message = "Por favor, preencha todos os campos."
            return render_template("index.html", error=error_message)
        
        connection = get_db_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT id, password, email, name, role, cpf FROM users WHERE email = %s OR cpf = %s", (entry, entry))
        user = cursor.fetchone()
        cursor.close()
        connection.close()

        if not user:
            error_message = "Usuário não encontrado. Verifique seu email ou CPF."
        elif not bcrypt.check_password_hash(user["password"], password):
            error_message = "Senha incorreta. Tente novamente."
        else:
            session["user_name"] = user["name"].split()[0]
            session["user_role"] = user["role"]
            session["user_id"] = user["id"]
            session["user_cpf"] = user["cpf"]   
            return redirect(url_for("home"))

        return render_template("index.html", error=error_message)
    
    return render_template("index.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/home")
@nocache
def home():
    
    if "user_id" not in session:
        return redirect(url_for("index"))

    user_name = session.get("user_name")
    user_role = session.get("user_role")
    return render_template("home.html")

@app.route("/admin", methods=["GET", "POST"])
@nocache
def admin():
    if "user_id" not in session or session.get("user_role") != 1 or not session.get("user_name"):
        return redirect(url_for("index"))

    user_name = session.get("user_name")
    user_role = session.get("user_role")

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        cpf = request.form.get("cpf")
        password = request.form.get("password")
        role = request.form.get("role")

        connection = get_db_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT id FROM users WHERE email = %s OR cpf = %s", (email, cpf))
        existing_user = cursor.fetchone()

        if existing_user:
            error = "Email ou CPF já existe."
            return render_template("admin.html", error=error)

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        cursor.execute("INSERT INTO users (name, email, cpf, password, role) VALUES (%s, %s, %s, %s, %s)",
               (name, email, cpf, hashed_password, role))
        connection.commit()
        cursor.close()
        connection.close()
        success = "Usuário cadastrado com sucesso!"
        return render_template("admin.html", success=success)

    return render_template("admin.html")

@app.route("/stations")
@nocache
def stations():
    if "user_id" not in session or session.get("user_role") != 1 or not session.get("user_name"):
        return redirect(url_for("index"))
    
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id, name, latitude, longitude, uuid, cdUser FROM stations ORDER BY createdAt DESC")
    stations = cursor.fetchall()
    connection.close()
    return render_template("stations.html", stations=stations)

@app.route("/add_station", methods=["GET", "POST"])
@nocache
def add_station():
    if "user_id" not in session or session.get("user_role") != 1 or not session.get("user_name"):
        return redirect(url_for("index"))

    connection = get_db_connection()
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    # Consultar todos os usuários disponíveis
    cursor.execute("SELECT id, name, cpf, email FROM users")
    users = cursor.fetchall()

    # Consultar todos os parâmetros disponíveis
    cursor.execute("SELECT id, name, unit FROM typeParameters")
    parameters = cursor.fetchall()

    if request.method == "POST":
        name = request.form.get("name")
        latitude = request.form.get("latitude")
        longitude = request.form.get("longitude")
        uuid = request.form.get("uuid")
        cdUser = request.form.get("cdUser")
        uuid_clean = uuid.replace(":", "").upper()
        selected_parameters = request.form.getlist("cdParameter")  # IDs dos parâmetros

        if not name or not latitude or not longitude or not uuid:
            return render_template("add_station.html", error="Preencha todos os campos obrigatórios.", parameters=parameters)

        if not selected_parameters:
            return render_template("add_station.html", error="Selecione pelo menos um parâmetro.", parameters=parameters)

        try:
            # Inserir a estação
            if cdUser:
                cursor.execute("INSERT INTO stations (name, latitude, longitude, uuid, cdUser) VALUES (%s, %s, %s, %s, %s)",
                (name, latitude, longitude, uuid_clean, cdUser)
                )
            else:
                cursor.execute(
                    "INSERT INTO stations (name, latitude, longitude, uuid) VALUES (%s, %s, %s, %s)",
                    (name, latitude, longitude, uuid_clean)
                )   
            station_id = cursor.lastrowid

            # Para cada parâmetro selecionado, atualizar o registro existente com cdStation NULL
            for param_id in selected_parameters:
                cursor.execute(
                    "INSERT INTO parameters (cdStation, cdTypeParameter) VALUES (%s, %s)",
                    (station_id, param_id)
                )

            connection.commit()
            success = "Estação cadastrada com sucesso!"
        except pymysql.err.IntegrityError:
            connection.rollback()
            error = "Erro ao cadastrar a estação. Verifique se o UUID já existe."
            return render_template("add_station.html", error=error, parameters=parameters)
        finally:
            connection.close()

        return render_template("add_station.html", success=success, parameters=parameters, users=users)


    return render_template("add_station.html", parameters=parameters, users=users)




@app.route("/parameters")
@nocache
def parameters():
    if "user_id" not in session or session.get("user_role") != 1 or not session.get("user_name"):
        return redirect(url_for("index"))

    connection = get_db_connection()
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM typeParameters ORDER BY name")
    parameters = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template("parameters.html", parameters=parameters)

@app.route("/add_parameter", methods=["GET", "POST"])
@nocache
def add_parameter():
    if "user_id" not in session or session.get("user_role") != 1 or not session.get("user_name"):
        return redirect(url_for("index"))

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT id, name FROM stations")
    stations = cursor.fetchall()

    if request.method == "POST":
        name = request.form.get("name")
        unit = request.form.get("unit")
        typeJson = request.form.get("typeJson")
        decimalPlaces = request.form.get("decimalPlaces")

        if not name or not unit or not typeJson or not decimalPlaces:
            return render_template("add_parameter.html", error="Preencha todos os campos obrigatórios.", stations=stations)

        try:
            cursor.execute("""
                INSERT INTO typeParameters (name, unit, typeJson, numberOfDecimalPlaces)
                VALUES (%s, %s, %s, %s)
            """, (name, unit, typeJson, decimalPlaces))

            connection.commit()
            return render_template("add_parameter.html", success="Parâmetro cadastrado com sucesso!", stations=stations)
        except pymysql.err.IntegrityError as e:
            return render_template("add_parameter.html", error=f"Erro de integridade: {e}", stations=stations)
        finally:
            connection.close()

    return render_template("add_parameter.html", stations=stations)

@app.route("/users", methods=["GET", "POST"])
@nocache
def users():
    user_name = session.get("user_name")
    user_role = session.get("user_role")

    if "user_id" not in session or session.get("user_role") != 1 or not session.get("user_name"):
        return redirect(url_for("index"))
    
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id, name, cpf, email, role, createdAt FROM users ORDER BY createdAt DESC")
    users = cursor.fetchall()
    connection.close()
    return render_template("users.html", users=users)

@app.route("/graphs", methods=["GET"])
@nocache
def graphs():
    if "user_id" not in session:
        return redirect(url_for("index"))
    
    user_id = session["user_id"]

    start_date_str = request.args.get("start_date")
    end_date_str = request.args.get("end_date")

    connection = get_db_connection()
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    
    cursor.execute("SELECT role FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()

    if user and user["role"] == 1:
        cursor.execute("""
            SELECT id, name, uuid, cdUser
            FROM stations
            ORDER BY createdAt DESC
        """)
        stations = cursor.fetchall()
    else:
        cursor.execute("""
            SELECT id, name, uuid, cdUser
            FROM stations
            WHERE cdUser = %s OR cdUser IS NULL
            ORDER BY createdAt DESC
        """, (user_id,))
        stations = cursor.fetchall()


    for station in stations:
        query = """
            SELECT tp.name, tp.unit, m.value, m.measureTime
            FROM parameters p
            JOIN typeParameters tp ON p.cdTypeParameter = tp.id
            JOIN measures m ON m.cdParameter = p.id
            WHERE p.cdStation = %s
        """
        query_params = [station["id"]]

        if start_date_str:
            query += " AND m.measureTime >= %s"
            query_params.append(start_date_str + " 00:00:00")
        if end_date_str:
            query += " AND m.measureTime <= %s"
            query_params.append(end_date_str + " 23:59:59")
        
        query += " ORDER BY m.measureTime"

        cursor.execute(query, tuple(query_params))
        measures = cursor.fetchall()

        # Agrupa os dados por parâmetro
        param_data = {}
        categories_set = set()

        for m in measures:
            param_name_unit = f"{m["name"]} ({m["unit"]})"
            if param_name_unit not in param_data:
                param_data[param_name_unit] = []
            param_data[param_name_unit].append({
                "time": m["measureTime"].strftime("%Y-%m-%d %H:%M"),
                "value": float(m["value"])
            })
            categories_set.add(m["measureTime"].strftime("%Y-%m-%d %H:%M"))

        categories = sorted(list(categories_set))

        series = []
        for param_name_unit, data_points in param_data.items():
            # Criar um array de valores alinhado com as categorias
            aligned_data = [None] * len(categories)
            for dp in data_points:
                try:
                    idx = categories.index(dp["time"])
                    aligned_data[idx] = dp["value"]
                except ValueError:
                    pass # Should not happen if categories are built correctly
            series.append({"name": param_name_unit, "data": aligned_data})

        station["categories"] = categories
        station["series"] = series

        print(station["series"])
    connection.close()
    return render_template("graphs.html", stations=stations, start_date=start_date_str, end_date=end_date_str)

@app.route("/deleteUser/<int:idUser>")
def deleteUser(idUser):
    if "user_id" not in session or session.get("user_role") != 1 or not session.get("user_name"):
        return redirect(url_for("index"))
    connection = get_db_connection()
    cursor = connection.cursor()
    
    cursor.execute("DELETE FROM users WHERE id = %s", (idUser,))
    connection.commit()
    
    cursor.close()
    connection.close()

    return redirect(url_for("users"))

@app.route("/edit_parameter/<int:parameter_id>", methods=["GET", "POST"])
@nocache
def edit_parameter(parameter_id):
    if "user_id" not in session or session.get("user_role") != 1 or not session.get("user_name"):
        return redirect(url_for("index"))

    connection = get_db_connection()
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    if request.method == "POST":
        name = request.form.get("name")
        unit = request.form.get("unit")
        typeJson = request.form.get("typeJson")
        decimalPlaces = request.form.get("decimalPlaces")

        if not name or not unit or not typeJson or not decimalPlaces:
            cursor.execute("SELECT * FROM typeParameters WHERE id = %s", (parameter_id,))
            parameter = cursor.fetchone()
            connection.close()
            return render_template("edit_parameter.html", parameter=parameter, error="Preencha todos os campos obrigatórios.")

        try:
            cursor.execute("""
                UPDATE typeParameters 
                SET name = %s, unit = %s, typeJson = %s, numberOfDecimalPlaces = %s
                WHERE id = %s
            """, (name, unit, typeJson, decimalPlaces, parameter_id))

            connection.commit()
            cursor.execute("SELECT * FROM typeParameters WHERE id = %s", (parameter_id,))
            parameter = cursor.fetchone()
            connection.close()
            return render_template("edit_parameter.html", parameter=parameter, success="Parâmetro atualizado com sucesso!")
        except pymysql.err.IntegrityError as e:
            cursor.execute("SELECT * FROM typeParameters WHERE id = %s", (parameter_id,))
            parameter = cursor.fetchone()
            connection.close()
            return render_template("edit_parameter.html", parameter=parameter, error=f"Erro de integridade: {e}")

    # GET request
    cursor.execute("SELECT * FROM typeParameters WHERE id = %s", (parameter_id,))
    parameter = cursor.fetchone()
    connection.close()
    
    if not parameter:
        return redirect(url_for("parameters"))
    
    return render_template("edit_parameter.html", parameter=parameter)

@app.route("/deleteParameter/<int:idParameter>")
def deleteParameter(idParameter):
    if "user_id" not in session or session.get("user_role") != 1 or not session.get("user_name"):
        return redirect(url_for("index"))
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SET SQL_SAFE_UPDATES = 0;")
    
    cursor.execute("DELETE FROM typeparameters WHERE id = %s", (idParameter,))
    connection.commit()

    cursor.execute("SET SQL_SAFE_UPDATES = 1;")
    
    cursor.close()
    connection.close()

    return redirect(url_for("parameters"))

@app.route("/edit_station/<int:station_id>", methods=["GET", "POST"])
@nocache
def edit_station(station_id):
    if "user_id" not in session or session.get("user_role") != 1 or not session.get("user_name"):
        return redirect(url_for("index"))

    connection = get_db_connection()
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    if request.method == "POST":
        name = request.form.get("name")
        latitude = request.form.get("latitude")
        longitude = request.form.get("longitude")
        uuid = request.form.get("uuid")
        cdUser = request.form.get("cdUser")
        if not cdUser:
            cdUser = None
        uuid_clean = uuid.replace(":", "").upper()
        selected_parameters = request.form.getlist("cdParameter")

        if not name or not latitude or not longitude or not uuid:
            # Buscar dados para recarregar a página
            cursor.execute("SELECT * FROM stations WHERE id = %s", (station_id,))
            station = cursor.fetchone()
            cursor.execute("SELECT id, name, unit FROM typeParameters")
            all_parameters = cursor.fetchall()
            cursor.execute("SELECT id, name, cpf, email FROM users")
            users = cursor.fetchall()
            cursor.execute("""
                SELECT tp.id FROM parameters p 
                JOIN typeParameters tp ON p.cdTypeParameter = tp.id 
                WHERE p.cdStation = %s
            """, (station_id,))
            current_params = [row["id"] for row in cursor.fetchall()]
            connection.close()
            return render_template("edit_station.html", station=station, parameters=all_parameters, current_parameters=current_params, users=users, error="Preencha todos os campos obrigatórios.")

        try:
            # Atualizar dados da estação
            cursor.execute("""
                UPDATE stations 
                SET name = %s, latitude = %s, longitude = %s, uuid = %s, cdUser = %s
                WHERE id = %s
            """, (name, latitude, longitude, uuid_clean, cdUser, station_id))

            # Remover parâmetros antigos
            cursor.execute("DELETE FROM parameters WHERE cdStation = %s", (station_id,))

            # Adicionar novos parâmetros
            if selected_parameters:
                for param_id in selected_parameters:
                    cursor.execute(
                        "INSERT INTO parameters (cdStation, cdTypeParameter) VALUES (%s, %s)",
                        (station_id, param_id)
                    )

            connection.commit()
            
            # Buscar dados atualizados
            cursor.execute("SELECT * FROM stations WHERE id = %s", (station_id,))
            station = cursor.fetchone()
            cursor.execute("SELECT id, name, unit FROM typeParameters")
            all_parameters = cursor.fetchall()
            cursor.execute("SELECT id, name FROM users")
            users = cursor.fetchall()
            cursor.execute("""
                SELECT tp.id FROM parameters p 
                JOIN typeParameters tp ON p.cdTypeParameter = tp.id 
                WHERE p.cdStation = %s
            """, (station_id,))
            current_params = [row["id"] for row in cursor.fetchall()]
            connection.close()
            return render_template("edit_station.html", station=station, parameters=all_parameters, users=users, current_params=current_params, success="Estação atualizada com sucesso!")
        except pymysql.err.IntegrityError as e:
            connection.rollback()
            cursor.execute("SELECT * FROM stations WHERE id = %s", (station_id,))
            station = cursor.fetchone()
            cursor.execute("SELECT id, name, unit FROM typeParameters")
            all_parameters = cursor.fetchall()
            cursor.execute("SELECT id, name FROM users")
            users = cursor.fetchall()
            cursor.execute("""
                SELECT tp.id FROM parameters p 
                JOIN typeParameters tp ON p.cdTypeParameter = tp.id 
                WHERE p.cdStation = %s
            """, (station_id,))
            current_params = [row["id"] for row in cursor.fetchall()]
            connection.close()
            return render_template("edit_station.html", station=station, parameters=all_parameters, users=users, current_params=current_params, error=f"Erro ao atualizar: {e}")

    # GET request
    cursor.execute("SELECT * FROM stations WHERE id = %s", (station_id,))
    station = cursor.fetchone()
    
    if not station:
        connection.close()
        return redirect(url_for("stations"))
    
    # Buscar todos os parâmetros disponíveis
    cursor.execute("SELECT id, name, unit FROM typeParameters")
    all_parameters = cursor.fetchall()

    # Buscar todos os usuários disponíveis
    cursor.execute("SELECT id, name FROM users")
    users = cursor.fetchall()
    
    # Buscar parâmetros atualmente associados à estação
    cursor.execute("""
        SELECT tp.id FROM parameters p 
        JOIN typeParameters tp ON p.cdTypeParameter = tp.id 
        WHERE p.cdStation = %s
    """, (station_id,))
    current_params = [row["id"] for row in cursor.fetchall()]
    
    connection.close()
    return render_template("edit_station.html", station=station, parameters=all_parameters, users=users, current_params=current_params)

@app.route("/deleteStation/<int:idStation>")
def deleteStation(idStation):
    if "user_id" not in session or session.get("user_role") != 1 or not session.get("user_name"):
        return redirect(url_for("index"))
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SET SQL_SAFE_UPDATES = 0;")
    
    cursor.execute("DELETE FROM stations WHERE id = %s", (idStation,))
    connection.commit()

    cursor.execute("SET SQL_SAFE_UPDATES = 1;")
    
    cursor.close()
    connection.close()

    return redirect(url_for("stations"))

@app.route("/edit_user/<int:user_id>", methods=["GET", "POST"])
@nocache
def edit_user(user_id):
    if "user_id" not in session or session.get("user_role") != 1 or not session.get("user_name"):
        return redirect(url_for("index"))

    connection = get_db_connection()
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        cpf = request.form.get("cpf")
        password = request.form.get("password")
        role = request.form.get("role")

        if not name or not email or not cpf or not role:
            cursor.execute("SELECT id, name, email, cpf, role FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            connection.close()
            return render_template("edit_user.html", user=user, error="Preencha todos os campos obrigatórios (exceto senha, se não for alterar).")

        try:
            if password:
                hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
                cursor.execute("UPDATE users SET name = %s, email = %s, cpf = %s, password = %s, role = %s WHERE id = %s",
                        (name, email, cpf, hashed_password, role, user_id))
            else:
                cursor.execute("UPDATE users SET name = %s, email = %s, cpf = %s, role = %s WHERE id = %s",
                        (name, email, cpf, role, user_id))
            connection.commit()
            cursor.execute("SELECT id, name, email, cpf, role FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            connection.close()
            return render_template("edit_user.html", user=user, success="Usuário atualizado com sucesso!")
        except pymysql.err.IntegrityError as e:
            cursor.execute("SELECT id, name, email, cpf, role FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            connection.close()
            return render_template("edit_user.html", user=user, error=f"Erro de integridade: {e}")
    else:
        cursor.execute("SELECT id, name, email, cpf, role FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        connection.close()
        if not user:
            return redirect(url_for("users"))
        return render_template("edit_user.html", user=user)

@app.route("/editUser/<int:idUser>")
def editUser(idUser):
    # Redireciona para a nova rota padronizada
    return redirect(url_for("edit_user", user_id=idUser))


@app.route("/about")
@nocache
def about():
    # Página sobre não requer login
    return render_template("about.html")

@app.route("/user_profile")
@nocache
def user_profile():
    if "user_id" not in session:
        return redirect(url_for("index"))

    user_id = session.get("user_id")
    connection = get_db_connection()
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    
    cursor.execute("SELECT id, name, email, cpf, role, createdAt FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    connection.close()
    
    if not user:
        return redirect(url_for("index"))
    
    return render_template("user_profile.html", user=user)

if __name__ == "__main__":
    app.run(debug=True)



