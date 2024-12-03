from openai import OpenAI
from dotenv import load_dotenv
import os
import json
from helpers import encodar_imagem
from tools_bot_cisspoder import consultar_produtos

load_dotenv()

cliente = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
modelo = "gpt-4o-mini"  # Confirme o modelo correto no portal OpenAI

def analisar_imagem(caminho_imagem):
    """
    Processa uma imagem com o modelo de visão da OpenAI e lida com a análise de defeitos ou consulta de produtos.
    """
    prompt = """
        Você recebeu uma imagem de um produto.
        Analise a imagem enviada e forneça informações detalhadas para realizar uma busca 
        por produtos similares. Inclua: "marca", "fabricante", "sessao", "grupo",
        "subgrupo", "faixa_etaria", "tipo_servico_destino", "sabor", "classe_produto", "volume".
        Se algum dado não for possível de ser retornado, não inclua esta variável no retorno.
    """

    try:
        # Codifica a imagem em Base64
        imagem_base64 = encodar_imagem(caminho_imagem)

        # Envia o prompt e a imagem ao modelo
        resposta = cliente.chat.completions.create(
        model=modelo,
        messages=[
            {
            "role": "user",
            "content": [
                {
                "type": "text",
                "text": prompt,
                },
                {
                "type": "image_url",
                "image_url": {
                    "url":  f"data:image/jpeg;base64,{imagem_base64}"
                },
                },
            ],
            }
        ],
        )
        # Extrai o conteúdo da resposta
        texto_resposta = resposta.choices[0].message.content
        return texto_resposta
      
    except Exception as e:
        return {
            "tipo": "erro",
            "conteudo": f"Erro ao processar a imagem: {e}",
        }


