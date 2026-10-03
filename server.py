from flask import Flask, jsonify, request
import os
from google import genai

app = Flask(__name__)

# ============================================================
# CONFIGURAÇÃO DO GEMINI
# ============================================================

api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    print("AVISO: GEMINI_API_KEY não configurada.")
    client = None
else:
    client = genai.Client(api_key=api_key)


# ============================================================
# ROTA PRINCIPAL
# ============================================================

@app.route("/")
def home():
    return jsonify({
        "status": "online",
        "name": "Marvin",
        "message": "Servidor do Marvin funcionando."
    })


# ============================================================
# TESTE DO SERVIDOR
# ============================================================

@app.route("/health")
def health():
    return jsonify({
        "status": "ok"
    })


# ============================================================
# TESTE DO GEMINI
# ============================================================

@app.route("/test-gemini")
def test_gemini():

    if client is None:
        return jsonify({
            "status": "erro",
            "message": "GEMINI_API_KEY não configurada no Render."
        }), 500

    try:

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents="Responda apenas: Olá, eu sou Marvin."
        )

        return jsonify({
            "status": "ok",
            "response": response.text
        })

    except Exception as e:

        print("ERRO GEMINI:")
        print(str(e))

        return jsonify({
            "status": "erro",
            "message": str(e)
        }), 500


# ============================================================
# EXECUÇÃO LOCAL
# ============================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=10000
    )
