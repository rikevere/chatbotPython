from flask import Flask,render_template, request, Response
from openai import OpenAI
from dotenv import load_dotenv
import os
from time import sleep
from helpers import *
from selecionar_persona import *
from assistente_bot_cisspoder import *
#from vision_limalimao import analisar_imagem
import uuid
from datetime import datetime
from conecta_db2 import pega_conexao_db2  # Importar a função para obter a conexão

load_dotenv()

cliente = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
modelo = "gpt-3.5-turbo-0125"
#modelo = "gpt-4-1106-preview"

app = Flask(__name__)
app.secret_key = 'ciss_poder'

assistente = pegar_json()
thread_id = assistente["thread_id"]
assistente_id = assistente["assistant_id"]
file_ids = assistente["file_ids"]

STATUS_COMPLETED = "completed"
STATUS_REQUIRES_ACTION = "requires_action"

caminho_imagem_enviada = None
UPLOAD_FOLDER = 'dados'

def bot(prompt):
    global caminho_imagem_enviada
    try:
        # Finalizar run ativo, se necessário
        run_id = finalizar_run_ativo(thread_id)
        if run_id:
            print(f"Run ativo finalizado ou em progresso: {run_id}")

        # Selecionar personalidade
        personalidade_key = selecionar_persona(prompt)
        personalidade = personas.get(personalidade_key, personas["neutro"])
        print(f"Personalidade escolhida: {personalidade_key}")

        # Enviar mensagem para ajustar personalidade
        cliente.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=f"Assuma a seguinte personalidade:\n{personalidade}"
        )

        # Enviar mensagem com o prompt do usuário
        cliente.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=prompt
        )

        # Executar o assistente
        run = cliente.beta.threads.runs.create(thread_id=thread_id, assistant_id=assistente_id)

        # Processar a execução
        while run.status != STATUS_COMPLETED:
            run = cliente.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
            print(f"Status do run: {run.status}")

            # Lidar com o status `requires_action`
            if run.status == STATUS_REQUIRES_ACTION:
                tools_acionadas = run.required_action.submit_tool_outputs.tool_calls
                respostas_tools_acionadas = []

                for uma_tool in tools_acionadas:
                    nome_funcao = uma_tool.function.name
                    print(f"Função acionada: {nome_funcao}")

                    # Obter a função correspondente
                    funcao_escolhida = minhas_funcoes.get(nome_funcao)
                    if funcao_escolhida:
                        # Obter os argumentos da função
                        argumentos = json.loads(uma_tool.function.arguments)
                        print(f"Argumentos recebidos: {argumentos}")

                        # Executar a função e capturar a saída
                        resposta_funcao = funcao_escolhida(argumentos)
                        print(f"Resultado da função {nome_funcao}: {resposta_funcao}")

                        # Adicionar a saída para enviar ao assistente
                        respostas_tools_acionadas.append({
                            "tool_call_id": uma_tool.id,
                            "output": resposta_funcao
                        })
                    else:
                        print(f"Função {nome_funcao} não encontrada em `minhas_funcoes`.")

                # Submeter as saídas das ferramentas ao assistente
                run = cliente.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread_id,
                    run_id=run.id,
                    tool_outputs=respostas_tools_acionadas
                )
            
            sleep(1)

        # Obter histórico
        historico = list(cliente.beta.threads.messages.list(thread_id=thread_id).data)
        print("Histórico completo:", historico)

        # Processar o histórico e extrair a resposta
        if historico:
            primeira_mensagem = historico[0]  # A primeira mensagem relevante
            print("Primeira mensagem no histórico:", primeira_mensagem)

            # Verificar se há conteúdo na mensagem
            if hasattr(primeira_mensagem, "content") and primeira_mensagem.content:
                # Extrair e concatenar texto dos blocos de conteúdo
                texto_resposta = " ".join(
                    bloco.text.value for bloco in primeira_mensagem.content if hasattr(bloco, "text")
                )
                print("Texto extraído:", texto_resposta)
                return {"content": texto_resposta}

        print("Formato inesperado de mensagem:", primeira_mensagem)
        return {"content": "Erro ao processar a resposta do assistente."}


    except Exception as erro:
        print(f"Erro no bot: {erro}")
        return {"content": f"Erro: {erro}"}

    
    
def finalizar_run_ativo(thread_id):
    try:
        # Obter o run ativo na thread
        run = cliente.beta.threads.runs.retrieve(thread_id=thread_id)
        print(f"Run ativo encontrado: {run.id} com status {run.status}")

        # Verificar se o status é requires_action
        if run.status == STATUS_REQUIRES_ACTION:
            print("Finalizando run com ações pendentes...")
            cliente.beta.threads.runs.submit_tool_outputs(
                thread_id=thread_id,
                run_id=run.id,
                tool_outputs=[]  # Envia uma saída vazia se não houver tool_outputs processados
            )
        elif run.status != STATUS_COMPLETED:
            print("Run ativo ainda em progresso. Aguardando finalização...")

        return run.id
    except Exception as e:
        print(f"Erro ao finalizar run ativo: {e}")
        return None


#View que vai disparar essa rota /upload_imagem do javaScript
@app.route('/upload_imagem', methods=['POST'])
def upload_imagem():
    global caminho_imagem_enviada
    if 'imagem' in request.files:
        imagem_enviada = request.files['imagem']
        
        nome_arquivo = str(uuid.uuid4()) + os.path.splitext(imagem_enviada.filename)[1]
        caminho_arquivo = os.path.join(UPLOAD_FOLDER, nome_arquivo)
        imagem_enviada.save(caminho_arquivo)
        caminho_imagem_enviada = caminho_arquivo

        return 'Imagem recebida com sucesso!', 200
    return 'Nenhum arquivo foi enviado', 400

@app.route("/chat", methods=["POST"])
def chat():
    prompt = request.json.get("msg", "")
    resposta = bot(prompt)

    # Valide o retorno de `bot()`
    print("Resposta do bot:", resposta)

    if isinstance(resposta, dict) and "content" in resposta:
        texto_resposta = resposta["content"]
    else:
        texto_resposta = "Erro: resposta inesperada do assistente."

    return texto_resposta



@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug = True)
