let chat = document.querySelector('#chat');
let input = document.querySelector('#input');
let botaoEnviar = document.querySelector('#botao-enviar');

// verificamos se a mensagem enviada é vazia:
async function enviarMensagem() {
    if(input.value == "" || input.value == null) return;
    let mensagem = input.value;
    input.value = "";

   // Exibição da mensagem que foi digitada na conversa
    let novaBolha = criaBolhaUsuario();
    novaBolha.innerHTML = mensagem;
    chat.appendChild(novaBolha);

   // Exibição da mensagem de resposta que vem da API
    let novaBolhaBot = criaBolhaBot();
    chat.appendChild(novaBolhaBot);
    vaiParaFinalDoChat();
    novaBolhaBot.innerHTML = "Analisando ..."
    
    // Envia requisição com a mensagem para a API do ChatBot
    //  fazendo a requisição para o endpoint /chat do nosso back-end em Flask
    const resposta = await fetch("http://127.0.0.1:5000/chat", {
        method: "POST",
        // indicamos no cabeçalho que o tipo de dado que estamos enviando é um JSON
        headers: {
        "Content-Type": "application/json",
        },
        // descrevemos o corpo da requisição (body) e montamos um JSON com um único campo msg, cujo conteúdo é a variável mensagem que capturamos do usuário logo no início da função
        body: JSON.stringify({'msg':mensagem}),
    });
    const textoDaResposta = await resposta.text();
    console.log(textoDaResposta);
    novaBolhaBot.innerHTML = textoDaResposta.replace(/\n/g, '<br>');
    vaiParaFinalDoChat();
}

function criaBolhaUsuario() {
    let bolha = document.createElement('p');
    bolha.classList = 'chat__bolha chat__bolha--usuario';
    return bolha;
}

function criaBolhaBot() {
    let bolha = document.createElement('p');
    bolha.classList = 'chat__bolha chat__bolha--bot';
    return bolha;
}

// responsável por fazer a rolagem da tela para que a mensagem do chatbot fique visível na tela
function vaiParaFinalDoChat() {
    chat.scrollTop = chat.scrollHeight;
}

botaoEnviar.addEventListener('click', enviarMensagem);
input.addEventListener("keyup", function(event) {
    event.preventDefault();
    if (event.keyCode === 13) {
        botaoEnviar.click();
    }
});