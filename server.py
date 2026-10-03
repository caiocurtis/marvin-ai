from flask import Flask, jsonify, request, Response
from openai import OpenAI
import os

app = Flask(__name__)

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)


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


@app.route("/tts")
def tts():

    texto = request.args.get("text", "").strip()

    if not texto:
        return jsonify({
            "error": "Informe o texto usando ?text="
        }), 400

    if len(texto) > 1000:
        return jsonify({
            "error": "Texto muito grande."
        }), 400

    try:

        response = client.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice="cedar",
            input=texto,
            instructions=(
                "Speak in Brazilian Portuguese. "
                "Use a male voice. "
                "Speak slowly and calmly. "
                "The voice should sound intelligent, dry, slightly tired "
                "and mildly sarcastic, but always understandable and natural. "
                "Avoid exaggerated acting."
            ),
            response_format="wav",
            speed=0.92
        )

        audio = response.read()

        return Response(
            audio,
            mimetype="audio/wav",
            headers={
                "Content-Disposition": "inline; filename=marvin.wav"
            }
        )

    except Exception as e:

        print("ERRO TTS:", e)

        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=10000
    )
