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

function avatarFala(mensagem) {
  const bubble = document.getElementById('speech-bubble');
  const texto = document.getElementById('speech-text');

  texto.textContent = mensagem;
  bubble.classList.remove('hidden');
}

function fecharBalão() {
  document.getElementById('speech-bubble').classList.add('hidden');
}


// 2. CRIPTOGRAFIA
function criarEnvelope() {
  const mensagem = document.getElementById('arquivoMensagem').files[0];
  const chavePublica = document.getElementById('chavePublica').files[0];
  const modo = document.getElementById('modo_aes1').value;
  const tam = document.getElementById('tam_chave').value;
  const saida = document.getElementById('saida').value;

  if (!mensagem || !chavePublica) {
    avatarFala('Por favor, selecione os arquivos necessários.');
    return;
  }

  const formData = new FormData();
  formData.append('mensagem', mensagem);
  formData.append('chave_publica', chavePublica);
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
      avatarFala('Envelope criado com sucesso!');
    })
    .catch(error => {
      console.error('Erro:', error);
      avatarFala('Erro ao criar envelope.');
    });
}

// 3. DESCRIPTOGRAFIA
async function abrirEnvelope() {
  const mensagemCifrada = document.getElementById('mensagemCifrada').files[0];
  const chaveCifrada = document.getElementById('chaveCifrada').files[0];
  const modo = document.getElementById('modo_aes2').value;
  const vetorIV = document.getElementById('vetorIV').files[0];
  const chavePrivada = document.getElementById('chavePrivada').files[0];

  if (!mensagemCifrada || !chaveCifrada || !vetorIV || !chavePrivada) {
    avatarFala('Por favor, selecione todos os arquivos necessários.');
    return;
  }

  const formData = new FormData();
  formData.append('mensagem_cifrada', mensagemCifrada);
  formData.append('chave_cifrada', chaveCifrada);
  formData.append('modo', modo);
  formData.append('iv', vetorIV);
  formData.append('chave_privada', chavePrivada);

  try {
    const response = await fetch('/abrir_envelope', {
      method: 'POST',
      body: formData
    });

    const resultado = await response.text();
    document.getElementById('decryptOutput').innerText = resultado;
    avatarFala('Envelope aberto com sucesso!');
  } catch (error) {
    avatarFala('Erro ao abrir envelope');
  }
}

// 4. GERAÇÃO DE CHAVES
async function gerarChaves() { 
  const keySize = document.getElementById('keySize').value;
  try {
    const response = await fetch('/gerar_chaves', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ tamanho_chave: parseInt(keySize) })
    });

    const texto = await response.text();
    if (!response.ok) {
      throw new Error(texto || 'Erro desconhecido ao gerar chaves.');
    }

    avatarFala('Chaves geradas com sucesso!');
  } catch (error) {
    console.error('Erro:', error);
    avatarFala('Erro ao gerar chaves.');
    setAvatarMode("error");
  }
}


