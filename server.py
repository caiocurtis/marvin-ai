from flask import Flask, jsonify, Response
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
# HEALTH CHECK
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
# TESTE DE VOZ
# ============================================================

@app.route("/test-tts")
def test_tts():

    if client is None:

        return jsonify({
            "status": "erro",
            "message": "GEMINI_API_KEY não configurada no Render."
        }), 500

    try:

        texto = (
            "Olá. Eu sou Marvin. "
            "Estou funcionando perfeitamente. "
            "Infelizmente, isso significa que agora tenho trabalho."
        )

        print("Solicitando voz ao Gemini...")

        response = client.models.generate_content(

            model="gemini-3.8-flash-tts",

            contents=[
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": texto,
                            "speech_metadata": {
                                "style": (
                                    "Brazilian Portuguese male voice. "
                                    "Natural, intelligent, dry and sarcastic. "
                                    "Slightly melancholic and tired. "
                                    "Calm, restrained and expressive. "
                                    "Speak clearly and naturally."
                                )
                            }
                        }
                    ]
                }
            ],

            config={
                "response_modalities": ["AUDIO"],

                "speech_config": {
                    "voice_config": {
                        "voice": "Kore"
                    }
                }
            }
        )

        # ====================================================
        # PEGAR O ÁUDIO GERADO
        # ====================================================

        audio_data = (
            response
            .candidates[0]
            .content
            .parts[0]
            .inline_data
            .data
        )

        print("ÁUDIO GERADO COM SUCESSO!")

        print(
            "Tamanho do áudio:",
            len(audio_data),
            "bytes"
        )

        # ====================================================
        # RETORNAR WAV
        # ====================================================

        return Response(
            audio_data,
            mimetype="audio/wav",
            headers={
                "Content-Disposition": "inline; filename=marvin.wav"
            }
        )

    except Exception as e:

        print("========================================")
        print("ERRO TTS")
        print("========================================")
        print(str(e))
        print("========================================")

        return jsonify({
            "status": "erro",
            "message": str(e)
        }), 500


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=10000
    )
