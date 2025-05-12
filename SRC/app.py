from flask import Flask, render_template
import pymysql #Conector com o banco de dadoflask

app = Flask(__name__)

def database():
    conexao = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        db='dht11_db',
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

@app.route('/', method['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    elif request.method == 'POST':
        entrada = request.form['entrada']
        senha = request.form['senha']


if __name__ == '__main__':
    app.run(debug=True)