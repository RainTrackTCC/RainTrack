import json
import mysql.connector
import paho.mqtt.client as mqtt
import unicodedata

# Conexão com o MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="rainTrack"
)
cursor = db.cursor(dictionary=True)

# Normaliza os nomes dos parâmetros para maiúsculas sem acentos
def normalize_param(name):
    nfkd = unicodedata.normalize('NFKD', name)
    only_ascii = nfkd.encode('ASCII', 'ignore').decode('utf-8')
    return only_ascii.upper()

# Callback quando o cliente se conecta ao broker
def on_connect(client, userdata, flags, rc):
    print("Conectado ao MQTT com código:", rc)
    client.subscribe("fatec/+/data")  # Assina todos os tópicos de estação

# Callback quando uma mensagem é recebida
def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        print(f"Recebido no tópico {msg.topic}: {payload}")
        data = json.loads(payload)

        # uuid da estação (UUID)
        station_uuid = data.get("uuid")
        if not station_uuid:
            print("Erro: uuid da estação não fornecido.")
            return

        # Remove uuid para sobrar apenas os parâmetros reais
        parameters_data = {k: v for k, v in data.items() if k != "uuid"}

        for param_name, value in parameters_data.items():
            # Normaliza para consultar no banco
            param_name_db = normalize_param(param_name)

            # Busca cdParameter correto para a estação
            cursor.execute("""
                SELECT p.id
                FROM parameters p
                JOIN typeParameters t ON p.cdTypeParameter = t.id
                JOIN stations s ON p.cdStation = s.id
                WHERE s.uuid = %s AND t.name = %s
            """, (station_uuid, param_name_db))

            result = cursor.fetchone()
            if result:
                cdParameter = result['id']
                cursor.execute(
                    "INSERT INTO measures (value, cdParameter) VALUES (%s, %s)",
                    (value, cdParameter)
                )
            else:
                print(f"Atenção: Parâmetro '{param_name}' não encontrado para a estação {station_uuid}")

        db.commit()
        print("Dados inseridos no banco com sucesso.")

    except Exception as e:
        print("Erro ao processar a mensagem:", e)

# Configuração do cliente MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Conectando ao broker
client.connect("test.mosquitto.org", 1883, 60)
client.loop_forever()
