from dotenv import load_dotenv
#clearmport os
#from retorna_periodo import *
from conecta_db2 import pega_conexao_db2  # Importar a função para obter a conexão
import Levenshtein

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


def retorna_produtos(descricao_base, limite=5):
    """
    Busca produtos no banco de dados com descrições mais próximas da string fornecida.
    """

    try:
        conn = pega_conexao_db2()
    except Exception as e:
        print(f"Erro ao estabelecer conexão com o banco de dados: {e}")
        exit()

    sql = """SELECT PG.IDSUBPRODUTO, PG.DESCRRESPRODUTO, ESA.QTDATUALESTOQUE, POLITICA_PRECO_PRODUTO.VALPRECOVAREJO
            FROM DBA.PRODUTO_GRADE PG
            JOIN ESTOQUE_SALDO_ATUAL ESA
                ON ESA.IDSUBPRODUTO = PG.IDSUBPRODUTO
                AND ESA.IDEMPRESA = 201
                AND ESA.IDLOCALESTOQUE = 1
            JOIN POLITICA_PRECO_PRODUTO 
                ON POLITICA_PRECO_PRODUTO.IDSUBPRODUTO = PG.IDSUBPRODUTO
                AND POLITICA_PRECO_PRODUTO.IDEMPRESA = 201
            WHERE ESA.QTDATUALESTOQUE > 0 AND PG.FLAGBLOQUEIAVENDA = 'F';"""
    
    try:
        import ibm_db
        stmt = ibm_db.exec_immediate(conn, sql,)
        produtos = []
        while True:
            row = ibm_db.fetch_assoc(stmt)
            if not row:
                break
            descricao_produto = row["DESCRRESPRODUTO"]
            id_produto = row["IDSUBPRODUTO"]
            saldo_produto = row["QTDATUALESTOQUE"]
            valor_produto = row["VALPRECOVAREJO"]
            distancia_hamming = Levenshtein.hamming(descricao_base, descricao_produto)
            produtos.append((id_produto, descricao_produto, saldo_produto, valor_produto, distancia_hamming))


        # Ordenar pelo menor valor de distância
        produtos_ordenados = sorted(produtos, key=lambda x: x[4])


        # Retornar os `limite` primeiros produtos
        produtos_similares = produtos_ordenados[:limite]
        
        lista_produtos_similares = ""
        for produto in produtos_similares:
            lista_produtos_similares = lista_produtos_similares + (f"ID: {produto[0]}, Descrição: {produto[1]}, Saldo: {produto[2]}, Valor: {produto[3]}\n")

        # Retornar os `limite` primeiros produtos
        #return produtos_ordenados[:limite], teste2
        return lista_produtos_similares
    
    except Exception as e:
        print(f"Erro ao buscar produtos similares: {e}")
        return []



chave = 41210624405054000103550040000005521000121002  
#chave = str(chave)
cpf = 83629440991
#dtfim = '04-19-2023'


descricao_pesquisa = "Nestlé Nestlé Doces e chocolates Chocolates Chocolate ao leite Todas as idades Lanches e sobremesas Chocolate Confeitaria Não especificado"

lista = retorna_produtos(descricao_pesquisa)

print(lista)
