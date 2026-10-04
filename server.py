from flask import Flask, Response, request, jsonify
from google import genai
import os
import base64
import io
import wave

app = Flask(__name__)

# =====================================================
# GEMINI
# =====================================================

client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY")
)


# =====================================================
# HOME
# =====================================================

@app.route("/")
def home():

    return {
        "status": "online",
        "name": "Marvin"
    }


# =====================================================
# HEALTH
# =====================================================

@app.route("/health")
def health():

    return {
        "status": "ok"
    }


# =====================================================
# TESTE GEMINI
# =====================================================

@app.route("/test-gemini")
def test_gemini():

    try:

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents="Responda apenas: Olá, eu sou Marvin."
        )

        return {
            "status": "ok",
            "response": response.text
        }

    except Exception as e:

        return {
            "status": "error",
            "error": str(e)
        }, 500


# =====================================================
# MARVIN TTS
# =====================================================

@app.route("/marvin-tts")
def marvin_tts():

    texto = request.args.get(
        "texto",
        "Olá. Eu sou Marvin. Isso provavelmente não vai terminar bem."
    )

    print()
    print("================================")
    print("MARVIN TTS")
    print("================================")
    print("Texto:", texto)

    try:

        response = client.models.generate_content(

            model="gemini-3.8-flash-tts",

            contents=texto,

            config={
                "response_modalities": ["AUDIO"],

                "speech_config": {
                    "voice_config": {
                        "prebuilt_voice_config": {
                            "voice_name": "Kore"
                        }
                    }
                }
            }
        )

        # -------------------------------------------------
        # LOCALIZAR AUDIO
        # -------------------------------------------------

        audio_data = None

        for candidate in response.candidates:

            if not candidate.content:
                continue

            for part in candidate.content.parts:

                if part.inline_data:

                    audio_data = part.inline_data.data

                    break

            if audio_data:
                break


        if audio_data is None:

            return {
                "status": "error",
                "error": "Gemini nao retornou audio."
            }, 500


        # -------------------------------------------------
        # DECODIFICAR BASE64 SE NECESSARIO
        # -------------------------------------------------

        if isinstance(audio_data, str):

            audio_data = base64.b64decode(
                audio_data
            )


        # -------------------------------------------------
        # TENTAR INTERPRETAR COMO WAV
        # -------------------------------------------------

        try:

            wav = wave.open(
                io.BytesIO(audio_data),
                "rb"
            )

            canais = wav.getnchannels()
            sample_rate = wav.getframerate()
            bits = wav.getsampwidth() * 8

            pcm = wav.readframes(
                wav.getnframes()
            )

            wav.close()

            print(
                "WAV recebido:",
                sample_rate,
                "Hz",
                canais,
                "canais",
                bits,
                "bits"
            )

        except Exception:

            # ---------------------------------------------
            # CASO JÁ SEJA PCM
            # ---------------------------------------------

            print(
                "Audio recebido como PCM bruto."
            )

            sample_rate = 24000
            canais = 1
            bits = 16

            pcm = audio_data


        # -------------------------------------------------
        # RETORNAR AUDIO
        # -------------------------------------------------

        print(
            "Bytes PCM:",
            len(pcm)
        )

        return Response(

            pcm,

            mimetype="application/octet-stream",

            headers={
                "Content-Type":
                    "application/octet-stream",

                "X-Sample-Rate":
                    str(sample_rate),

                "X-Channels":
                    str(canais),

                "X-Bits":
                    str(bits)
            }
        )


    except Exception as e:

        print(
            "ERRO TTS:",
            str(e)
        )

        return jsonify({

            "status": "error",

            "error": str(e)

        }), 500


# =====================================================
# SERVIDOR
# =====================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=10000
    )
