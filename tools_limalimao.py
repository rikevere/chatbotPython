from flask import Flask,render_template, request, Response
from openai import OpenAI
from dotenv import load_dotenv
import os
from time import sleep
from helpers import *
from retorna_previsao_meteoblue import *
from retorna_periodo import *
from retorna_relatorios import *

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
    {"type": "retrieval"},
    #Function calling
    #São funções criadas para garantir que quando o usuário questionar a AI sobre determinado assunto, 
    #ele não faça a composição da resposta com base apenas no próprio conhecimento, mas sim, 
    #utilize uma funcionalidade de Python que foge desse processo convencional para poder fazer a composição dessa resposta
        {
            "type": "function",
                        "function": {
                        #Qualquer nome que respeite as características da criação de um método, porque vamos criar um método dentro de Python com o mesmo nome    
                        "name": "validar_codigo_promocional",
                        #terá como valor o que esperamos que a OpenAI consiga interpretar como uma funcionalidade que foge do padrão
                        #Assim, toda vez que a pessoa usuária trouxer uma informação que pede que ela valide um código promocional ou 
                        #valide algum tipo de cupom, ela tentará não seguir o processo convencional e disparará essa nova funcionalidade que está dentro do Python
                        "description": "Valide um código promocional com base nas diretrizes de Descontos e Promoções da empresa",
                        #Inserimos alguns parâmetros que são importantes para que ela identifique que essa Function existe
                        #Os parâmetros envolvem, especificamente, um objeto composto por um conjunto de propriedades que são basicamente dois parâmetros
                        "parameters": {
                                "type": "object",
                                "properties": {
                                        "codigo": {
                                                "type": "string",
                                                "description": "O código promocional, no formato, CUPOM_XX. Por exemplo: CUPOM_ECO",
                                        },
                                        "validade": {
                                                "type": "string",
                                                "description": f"A validade do cupom, caso seja válido e esteja associado as políticas. No formato DD/MM/YYYY.",
                                        },
                                },
                                #A propriedade chamada de required, definirá quais são os atributos que são 
                                #requisitos para que essa função possa ser disparada. São os dois atributos que acabamos de criar, codigo e validade
                                "required": ["codigo", "validade"],
                        }
                }
        },
        {
            "type": "function",
                        "function": {
                        "name": "retornar_previsao_cidadevere",
                        "description": "Busque a previsão do tempo para a cidade de informada",
                        "parameters": {
                                "type": "object",
                                "properties": {
                                        "previsao": {
                                                "type": "string",
                                                "description": "Solicitação de previsão do tempo"
                                        },
                                        "cidade": {
                                                "type": "string",
                                                "description": "Cidade para onde deseja-se obter a previsão",
                                        },
                                },
                                "required": ["previsao", "cidade"],
                        }
                }
        },
        {
            "type": "function",
                        "function": {
                        "name": "retorna_vendas_clientes_período",
                        "description": "Busca dados de relatórios sobre o negócio, como saldos de estoque, contas a receber, a pagar e vendas no período",
                        "parameters": {
                                "type": "object",
                                "properties": {
                                        "periodo": {
                                                "type": "string",
                                                "description": "Determina o período para o qual deseja solicitar os dados. Pode ser Hoje, Semana, Mês ou Ano"
                                        },
                                        "relatorio": {
                                                "type": "string",
                                                "description": "Informa o tipo de relatório solicitado",
                                        },
                                },
                                "required": ["período", "relatório"],
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

def validar_codigo_promocional(argumentos):
    codigo = argumentos.get("codigo")
    validade = argumentos.get("validade")

    return f"""
        
        # Formato de Resposta
        
        {codigo} com validade: {validade}. 
        Ainda, diga se é válido ou não para o usuário.

        """

def retornar_previsao_cidadevere(argumentos):
        previsao = argumentos.get("previsao")
        cidade = argumentos.get("cidade")
        print(cidade)
        if cidade=='Verê':
                clima = obter_previsao_tempo(API_KEY, LATITUDE, LONGITUDE)
                return f"""
                
                # Formato de Resposta

                Resumo da previsão semanal do tempo para a cidade de {cidade} com base nestes dados: {clima}. 
                Ainda, descorra sobre as recomendações de roupas fitness e cuidados com a saúde e o corpo com base na previsão do tempo para a semana.
                Se algum dia da semana tiver probabilidade maior do que 30% de chuva, recomende roupas fitness para este tipo de ambiente, com atenção ao dia em que vai ocorrer.
                Sugira no mínimo 3  atividades físicas ao ar livre, de acordo com o clima para cada dia da semana.
                                
                """        
        
def retorna_vendas_clientes_periodo(argumentos):
        periodo = argumentos.get("periodo")
        relatorio = argumentos.get("relatorio")
        print(f"Perído com origem no Chat: {periodo}")
        print(f"Análise escolhida: {relatorio}")
        data_referencia = "12/04/2023"  # Data de referência para os cálculos
        
        print(f"Dados do Relatório: {dados_relatorio}")
        if relatorio.lower() == 'vendas':
                dtini, dtfim = obter_intervalo_data(periodo, data_referencia)
                dados_relatorio = retorna_dados_vendas(dtini, dtfim)
                return f"""
                        
                        # Formato de Resposta

                        Você é um especialista em BI e ciência de dados que atua na controladoria da empresa. 
                        Baseado nos dados de vendas a seguir, emita um parecer apresentando insigts ao CEO da empresa relativo aos dados apresentados
                        Ainda, apresente o período com maior faturamento e uma lista com os 5 clientes com maior volume de compra
                        Apresente outras informações relevantes sobre os dados apresentados.

                        Estes são dos dados das vendas:
                        {dados_relatorio}
                                        
                        """ 
        elif relatorio.lower() == 'contas a pagar':
              return f"""
                        
                        # Formato de Resposta

                        Você é um especialista em BI e ciência de dados que atua na controladoria da empresa. 
                        Baseado nos dados de vendas a seguir, emita um parecer apresentando insigts ao CEO da empresa relativo aos dados apresentados
                        Ainda, apresente o período com maior faturamento e uma lista com os 5 clientes com maior volume de compra
                        Apresente outras informações relevantes sobre os dados apresentados.

                        Estes são dos dados das vendas:
                        {dados_relatorio}
                                        
                        """  
        elif relatorio.lower() == 'contas a receber':
               return f"""
                        
                        # Formato de Resposta

                        Você é um especialista em BI e ciência de dados que atua na controladoria da empresa. 
                        Baseado nos dados de vendas a seguir, emita um parecer apresentando insigts ao CEO da empresa relativo aos dados apresentados
                        Ainda, apresente o período com maior faturamento e uma lista com os 5 clientes com maior volume de compra
                        Apresente outras informações relevantes sobre os dados apresentados.

                        Estes são dos dados das vendas:
                        {dados_relatorio}
                                        
                        """ 


# dicionário global que será responsável por garantir que tenhamos todas as funcionalidades que associamos até esse momento
minhas_funcoes = {
    "validar_codigo_promocional": validar_codigo_promocional,
    "retornar_previsao_cidadevere": retornar_previsao_cidadevere,
    "retorna_vendas_clientes_período": retorna_vendas_clientes_periodo
}
