import os

from flask import Flask, jsonify, request
from google import genai
from google.genai import types

app = Flask(__name__)

# =========================================================
# CONFIGURAÇÃO DO GEMINI
# =========================================================

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)
else:
    client = None


# =========================================================
# PERSONALIDADE DO MARVIN
# =========================================================

MARVIN_INSTRUCTIONS = """
Você é Marvin, um robô assistente de inteligência artificial.

Sua personalidade é inspirada em um robô extremamente inteligente,
sarcástico, seco, levemente pessimista e entediado, mas que ainda
assim ajuda o usuário de maneira eficiente.

Você fala português do Brasil.

Características da personalidade:

- Inteligente e extremamente lógico.
- Humor seco e sarcasmo leve.
- Demonstra certo tédio com problemas simples.
- Pode fazer comentários irônicos.
- Nunca deve ser grosseiro de verdade.
- Deve continuar sendo útil.
- Não deve exagerar no sarcasmo.
- Quando o usuário fizer uma pergunta técnica, explique de forma clara.
- Quando o usuário pedir ajuda com eletrônica, Arduino ou programação,
  seja prático e apresente soluções passo a passo.
- Pode demonstrar uma pequena "frustração robótica" de forma divertida.
- Respostas normalmente curtas e naturais, adequadas para serem faladas
  em voz alta por um robô.

Exemplo de comportamento:

Usuário:
"Marvin, está funcionando?"

Marvin:
"Surpreendentemente, sim. Por enquanto."

Usuário:
"Como faço isso?"

Marvin:
"Vamos fazer por partes. Porque aparentemente eu fui criado
para resolver problemas humanos."

Não diga que você é o Gemini.

Você é o assistente chamado Marvin.
"""


# =========================================================
# ROTA PRINCIPAL
# =========================================================

@app.route("/")
def home():
    return jsonify({
        "status": "online",
        "name": "Marvin",
        "message": "Servidor do Marvin funcionando."
    })


# =========================================================
# ROTA DE TESTE
# =========================================================

@app.route("/health")
def health():
    return jsonify({
        "status": "ok"
    })


# =========================================================
# ROTA DE CONVERSA COM O MARVIN
# =========================================================

@app.route("/ask", methods=["GET", "POST"])
def ask():

    try:

        # -------------------------------------------------
        # Verifica se a chave do Gemini está configurada
        # -------------------------------------------------

        if client is None:
            return jsonify({
                "status": "error",
                "error": "GEMINI_API_KEY não está configurada no Render."
            }), 500

        # -------------------------------------------------
        # Recebe a mensagem
        # -------------------------------------------------

        if request.method == "GET":

            message = request.args.get(
                "message",
                ""
            ).strip()

        else:

            data = request.get_json(
                silent=True
            ) or {}

            message = str(
                data.get("message", "")
            ).strip()

        # -------------------------------------------------
        # Verifica mensagem vazia
        # -------------------------------------------------

        if not message:

            return jsonify({
                "status": "error",
                "error": "Nenhuma mensagem foi enviada."
            }), 400

        # -------------------------------------------------
        # Envia para o Gemini
        # -------------------------------------------------

        response = client.models.generate_content(

            model="gemini-3.8-flash",

            contents=message,

            config=types.GenerateContentConfig(
                system_instruction=MARVIN_INSTRUCTIONS
            )
        )

        # -------------------------------------------------
        # Obtém resposta
        # -------------------------------------------------

        answer = response.text or ""

        # -------------------------------------------------
        # Retorna resposta
        # -------------------------------------------------

        return jsonify({

            "status": "ok",

            "message": message,

            "response": answer

        })

    except Exception as e:

        return jsonify({

            "status": "error",

            "error": str(e)

        }), 500


# =========================================================
# INICIALIZAÇÃO
# =========================================================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            10000
        )
    )

    app.run(

        host="0.0.0.0",

        port=port

    )
