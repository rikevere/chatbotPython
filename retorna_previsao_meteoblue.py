import requests
from dotenv import load_dotenv
import os

load_dotenv()

# Substitua 'SUA_CHAVE_API' pela sua chave API real do Meteoblue
API_KEY = os.getenv("METEOBLUE_API_KEY")
# Valores de latitude e longitude da localização da cidade de Verê
LATITUDE = os.getenv("LATITUDE_VERE")
LONGITUDE = os.getenv("LONGITUDE_VERE")

def obter_previsao_tempo(api_key, latitude, longitude):
    # Substitua URL_BASE_API pela URL base do endpoint da API do Meteoblue
    URL_BASE_API = f"https://my.meteoblue.com/packages/basic-day?apikey={api_key}&lat={latitude}&lon={longitude}&asl=769&format=json"
    # Faz a solicitação GET à API
    resposta = requests.get(URL_BASE_API)
    # Verifica se a solicitação foi bem-sucedida
    if resposta.status_code == 200:
        # Processa a resposta JSON
        dados_previsao = resposta.json()
        # Implemente aqui o processamento dos dados conforme necessário
        return dados_previsao
    else:
        print(f"Erro ao obter a previsão do tempo: {resposta.status_code}")


#print(obter_previsao_tempo(API_KEY, LATITUDE, LONGITUDE))
