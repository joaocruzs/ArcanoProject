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
        msg_file = request.files['mensagem']
        pub_file = request.files['chave_publica']

        caminho_msg = os.path.join(UPLOAD_FOLDER, secure_filename(msg_file.filename))
        caminho_pub = os.path.join(UPLOAD_FOLDER, secure_filename(pub_file.filename))

        msg_file.save(caminho_msg)
        pub_file.save(caminho_pub)

        modo = request.form.get('modo', 'CBC')
        tam = int(request.form.get('tam', 256))
        saida = request.form.get('saida', 'hex')

        return criar_envelope(caminho_msg, caminho_pub, modo, tam, saida)
    
    except Exception as e:
        return f"Erro ao criar envelope: {str(e)}"

# 3. ABRIR ENVELOPE
def route_abrir_envelope():
    try:
        msg_cif = request.files['mensagem_cifrada']
        chave_cif = request.files['chave_cifrada']
        iv = request.files['iv']
        priv = request.files['chave_privada']

        caminho_msg = os.path.join(UPLOAD_FOLDER, secure_filename(msg_cif.filename))
        caminho_chave = os.path.join(UPLOAD_FOLDER, secure_filename(chave_cif.filename))
        caminho_iv = os.path.join(UPLOAD_FOLDER, secure_filename(iv.filename))
        caminho_priv = os.path.join(UPLOAD_FOLDER, secure_filename(priv.filename))

        msg_cif.save(caminho_msg)
        chave_cif.save(caminho_chave)
        iv.save(caminho_iv)
        priv.save(caminho_priv)

        modo = request.form.get('modo', 'CBC')

        return abrir_envelope(caminho_msg, caminho_chave, modo, caminho_iv, caminho_priv)
    
    except Exception as e:
        return f"Erro ao abrir envelope: {str(e)}"

# 4. GERAR CHAVES
@app.route('/gerar_chaves', methods=['POST'])
def route_gerar_chaves():
    data = request.get_json()
    tamanho = data.get('tamanho_chave', 2048)
    return gerar_chaves(tamanho)


if __name__ == '__main__':
    app.run(debug=True)
