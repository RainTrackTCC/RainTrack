from flask import Flask, flash, render_template, request, redirect, url_for
import pymysql.cursors
from dotenv import load_dotenv
import os
import pymysql #Conector com o banco de dadoflask

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

@app.route('/home')
def home():
    # dados = get_data()
    user_name = request.args.get('user_name')
    user_role = request.args.get('user_role')
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

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        entry = request.form.get('entry')
        password = request.form.get('password')
        
        if not entry or not password:
            error_message = 'Por favor, preencha todos os campos.'
            return render_template('index.html', error=error_message)
        
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(pymysql.cursors.DictCursor)
            cursor.execute("SELECT password, email, name, role, cpf FROM users WHERE email = %s OR cpf = %s", (entry, entry))
            user = cursor.fetchone()
            if user and user['password'] == password:
                return redirect(url_for('home', user_name=user['name'], user_role=user['role']))
            else:
                if user is None:
                    error_message = 'Usuário não encontrado. Verifique seu email ou CPF.'
                else:
                    error_message = 'Senha incorreta. Tente novamente.'
                return render_template('index.html', error=error_message)
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True) 