import requests
import json
import time
import paho.mqtt.client as mqtt

# CONFIGURAÇÕES
OWM_API_KEY = 'SUACHAVE'  # <- Insira sua chave da OpenWeatherMap
CITY = 'Blumenau,BR'
MQTT_BROKER = 'broker.hivemq.com'  # Pode usar o seu broker local também
MQTT_PORT = 1883
MQTT_TOPIC = 'blumenau/clima'


def obter_dados_clima():
    url = f'https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={OWM_API_KEY}&units=metric&lang=pt_br'
    response = requests.get(url)
    data = response.json()

    if response.status_code != 200:
        print("Erro ao buscar dados do clima:", data)
        return None

    clima = {
        'cidade': data.get('name'),
        'temperatura': data['main']['temp'],
        'sensacao': data['main']['feels_like'],
        'umidade': data['main']['humidity'],
        'vento': data['wind']['speed'],
        'descricao': data['weather'][0]['description']
    }

    return clima


def publicar_mqtt(payload):
    client = mqtt.Client()
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()

    mensagem = json.dumps(payload, ensure_ascii=False)
    client.publish(MQTT_TOPIC, mensagem)
    print(f'Publicado em {MQTT_TOPIC}: {mensagem}')

    client.loop_stop()
    client.disconnect()


# LOOP PRINCIPAL
if __name__ == "__main__":
    dados = obter_dados_clima()
    if dados:
        publicar_mqtt(dados)
