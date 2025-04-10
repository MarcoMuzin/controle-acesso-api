from flask import Flask, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)
ARQUIVO_USUARIOS = "users.json"

def carregar_usuarios():
    if not os.path.exists(ARQUIVO_USUARIOS):
        return {"usuarios": []}
    with open(ARQUIVO_USUARIOS, "r") as f:
        return json.load(f)

def salvar_usuarios(dados):
    with open(ARQUIVO_USUARIOS, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

@app.route("/registrar", methods=["POST"])
def registrar_id():
    data = request.get_json()
    user_id = data.get("id")
    if not user_id:
        return jsonify({"erro": "ID não fornecido"}), 400

    dados = carregar_usuarios()
    usuarios = dados.get("usuarios", [])

    print("🔍 Usuários carregados:", usuarios)

    for usuario in usuarios:
        if usuario.get("id") == user_id:
            return jsonify({"mensagem": "ID já registrado"}), 200

    for usuario in usuarios:
        if not usuario.get("id"):
            usuario["id"] = user_id
            salvar_usuarios({"usuarios": usuarios})
            return jsonify({"mensagem": "ID registrado com sucesso"}), 200

    return jsonify({"erro": "Limite de usuários atingido"}), 403

@app.route("/verificar", methods=["GET"])
def verificar_acesso():
    user_id = request.args.get("id")
    login = request.args.get("login")
    senha = request.args.get("senha")

    if not all([user_id, login, senha]):
        return jsonify({"erro": "Dados incompletos"}), 400

    dados = carregar_usuarios()
    usuarios = dados.get("usuarios", [])

    for usuario in usuarios:
        if usuario.get("id") == user_id and usuario.get("login") == login and usuario.get("senha") == senha:
            status = usuario.get("status")

            if status == "liberado":
                return jsonify({"status": "liberado"})

            elif status == "trial":
                data_registro = usuario.get("data_registro")
                dias_trial = usuario.get("dias_trial", 0)

                if not data_registro:
                    usuario["data_registro"] = datetime.now().strftime("%Y-%m-%d")
                    salvar_usuarios({"usuarios": usuarios})
                    return jsonify({"status": "trial", "dias_restantes": dias_trial})

                else:
                    inicio = datetime.strptime(data_registro, "%Y-%m-%d")
                    dias_passados = (datetime.now() - inicio).days
                    dias_restantes = max(0, dias_trial - dias_passados)

                    if dias_restantes > 0:
                        return jsonify({"status": "trial", "dias_restantes": dias_restantes})
                    else:
                        return jsonify({"status": "bloqueado"})

            else:
                return jsonify({"status": "bloqueado"})

    return jsonify({"erro": "Credenciais inválidas ou não encontradas"}), 403

@app.route("/saúdez")  # rota para health check da Render
def saudez():
    return "OK", 200

if __name__ == "__main__":
    app.run(debug=True)
