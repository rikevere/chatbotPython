let chat = document.querySelector('#chat');
let input = document.querySelector('#input');
let botaoEnviar = document.querySelector('#botao-enviar');
// Variável serve para podermos garantir que o caminho que temos dentro dessa escolha que acontecerá no JavaScript, 
// vai passar para o Flask (python) e voltar para cá para poder ser interpretado, ficando armazenado em uma variável.
let imagemSelecionada;
// acessa o nosso documento e faz uma query selector para acessar, no HTML, o objeto ou o elemento que tem o ID #mais_arquivo. 
// Assim, conseguimos capturar aquele elemento para poder adicionar um evento adequado para ele.
let botaoAnexo = document.querySelector('#mais_arquivo');
// recurso que vamos poder utilizar para garantir que a imagem selecionada pela pessoa usuária com o campo de input, 
//apareça pelo menos uma vez antes da execução para ter uma dupla etapa de confirmação para quem está utilizando o nosso chatbot.
let miniaturaImagem;

// Essa função terá a responsabilidade de buscar a imagem da nossa aplicação em Python, pelo Flask, e transferi-la para o JavaScript, 
// permitindo que possamos renderizá-la na tela da pessoa usuária através do HTML
async function pegarImagem() {
    // Este trecho de código vai criar um arquivo de entrada, através da diretriz de um documento (document.createElement('input')), 
    // onde criamos um elemento chamado de input. Esse input vai ler e aceitar arquivos do tipo imagem.
    let fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = 'image/*';
    // Para acionar a troca de mensagens assim que a imagem for selecionada, precisamos criar um procedimento que garanta que uma ação 
    // seja disparada toda vez que o estado do input for modificado. Esse procedimento será crucial para orquestrar a correta exibição 
    // da imagem na tela e garantir uma resposta adequada ao Flask. Para isso, vamos criar uma instrução onde adicionamos esse evento assíncrono, que é do tipo onchange
    // Quando fileInput for alterado e mudar de estado, vamos executar o que estiver no bloco de instrução.
    fileInput.onchange = async e => {
        if (miniaturaImagem) {
            miniaturaImagem.remove(); 
    }
    // vamos verificar qual é o conteúdo da imagem que foi selecionada por esta variável (e), e fazer com que tenhamos o foco nela e 
    // pegar o primeiro arquivo que foi selecionado. Esse arquivo vai ser alocado dentro da variável imagemSelecionada
    imagemSelecionada = e.target.files[0];
    // Abaixo, criamos um elemento novo que será do tipo imagem, do HTML. Em seguida, vai buscar e construir uma URL, que será o caminho que 
    // teremos para poder acessar essa imagem internamente ou localmente, com base em imagemSelecionada
    miniaturaImagem = document.createElement('img');
    miniaturaImagem.src = URL.createObjectURL(imagemSelecionada);
    miniaturaImagem.style.maxWidth = '3rem';
    miniaturaImagem.style.maxHeight = '3rem';
    miniaturaImagem.style.margin = '0.5rem';
    // cluir uma instrução que vai selecionar um elemento cuja classe seja .entrada__container e 
    // inserir, antes do elemento input, o elemento miniaturaImagem para que fique posicionado adequadamente.
    document.querySelector('.entrada__container').insertBefore(miniaturaImagem, input);
    // Para que essa imagem seja enviada para o Flask, precisamos criar uma variável do tipo FormData
    // Permitindo que a imagem seja mpacotada e transferida de uma linguagem, que é o JavaScript, para outra que é o Python
    // Depois, vamos adicionar a esse FormData uma chave de imagem cuja imagemSelecionada será atribuída a este valor
    let formData = new FormData();
    formData.append('imagem', imagemSelecionada);

    // cria um procedimento de resposta assíncrona, que vai ser associado à nossa URL de base para a rota upload_imagem
    // para garantir que toda vez que uma rota for selecionada do lado do Flask, ela invoque, dentro do JavaScript
    // gerando uma ação com o método do tipo POST e enviar no corpo dessa ação a imagem que acabamos de salvar.
    const response = await fetch('http://127.0.0.1:5000/upload_imagem', {
        method: 'POST',
        body: formData
    });
    
    // verificar do lado do JavaScript, se a respostaencontrou algum problema. Então, captura a resposta que virá da rota do Flask
    // e exibe no console para poder ter um controle e depurar melhor o código caso exista algum problema.
    const resposta = await response.text();
    console.log(resposta);
    console.log(imagemSelecionada);
    };
    // Para fechar a tela de input da pessoa usuária depois que ela selecionar a imagem, forçamos que o fileInput gere um autoclick
    // Garantindo que ao selecionar a imagem, ele seja fechado e possamos avançar para o restante do procedimento do fluxo da nossa aplicação.
    fileInput.click();
}


// verificamos se a mensagem enviada é vazia:
async function enviarMensagem() {
    if(input.value == "" || input.value == null) return;
    let mensagem = input.value;
    input.value = "";

    if (miniaturaImagem) {
        miniaturaImagem.remove(); 
    }

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
// botão de anexo receberá um evento do tipo click, que vai invocar o método pegarImagem.
botaoAnexo.addEventListener('click', pegarImagem);