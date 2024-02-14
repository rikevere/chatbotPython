import requests

def obter_previsao_tempo(api_key, latitude, longitude):
    # Substitua URL_BASE_API pela URL base do endpoint da API do Meteoblue
    URL_BASE_API = "https://my.meteoblue.com/packages/basic-day?"
    
    # Configura os parâmetros da solicitação, incluindo sua chave API e as coordenadas da localização
    parametros = {
        "apikey": api_key,
        "lat": latitude,
        "lon": longitude,
        # Adicione mais parâmetros conforme necessário
    }
    
    # Faz a solicitação GET à API
    resposta = requests.get(URL_BASE_API, params=parametros)
    
    # Verifica se a solicitação foi bem-sucedida
    if resposta.status_code == 200:
        # Processa a resposta JSON
        dados_previsao = resposta.json()
        # Implemente aqui o processamento dos dados conforme necessário
        print(dados_previsao)
    else:
        print(f"Erro ao obter a previsão do tempo: {resposta.status_code}")

# Substitua 'SUA_CHAVE_API' pela sua chave API real do Meteoblue
API_KEY = "uhM3tzcGWkjprIO2"
# Substitua pelos valores de latitude e longitude da localização desejada
LATITUDE = "-25.881"
LONGITUDE = "-52.908"

obter_previsao_tempo(API_KEY, LATITUDE, LONGITUDE)
