from dotenv import load_dotenv
import fdb
import os
from retorna_periodo import *
from conecta_firebird import *

load_dotenv()

conexao = conexao_firebird

    # Executando uma consulta SQL
def retorna_dados_vendas(dataini, datafim):
        cur = conexao.cursor()
        cur.execute(f"""SELECT                      
                    PCABVDA.EMPRESA,  
                    PCABVDA.DTEMISSAO,  
                    PCABVDA.HREMISSAO,  
                    PCABVDA.NROVDA,  
                    PPESCLI.NOME AS NOME_CLIENTE,                                                              
                    PREPRESE.DESCRICAO AS NOME_VENDEDOR,
                    PCABVDA.NROPEDCLI,
                    RETORNATOTALVDA.VLRTOTAL AS TOTAL      
                    FROM PCABVDA  
                    INNER JOIN PPESCLI 
                        ON PPESCLI.EMPRESA = PCABVDA.ESTABCLIENTE    
                    AND PPESCLI.CLIENTE = PCABVDA.CLIENTE    
                    LEFT JOIN PREPRESE      
                        ON PREPRESE.EMPRESA  = PCABVDA.ESTABREPRESENT    
                    AND PREPRESE.REPRESENT = PCABVDA.REPRESENT
                    LEFT JOIN PCUPOM
                        ON PCUPOM.EMPRESA = PCABVDA.EMPRESA
                    AND PCUPOM.NROVDA = PCABVDA.NROVDA
                    LEFT JOIN RETORNATOTALVDA(PCABVDA.EMPRESA, PCABVDA.NROVDA)    
                        ON 0=0
                    WHERE   PCABVDA.EMPRESA = 1003
                        AND PCABVDA.DTEMISSAO BETWEEN '{dataini}' AND '{datafim}'
                    ORDER BY DTEMISSAO""")

        # Obtendo os nomes das colunas
        colunas = [desc[0] for desc in cur.description]

        # Obtendo os valores
        valores = cur.fetchall()

        ## Iterando sobre os resultados
        #if valores:
        #    print("Nomes das Colunas: ", colunas)
        #    for valor in valores:
        #        print("Valores: ", valor)

        # Fechando o cursor e a conexão
        cur.close()
        conexao.close()

        return colunas, valores



