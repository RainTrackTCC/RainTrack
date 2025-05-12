from flask import Flask, render_template, request, redirect, url_for
from dotenv import load_dotenv
import os
import pymysql #Conector com o banco de dadoflask


app = Flask(__name__)

def database():
    conexao = pymysql.connect(
        host = os.getenv('DB_HOST'),
        user = os.getenv('DB_USER'),
        password = os.getenv('DB_PASSWORD'),
        db = os.getenv('DB_NAME'),
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        with conexao.cursor() as cursor:
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
        conexao.close()

@app.route('/home')
def home():
    dados = database()
    print(dados)
    return render_template("home.html", dados=dados)

@app.route('/', methods = ['GET', 'POST'])
def index():
    if request.method == 'POST':
        entrada = request.form['entrada']
        senha = request.form['senha']

        conexao = database()
        if conexao:
            cursor = conexao.cursor(pymysql.cursors.DictCursor)
            cursor.execute("SELECT * FROM users WHERE email = %s or cpf = %s", (entrada, entrada))
            user = cursor.fetchone()
            if user['senha'] == senha:
                return redirect(url_for('home'))
            else:
                return render_template('index.html', error='Invalid credentials')

if __name__ == '__main__':
    app.run(debug=True)