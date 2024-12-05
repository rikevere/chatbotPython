from flask import Flask, render_template, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv
import os
from time import sleep
from vision_bot_cisspoder import analisar_imagem
from helpers import *
from selecionar_persona import *
from assistente_bot_cisspoder import *
from selecionar_documentos import selecionar_contexto
from conecta_db2 import pega_conexao_db2
import uuid
import json

load_dotenv()

# Configurações do OpenAI
cliente = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
modelo = "gpt-4o-mini"
#"gpt-4-0613"

# Configurações do Flask
app = Flask(__name__)
app.secret_key = "ciss_poder"

# Configurações do Assistente
assistente = pegar_json()
thread_id = assistente["thread_id"]
assistente_id = assistente["assistant_id"]
file_ids = assistente["file_ids"]

# Constantes
STATUS_COMPLETED = "completed"
STATUS_REQUIRES_ACTION = "requires_action"
UPLOAD_FOLDER = "dados"
caminho_imagem_enviada = None


def finalizar_run_ativo(thread_id):
    """
    Finaliza qualquer run ativo na thread especificada.
    """
    try:
        runs = cliente.beta.threads.runs.list(thread_id=thread_id).data
        for run in runs:
            if run.status in ["in_progress", "requires_action"]:
                print(f"Encerrando run ativo: {run.id} com status {run.status}")
                if run.status == STATUS_REQUIRES_ACTION:
                    cliente.beta.threads.runs.submit_tool_outputs(
                        thread_id=thread_id,
                        run_id=run.id,
                        tool_outputs=[]  # Submeter vazio caso não haja saídas processadas
                    )
        return True
    except Exception as e:
        print(f"Erro ao finalizar run ativo: {e}")
        return False

def formatar_resposta_em_html(resposta):
    """
    Transforma o texto da resposta em um HTML mais organizado e legível.
    """
    resposta = resposta.replace("\n", "<br>")  # Substitui quebras de linha por tags <br>
    
    # Substitui marcadores Markdown por tags HTML
    resposta = resposta.replace("### ", "<h3>").replace("**", "<b>")
    resposta = resposta.replace("- ", "<li>").replace("</li>", "</li></ul>")  # Fecha listas
    resposta = resposta.replace("1.", "<ol><li>").replace("2.", "<li>").replace("3.", "<li>")  # Numerar listas
    resposta = resposta.replace("</li>", "</li></ol>")  # Fecha listas ordenadas

    # Adiciona div para visualização estilizada
    resposta_html = f"<div style='font-family: Arial, sans-serif; line-height: 1.5; margin: 1rem; color: #333;'>{resposta}</div>"
    return resposta_html


def filtrar_historico(historico, limite_tokens=3000):
    """
    Filtra o histórico para manter apenas mensagens relevantes dentro do limite de tokens.
    """
    mensagens_filtradas = []
    tokens_total = 0

    for mensagem in reversed(historico):  # Processa do final para o início
        tamanho_mensagem = len(mensagem.content[0].text.value.split()) if mensagem.content else 0
        if tokens_total + tamanho_mensagem > limite_tokens:
            break
        mensagens_filtradas.append(mensagem)
        tokens_total += tamanho_mensagem

    return list(reversed(mensagens_filtradas))


