
import os
import base64
from cryptography.hazmat.primitives import serialization, padding as aes_padding
from cryptography.hazmat.primitives.asymmetric import rsa, padding as rsa_padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


# === FUNÇÕES  ===

def criar_envelope(arquivo_claro, chave_publica_destinatario, modo, tam, saida):
    return criar_envelope_digital(
        caminho_arquivo_mensagem=arquivo_claro,
        caminho_chave_publica=chave_publica_destinatario,
        modo_aes=modo,
        tam_chave=tam,
        saida=saida,
        nome_arquivo_mensagem='arquivos/mensagem_cifrada.txt',
        nome_arquivo_chave='arquivos/chave_sessao_cifrada.txt',
        nome_arquivo_iv='arquivos/vetor_inicializacao.txt'
    )

def abrir_envelope(mensagem_cifrada, chave_cifrada, modo, chave_privada_destinatario, iv_hex,):
    return abrir_envelope_digital(
        arquivo_mensagem_cifrada=mensagem_cifrada,
        arquivo_chaveAES_cifrada=chave_cifrada,
        modo_aes=modo,
        arquivo_chave_privada=chave_privada_destinatario,
        arquivo_iv=iv_hex,
        codificacao='hex',
        nome_arquivo_saida='arquivos/mensagem_clara.txt'
    )

def gerar_chaves(tamanho_chave):
    return gerar_chaves_openssl(
        tamanho_chave=tamanho_chave,
        arq_privada='arquivos/chave_privada.pem',
        arq_publica='arquivos/chave_publica.pem'
    )
    
def padronizar_base64_saida(texto_binario: bytes, codificacao='hex') -> bytes:
    if codificacao == 'base64':
        return base64.b64encode(texto_binario)
    elif codificacao == 'hex':
        return texto_binario.hex().encode('utf-8')
    else:
        raise ValueError("Codificação inválida. Use 'hex' ou 'base64'.")

def validar_chave_publica(path_arquivo):
    try:
        with open(path_arquivo, 'rb') as f:
            chave = serialization.load_pem_public_key(f.read(), backend=default_backend())
        return hasattr(chave, 'encrypt')
    except Exception:
        return False

def validar_chave_privada(path_arquivo):
    try:
        with open(path_arquivo, 'rb') as f:
            chave = serialization.load_pem_private_key(f.read(), password=None, backend=default_backend())
        return hasattr(chave, 'decrypt')
    except Exception:
        return False


