import requests
from dotenv import load_dotenv
import os

def encontrar_cidade(latitude, longitude):
    url = f"http://nominatim.openstreetmap.org/reverse?format=json&lat={latitude}&lon={longitude}"
    resposta = requests.get(url)
    if resposta.status_code == 200:
        dados = resposta.json()
        #abaixo exemplo de como pegar dados de um JSON
        cidade = dados['address'].get('village')
        rua =  dados['address'].get('road')
        estado =  dados['address'].get('state')
        pais = dados['address'].get('country')
        return cidade, rua, estado, pais 
    else:
        return "Não foi possível encontrar a cidade."

#cidade, rua, estado, pais = encontrar_cidade(-25.88001, -52.90846)
#print(f"A cidade correspondente às coordenadas é: {cidade} - {rua}, estado do {estado} - {pais}")
