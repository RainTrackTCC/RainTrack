#include <WiFi.h>
#include <PubSubClient.h>
#include "DHT.h"

#define DHTPIN 4
#define DHTTYPE DHT11

char* ssid = "Wifi-Igor";
char* pwd = "isabelli2014";
char* mqtt_server = "test.mosquitto.org";

WiFiClient wclient;
PubSubClient mqttClient(wclient);
DHT dht(DHTPIN, DHTTYPE);

unsigned long lastSend = 0;
const long interval = 10000; // 5 minutos

void connectWifi(){
  WiFi.begin(ssid, pwd);
  Serial.print("Conectando ao WiFi");
  while(WiFi.status() != WL_CONNECTED){
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConectado ao WiFi");
}

void connectMqtt(){
  while (!mqttClient.connected()){
    if (mqttClient.connect("esp32-dht11")){
      Serial.println("Conectado ao MQTT");
    } else {
      Serial.println("Tentando MQTT de novo em 5s...");
      delay(5000);
    }
  }
}

void setup(){
  Serial.begin(115200);
  dht.begin();
  connectWifi();
  mqttClient.setServer(mqtt_server, 1883);
}

void loop(){
  if (!mqttClient.connected()){
    connectMqtt();
  }
  mqttClient.loop();

  unsigned long now = millis();
  if (now - lastSend >= interval){
    lastSend = now;
    float h = dht.readHumidity();
    float t = dht.readTemperature();

    if (isnan(h) || isnan(t)) {
      Serial.println("Erro ao ler DHT11");
      return;
    }

    char msg[100];
    snprintf(msg, sizeof(msg), "{\"temperature\": %.2f, \"humidity\": %.2f}", t, h);
    Serial.print("Enviando: ");
    Serial.println(msg);

    mqttClient.publish("fatec/dht11/data", msg);
  }
}
