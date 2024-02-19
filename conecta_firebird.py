from dotenv import load_dotenv
import fdb
import os

load_dotenv()


def pega_conexao_fb():
    # Substitua estas variáveis pelos seus valores reais
    hostname = '127.0.0.1'  # ou IP do servidor
    database = 'c:/viasoft/dados/dadosnovo.fdb'
    user = os.getenv("USER_FIREBIRD")
    password = os.getenv("PASSWORD_FIREBIRD")
    port = 3050  # Porta padrão do Firebird

    try:
        con = fdb.connect(host=hostname, database=database, user=user, password=password, port=port)
        print("Conexão com o banco de dados estabelecida com sucesso.")
        return con
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None