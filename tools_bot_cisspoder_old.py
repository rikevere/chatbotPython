#from EventosAgendaGoogle.criar_evento_calendario import criar_evento_chatgpt
from flask import Flask, render_template, request, Response
from openai import OpenAI
from dotenv import load_dotenv
import os
from time import sleep
from helpers import *
#from retorna_previsao_meteoblue import *
#from retorna_periodo import *
from retorna_relatorios import *
import html

load_dotenv()

cliente = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
modelo = "gpt-4-1106-preview"

# Substitua 'SUA_CHAVE_API' pela sua chave API real do Meteoblue
API_KEY = os.getenv("METEOBLUE_API_KEY")
# Valores de latitude e longitude da localização da cidade de Verê
LATITUDE = os.getenv("LATITUDE_VERE")
LONGITUDE = os.getenv("LONGITUDE_VERE")

#varíável global para acessar todas as ferramentas.
minhas_tools = [
    #ferramenta retrieval, responsável por garantir que o assitente possa acessar arquivo ou thread associada e devolver resposta referenciando o arquivo
    #por exemplo, quando em conversas anteriores eu passei um arquivo PDF e em conversas futuras eu quero que a AI tenha condições de acessá-lo novamente.
    #{"type": "retrieval"},
    #Function calling
    #São funções criadas para garantir que quando o usuário questionar a AI sobre determinado assunto, 
    #ele não faça a composição da resposta com base apenas no próprio conhecimento, mas sim, 
    #utilize uma funcionalidade de Python que foge desse processo convencional para poder fazer a composição dessa resposta
        {
            "type": "function",
                        "function": {
                        #Qualquer nome que respeite as características da criação de um método, porque vamos criar um método dentro de Python com o mesmo nome    
                        "name": "validar_notafiscal",
                        #terá como valor o que esperamos que a OpenAI consiga interpretar como uma funcionalidade que foge do padrão
                        #Assim, toda vez que a pessoa usuária trouxer uma informação que pede que ela valide um código promocional ou 
                        #valide algum tipo de cupom, ela tentará não seguir o processo convencional e disparará essa nova funcionalidade que está dentro do Python
                        "description": "Valide o número da nota fiscal de um cliente pela Chave de Acesso",
                        #Inserimos alguns parâmetros que são importantes para que ela identifique que essa Function existe
                        #Os parâmetros envolvem, especificamente, um objeto composto por um conjunto de propriedades que são basicamente dois parâmetros
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
                                #A propriedade chamada de required, definirá quais são os atributos que são 
                                #requisitos para que essa função possa ser disparada. São os dois atributos que acabamos de criar, codigo e validade
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
#Para que ela possa identificar que é um desvio de processo, que é uma ação que não vai depender 
#penas do conhecimento da própria OpenAI, e sim de uma função de Python, ela terá que identificar 
#na mensagem da pessoa usuária um codigo, e eventualmente uma validade. Se a validade não estiver 
#na mensagem, ela tentará buscar nos arquivos, se ela não estiver no arquivo, muito provavelmente não é um cupom válido.


#Utilizando o Playground da OpenAI, ou a API diretamente, basta fornecer a descrição e os parâmetros desejados e obter 
#a estrutura correspondente. Confira o passo a passo:

#1. No "System" do Playground da OpenAI (ou via API) insira:
#Você é um gerador de estrutura de chamada do recurso de function calling para a API do GPT. 
#Você receberá a descrição de uma função e deve escrever o código da estrutura da função seguindo o mesmo padrão do exemplo a seguir.

#adicione o exemplo acima

#2. No "User" insira a descrição desejada, por exemplo:
#Valida um cupom devolvendo true se ainda estiver dentro da validade e for um código válido de cupom, 
#false caso contrário. valida_cupom(codigo: string, validade: string)
#3. A OpenAI gerará a estrutura de função correspondente:

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


#def retornar_previsao_cidadevere(argumentos):
#        previsao = argumentos.get("previsao")
#        cidade = argumentos.get("cidade")
#        print(cidade)
#        if cidade.lower() == 'verê' or cidade.lower() == 'vere':
#                clima = obter_previsao_tempo(API_KEY, LATITUDE, LONGITUDE)
#                return f"""
#                
#                # Formato de Resposta
#
#                Resumo da previsão semanal do tempo para a cidade de {cidade} com base nestes dados: {clima}. 
#                Ainda, descorra sobre as recomendações de roupas fitness e cuidados com a saúde e o corpo com base na previsão do tempo para a semana.
#                Se algum dia da semana tiver probabilidade maior do que 30% de chuva, recomende roupas fitness para este tipo de ambiente, com atenção ao dia em que vai ocorrer.
#                Sugira no mínimo 3  atividades físicas ao ar livre, de acordo com o clima para cada dia da semana.
#                                
#                """        
        

# dicionário global que será responsável por garantir que tenhamos todas as funcionalidades que associamos até esse momento
minhas_funcoes = {
    "validar_notafiscal": validar_notafiscal,
    #"retorna_vendas_clientes_período": retorna_relatorios_periodo,
    #"cria_agendas_google": criar_evento_chatgpt
}
