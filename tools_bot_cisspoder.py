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
                        "name": "extrai_caracteristicas_produto",
                        "description": "Extrai características de produtos a partir de descrições e imagens fornecidas para busca e registro no banco de dados",
                        "parameters": {
                        "type": "object",
                        "properties": {
                                "marca": {
                                "type": "string",
                                "description": "Marca do produto ou serviço, exemplo: 'Atos Indústria'"
                                },
                                "fabricante": {
                                "type": "string",
                                "description": "Fabricante do produto, exemplo: 'Atos'"
                                },
                                "sessao": {
                                "type": "string",
                                "description": "Sessão ou categoria do produto, exemplo: 'Peças e Acessórios Automotivos'"
                                },
                                "grupo": {
                                "type": "string",
                                "description": "Grupo específico do produto, exemplo: 'Engates para Reboque'"
                                },
                                "subgrupo": {
                                "type": "string",
                                "description": "Subgrupo específico do produto, exemplo: 'Protetores e Engates'"
                                },
                                "faixa_etaria": {
                                "type": "string",
                                "description": "Faixa etária indicada para o produto, caso aplicável, exemplo: 'Não especificado'"
                                },
                                "tipo_servico_destino": {
                                "type": "string",
                                "description": "Tipo de serviço ou uso destinado, exemplo: 'Automóveis'"
                                },
                                "sabor": {
                                "type": "string",
                                "description": "Sabor do produto, caso aplicável, exemplo: 'Não aplicável'"
                                },
                                "classe_produto": {
                                "type": "string",
                                "description": "Classe ou tipo do produto, exemplo: 'Não especificado'"
                                },
                                "volume": {
                                "type": "string",
                                "description": "Dimensões do produto, exemplo: '97 cm x 59 cm x 19 cm'"
                                }
                        },
                        "required": [
                                "marca",
                                "fabricante",
                                "sessao",
                                "grupo",
                                "subgrupo",
                                "faixa_etaria",
                                "tipo_servico_destino",
                                "sabor",
                                "classe_produto",
                                "volume"
                        ]
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


def consultar_produtos(params):
        # Parâmetros recebidos da API
        marca = params.get("marca")
        fabricante = params.get("fabricante")
        sessao = params.get("sessao")
        grupo = params.get("grupo")
        subgrupo = params.get("subgrupo")
        faixa_etaria = params.get("faixa_etaria")
        tipo_servico_destino = params.get("tipo_servico_destino")
        sabor = params.get("sabor")
        classe_produto = params.get("classe_produto")
        volume = params.get("volume")
        pesquisa = f"{marca} {fabricante} {sessao} {grupo} {subgrupo} {faixa_etaria} {tipo_servico_destino} {sabor} {classe_produto} {volume}"
        print(f"Variáveis Consulta: {marca} {fabricante} {sessao} {grupo} {subgrupo} {faixa_etaria} {tipo_servico_destino} {sabor} {classe_produto} {volume}")
        try:
                dados_relatorio = retorna_produtos(pesquisa)
        except Exception as erro:
                "Erro na chamada da função Dados Vendas: %s" % erro
                print('"Erro na chamada da função Dados Vendas:', erro)
                sleep(1)        
        if dados_relatorio:
                return f"""
                        
                        # Formato de Resposta

                        Você é promotor de vendas que recebeu uma imagem de um produto que o cliente comprou. Com base nos produtos similares aos da foto da lista abaixo e nos
                        dados de quantidade disponível e preço, apresente os 5 (se existentes na lista) que mais possuem proximidade com os da foto encaminhada, ofertando-os ao cliente.

                        Estes são os produtos:
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
    "extrai_caracteristicas_produto": consultar_produtos,  # Configuração correta para consulta
}

