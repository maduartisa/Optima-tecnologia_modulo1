from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

"""
============================================
📌 COMO RODAR ESTE SISTEMA (PASSO A PASSO)
============================================

1. Instale o Python (3.8 ou superior)

2. Instale as dependências:
   pip install flask flask-cors

3. Salve este arquivo como:
   app.py

4. Execute no terminal:
   python app.py

5. Acesse no navegador:
   http://127.0.0.1:5000

============================================
✅ ENDPOINTS DISPONÍVEIS
============================================
GET    /                  → interface web
GET    /ambientes         → listar ambientes
POST   /ambientes         → criar novo
GET    /ambientes/<id>    → obter específico
PUT    /ambientes/<id>    → atualizar
DELETE /ambientes/<id>    → remover
============================================
"""

app = Flask(__name__, template_folder='templates')
CORS(app)

# Simulação de banco de dados em memória
ambientes = [
    {
        "id": 1,
        "nome": "Loja 01",
        "categoria": "Loja",
        "andar": "Térreo",
        "zona": "Comercial",
        "nivel_acesso": 1
    },
    {
        "id": 2,
        "nome": "Sala 12",
        "categoria": "Sala Comercial",
        "andar": "3º Andar",
        "zona": "Privativa",
        "nivel_acesso": 3
    },
    {
        "id": 3,
        "nome": "Cinema 01",
        "categoria": "Entretenimento",
        "andar": "2º Andar",
        "zona": "Lazer",
        "nivel_acesso": 2
    }
]


# Rota raiz - Interface Web
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


# Listar todos ambientes
@app.route('/ambientes', methods=['GET'])
def listar_ambientes():
    return jsonify(ambientes)


# Obter ambiente específico
@app.route('/ambientes/<int:id>', methods=['GET'])
def obter_ambiente(id):
    for amb in ambientes:
        if amb["id"] == id:
            return jsonify(amb)
    return jsonify({"erro": "Ambiente não encontrado"}), 404


# Criar novo ambiente
@app.route('/ambientes', methods=['POST'])
def criar_ambiente():
    data = request.json
    
    # Validação de campos obrigatórios
    campos_obrigatorios = ['nome', 'categoria', 'andar', 'zona', 'nivel_acesso']
    if not all(field in data for field in campos_obrigatorios):
        return jsonify({"erro": "Campos obrigatórios faltando: " + str(campos_obrigatorios)}), 400
    
    novo = {
        "id": len(ambientes) + 1,
        "nome": data.get("nome"),
        "categoria": data.get("categoria"),
        "andar": data.get("andar"),
        "zona": data.get("zona"),
        "nivel_acesso": data.get("nivel_acesso")
    }
    ambientes.append(novo)
    return jsonify(novo), 201


# Atualizar ambiente
@app.route('/ambientes/<int:id>', methods=['PUT'])
def atualizar_ambiente(id):
    data = request.json
    for amb in ambientes:
        if amb["id"] == id:
            amb.update(data)
            return jsonify(amb)
    return jsonify({"erro": "Ambiente não encontrado"}), 404


# Deletar ambiente
@app.route('/ambientes/<int:id>', methods=['DELETE'])
def deletar_ambiente(id):
    global ambientes
    ambiente_removido = None
    for amb in ambientes:
        if amb["id"] == id:
            ambiente_removido = amb
            break
    
    if ambiente_removido is None:
        return jsonify({"erro": "Ambiente não encontrado"}), 404
    
    ambientes = [a for a in ambientes if a["id"] != id]
    return jsonify({"mensagem": "Removido com sucesso", "ambiente": ambiente_removido}), 200


# Rodar servidor
if __name__ == '__main__':
    print("🚀 Servidor iniciado em: http://127.0.0.1:5000")
    app.run(debug=True)
