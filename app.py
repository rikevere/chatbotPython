from flask import Flask,render_template, request, Response
from openai import OpenAI
from dotenv import load_dotenv
import os
from time import sleep
from helpers import *
from selecionar_persona import *
from assistente_limalimao import *
from vision_limalimao import analisar_imagem
import uuid

load_dotenv()

cliente = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
modelo = "gpt-4-1106-preview"

app = Flask(__name__)
app.secret_key = 'alura'

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
    maximo_tentativas = 1
    repeticao = 0

    while True:
        try:
            personalidade = personas[selecionar_persona(prompt)]

            cliente.beta.threads.messages.create(
                thread_id=thread_id, 
                role = "user",
                content =  f"""
                Assuma, de agora em diante, a personalidade abaixo. 
                Ignore as personalidades anteriores.

                # Persona
                {personalidade}
                """,
                file_ids=file_ids
            )
            print("finalizou o ajuste de personalidade")

            resposta_vision = ""
            if caminho_imagem_enviada != None:
                resposta_vision = analisar_imagem(caminho_imagem_enviada)
                resposta_vision+= ". Na resposta final, apresente detalhes da descrição da imagem."
                os.remove(caminho_imagem_enviada)
                caminho_imagem_enviada = None
            print("Concluiu a analise de imagem")

            cliente.beta.threads.messages.create(
            thread_id=thread_id,
            role = "user",
            content =  resposta_vision+prompt,
            file_ids=file_ids
            )
            print(resposta_vision+prompt)
            run = cliente.beta.threads.runs.create(
                    thread_id=thread_id,
                    assistant_id=assistente_id
                )
            print("entrando no While")
            while run.status !=STATUS_COMPLETED:
                run = cliente.beta.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=run.id
            )
                #Inserimos o log para poder verificar o status de como o assistente está de fato se comportando
                print(f"Status: {run.status}")

                #desvio condicional que verificará se o status da execução em cima da thread que foi criada pelo assistente é um status de ação requerida
                if run.status == STATUS_REQUIRES_ACTION:
                    print("entrou nas funções")
                    #recupera todas as ferramentas que foram ativadas
                    tools_acionadas = run.required_action.submit_tool_outputs.tool_calls
                    #lista de informações que conterão todas as respostas das ferramentas que foram acionadas
                    respostas_tools_acionadas = []     
                    for uma_tool in tools_acionadas:
                        nome_funcao = uma_tool.function.name
                        print(f"Selecionando Função: {nome_funcao}")
                        #baseado no dicionario presente em "tool_limalimao", retorna o nome da função em Python que dever ser utilizada
                        #com base na função que a OpenAI selecionou no mesmo arquivo
                        #a variável "função_escolhida" passa a ser a própria função
                        funcao_escolhida = minhas_funcoes[nome_funcao]
                        argumentos = json.loads(uma_tool.function.arguments)
                        print(f"Selecionando Argumentos: {argumentos}")
                        #neste ponto e para este exemplo, "funcao_escolhida" é igual a "validar_codigo_promocional(), do arquivo tools e receberá os argumentos"
                        #o retono é armazenado em "resposta_funcao"
                        resposta_funcao = funcao_escolhida(argumentos)
                        print(f"Retorno da função: {nome_funcao} para o GPT: {resposta_funcao}")
                        #para tirar aquele status de ação requerida, precisamos entregar essa resposta para a function. Dentro do laço de repetição
                        respostas_tools_acionadas.append({
                                "tool_call_id": uma_tool.id,
                                "output": resposta_funcao
                            })
                    
                    run = cliente.beta.threads.runs.submit_tool_outputs(
                    thread_id = thread_id,
                    run_id = run.id,
                    tool_outputs=respostas_tools_acionadas
                    )
                print("não entrou nas funções")
            historico = list(cliente.beta.threads.messages.list(thread_id=thread_id).data)
            resposta = historico[0]
            return resposta    
            
        except Exception as erro:
                repeticao += 1
                if repeticao >= maximo_tentativas:
                        return "Erro no GPT: %s" % erro
                print('Erro de comunicação com OpenAI:', erro)
                sleep(1)

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
    prompt = request.json["msg"]
    #print(prompt)
    resposta = bot(prompt)
    texto_resposta = resposta.content[0].text.value
    #print(texto_resposta)
    return texto_resposta

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug = True)
