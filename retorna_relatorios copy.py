from dotenv import load_dotenv
from conecta_db2 import pega_conexao_db2  # Importar a função para obter a conexão
import ibm_db
import Levenshtein

load_dotenv()

import ibm_db

def buscar_produtos_similares(descricao_base, limite=5):
    """
    Busca produtos no banco de dados com descrições mais próximas da string fornecida.
    """

    try:
        conn = pega_conexao_db2()
    except Exception as e:
        print(f"Erro ao estabelecer conexão com o banco de dados: {e}")
        exit()

    sql = """SELECT PG.IDSUBPRODUTO, PG.DESCRRESPRODUTO 
                FROM DBA.PRODUTO_GRADE PG
                JOIN ESTOQUE_SALDO_ATUAL ESA
                    ON ESA.IDSUBPRODUTO = PG.IDSUBPRODUTO
                AND ESA.IDEMPRESA = 1
                AND ESA.IDLOCALESTOQUE = 1
                WHERE ESA.QTDATUALESTOQUE > 0 AND PG.FLAGBLOQUEIAVENDA = 'F';"""
    
    try:
        import ibm_db
        stmt = ibm_db.exec_immediate(conn, sql,)
        produtos_DIST = []
        produtos_SIMI = []
        while True:
            row = ibm_db.fetch_assoc(stmt)
            if not row:
                break
            descricao_produto = row["DESCRRESPRODUTO"]
            id_produto = row["IDSUBPRODUTO"]
            #distancia = levenshtein_distance(descricao_base, descricao_produto)
            distancia_Levenshtein = Levenshtein.distance(descricao_base, descricao_produto)
            distancia_hamming = Levenshtein.hamming(descricao_base, descricao_produto)
            #similaridade = Levenshtein.jaro_winkler(descricao_base, descricao_produto)
            produtos_DIST.append((id_produto, descricao_produto, distancia_Levenshtein))
            produtos_SIMI.append((id_produto, descricao_produto, distancia_hamming))


        # Ordenar pelo menor valor de distância
        produtos_ordenados_DIST = sorted(produtos_DIST, key=lambda x: x[2])
        produtos_ordenados_SIMI = sorted(produtos_SIMI, key=lambda x: x[2])

        # Retornar os `limite` primeiros produtos
        return produtos_ordenados_DIST[:limite], produtos_ordenados_SIMI[:limite]
    
    except Exception as e:
        print(f"Erro ao buscar produtos similares: {e}")
        return []


descricao_pesquisa = "PremieR Não se aplica Alimentos para Pets Ração para Cães Ração para Raças Específicas Adultos Nutrição Pet Frango Super Premium 12 kg"

produtos_similares_DIST, produtos_similares_SIMI = buscar_produtos_similares(descricao_pesquisa, limite=5)


print("Produtos Similares Encontrados distancia_Levenshtein:")
for produto in produtos_similares_DIST:
    print(f"ID: {produto[0]}, Descrição: {produto[1]}, Distância: {produto[2]}")

print("Produtos Similares Encontrados distancia_hamming:")
for produto in produtos_similares_SIMI:
    print(f"ID: {produto[0]}, Descrição: {produto[1]}, Distância: {produto[2]}")

