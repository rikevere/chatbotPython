from openai import OpenAI
from dotenv import load_dotenv
import os
from time import sleep
from helpers import *
from selecionar_persona import *

load_dotenv()

cliente = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
modelo = "gpt-4"
contexto = carrega("chatbotPython/dados/ecomart.txt")
#1. - Primeiro, criamos um assistente chamado "Atendente EcoMart", que segue um contexto e tem uma persona definida
assistente = cliente.beta.assistants.create(
    name="Atendente EcoMart",
    instructions = f"""
        Você é um chatbot de atendimento a clientes de um e-commerce. 
        Você não deve responder perguntas que não sejam dados do ecommerce informado!
        Além disso, adote a persona abaixo para responder ao cliente.
        
        ## Contexto
        {contexto}
        
        ## Persona
        
        {personas["neutro"]}
    """,
    model = modelo,
)
#2. - Após a criação do assistente, criamos uma thread para a sessão de conversa entre o assistente e um usuário
thread = cliente.beta.threads.create(
    messages=[
        {
            "role": "user",
            "content": "Liste os produtos"
        }
    ]
)
#2.1 - Após a criação da thread, incluímos mais informações de prompt na sessão de conversa entre o assistente e um usuário
cliente.beta.threads.messages.create(
    thread_id=thread.id,
    role = "user",
    content =  " da categoria moda sustentável"
)
#3. Executamos o assistente no thread criado para processar a mensagem do usuário
run = cliente.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistente.id
)
#4. - Incluímos um loop para verificar o status da execução até que seja completada.
while run.status !="completed":
    run = cliente.beta.threads.runs.retrieve(
        thread_id=thread.id,
        run_id=run.id
    )
#5. - Após a execução, recuperamos a resposta do assistente e procedemos com a exclusão do assistente e do thread
historico = cliente.beta.threads.messages.list(thread_id=thread.id).data
resposta = historico[0]
print(print(f"role: {resposta.role}\nConteúdo: {resposta.content[0].text.value}"))

#cliente.beta.assistants.delete(assistant_id=assistente.id)
#cliente.beta.threads.delete(thread_id=thread.id)


#historico = cliente.beta.threads.messages.list(thread_id=thread.id).data

#for mensagem in historico:
#   print(mensagem.content[0].text.value)