import requests
import json
import time
import paho.mqtt.client as mqtt

# CONFIGURAÇÕES
OWM_API_KEY = 'SUACHAVE'  # <- Insira sua chave da OpenWeatherMap
CITY = 'Blumenau,BR'
MQTT_BROKER = 'broker.hivemq.com'
MQTT_PORT = 1883
MQTT_TOPIC = 'blumenau/clima'

TELEGRAM_BOT_TOKEN = 'SEU_TOKEN_AQUI'
TELEGRAM_CHAT_ID = 'SEU_CHAT_ID_AQUI'  # geralmente começa com - se for grupo

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

def enviar_telegram(payload):
    texto = (
        f"🌤 Clima em {payload['cidade']}:\n"
        f"🌡 Temperatura: {payload['temperatura']}°C\n"
        f"🤒 Sensação: {payload['sensacao']}°C\n"
        f"💧 Umidade: {payload['umidade']}%\n"
        f"💨 Vento: {payload['vento']} m/s\n"
        f"🔎 Descrição: {payload['descricao'].capitalize()}"
    )

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    params = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": texto,
        "parse_mode": "HTML"
    }

    response = requests.post(url, data=params)
    if response.status_code == 200:
        print("Mensagem enviada ao Telegram com sucesso.")
    else:
        print("Erro ao enviar mensagem para o Telegram:", response.text)


# LOOP PRINCIPAL
if __name__ == "__main__":
    dados = obter_dados_clima()
    if dados:
        publicar_mqtt(dados)
        enviar_telegram(dados)
