from flask import Flask, render_template, request, redirect, url_for
import pymysql.cursors
from dotenv import load_dotenv
import os
import pymysql #Conector com o banco de dadoflask

load_dotenv()
app = Flask(__name__)

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
            cursor.execute("SELECT temperature, humidity, timestamp FROM dht11_readings ORDER BY timestamp")
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
    dados = get_data()
    print(dados)
    return render_template("home.html", dados=dados)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        entrada = request.form['entrada']
        senha = request.form['senha']
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(pymysql.cursors.DictCursor)
            cursor.execute("SELECT * FROM users WHERE email = %s or cpf = %s", (entrada, entrada))
            user = cursor.fetchone()
            if user and user['senha'] == senha:
               return redirect(url_for('home'))
            else:
                return render_template('index.html', error='Invalid credentials')
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)