from dotenv import load_dotenv
import os
os.environ['PYTHONIOENCODING'] = 'UTF-8'
os.add_dll_directory('C:/Program Files/IBM/SQLLIB/BIN')
import ibm_db

# Carregar variáveis do arquivo .env
load_dotenv()

def pega_conexao_db2():
    """
    Estabelece a conexão com o banco DB2 e retorna o objeto de conexão.
    """
    # Configurações de conexão
    dsn = (
       f"DATABASE={os.getenv('DB_DATABASE')};"
       f"HOSTNAME={os.getenv('DB_HOSTNAME')};"
       f"PORT={os.getenv('DB_PORT')};"
       f"PROTOCOL={os.getenv('DB_PROTOCOL')};"
       f"UID={os.getenv('DB_UID')};"
       f"PWD={os.getenv('DB_PWD')};"
    )

    try:
        conn = ibm_db.connect(dsn, "", "")
        print("Conexão bem-sucedida!")
        return conn  # Retorna a conexão para ser usada externamente
    except Exception as e:
        print("Erro ao conectar ao banco de dados:", repr(e))  # Mostra o erro completo
        raise e  # Levanta a exceção para tratamento posterior
