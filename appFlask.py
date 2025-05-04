from flask import Flask, request, send_from_directory
from flask_cors import CORS
import tempfile
import os
from envelopeDigital import criar_envelope, abrir_envelope, gerar_chaves


app = Flask(__name__, static_folder='', static_url_path='')
CORS(app)

UPLOAD_FOLDER = 'arquivos'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return app.send_static_file('index.html')

# 1. SERVIR ARQUIVOS GERADOS
@app.route('/arquivos/<path:nome_arquivo>')
def servir_arquivo(nome_arquivo):
    return send_from_directory(UPLOAD_FOLDER, nome_arquivo)

# 2. CRIAR ENVELOPE
@app.route('/criar_envelope', methods=['POST'])
def route_criar_envelope():
    try:
        for nome in ['mensagem_cifrada.txt', 'chave_sessao_cifrada.txt', 'vetor_inicializacao.txt']:
            caminho = os.path.join(UPLOAD_FOLDER, nome)
            if os.path.exists(caminho):
                os.remove(caminho)

        with tempfile.NamedTemporaryFile(delete=False) as tmp_msg, \
             tempfile.NamedTemporaryFile(delete=False) as tmp_pub:

            tmp_msg.write(request.files['mensagem'].read())
            tmp_pub.write(request.files['chave_publica'].read())

            caminho_msg = tmp_msg.name
            caminho_pub = tmp_pub.name

        modo = request.form.get('modo', 'CBC')
        tam = int(request.form.get('tam', 256))
        saida = request.form.get('saida', 'hex')

        resultado = criar_envelope(caminho_msg, caminho_pub, modo, tam, saida)

        os.remove(caminho_msg)
        os.remove(caminho_pub)

        return resultado

    except Exception as e:
        return f"Erro ao criar envelope digital: {str(e)}", 400


# 3. ABRIR ENVELOPE
@app.route('/abrir_envelope', methods=['POST'])
def route_abrir_envelope():
    try:
        modo = request.form.get('modo', 'CBC')

        with tempfile.NamedTemporaryFile(delete=False) as tmp_msg_cif, \
             tempfile.NamedTemporaryFile(delete=False) as tmp_chave_cif, \
             tempfile.NamedTemporaryFile(delete=False) as tmp_priv:

            tmp_msg_cif.write(request.files['mensagem_cifrada'].read())
            tmp_chave_cif.write(request.files['chave_cifrada'].read())
            tmp_priv.write(request.files['chave_privada'].read())

            caminho_msg = tmp_msg_cif.name
            caminho_chave = tmp_chave_cif.name
            caminho_priv = tmp_priv.name

        caminho_iv = None
        if modo == 'CBC':
            with tempfile.NamedTemporaryFile(delete=False) as tmp_iv:
                tmp_iv.write(request.files['iv'].read())
                caminho_iv = tmp_iv.name

        abrir_envelope(caminho_msg, caminho_chave, modo, caminho_priv, caminho_iv)

        caminho_mensagem_clara = os.path.join('arquivos', 'mensagem_clara.txt')
        with open(caminho_mensagem_clara, 'r', encoding='utf-8') as f:
            mensagem = f.read()

        os.remove(caminho_msg)
        os.remove(caminho_chave)
        os.remove(caminho_priv)
        if caminho_iv:
            os.remove(caminho_iv)
        os.remove(caminho_mensagem_clara)

        return mensagem

    except Exception as e:
        return f"Erro ao abrir envelope: {str(e)}", 400


# 4. GERAR CHAVES
@app.route('/gerar_chaves', methods=['POST'])
def route_gerar_chaves():
    data = request.get_json()
    tamanho = data.get('tamanho_chave', 2048)
    return gerar_chaves(tamanho)


if __name__ == '__main__':
    app.run(debug=True)
