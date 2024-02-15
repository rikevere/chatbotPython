from openai import OpenAI
from dotenv import load_dotenv
import os
from time import sleep
from helpers import *

load_dotenv()

cliente = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
modelo = "gpt-4-1106-preview"

politicas_limalimao = carrega('chatbotPython/dados/politicas_limalimao.txt')
dados_limalimao = carrega('chatbotPython/dados/dados_limalimao.txt')
produtos_limalimao = carrega('chatbotPython/dados/produtos_limalimao.txt')

def selecionar_documento(resposta_openai):
    if "políticas" in resposta_openai:
        return dados_limalimao + "\n" + politicas_limalimao
    elif "produtos" in resposta_openai:
        return dados_limalimao + "\n" + produtos_limalimao
    else:
        return dados_limalimao 

def selecionar_contexto(mensagem_usuario):
    prompt_sistema = f"""
    A empresa lima limão possui três documentos principais que detalham diferentes aspectos do negócio:

    #Documento 1 "\n {dados_limalimao} "\n"
    #Documento 2 "\n" {politicas_limalimao} "\n"
    #Documento 3 "\n" {produtos_limalimao} "\n"

    Avalie o prompt do usuário e retorne o documento mais indicado para ser usado no contexto da resposta. Retorne dados se for o Documento 1, políticas se for o Documento 2 e produtos se for o Documento 3. 

    """
    resposta = cliente.chat.completions.create(
            model=modelo,
            messages=[
                {
                    "role": "system",
                    "content": prompt_sistema
                },
                {
                    "role": "user",
                    "content" : mensagem_usuario
                }
            ],
            temperature=1,
        )

    contexto = resposta.choices[0].message.content.lower()
    return contexto
