import requests

# Substitua 'SUA_CHAVE_API' pela sua chave API real do ClimaTempo
# Substitua 'ID_DA_CIDADE' pelo ID real da cidade
chave_api = "1698779385f928db22721051eeead76e"
id_cidade = "ID_DA_CIDADE"
nome_cidade = ""

def obter_temperatura_climatica(chave_api, id_cidade):
    # URL para obter a temperatura climática pela ID da cidade
    url = f"http://apiadvisor.climatempo.com.br/api/v1/climate/temperature/locale/{id_cidade}?token={chave_api}"
    print(f"http://apiadvisor.climatempo.com.br/api/v1/climate/temperature/locale/{id_cidade}?token={chave_api}")
    # Faz a solicitação GET à API
    resposta = requests.get(url)

    # Verifica se a solicitação foi bem-sucedida
    if resposta.status_code == 200:
        dados = resposta.json()
        # Assumindo que a resposta contém os dados de temperatura climática, imprime os resultados
        print(f"Dados Climáticos para a cidade ID {id_cidade}:")
        print(dados)  # Imprime os dados brutos, ajuste conforme necessário para acessar informações específicas
    else:
        print(f"Erro ao obter dados climáticos: {resposta.status_code}")

def buscar_id_cidade(nome_cidade, chave_api):
    # URL para a busca de cidades na API do ClimaTempo
    url = f"http://apiadvisor.climatempo.com.br/api/v1/locale/city?name={nome_cidade}&token={chave_api}"
    print(f"http://apiadvisor.climatempo.com.br/api/v1/locale/city?name={nome_cidade}&token={chave_api}")
    # Faz a solicitação GET à API
    resposta = requests.get(url)

    # Verifica se a solicitação foi bem-sucedida
    if resposta.status_code == 200:
        cidades = resposta.json()
        if cidades:
            # Assumindo que a primeira cidade retornada é a desejada
            primeira_cidade = cidades[0]
            print(f"ID da cidade '{nome_cidade}': {primeira_cidade['id']}")
            print(f"Nome completo: {primeira_cidade['name']}, {primeira_cidade['state']}, {primeira_cidade['country']}")
            return primeira_cidade['id']
        else:
            print("Nenhuma cidade encontrada.")
            return None
    else:
        print(f"Erro ao buscar a cidade: {resposta.status_code}")
        return None

#
nome_cidade = input(f"Nome da Cidade: ")
id_retornado_cidade = buscar_id_cidade(nome_cidade, chave_api)
print(f"o ID da cidade informada é: {id_retornado_cidade}") 
obter_temperatura_climatica(chave_api, id_retornado_cidade)