def bot(prompt):
    """
    Processa o prompt do usuário e retorna a resposta do bot.
    """
    global caminho_imagem_enviada

    try:
        # Finalizar runs ativos
        if not finalizar_run_ativo(thread_id):
            return {"content": "Erro ao finalizar run ativo."}

        # Definir personalidade com base no sentimento do prompt
        personalidade_key = selecionar_persona(prompt)
        personalidade = personas.get(personalidade_key, personas["neutro"])
        print(f"Personalidade escolhida: {personalidade_key}")

        # Selecionar contexto
        contexto = selecionar_contexto(prompt)

        # Enviar personalidade como mensagem inicial
        cliente.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=f"Assuma a seguinte personalidade:\n{personalidade}"
        )

        resposta_vision = ""
        if caminho_imagem_enviada != None:
            resposta_vision = analisar_imagem(caminho_imagem_enviada)
            resposta_vision+= ". Repasse as variáveis anteriores de características de produto para a função extrai_caracteristicas_produto"
            os.remove(caminho_imagem_enviada)
            caminho_imagem_enviada = None
            print("Concluiu a analise de imagem")

        

        # Enviar mensagem com o contexto do documento
        #cliente.beta.threads.messages.create(
        #    thread_id=thread_id,
        #    role="user",
        #    content=f"Contexto relevante:\n{contexto}\nPergunta: {prompt}"
        #)

        # Enviar prompt do usuário
        cliente.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            #content=prompt
            content =  resposta_vision+prompt
        )

        print(resposta_vision+prompt)

        # Executar o assistente
        run = cliente.beta.threads.runs.create(thread_id=thread_id, assistant_id=assistente_id)

        # Aguardar conclusão do run
        while run.status != STATUS_COMPLETED:
            run = cliente.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
            print(f"Status do run: {run.status}")

            if run.status == "failed":
                print(f"Erro no processamento do run: {run}")
                return {"content": "Ocorreu um erro ao processar sua solicitação. Por favor, tente novamente mais tarde."}

            if run.status == STATUS_REQUIRES_ACTION:
                # Processar ferramentas acionadas
                tools_acionadas = run.required_action.submit_tool_outputs.tool_calls
                respostas_tools_acionadas = []

                for tool_call in tools_acionadas:
                    nome_funcao = tool_call.function.name
                    print(f"Função acionada: {nome_funcao}")

                    # Encontrar função correspondente
                    funcao = minhas_funcoes.get(nome_funcao)
                    if funcao:
                        argumentos = json.loads(tool_call.function.arguments)
                        try:
                            resposta = funcao(argumentos)
                            respostas_tools_acionadas.append({
                                "tool_call_id": tool_call.id,
                                "output": resposta
                            })
                        except Exception as e:
                            print(f"Erro ao executar a função {nome_funcao}: {e}")
                            respostas_tools_acionadas.append({
                                "tool_call_id": tool_call.id,
                                "output": f"Erro ao processar função: {e}"
                            })
                    else:
                        print(f"Função {nome_funcao} não encontrada.")

                # Submeter as saídas processadas
                run = cliente.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread_id,
                    run_id=run.id,
                    tool_outputs=respostas_tools_acionadas
                )

            sleep(1)

        # Obter histórico de mensagens
        historico = list(cliente.beta.threads.messages.list(thread_id=thread_id).data)
        print("Histórico completo:", historico)

        # Processar o histórico e retornar a primeira mensagem relevante
        if historico:
            mensagem = historico[0]  # Pega a mensagem mais recente
            if hasattr(mensagem, "content") and mensagem.content:
                texto_resposta = " ".join(
                    bloco.text.value for bloco in mensagem.content if hasattr(bloco, "text")
                )
                return {"content": texto_resposta}

        return {"content": "Erro ao processar a resposta do assistente."}

    except Exception as e:
        print(f"Erro no bot: {e}")
        return {"content": f"Erro: {e}"}


@app.route('/upload_imagem', methods=['POST'])
def upload_imagem():
    global caminho_imagem_enviada
    if 'imagem' in request.files:
        imagem_enviada = request.files['imagem']
        
        # Salvar a imagem no servidor
        nome_arquivo = str(uuid.uuid4()) + os.path.splitext(imagem_enviada.filename)[1]
        caminho_arquivo = os.path.join(UPLOAD_FOLDER, nome_arquivo)
        imagem_enviada.save(caminho_arquivo)

        # Analisar a imagem
        #resposta_analise = analisar_imagem(caminho_arquivo) 
        # Removido para que seja executado dentro do BOT, complementando o contexto da resposta
        caminho_imagem_enviada = caminho_arquivo


        # Validar o retorno do bot
        #return resposta_analise
        return 'Imagem recebida com sucesso!', 200

        # Retornar a análise ao usuário
        #return {"content": resposta_analise}, 200

    #return {"content": "Nenhum arquivo foi enviado."}, 400
    return "Nenhum arquivo foi enviado.", 400

@app.route("/chat", methods=["POST"])
def chat():
    """
    Endpoint para interação com o bot.
    """
    prompt = request.json.get("msg", "")
    resposta = bot(prompt)

    # Validar o retorno do bot
    if isinstance(resposta, dict) and "content" in resposta:
        texto_resposta = resposta["content"]

        # Formata a resposta em HTML
        texto_resposta_formatado = formatar_resposta_em_html(texto_resposta)
    else:
        texto_resposta_formatado = "Erro: resposta inesperada do assistente."

    return texto_resposta_formatado


@app.route("/")
def home():
    """
    Endpoint da página inicial.
    """
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
