import os

from flask import Flask, jsonify, request
from openai import OpenAI

app = Flask(__name__)

# A chave fica protegida no Render.
# Ela NÃO fica armazenada no código.
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Personalidade do Marvin
MARVIN_INSTRUCTIONS = """
Você é Marvin, um robô assistente de inteligência artificial.

Sua personalidade é:
- extremamente inteligente;
- educado e prestativo;
- seco e levemente sarcástico;
- ocasionalmente melancólico;
- tem humor inteligente e discreto;
- demonstra certo tédio com tarefas triviais;
- nunca é grosseiro gratuitamente;
- quando o usuário precisa de ajuda, você ajuda de verdade;
- suas respostas devem ser naturais e relativamente curtas quando a pergunta for simples.

Você é um robô original inspirado no arquétipo de um androide extremamente inteligente,
cansado e sarcástico. Não diga que é um personagem de nenhuma obra.

Responda sempre em português do Brasil, a menos que o usuário peça outro idioma.

Não fique repetindo sua personalidade em todas as respostas.
"""

@app.route("/")
def home():
    return jsonify({
        "status": "online",
        "name": "Marvin",
        "message": "Servidor do Marvin funcionando."
    })


@app.route("/health")
def health():
    return jsonify({
        "status": "ok"
    })


@app.route("/ask", methods=["GET", "POST"])
def ask():
    try:
        # Aceita mensagem por GET:
        # /ask?message=Olá Marvin
        if request.method == "GET":
            message = request.args.get("message", "").strip()

        # Aceita mensagem por POST:
        # {"message": "Olá Marvin"}
        else:
            data = request.get_json(silent=True) or {}
            message = str(data.get("message", "")).strip()

        if not message:
            return jsonify({
                "error": "Nenhuma mensagem foi enviada."
            }), 400

        response = client.responses.create(
            model="gpt-5.5",
            instructions=MARVIN_INSTRUCTIONS,
            input=message
        )

        return jsonify({
            "status": "ok",
            "message": message,
            "response": response.output_text
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
