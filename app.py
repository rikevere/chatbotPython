from flask import Flask, render_template, request
from openai import OpenAI
from dotenv import load_dotenv
import os
from time import sleep
from helpers import *
from selecionar_persona import *
from assistente_bot_cisspoder import *
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
    try:
        # Finalizar runs ativos
        if not finalizar_run_ativo(thread_id):
            return {"content": "Erro ao finalizar run ativo."}

        # Definir personalidade com base no sentimento do prompt
        personalidade_key = selecionar_persona(prompt)
        personalidade = personas.get(personalidade_key, personas["neutro"])
        print(f"Personalidade escolhida: {personalidade_key}")

        # Enviar personalidade como mensagem inicial
        cliente.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=f"Assuma a seguinte personalidade:\n{personalidade}"
        )

        # Enviar prompt do usuário
        cliente.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=prompt
        )

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


@app.route("/upload_imagem", methods=["POST"])
def upload_imagem():
    """
    Endpoint para upload de imagem.
    """
    global caminho_imagem_enviada
    if "imagem" in request.files:
        imagem = request.files["imagem"]
        nome_arquivo = f"{uuid.uuid4()}{os.path.splitext(imagem.filename)[1]}"
        caminho_arquivo = os.path.join(UPLOAD_FOLDER, nome_arquivo)
        imagem.save(caminho_arquivo)
        caminho_imagem_enviada = caminho_arquivo
        return "Imagem recebida com sucesso!", 200

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
        return resposta["content"]
    return "Erro: resposta inesperada do assistente."


@app.route("/")
def home():
    """
    Endpoint da página inicial.
    """
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
