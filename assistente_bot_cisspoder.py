from openai import OpenAI
from dotenv import load_dotenv
import os
from time import sleep
from helpers import *
from selecionar_persona import *
import json
from chatbotPython.tools_bot_cisspoder_old import *

load_dotenv()

cliente = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
modelo = "gpt-4-1106-preview"
contexto = carrega("dados/bot_cisspoder.txt")

def criar_lista_ids():
        lista_ids_arquivos = []

        file_dados = cliente.files.create(
                file=open("dados/dados_bot_cisspoder.txt", "rb"),
                purpose="assistants"
        )
        lista_ids_arquivos.append(file_dados.id)

        file_politicas = cliente.files.create(
                file=open("dados/politicas_bot_cisspoder.txt", "rb"),
                purpose="assistants"
        )
        lista_ids_arquivos.append(file_politicas.id)

        file_recursos = cliente.files.create(
                file=open("dados/recursos_bot_cisspoder.txt","rb"),
                purpose="assistants"
        )

        lista_ids_arquivos.append(file_recursos.id)
        return lista_ids_arquivos

def pegar_json():
        filename = "dados/assistentes.json"

        if not os.path.exists(filename):
                thread_id = criar_thread()
                file_id_list = criar_lista_ids()
                assistant_id = criar_assistente(file_id_list)
                data = {
                        "assistant_id": assistant_id.id,
                        "thread_id": thread_id.id,
                        "file_ids": file_id_list
                }

                with open(filename, "w", encoding="utf-8") as file:
                        json.dump(data, file, ensure_ascii=False, indent=4)
                print("Arquivo 'assistentes.json' criado com sucesso.")

        try:
                with open(filename, "r", encoding="utf-8") as file:
                        data = json.load(file)
                        return data
        except FileNotFoundError:
                print("Arquivo 'assistentes.json' não encontrado.")

    

def criar_thread():
    #Threads não têm limite de tamanho. Você pode adicionar quantas mensagens quiser a um tópico. 
    #O Assistente garantirá que as solicitações ao modelo se ajustem à janela de contexto máxima, 
    #usando técnicas de otimização relevantes, como truncamento, que testamos extensivamente com ChatGPT. 
    #Ao usar a API Assistants, você delega o controle sobre quantos tokens de entrada são passados ​​ao modelo 
    #para qualquer execução, o que significa que você tem menos controle sobre o custo de execução do seu Assistant 
    #em alguns casos, mas não precisa lidar com a complexidade de gerenciar você mesmo a janela de contexto.
    return cliente.beta.threads.create()

def criar_assistente(file_ids=[]):
    assistente = cliente.beta.assistants.create(
        name="BOT CISSPoder",
        description="""
            Você é analista de dados de uma empresa. Especialista em BI, vendas e marketing. 
            Você não deve responder perguntas que não sejam dos dados fornecidos em functions calling
            Além disso, a thread para responder as perguntas.
        """,
        model=modelo,
        tools=minhas_tools,
        tool_resources={
            "code_interpreter": {
                "file_ids": file_ids  # Corrigido: passando a lista diretamente
            }
        }
    )
    return assistente

