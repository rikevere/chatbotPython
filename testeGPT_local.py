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
    NOTAS_ENTRADA_SAIDA.DTMOVIMENTO BETWEEN '2023-01-01' AND '2023-07-31' AND
    UPPER(NOTAS.TIPONOTAFISCAL) = 'S' AND
    UPPER(NOTAS.FLAGNOTAPROPRIA) = 'F"
    NOTAS_ENTRADA_SAIDA.IDOPERACAO <> 1301 AND
    NOTAS_ENTRADA_SAIDA.IDOPERACAO > 1000 AND
    UPPER(NOTAS.FLAGNOTACANCEL) = 'F' AND
    UPPER(NOTA.FLAGNOTACANCEL = 'F'
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

# Processar localmente para reduzir a massa de dados
def processar_dados(df, token_limit=128000):
    hoje = datetime.now()
    # Calcular dias sem compras
    df['DIAS_SEM_COMPRAS'] = (hoje - df['DATA_COMPRA']).dt.days
    # Classificar clientes
    df['STATUS_CLIENTE'] = df['DIAS_SEM_COMPRAS'].apply(
        lambda dias: "Inativo Crítico" if dias > 180 else "Inativo Recente" if dias > 90 else "Ativo"
    )
    # Agregar dados por cliente
    resumo = df.groupby('CLIENTE_ID').agg(
        Nome_Cliente=('NOME_CLIENTE', 'first'),
        Total_Compras=('VALOR_COMPRA', 'sum'),
        Ultima_Compra=('DATA_COMPRA', 'max'),
        Produtos_Comprados=('PRODUTO_NOME', lambda x: ', '.join(x.unique())),
        Status_Cliente=('STATUS_CLIENTE', 'first')
    ).reset_index()

    # Filtrar clientes por prioridade: primeiro os inativos
    resumo_inativos = resumo[resumo['STATUS_CLIENTE'].isin(["Inativo Crítico", "Inativo Recente"])]
    resumo_ativos = resumo[resumo['STATUS_CLIENTE'] == "ATIVO"]

    # Estimar tokens
    def estimar_tokens(dataframe):
        texto = dataframe.to_dict(orient="records")
        return len(str(texto))
    
    # Combinar os dados respeitando o limite de tokens
    token_atual = 0
    dados_para_envio = []
    
    for dataframe in [resumo_inativos, resumo_ativos]:
        for _, linha in dataframe.iterrows():
            linha_dict = linha.to_dict()
            token_linha = estimar_tokens(pd.DataFrame([linha_dict]))  # Usa a função para calcular tokens
            
            if token_atual + token_linha <= token_limit:
                dados_para_envio.append(linha_dict)
                token_atual += token_linha
            else:
                break  # Para quando atingir o limite de tokens

    return pd.DataFrame(dados_para_envio)

# Resumo dos dados
resumo_df = processar_dados(df)

# Gerar prompt reduzido para envio à API
def gerar_prompt_geral(resumo_df):
    prompt = f"""
    Baseado no seguinte resumo de clientes:
    {resumo_df.to_dict(orient="records")}

    **Tarefas:**
    1. Identifique os clientes inativos críticos e recentes e sugira campanhas de reengajamento.
    2. Para os clientes ativos, sugira produtos complementares baseados em suas compras anteriores.
    3. Proponha um plano promocional com base nos padrões de compras.

    Responda com um plano claro e conciso.
    """
    return prompt

print(gerar_prompt_geral(resumo_df))

# Enviar resumo para a API

prompt = gerar_prompt_geral(resumo_df)
try:
    response = client.chat.completions.create(
            model="o1-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                    ],
                }
            ]        

    )
    print(response.choices[0].message.content)
except Exception as e:
    print(f"Erro ao gerar sugestões: {e}")