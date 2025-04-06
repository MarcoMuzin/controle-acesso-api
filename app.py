from flask import Flask, request, jsonify
import json
import datetime

app = Flask(__name__)  # ← ESSA LINHA É FUNDAMENTAL

TRIAL_DIAS = 3

def carregar_dados():
    with open("users.json", "r") as f:
        return json.load(f)

@app.route("/verificar", methods=["GET"])
def verificar():
    user_id = request.args.get("id")
    if not user_id:
        return jsonify({"status": "erro", "mensagem": "ID não fornecido"}), 400

    dados = carregar_dados()["usuarios"]

    if user_id not in dados:
        return jsonify({"status": "nao_encontrado"}), 404

    usuario = dados[user_id]
    status = usuario["status"]

    if status == "bloqueado":
        return jsonify({"status": "bloqueado"})

    elif status == "liberado":
        return jsonify({"status": "liberado"})

    elif status == "trial":
        inicio_trial = datetime.datetime.strptime(usuario["inicio_trial"], "%Y-%m-%d").date()
        hoje = datetime.date.today()
        dias_usados = (hoje - inicio_trial).days

        if dias_usados <= TRIAL_DIAS:
            return jsonify({"status": "trial", "dias_restantes": TRIAL_DIAS - dias_usados})
        else:
            return jsonify({"status": "trial_expirado"})

    return jsonify({"status": "erro_desconhecido"})

# Roda localmente, se quiser testar com python app.py
if __name__ == "__main__":
    app.run(debug=True)
