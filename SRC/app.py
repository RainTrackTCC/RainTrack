from flask import Flask, flash, render_template, request, redirect, url_for, session
from flask import make_response
from functools import wraps
import pymysql.cursors
from dotenv import load_dotenv
import os
import pymysql

load_dotenv()
app = Flask(__name__)
app.secret_key = "chaveSegurança"

def nocache(view):
    @wraps(view)
    def no_cache_view(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    return no_cache_view

@app.context_processor
def inject_user():
    return {
        'user_name': session.get('user_name'),
        'user_role': session.get('user_role')
    }

def get_db_connection():
    connection = pymysql.connect(
        host = os.getenv('DB_HOST'),
        user = os.getenv('DB_USER'),
        password = os.getenv('DB_PASSWORD'),
        db = os.getenv('DB_NAME'),
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection

@app.route('/', methods=['GET', 'POST'])
@nocache
def index():
    if request.method == 'POST':
        entry = request.form.get('entry')
        password = request.form.get('password')
        
        if not entry or not password:
            error_message = 'Por favor, preencha todos os campos.'
            return render_template('index.html', error=error_message)
        
        connection = get_db_connection()
        connection = get_db_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT password, email, name, role, cpf FROM users WHERE email = %s OR cpf = %s", (entry, entry))
        user = cursor.fetchone()
        cursor.close()
        connection.close()

        if not user:
            error_message = 'Usuário não encontrado. Verifique seu email ou CPF.'
        elif user['password'] != password:
            error_message = 'Senha incorreta. Tente novamente.'
        else:
            session['user_name'] = user['name'].split()[0]
            session['user_role'] = user['role']
            session['user_id'] = user['cpf']
            return redirect(url_for('home'))

        return render_template('index.html', error=error_message)
    
    return render_template('index.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/home')
@nocache
def home():
    session.clear()
    if 'user_id' not in session:
        session['user_name'] = "Convidado"
        session['user_role'] = 0
        session['user_id'] = 12345678910
        return redirect(url_for('home'))

    user_name = session.get('user_name')
    user_role = session.get('user_role')
    return render_template("home.html")

@app.route('/admin', methods=['GET', 'POST'])
@nocache
def admin():
    user_name = session.get('user_name')
    user_role = session.get('user_role')

    if not user_name or user_role != 1:
        return redirect(url_for('index'))

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        cpf = request.form.get('cpf')
        password = request.form.get('password')
        role = request.form.get('role')

        connection = get_db_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT id FROM users WHERE email = %s OR cpf = %s", (email, cpf))
        existing_user = cursor.fetchone()

        if existing_user:
            error = "Email ou CPF já existe."
            return render_template("admin.html", error=error)

        cursor.execute("INSERT INTO users (name, email, cpf, password, role) VALUES (%s, %s, %s, %s, %s)",
                       (name, email, cpf, password, role))
        connection.commit()
        cursor.close()
        connection.close()
        success = "Usuário cadastrado com sucesso!"
        return render_template("admin.html", success=success)

    return render_template("admin.html")

@app.route('/stations')
@nocache
def stations():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT name, latitude, longitude, uuid FROM stations ORDER BY createdAt DESC")
    stations = cursor.fetchall()
    connection.close()
    return render_template("stations.html", stations=stations)

@app.route('/add_station', methods=['GET', 'POST'])
@nocache
def add_station():
    if 'user_id' not in session:
        return redirect(url_for('index'))

    connection = get_db_connection()
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    # Consultar todos os parâmetros disponíveis
    cursor.execute("SELECT id, name, unit FROM typeParameters")
    parameters = cursor.fetchall()

    if request.method == 'POST':
        name = request.form.get('name')
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        uuid = request.form.get('uuid')
        uuid_clean = uuid.replace(":", "").upper()
        selected_parameters = request.form.getlist('cdParameter')  # IDs dos parâmetros

        if not name or not latitude or not longitude or not uuid:
            return render_template("add_station.html", error="Preencha todos os campos obrigatórios.", parameters=parameters)

        if not selected_parameters:
            return render_template("add_station.html", error="Selecione pelo menos um parâmetro.", parameters=parameters)

        try:
            # Inserir a estação
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

        return render_template("add_station.html", success=success, parameters=parameters)


    return render_template("add_station.html", parameters=parameters)




@app.route('/parameters')
@nocache
def parameters():
    if 'user_id' not in session:
        return redirect(url_for('index'))

    connection = get_db_connection()
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM typeParameters ORDER BY name")
    parameters = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template('parameters.html', parameters=parameters)

@app.route('/add_parameter', methods=['GET', 'POST'])
@nocache
def add_parameter():
    if 'user_id' not in session:
        return redirect(url_for('index'))

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT id, name FROM stations")
    stations = cursor.fetchall()

    if request.method == 'POST':
        name = request.form.get('name')
        unit = request.form.get('unit')
        typeJson = request.form.get('typeJson')
        decimalPlaces = request.form.get('decimalPlaces')

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

@app.route('/users', methods=['GET', 'POST'])
@nocache
def users():
    user_name = session.get('user_name')
    user_role = session.get('user_role')

    if not user_name or user_role != 1:
        return redirect(url_for('index'))
    
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id, name, cpf, email, role, createdAt FROM users ORDER BY createdAt DESC")
    users = cursor.fetchall()
    connection.close()
    return render_template("users.html", users=users)

@app.route('/graphs')
@nocache
def graphs():
    if 'user_id' not in session:
        return redirect(url_for('index'))

    connection = get_db_connection()
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    
    # Pega todas as estações
    cursor.execute("SELECT id, name, uuid FROM stations ORDER BY createdAt DESC")
    stations = cursor.fetchall()

    for station in stations:
        # Pega todos os parâmetros desta estação
        cursor.execute("""
            SELECT tp.name, tp.unit, m.value, m.measureTime
            FROM parameters p
            JOIN typeParameters tp ON p.cdTypeParameter = tp.id
            JOIN measures m ON m.cdParameter = p.id
            WHERE p.cdStation = %s
            ORDER BY m.measureTime
        """, (station['id'],))
        measures = cursor.fetchall()

        # Agrupa os dados por parâmetro
        param_dict = {}
        categories = sorted(list({m['measureTime'].strftime("%H:%M") for m in measures}))  # horários
        for m in measures:
            key = f"{m['name']} ({m['unit']})"
            if key not in param_dict:
                param_dict[key] = [None]*len(categories)
            idx = categories.index(m['measureTime'].strftime("%H:%M"))
            param_dict[key][idx] = m['value']

        station['categories'] = categories
        station['series'] = [{"name": k, "data": v} for k,v in param_dict.items()]

    connection.close()
    return render_template('graphs.html', stations=stations)

@app.route('/deleteUser/<int:idUser>')
def deleteUser(idUser):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    cursor.execute("DELETE FROM users WHERE id = %s", (idUser,))
    connection.commit()
    
    cursor.close()
    connection.close()

    return redirect(url_for('users'))

if __name__ == '__main__':
    app.run(debug=True)