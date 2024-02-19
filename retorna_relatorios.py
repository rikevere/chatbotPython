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
port = 3050  # Porta padrão do Firebird

try:
    con = fdb.connect(host=hostname, database=database, user=user, password=password, port=port)
    print("Conexão com o banco de dados estabelecida com sucesso.")
    # Executando uma consulta SQL
    def retorna_dados_vendas(dataini, datafim):      
        cur = con.cursor()
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

        # Fecha o cursor
        cur.close()

        return colunas, valores

    def retorna_dados_contas_a_pagar(dataini, datafim):
        cur = con.cursor()
        cur.execute(f"""SELECT VDUPPAG.DUPPAG, VDUPPAG.DTEMISSAO,
                    VDUPPAG.DTENTRADA, VDUPPAG.DTPREVREC, 
                    VDUPPAG.DTVENCTO, VDUPPAG.VALOR,
                    VDUPPAG.JUROS, VDUPPAG.DESCONTOS,
                    VDUPPAG.MESCOMPET, VDUPPAG.ANOCOMPET,
                    PPESSFOR.NOME, VDUPPAG.FORNECEDOR,
                    VDUPPAG.HISTORICO,
                    VDUPPAG.PAGO AS TOTPAG, 
                    VDUPPAG.SALDO, VDUPPAG.MOEDA, 
                    VDUPPAG.ANALITICA, VDUPPAG.PORTADOR, 
                    PPORTADO.DESCRICAO AS NOMEPORT, 
                    VDUPPAG.ESTABFORNECEDOR, 
                    VDUPPAG.JUROSPEND, VDUPPAG.DESCPEND, 
                    VDUPPAG.CENCUSCOD, VDUPPAG.CENTROCUS, 
                    VDUPPAG.SITUACAO, PSITUACA.DESCRICAO AS DESCSITUAC 
                    FROM VDUPPAG
                    LEFT JOIN PPESSFOR
                    ON (VDUPPAG.ESTABFORNECEDOR = PPESSFOR.EMPRESA)
                    AND (VDUPPAG.FORNECEDOR = PPESSFOR.FORNECEDOR)
                    LEFT JOIN PPORTADO 
                    ON (VDUPPAG.EMPRESA = PPORTADO.EMPRESA) 
                    AND (VDUPPAG.PORTADOR = PPORTADO.PORTADOR) 
                    LEFT JOIN PSITUACA 
                    ON (VDUPPAG.SITUACAO = PSITUACA.SITUACAO) 
                    WHERE (VDUPPAG.EMPRESA = 1003)
                    AND ( (VDUPPAG.QUITADA <> 'S') OR
                    (VDUPPAG.QUITADA IS NULL) )
                    AND (VDUPPAG.AUTORIZADA = 'S') 
                    AND ( (PSITUACA.LISTBAIXA IS NULL) OR 
                    (PSITUACA.LISTBAIXA = 'S') )
                    AND (VDUPPAG.ESTABFORNECEDOR = 1003)
                    AND VDUPPAG.DTVENCTO BETWEEN '{dataini}' AND '{datafim}'
                    ORDER BY VDUPPAG.DTVENCTO""")

        # Obtendo os nomes das colunas
        colunas = [desc[0] for desc in cur.description]

        # Obtendo os valores
        valores = cur.fetchall()

        # Fecha o cursor
        cur.close()

        return colunas, valores

    def retorna_dados_contas_a_receber(dataini, datafim):
        cur = con.cursor()
        cur.execute(f"""SELECT VDUPREC.DUPREC,      VDUPREC.CLIENTE,      VDUPREC.DTEMISSAO, 
                    VDUPREC.DTVENCTO,    VDUPREC.JUROS,        VDUPREC.DESCONTO, 
                    VDUPREC.VALOR,       VDUPREC.FATURA,
                    VDUPREC.HISTORICO,   VDUPREC.SITUACAO,     VDUPREC.PORTADOR AS PORTADOR, 
                    VDUPREC.VENCTOORIG,  VDUPREC.NOSSONUMERO,  VDUPREC.MESCOMPET, 
                    VDUPREC.ANOCOMPET,   VDUPREC.VALDUP,       VDUPREC.SALDO, 
                    PPESCLI.CLIENTE || ' - ' || PPESCLI.NOME AS NOME,  PPESCLI.TELEFONE, 
                    VDUPREC.RECEBIDO AS TOTREC, VDUPREC.MOEDA, PPORTADO.DESCRICAO AS NOMEPORT, 
                    VDUPREC.ANADESC,     VDUPREC.ESTABCLIENTE, VDUPREC.JUROSPEND, 
                    VDUPREC.DESCPEND,    VDUPREC.DTBASEJUROS,  VDUPREC.MULTA, 
                    VDUPREC.CENCUSCOD,   VDUPREC.CENTROCUS,    PSITUACA. DESCRICAO AS DESCSITUAC, 
                    PREPRESE.REPRESENT,  PREPRESE.DESCRICAO AS NOMEREPRE, VDUPREC.EMPRESA 
                    FROM VDUPREC
                    LEFT JOIN PPESCLI 
                    ON (VDUPREC.ESTABCLIENTE = PPESCLI.EMPRESA) 
                    AND (VDUPREC.CLIENTE      = PPESCLI.CLIENTE) 
                    LEFT JOIN PPORTADO 
                    ON (VDUPREC.EMPRESA  = PPORTADO.EMPRESA) 
                    AND (VDUPREC.PORTADOR = PPORTADO.PORTADOR) 
                    LEFT JOIN PSITUACA 
                    ON (VDUPREC.SITUACAO = PSITUACA.SITUACAO) 
                    LEFT JOIN PREPRESE 
                    ON (VDUPREC.ESTABREPRESENT = PREPRESE.EMPRESA) 
                    AND (VDUPREC.REPRESENT      = PREPRESE.REPRESENT) 
                    LEFT JOIN FILIAL 
                    ON (VDUPREC.EMPRESA = FILIAL.ESTAB) 
                    WHERE (VDUPREC.EMPRESA  = 1003 )
                    AND ( (VDUPREC.QUITADA <> 'S') OR
                    (VDUPREC.QUITADA IS NULL) )
                    AND ( (PSITUACA.LISTBAIXA IS NULL) OR 
                    (PSITUACA.LISTBAIXA = 'S') )
                    AND VDUPREC.DTVENCTO BETWEEN '{dataini}' AND '{datafim}'
                    ORDER BY VDUPREC.DTVENCTO""")

        # Obtendo os nomes das colunas
        colunas = [desc[0] for desc in cur.description]

        # Obtendo os valores
        valores = cur.fetchall()

        # Fecha o cursor
        cur.close()

        return colunas, valores
          
except Exception as e:
    print(f"Erro ao executar operações no banco de dados: {e}")
finally:
    # Certifique-se de que a conexão seja fechada
    if con:
        con.close()