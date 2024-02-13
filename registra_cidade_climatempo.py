import requests

# Substitua 'SUA_CHAVE_API' pela sua chave API real do ClimaTempo
CHAVE_API = "1698779385f928db22721051eeead76e"
# Substitua 'ID_DA_CIDADE' pelo ID real da cidade que você deseja registrar ao seu token
ID_CIDADE = "6265"


def registrar_cidade(chave_api, id_cidade):
    # Endpoint para registrar a cidade ao token
    url = f'http://apiadvisor.climatempo.com.br/api-manager/user-token/{chave_api}/locales'

    # Dados para serem enviados na solicitação POST
    dados = {'localeId[]': id_cidade}

    # Faz a solicitação POST
    resposta = requests.post(url, data=dados)

    # Verifica se a solicitação foi bem-sucedida
    if resposta.status_code == 200:
        print('Cidade registrada com sucesso ao token.')
    else:
        print(f'Erro ao registrar a cidade: {resposta.status_code}')
        print(resposta.text)

registrar_cidade(CHAVE_API, ID_CIDADE)
