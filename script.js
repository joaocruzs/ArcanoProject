const toggleBtn = document.getElementById("toggleSidebar");
const sidebar = document.getElementById("sidebar");
const projectTitle = document.getElementById("project-title");
const avatar = document.getElementById("avatar");
const speechBubble = document.getElementById("speechBubble");
const toggleAuthors = document.getElementById("toggleAuthors");
const authors = document.getElementById("authors");
const body = document.body;

// 1. BARRA LATERAL
let sidebarExpanded = true;
toggleBtn.addEventListener("click", (event) => {
  event.stopPropagation();
  sidebarExpanded = !sidebarExpanded;
  if (sidebarExpanded) {
    sidebar.classList.add("expanded");
    projectTitle.style.display = "inline";
    avatar.style.display = "inline";
    toggleAuthors.style.display = "inline";
  } else {
    sidebar.classList.remove("expanded");
    projectTitle.style.display = "none";
    avatar.style.display = "none";
    speechBubble.classList.add("hidden");
    toggleAuthors.style.display = "none";
    authors.classList.add("hidden");
  }
});

toggleAuthors.addEventListener("click", (event) => {
  event.stopPropagation();
  authors.classList.toggle("hidden");
});

// 1.1 RESETAR PÁGINA
projectTitle.addEventListener("click", (event) => {
  event.stopPropagation();
  location.reload();
});

// 1.2. AVATAR
let currentAvatar = "imagens/iconVerde.png";

function setAvatarMode(mode) {
  let newAvatar = currentAvatar;

  switch (mode) {
    case "crypto":
      newAvatar = "imagens/iconVermelho.png";
      body.style.backgroundColor = "#cc3d3d";
      avatar.style.borderColor = "#cc3d3d";
      break;
    case "decrypto":
      newAvatar = "imagens/iconAzul.png";
      body.style.backgroundColor = "#3d9ccc";
      avatar.style.borderColor = "#3d9ccc";
      break;
    case "chaves":
      newAvatar = "imagens/iconAmarelo.png";
      body.style.backgroundColor = "#ddd900";
      avatar.style.borderColor = "#ddd900";
      break;
    case "error":
      newAvatar = "imagens/iconCinza.png";
      body.style.backgroundColor = "#474747";
      avatar.style.borderColor = "#474747";
      break;
    default:
      newAvatar = "imagens/icon.png";
      body.style.backgroundColor = "#44e844";
      avatar.style.borderColor = "#44e844";
  }

  if (newAvatar !== currentAvatar) {
    avatar.style.opacity = 0;

    setTimeout(() => {
      avatar.src = newAvatar;
      currentAvatar = newAvatar;
      avatar.style.opacity = 1;
    }, 150);
  }
}

// 2. CRIPTOGRAFIA
function criarEnvelope() {
  const mensagemTexto = document.getElementById('mensagemTexto').value.trim();
  const chavePublicaTexto = document.getElementById('chavePublicaTexto').value.trim();
  const modo = document.getElementById('modo_aes1').value;
  const tam = document.getElementById('tam_chave').value;
  const saida = document.getElementById('saida').value;

  if (!mensagemTexto || !chavePublicaTexto) {
    alert('Por favor, preencha os dois campos de texto.');
    return;
  }

  const mensagemBlob = new Blob([mensagemTexto], { type: 'text/plain' });
  const mensagemFile = new File([mensagemBlob], 'mensagem.txt');

  const chaveBlob = new Blob([chavePublicaTexto], { type: 'text/plain' });
  const chaveFile = new File([chaveBlob], 'chave_publica.pem');

  const formData = new FormData();
  formData.append('mensagem', mensagemFile);
  formData.append('chave_publica', chaveFile);
  formData.append('modo', modo);
  formData.append('tam', tam);
  formData.append('saida', saida);

  fetch('/criar_envelope', {
    method: 'POST',
    body: formData
  })
    .then(response => response.text())
    .then(data => {
      document.getElementById('cryptOutput').textContent = data;
      setAvatarMode("crypto");
    })
    .catch(error => {
      console.error('Erro:', error);
      document.getElementById('cryptOutput').textContent = 'Erro ao criar envelope.';
      setAvatarMode("error");
    });
}


// 3. DESCRIPTOGRAFIA
async function abrirEnvelope() {
  const mensagemCifradaTexto = document.getElementById('mensagemCifradaTexto').value.trim();
  const chaveCifradaTexto = document.getElementById('chaveCifradaTexto').value.trim();
  const modo = document.getElementById('modo_aes2').value;
  const ivTexto = document.getElementById('vetorIVTexto').value.trim();
  const chavePrivadaTexto = document.getElementById('chavePrivadaTexto').value.trim();

  if (!mensagemCifradaTexto || !chaveCifradaTexto || !ivTexto || !chavePrivadaTexto) {
    alert('Por favor, preencha todos os campos necessários.');
    return;
  }

  const formData = new FormData();
  formData.append('mensagem_cifrada', new File([mensagemCifradaTexto], 'msg_cifrada.txt'));
  formData.append('chave_cifrada', new File([chaveCifradaTexto], 'chave_cifrada.txt'));
  formData.append('modo', modo);
  formData.append('iv', new File([ivTexto], 'iv.txt'));
  formData.append('chave_privada', new File([chavePrivadaTexto], 'chave_privada.pem'));

  try {
    const response = await fetch('/abrir_envelope', {
      method: 'POST',
      body: formData
    });

    const resultado = await response.text();
    document.getElementById('decryptOutput').innerText = resultado;
    setAvatarMode("decrypto");
  } catch (error) {
    document.getElementById('decryptOutput').innerText = 'Erro ao abrir envelope: ' + error.message;
    setAvatarMode("error");
  }
}


// 4. GERAÇÃO DE CHAVES
async function gerarChaves() {
  const keySize = document.getElementById('keySize').value;
  const resChave = document.getElementById('res-chave');

  try {
    const response = await fetch('/gerar_chaves', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ tamanho_chave: parseInt(keySize) })
    });

    const resultado = await response.text();
    resChave.innerText = resultado;
  } catch (error) {
    resChave.innerText = 'Erro ao gerar chaves: ' + error.message;
  }

  setAvatarMode("chaves");
}

