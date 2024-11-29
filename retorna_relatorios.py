from dotenv import load_dotenv
#clearmport os
#from retorna_periodo import *
from conecta_db2 import pega_conexao_db2  # Importar a função para obter a conexão

load_dotenv()


def retorna_nota_cliente(chave_de_acesso, cpf):   
    print(cpf)
    print(chave)
    try:
        conn = pega_conexao_db2()
    except Exception as e:
        print(f"Erro ao estabelecer conexão com o banco de dados: {e}")
        exit()

    # Consulta SQL para carregar os dados da nota do cliente por CPF ou Chave de Acesso
    sql = F"""SELECT
        EA.PERDESCONTO,
        E.NOMEFANTASIA AS NOME_DA_LOJA,
        N.NUMNOTA AS NUMERO_DA_NOTA,
        N.SERIENOTA AS SERIE_DA_NOTA,
        V.NOME AS NOME_DO_VENDEDOR,
        CF.FONE1 AS TELEFONE_CLIENTE,
        CF.NOME AS NOME_CLIENTE,
        CF.BAIRRO AS BAIRRO_CLIENTE,
        CF.ENDERECO AS ENDERECO_CLIENTE,
        CF.CNPJCPF AS CPF_CNPJ_CLIENTE,
        CF.UFCLIFOR AS ESTADO_DO_CLIENTE,
        CI.DESCRCIDADE AS CIDADE_CLIENTE,
        NES.DTMOVIMENTO AS DATA_DA_NOTA,
        PV.FABRICANTE AS FABRICANTE_PRODUTO,
        PV.IDSUBPRODUTO AS CODIGO_PRODUTO,
        PV.DESCRCOMPRODUTO || PV.SUBDESCRICAO AS DESCRICAO_PRODUTO,
        PV.EMBALAGEMSAIDA AS EMBALAGEM_VENDA,
        CAST(TRUNC(EA.QTDPRODUTO, 0) AS NUMERIC(10, 0)) AS QUANTIDADE_PRODUTO,
        CAST(ROUND((EA.VALTOTLIQUIDO / EA.QTDPRODUTO), 2) AS NUMERIC(10, 2)) AS VALOR_UNITARIO_LIQUIDO_PRODUTO,
        EA.VALTOTBRUTO AS VALOR_TOTAL_BRUTO,
        EA.VALTOTLIQUIDO AS VALOR_TOTAL_LIQUIDO,
        NES.VALFRETENOTA AS VALOR_DE_FRETE_NOTA,
        NES.OBSFISCAL || NES.OBSNOTA AS OBSERVACOES_DA_NOTA,
        (EA.VALDESCONTOFINANCEIRO + EA.VALDESCONTOPRO) AS DESCONTO_NOTA,
        (EA.VALACRESCIMOFINANCEIRO + EA.VALACRESCIMOPRO) AS ACRESCIMO_NOTA,
        OI.DESCROPERACAO AS TIPO_DE_MOVIMENTO_DA,
        CASE WHEN TRIM(CF.NOMEFANTASIA) = '' THEN 'N O INFORMADO' ELSE CF.NOMEFANTASIA END AS NOME_FANTASIA_CLIENTE
        FROM
        NOTAS N
        JOIN NOTA_FISCAL_ELETRONICA NFE
            ON N.IDEMPRESA = NFE.IDEMPRESA AND N.IDPLANILHA = NFE.IDPLANILHA
        JOIN CLIENTE_FORNECEDOR CF
            ON N.IDCLIFOR = CF.IDCLIFOR
        JOIN CIDADES_IBGE CI
            ON CF.IDCIDADE = CI.IDCIDADE
        JOIN EMPRESA E
            ON N.IDEMPRESA = E.IDEMPRESA
        LEFT JOIN ESTOQUE_ANALITICO EA
            ON N.IDEMPRESA = EA.IDEMPRESA AND N.IDPLANILHA = EA.IDPLANILHA
        LEFT JOIN CLIENTE_FORNECEDOR V
            ON EA.IDVENDEDOR = V.IDCLIFOR
        LEFT JOIN PRODUTOS_VIEW PV
            ON EA.IDPRODUTO = PV.IDPRODUTO AND EA.IDSUBPRODUTO = PV.IDSUBPRODUTO
        JOIN NOTAS_ENTRADA_SAIDA NES
            ON N.IDEMPRESA = NES.IDEMPRESA AND N.IDPLANILHA = NES.IDPLANILHA
        JOIN OPERACAO_INTERNA OI
            ON NES.IDOPERACAO = OI.IDOPERACAO AND EA.IDOPERACAO = OI.IDOPERACAO
        WHERE
        (NFE.CHAVENFE = '{chave_de_acesso}' OR CF.CNPJCPF = '{cpf}');"""

    # AND (CF.CNPJCPF = '{cpf}' OR {cpf} IS NULL)
    # Executar a consulta e carregar os resultados em um DataFrame
    try:
        import ibm_db
        stmt = ibm_db.exec_immediate(conn, sql,)
        rows = []
        while True:
            row = ibm_db.fetch_assoc(stmt)
            if not row:
                break
            rows.append(row)
        
        # Fechar a conexão
        ibm_db.close(conn)  

    except Exception as e:
        print(f"Erro ao executar a consulta SQL: {e}")
        exit()

    return rows

chave = 41210624405054000103550040000005521000121002  
#chave = str(chave)
cpf = 83629440991
#dtfim = '04-19-2023'

#dados = retorna_dados_vendas(dtini, dtfim)
#dados1 = retorna_dados_contas_a_pagar(dtini, dtfim)
#dados2 = retorna_dados_contas_a_receber(dtini, dtfim)

#print(retorna_nota_cliente(chave, cpf))
#print(dados1)
#print(dados2)