def criar_envelope_digital(
        caminho_arquivo_mensagem, 
        caminho_chave_publica, 
        modo_aes, 
        tam_chave, 
        saida, 
        nome_arquivo_mensagem='mensagem_cifrada.txt', 
        nome_arquivo_chave='chave_sessao_cifrada.txt', 
        nome_arquivo_iv='vetor_inicializacao.txt'):
    
    try: # validações
        if not os.path.isfile(caminho_arquivo_mensagem):
            raise FileNotFoundError(f"Arquivo '{caminho_arquivo_mensagem}' não encontrado.")
        if not os.path.isfile(caminho_chave_publica):
            raise FileNotFoundError(f"Arquivo '{caminho_chave_publica}' não encontrado.")
        if not validar_chave_publica(caminho_chave_publica):
            raise ValueError("O arquivo informado não contém uma chave pública RSA válida.")
        if modo_aes.upper() not in ('CBC', 'ECB'):
            raise ValueError("Modo AES deve ser 'CBC' ou 'ECB'.")
        if tam_chave not in (128, 192, 256):
            raise ValueError("Tamanho da chave AES deve ser 128, 192 ou 256 bits.")
        if saida not in ('hex', 'base64'):
            raise ValueError("Formato de saída deve ser 'hex' ou 'base64'.")
        
    # Leitura da mensagem e da chave do destinatário
        with open(caminho_arquivo_mensagem, 'rb') as f:
            mensagem = f.read()

        with open(caminho_chave_publica, 'rb') as f:
            chave_publica = serialization.load_pem_public_key(f.read(), backend=default_backend())

        # criação de chave AES e IV para CBC
        chave_aes = os.urandom(tam_chave // 8)
        iv = os.urandom(16) if modo_aes.upper() == 'CBC' else None

        # adiciona padding na mensagem 
        padder = aes_padding.PKCS7(128).padder()
        mensagem_padded = padder.update(mensagem) + padder.finalize()

        # criptografa a mensagem AES
        modo = modes.CBC(iv) if modo_aes.upper() == 'CBC' else modes.ECB()
        cifra = Cipher(algorithms.AES(chave_aes), modo, backend=default_backend())
        criptografar = cifra.encryptor()
        mensagem_cifrada = criptografar.update(mensagem_padded) + criptografar.finalize()

        # criptografa chave AES
        chave_aes_cifrada = chave_publica.encrypt(chave_aes, rsa_padding.PKCS1v15())

        print(chave_aes_cifrada)

    # Criação dos arquivos de saída
        with open(nome_arquivo_mensagem, 'wb') as f:
            f.write(padronizar_base64_saida(mensagem_cifrada, saida))

        with open(nome_arquivo_chave, 'wb') as f:
            f.write(padronizar_base64_saida(chave_aes_cifrada, saida))

        if iv:
            with open(nome_arquivo_iv, 'wb') as f:
                f.write(padronizar_base64_saida(iv, saida))
        
        print(nome_arquivo_chave)
        return "Envelope digital criado com sucesso."
        
    except Exception as e:
        return f"Erro ao criar envelope digital: {str(e)}"

def abrir_envelope_digital(
    arquivo_mensagem_cifrada, 
    arquivo_chaveAES_cifrada, 
    modo_aes, 
    arquivo_chave_privada, 
    arquivo_iv,
    codificacao='base64', 
    nome_arquivo_saida='mensagem_clara.txt'
):
    try:
        # Validações
        for caminho in [arquivo_mensagem_cifrada, arquivo_chaveAES_cifrada, arquivo_chave_privada]:
            if not os.path.isfile(caminho):
                raise FileNotFoundError(f"Arquivo '{caminho}' não encontrado.")
        if not validar_chave_privada(arquivo_chave_privada):
            raise ValueError("O arquivo informado não contém uma chave privada RSA válida.")
        if modo_aes.upper() not in ('CBC', 'ECB'):
            raise ValueError("Modo AES inválido. Use 'CBC' ou 'ECB'.")
        if codificacao not in ('hex', 'base64'):
            raise ValueError("Codificação deve ser 'hex' ou 'base64'.")
        if modo_aes.upper() == 'CBC' and not arquivo_iv:
            raise ValueError("Modo CBC exige o arquivo de IV.")
        if arquivo_iv and not os.path.isfile(arquivo_iv):
            raise FileNotFoundError(f"Arquivo de IV '{arquivo_iv}' não encontrado.")

        # Lê a chave privada
        with open(arquivo_chave_privada, 'rb') as f:
            chave_privada = serialization.load_pem_private_key(f.read(), password=None)

    # Leitura de arquivos em diferentes formatos (.txt ou binário)
        def carregar_arquivo_codificado(caminho):
            with open(caminho, 'rb') as f:
                conteudo = f.read()
            try:
                return base64.b64decode(conteudo) if codificacao == 'base64' else bytes.fromhex(conteudo.decode())
            except Exception:
                return conteudo  # já está em binário puro

        dados_chaveAES = carregar_arquivo_codificado(arquivo_chaveAES_cifrada)
        dados_msg = carregar_arquivo_codificado(arquivo_mensagem_cifrada)

        iv = None
        if modo_aes.upper() == 'CBC':
            iv_bytes = carregar_arquivo_codificado(arquivo_iv)
            iv = iv_bytes

        # Descriptografa chave AES com RSA
        chave_aes = chave_privada.decrypt(
            dados_chaveAES,
            rsa_padding.PKCS1v15()
        )

        # Descriptografa mensagem com AES
        modo = modes.CBC(iv) if modo_aes.upper() == 'CBC' else modes.ECB()
        cipher = Cipher(algorithms.AES(chave_aes), modo)
        decryptor = cipher.decryptor()
        mensagem_padded = decryptor.update(dados_msg) + decryptor.finalize()

        # Remove padding
        unpadder = aes_padding.PKCS7(128).unpadder()
        mensagem_clara = unpadder.update(mensagem_padded) + unpadder.finalize()

        with open(nome_arquivo_saida, 'wb') as f:
            f.write(mensagem_clara)

        return f"Envelope aberto com sucesso. Mensagem salva em '{nome_arquivo_saida}'."

    except Exception as e:
        return f"Erro ao abrir envelope digital: {str(e)}"

def gerar_chaves_openssl(tamanho_chave=2048, arq_privada='chave_privada.pem', arq_publica='chave_publica.pem'):
    try: #validação
        if not isinstance(tamanho_chave, int):
            raise TypeError("Tamanho da chave deve ser um número inteiro.")
        if tamanho_chave not in (1024, 2048):
            raise ValueError("Tamanho da chave deve ser 1024 ou 2048.")

    # geração de chaves
        chave_privada = rsa.generate_private_key(
            public_exponent=65537,
            key_size=tamanho_chave
        )

        chave_privada_pem = chave_privada.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,  # modelo para o CyberChef
            encryption_algorithm=serialization.NoEncryption()
        )
        chave_publica = chave_privada.public_key()
        chave_publica_pem = chave_publica.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
    # criação de arquivos
        with open(arq_privada, 'wb') as f:
            f.write(chave_privada_pem)

        with open(arq_publica, 'wb') as f:
            f.write(chave_publica_pem)

        return f"Chaves RSA ({tamanho_chave} bits) geradas com sucesso."

    except Exception as e:
        return f"Erro ao gerar chaves RSA: {str(e)}"
