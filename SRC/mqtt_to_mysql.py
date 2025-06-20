import json
import mysql.connector
import paho.mqtt.client as mqtt

# Conexão com o MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="rainTrack"
)
cursor = db.cursor()

def on_connect(client, userdata, flags, rc):
    print("Conectado ao MQTT com código: " + str(rc))
    client.subscribe("fatec/dht11/data")

def on_message(client, userdata, msg):
    print(f"Recebido: {msg.payload.decode()}")
    try:
        data = json.loads(msg.payload.decode())
        temperature = data['temperature']
        humidity = data['humidity']
        cursor.execute("INSERT INTO readings (temperature, humidity) VALUES (%s, %s)", (temperature, humidity))
        db.commit()
        print("Dados inseridos no banco com sucesso.")
    except Exception as e:
        print("Erro ao inserir no banco:", e)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("192.168.0.12", 1883, 60)
client.loop_forever()
