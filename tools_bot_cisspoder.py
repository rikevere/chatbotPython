from flask import Flask, render_template, request, Response
from openai import OpenAI
from dotenv import load_dotenv
import os
from time import sleep
from helpers import *
from retorna_relatorios import *
import html

load_dotenv()

cliente = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
modelo = "gpt-4o-mini"
#"gpt-4-1106-preview"

# Substitua 'SUA_CHAVE_API' pela sua chave API real do Meteoblue
API_KEY = os.getenv("METEOBLUE_API_KEY")
# Valores de latitude e longitude da localização da cidade de Verê
LATITUDE = os.getenv("LATITUDE_VERE")
LONGITUDE = os.getenv("LONGITUDE_VERE")

#varíável global para acessar todas as ferramentas.
minhas_tools = [
        {
            "type": "function",
                        "function": {    
                        "name": "validar_notafiscal",
                        "description": "Valide o número da nota fiscal de um cliente pela Chave de Acesso",
                        "parameters": {
                                "type": "object",
                                "properties": {
                                        "chave_de_acesso": {
                                                "type": "string",
                                                "description": "A chave de acesso, composta por 44 caracteres numéricos. Por exemplo: 35170705248891000181550010000011831339972127",
                                        },
                                        "CPF_CNPJ": {
                                                "type": "string",
                                                "description": "O CPF ou o CNPJ do cliente da Nota.",
                                        },
                                },
                                "required": ["chave_de_acesso", "CPF_CNPJ"],
                        }
                }
        },
        {
            "type": "function",
                        "function": {
                        "name": "retorna_clientes_sem_recorrencia",
                        "description": "Busca dados dados de vendas do último ano e retorna clientes que não tiveram recorrência em compras na loja em uma quantidade de meses a partir da emissão do relatório, priorizando clientes de maior relevância financeira.",
                        "parameters": {
                                "type": "object",
                                "properties": {
                                        "periodo": {
                                                "type": "string",
                                                "description": "Informa a quantidade de meses com ausência de compra dos clientes",
                                        },
                                },
                                "required": ["periodo"],
                        }
                }
        },   
        {       
            "type": "function",
                        "function": {
                        "name": "clientes_por_produto",
                        "description": "Retorna quais foram os clientes que adquiriram determinado produto",
                        "parameters": {
                                "type": "object",
                                "properties": {
                                        "produto_id": {
                                                "type": "string",
                                                "description": "Especifica o código do produto."
                                        },
                                        "produto_desc": {
                                                "type": "string",
                                                "description": "Retorna a descrição do produto a ser analisado.",
                                        },
                                },
                                "required": ["produto_id", "produto_desc"],
                        }
                }
        }


]

def validar_notafiscal(argumentos):
        chave_nota = argumentos.get("chave_de_acesso")
        cpf_cli = argumentos.get("CPF_CNPJ")
        print(f"Chave de Acesso: {chave_nota}")
        print(f"CPF_CNPJ: {cpf_cli}")
        try:
                dados_relatorio = retorna_nota_cliente(chave_nota, cpf_cli)
        except Exception as erro:
                "Erro na chamada da função Dados Vendas: %s" % erro
                print('"Erro na chamada da função Dados Vendas:', erro)
                sleep(1)        
        if dados_relatorio:
                return f"""
                        
                        # Formato de Resposta

                        Você é o Customer success da empresa e deve ser empatico e criar engajamento com o cliente sobre os dados da nota fiscal retornada. 
                        Baseado nos dados das notas que você possui no relatório a seguir, faça sugestões ao cliente de outros produtos similares que ele pode comprar
                        que possam gerar engajamento de recompra.
                        Apresente outras informações relevantes sobre os dados apresentados para o cliente, detacando informações como o desconto que recebeu, se a nota obteve valor de frete.
                        Valores financeiros sempre devem contemplar o símbolo de Reais (R$). Por exemplo: R$ 1.250,00

                        Estes são dos dados da(s) Nota(s):
                        {dados_relatorio}
                                        
                        """ 
        else:
                print("Não está retornando dados SQL")
                return f"""
                        
                        # Formato de Resposta

                        Nenhum nota foi encontrata para os dados informados."""

# dicionário global que será responsável por garantir que tenhamos todas as funcionalidades que associamos até esse momento
minhas_funcoes = {
    "validar_notafiscal": validar_notafiscal,

}
