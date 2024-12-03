let chat = document.querySelector('#chat');
let input = document.querySelector('#input');
let botaoEnviar = document.querySelector('#botao-enviar');
let botaoAnexo = document.querySelector('#mais_arquivo');
let miniaturaImagem = null;
let imagemSelecionada = null;

// Função para selecionar e enviar uma imagem
async function pegarImagem() {
    let fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = 'image/*';
    fileInput.onchange = async e => {
        if (miniaturaImagem) {
            miniaturaImagem.remove(); 
        }
        imagemSelecionada = e.target.files[0];
        miniaturaImagem = document.createElement('img');
        miniaturaImagem.src = URL.createObjectURL(imagemSelecionada);
        miniaturaImagem.style.maxWidth = '3rem';
        miniaturaImagem.style.maxHeight = '3rem';
        miniaturaImagem.style.margin = '0.5rem';
        document.querySelector('.entrada__container').insertBefore(miniaturaImagem, input);

        // Criar um feedback visual
        let novaBolhaBot = criaBolhaBot();
        novaBolhaBot.innerHTML = "Analisando a imagem...";
        chat.appendChild(novaBolhaBot);
        vaiParaFinalDoChat();

        // Preparar envio da imagem
        let formData = new FormData();
        formData.append('imagem', imagemSelecionada);

        try {
            const response = await fetch('http://127.0.0.1:5000/upload_imagem', {
                method: 'POST',
                body: formData
            });

            const resposta = await response.text();
            console.log(resposta);
            novaBolhaBot.innerHTML = resposta.replace(/\n/g, '<br>');

        } catch (error) {
            console.error("Erro ao enviar imagem:", error);
            novaBolhaBot.innerHTML = "Erro ao analisar a imagem. Por favor, tente novamente.";
        } finally {
            if (miniaturaImagem) miniaturaImagem.remove();
            miniaturaImagem = null;
            vaiParaFinalDoChat();
        }
    };
    fileInput.click();
}

// Função para enviar uma mensagem de texto
async function enviarMensagem() {
    if (!input.value.trim()) return;
    let mensagem = input.value.trim();
    input.value = "";

    let novaBolha = criaBolhaUsuario();
    novaBolha.innerHTML = mensagem;
    chat.appendChild(novaBolha);

    let novaBolhaBot = criaBolhaBot();
    novaBolhaBot.innerHTML = "Analisando...";
    chat.appendChild(novaBolhaBot);
    vaiParaFinalDoChat();

    try {
        const resposta = await fetch("http://127.0.0.1:5000/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({'msg': mensagem}),
        });
        const textoDaResposta = await resposta.text();
        novaBolhaBot.innerHTML = textoDaResposta;  // Renderiza o HTML diretamente

    } catch (error) {
        console.error("Erro ao enviar mensagem:", error);
        novaBolhaBot.innerHTML = "Erro ao processar sua mensagem. Por favor, tente novamente.";
    }
}

// Funções auxiliares
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

function vaiParaFinalDoChat() {
    chat.scrollTop = chat.scrollHeight;
}

// Eventos de clique e teclado
botaoEnviar.addEventListener('click', enviarMensagem);
input.addEventListener("keyup", function(event) {
    event.preventDefault();
    if (event.keyCode === 13) {
        botaoEnviar.click();
    }
});
botaoAnexo.addEventListener('click', pegarImagem);
