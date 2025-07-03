from flask import Flask, flash, render_template, request, redirect, url_for, session
import pymysql.cursors
from dotenv import load_dotenv
import os
import pymysql

load_dotenv()
app = Flask(__name__)
app.secret_key = "chaveSegurança"

def get_db_connection():
    connection = pymysql.connect(
        host = os.getenv('DB_HOST'),
        user = os.getenv('DB_USER'),
        password = os.getenv('DB_PASSWORD'),
        db = os.getenv('DB_NAME'),
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection

def get_data():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT temperature, humidity, timestamp FROM measures ORDER BY timestamp")
            results = cursor.fetchall()

        tempo = [linha["timestamp"].strftime("%H:%M") for linha in results]
        temperaturas = [linha["temperature"] for linha in results]
        humidades = [linha["humidity"] for linha in results]

        return {
            "categories": tempo,
            "series": [
                { "name": "Temperatura (°C)", "data": temperaturas },
                { "name": "Humidade (%)", "data": humidades }
            ]
        }
    finally:
        connection.close()

@app.route('/', methods=['GET', 'POST'])
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
            session['user_name'] = user['name']
            session['user_role'] = user['role']
            return redirect(url_for('home'))

        return render_template('index.html', error=error_message)
    
    return render_template('index.html')

@app.route('/home')
def home():
    # dados = get_data()
    user_name = session.get('user_name')
    user_role = session.get('user_role')
    return render_template("home.html", user_name=user_name, user_role=user_role)
    # print(dados)
    # return render_template("home.html", dados=dados, user_name=user_name, user_role=user_role)

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        cpf = request.form['cpf']
        senha = request.form['senha']
        connection = get_db_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT id FROM users WHERE email = %s OR cpf = %s", (email, cpf))
        user = cursor.fetchone()

        if user:
            error_message = "Email ou CPF já existem."
            return render_template("register.html", error=error_message)
        cursor.execute("INSERT INTO users (nome, email, cpf, senha) VALUES (%s, %s, %s, %s)",
                       (nome, email, cpf, senha))
        connection.commit()
        cursor.close()
        connection.close()
        return redirect(url_for('index', success='true'))

    return render_template("register.html") 

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    user_name = session.get('user_name')
    user_role = session.get('user_role')

    if not user_name or user_role != 1:
        return redirect(url_for('index'))

    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        cpf = request.form.get('cpf')
        senha = request.form.get('senha')
        role = request.form.get('role')

        connection = get_db_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT id FROM users WHERE email = %s OR cpf = %s", (email, cpf))
        existing_user = cursor.fetchone()

        if existing_user:
            error = "Email ou CPF já existe."
            return render_template("admin.html", user_name=user_name, user_role=user_role, error=error)

        cursor.execute("INSERT INTO users (nome, email, cpf, senha, role) VALUES (%s, %s, %s, %s, %s)",
                       (nome, email, cpf, senha, role))
        connection.commit()
        cursor.close()
        connection.close()
        success = "Usuário cadastrado com sucesso!"
        return render_template("admin.html", user_name=user_name, user_role=user_role, success=success)

    return render_template("admin.html", user_name=user_name, user_role=user_role)

if __name__ == '__main__':
    app.run(debug=True) 