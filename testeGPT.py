from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
import pandas as pd
import os
from conecta_db2 import pega_conexao_db2  # Importar a função para obter a conexão

# Carregar a chave do arquivo .env
load_dotenv()
client = OpenAI(
    api_key = os.getenv("OPENAI_API_KEY")
)
# Obter a conexão com o banco
try:
    conn = pega_conexao_db2()
except Exception as e:
    print(f"Erro ao estabelecer conexão com o banco de dados: {e}")
    exit()

# Consulta SQL para carregar os dados
sql = """
SELECT
    NOTAS.IDPLANILHA, 
    NOTAS.IDCLIFOR AS CLIENTE_ID,
    CLIENTE_FORNECEDOR.NOME AS NOME_CLIENTE,
    NOTAS_ENTRADA_SAIDA.DTMOVIMENTO AS DATA_COMPRA,
    ESTOQUE_ANALITICO.IDSUBPRODUTO AS PRODUTO_ID,
    PRODUTO.DESCRCOMPRODUTO AS PRODUTO_NOME,
    GRUPO.DESCRGRUPO AS CATEGORIA,
    ESTOQUE_ANALITICO.VALTOTLIQUIDO AS VALOR_COMPRA,
    ESTOQUE_ANALITICO.QTDPRODUTO AS QUANTIDADE,
    CASE 
        WHEN CLIENTE_FORNECEDOR.FLAGINATIVO = 'F' THEN 'ATIVO'
        WHEN CLIENTE_FORNECEDOR.FLAGINATIVO = 'T' THEN 'INATIVO'
        ELSE 'STATUS INDEFINIDO'
    END AS STATUS_CLIENTE,
    COUNT(*) OVER (PARTITION BY ESTOQUE_ANALITICO.IDSUBPRODUTO, MONTH(NOTAS_ENTRADA_SAIDA.DTMOVIMENTO)) AS RECORRENCIA_MENSAL
FROM
    NOTAS
INNER JOIN NOTAS_ENTRADA_SAIDA ON
        NOTAS.IDEMPRESA = NOTAS_ENTRADA_SAIDA.IDEMPRESA AND
        NOTAS.IDPLANILHA = NOTAS_ENTRADA_SAIDA.IDPLANILHA
INNER JOIN ESTOQUE_ANALITICO ON
        ESTOQUE_ANALITICO.IDEMPRESA = NOTAS.IDEMPRESA AND 
        ESTOQUE_ANALITICO.IDPLANILHA = NOTAS.IDPLANILHA 
INNER JOIN CLIENTE_FORNECEDOR ON
        CLIENTE_FORNECEDOR.IDCLIFOR = NOTAS.IDCLIFOR  
INNER JOIN PRODUTO ON
        PRODUTO.IDPRODUTO = ESTOQUE_ANALITICO.IDSUBPRODUTO  
INNER JOIN GRUPO ON
        GRUPO.IDGRUPO = PRODUTO.IDGRUPO    
WHERE
    NOTAS_ENTRADA_SAIDA.IDEMPRESA = 1 AND
    NOTAS_ENTRADA_SAIDA.DTMOVIMENTO BETWEEN '2024-01-01' AND '2024-12-31' AND
    UPPER(NOTAS.TIPONOTAFISCAL) = 'S' AND
    NOTAS_ENTRADA_SAIDA.IDOPERACAO <> 1301 AND
    UPPER(NOTAS.FLAGNOTACANCEL) = 'F'
"""

# Executar a consulta e carregar os resultados em um DataFrame
try:
    import ibm_db
    stmt = ibm_db.exec_immediate(conn, sql)
    rows = []
    while True:
        row = ibm_db.fetch_assoc(stmt)
        if not row:
            break
        rows.append(row)

    # Criar um DataFrame com os resultados
    df = pd.DataFrame(rows)

    # Converter Data_Compra para datetime
    df['DATA_COMPRA'] = pd.to_datetime(df['DATA_COMPRA'])

except Exception as e:
    print(f"Erro ao executar a consulta SQL: {e}")
    exit()

# Função para classificar clientes inativos
def classificar_inatividade(row):
    ultima_compra = row['DATA_COMPRA']  # Já é um Timestamp
    dias_sem_compras = (datetime.now() - ultima_compra).days
    if dias_sem_compras > 180:
        return "Inativo Crítico"
    elif dias_sem_compras > 90:
        return "Inativo Recente"
    return "Ativo"

df['STATUS_CLIENTE'] = df.apply(classificar_inatividade, axis=1)

# Função para sugerir promoções usando ChatGPT
def sugerir_promocao(cliente_id, historico_compras):
    prompt = f"""
    O cliente com ID {cliente_id} comprou os seguintes produtos: {historico_compras}.
    Sugira campanhas promocionais para reengajá-lo e produtos similares que ele possa gostar.
    """
    response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "Você é um assistente que ajuda vendedores a criarem campanhas."
                },
                {"role": "user", "content": prompt}
            ],
            model="gpt-3.5-turbo",
    )
    #    model="gpt-4",  # ou "gpt-3.5-turbo", o1-mini, o1-preview
    #    messages=[
    #        {"role": "system", "content": "Você é um assistente que ajuda vendedores a criarem campanhas."},
    #        {"role": "user", "content": prompt}
    #    ]
    #)
    return response.choices[0].message.content

# Teste: Sugerir promoção para o cliente 102
cliente_18368 = df[df['CLIENTE_ID'] == 18368]
historico = cliente_18368[['PRODUTO_NOME', 'CATEGORIA']].to_dict(orient='records')
print(f"""comprou os seguintes produtos: {historico}""")
print(sugerir_promocao(18368, historico))
