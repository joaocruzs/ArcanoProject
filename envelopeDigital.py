
from cryptography.hazmat.primitives import serialization, padding as aes_padding
from cryptography.hazmat.primitives.asymmetric import rsa, padding as rsa_padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os, base64

# === FUNÇÕES  ===

def criar_envelope(arquivo_claro, chave_publica_destinatario, modo, tam, saida):
    return criar_envelope_modificado(
        caminho_arquivo_mensagem=arquivo_claro,
        caminho_chave_publica=chave_publica_destinatario,
        modo_aes=modo,
        tam_chave=tam,
        saida=saida,
        nome_arquivo_mensagem='arquivos/mensagem_cifrada.txt',
        nome_arquivo_chave='arquivos/chave_sessao_cifrada.txt',
        nome_arquivo_iv='arquivos/vetor_inicializacao.txt'
    )

def abrir_envelope(mensagem_cifrada, chave_cifrada, modo, chave_privada_destinatario, iv_hex):
    return abrir_envelope_modificado(
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
    
def criar_envelope_modificado(
    caminho_arquivo_mensagem,
    caminho_chave_publica,
    modo_aes,
    tam_chave,
    saida,
    nome_arquivo_mensagem,
    nome_arquivo_chave,
    nome_arquivo_iv
):
    if not os.path.isfile(caminho_arquivo_mensagem):
        raise FileNotFoundError(f"Arquivo '{caminho_arquivo_mensagem}' não encontrado.")
    if not os.path.isfile(caminho_chave_publica):
        raise FileNotFoundError(f"Arquivo '{caminho_chave_publica}' não encontrado.")

    with open(caminho_arquivo_mensagem, 'rb') as f:
        mensagem = f.read()
    with open(caminho_chave_publica, 'rb') as f:
        chave_publica = serialization.load_pem_public_key(f.read(), backend=default_backend())

    chave_aes = os.urandom(tam_chave // 8)
    iv = os.urandom(16) if modo_aes.upper() == 'CBC' else None

    padder = aes_padding.PKCS7(128).padder()
    mensagem_padded = padder.update(mensagem) + padder.finalize()

    modo = modes.CBC(iv) if modo_aes.upper() == 'CBC' else modes.ECB()
    cifra = Cipher(algorithms.AES(chave_aes), modo, backend=default_backend())
    criptografar = cifra.encryptor()
    mensagem_cifrada = criptografar.update(mensagem_padded) + criptografar.finalize()

    chave_codificada = base64.b64encode(chave_aes) if saida == 'base64' else chave_aes.hex().encode()
    chave_aes_cifrada = chave_publica.encrypt(chave_codificada, rsa_padding.PKCS1v15())

    with open(nome_arquivo_mensagem, 'wb') as f:
        f.write(base64.b64encode(mensagem_cifrada) if saida == 'base64' else mensagem_cifrada.hex().encode())

    with open(nome_arquivo_chave, 'wb') as f:
        f.write(base64.b64encode(chave_aes_cifrada) if saida == 'base64' else chave_aes_cifrada.hex().encode())

    if iv:
        with open(nome_arquivo_iv, 'wb') as f:
            f.write(base64.b64encode(iv) if saida == 'base64' else iv.hex().encode())

    return "Envelope digital (modificado) criado com sucesso."


def abrir_envelope_modificado(
    arquivo_mensagem_cifrada,
    arquivo_chaveAES_cifrada,
    modo_aes,
    arquivo_chave_privada,
    arquivo_iv,
    codificacao,
    nome_arquivo_saida
):
    with open(arquivo_chave_privada, 'rb') as f:
        chave_privada = serialization.load_pem_private_key(f.read(), password=None)

    with open(arquivo_chaveAES_cifrada, 'rb') as f:
        dados_chaveAES = f.read()
    with open(arquivo_mensagem_cifrada, 'rb') as f:
        dados_msg = f.read()
    if modo_aes.upper() == 'CBC' and arquivo_iv:
        with open(arquivo_iv, 'r') as f:
            iv_conteudo = f.read().strip()
        iv = base64.b64decode(iv_conteudo) if codificacao == 'base64' else bytes.fromhex(iv_conteudo)
    else:
        iv = None

    chave_codificada = chave_privada.decrypt(
        base64.b64decode(dados_chaveAES) if codificacao == 'base64' else bytes.fromhex(dados_chaveAES.decode()),
        rsa_padding.PKCS1v15()
    )

    chave_aes = base64.b64decode(chave_codificada) if codificacao == 'base64' else bytes.fromhex(chave_codificada.decode())

    modo = modes.CBC(iv) if modo_aes.upper() == 'CBC' else modes.ECB()
    cipher = Cipher(algorithms.AES(chave_aes), modo)
    decryptor = cipher.decryptor()
    dados_msg = base64.b64decode(dados_msg) if codificacao == 'base64' else bytes.fromhex(dados_msg.decode())
    mensagem_padded = decryptor.update(dados_msg) + decryptor.finalize()

    unpadder = aes_padding.PKCS7(128).unpadder()
    mensagem_clara = unpadder.update(mensagem_padded) + unpadder.finalize()

    with open(nome_arquivo_saida, 'wb') as f:
        f.write(mensagem_clara)

    return f"Envelope modificado aberto com sucesso. Mensagem salva em '{nome_arquivo_saida}'."

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
