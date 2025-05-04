# ArcanoProject

Sistema web para criptografia e descriptografia de mensagens com **criptografia híbrida**, compatível com a ferramenta [CyberChef](https://gchq.github.io/CyberChef/).
Ele permite a criação de chaves RSA, a construção de envelopes digitais (AES + RSA) e a abertura de envelopes criptografados.

## 1. Funcionalidades
O sistema implementa três operações principais:

* **Criar Chaves RSA**
  Geração de pares de chaves públicas/privadas no formato PEM, compatíveis com OpenSSL e CyberChef.

* **Criar Envelope Digital**
  Cifra a mensagem com AES (ECB ou CBC) e cifra a chave de sessão com RSA. Gera três arquivos:
  `mensagem_cifrada`, `chave_aes_cifrada`, `vetor_iv` (quando CBC).

* **Abrir Envelope Digital**
  Reverte o processo: descriptografa a chave AES com RSA e usa essa chave para recuperar a mensagem original.

## 2. Interface Web

A interface é responsiva e interativa, com um assistente que responde às ações do usuário.

* `index.html` – estrutura da interface
* `styles.css` – estilo e animações
* `script.js` – lógica do front-end, comunicação com o back-end

## 3. Comunicação Back-End

A ponte entre a interface e os algoritmos foi feita com **Flask**, usando chamadas assíncronas `fetch`.
* `appFlask.py` – servidor Flask que recebe as requisições da interface e executa as funções de criptografia

## 4. Algoritmos Criptográficos

Os algoritmos de criptografia estão no módulo:

* `envelopeDigital.py`
