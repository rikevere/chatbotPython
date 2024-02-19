from dotenv import load_dotenv
import fdb
import os
from retorna_periodo import *

load_dotenv()

# Substitua estas variáveis pelos seus valores reais
hostname = '127.0.0.1'  # ou IP do servidor
database = 'c:/viasoft/dados/dadosnovo.fdb'
user = os.getenv("USER_FIREBIRD")
password = os.getenv("PASSWORD_FIREBIRD")

try:
    # Estabelecendo a conexão
    conexao_firebird = fdb.connect(dsn=hostname + ':' + database, user=user, password=password)
    print("Conexão estabelecida com sucesso!")

except fdb.fbcore.DatabaseError as e:
    print(f"Erro ao conectar ao banco de dados Firebird: {e}")

finally:
    # Certifique-se de que a conexão seja fechada mesmo se ocorrer um erro
    if 'con' in locals() and conexao_firebird:
        conexao_firebird.close()