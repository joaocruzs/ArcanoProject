from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from envelopeDigital import criar_envelope, abrir_envelope, gerar_chaves


app = Flask(__name__, static_url_path='', static_folder='.')
CORS(app)

@app.route('/')
def index():
    return app.send_static_file('index.html')

# 1. PASTA DE ARQUIVOS
UPLOAD_FOLDER = 'arquivos'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 2. CRIAR ENVELOPE
@app.route('/criar_envelope', methods=['POST'])
def route_criar_envelope():
    try:
        mensagem = request.files['mensagem'].read()
        chave_pub_pem = request.files['chave_publica'].read()

        modo = request.form.get('modo', 'CBC')
        tam = int(request.form.get('tam', 256))
        saida = request.form.get('saida', 'hex')

        return criar_envelope(mensagem, chave_pub_pem, modo, tam, saida)

    except Exception as e:
        return f"Erro ao criar envelope: {str(e)}", 400


# 3. ABRIR ENVELOPE
@app.route('/abrir_envelope', methods=['POST'])
def route_abrir_envelope():
    try:
        mensagem_cifrada = request.files['mensagem_cifrada'].read()
        chave_cifrada = request.files['chave_cifrada'].read()
        iv = request.files['iv'].read()
        chave_privada_pem = request.files['chave_privada'].read()

        modo = request.form.get('modo', 'CBC')

        return abrir_envelope(mensagem_cifrada, chave_cifrada, modo, iv, chave_privada_pem)

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
