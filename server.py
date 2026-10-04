from flask import Flask, Response, request, jsonify
from google import genai
import os
import math
import struct
import base64
import io
import wave


# =====================================================
# FLASK
# =====================================================

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
# TESTE PCM
# =====================================================

@app.route("/test-pcm")
def test_pcm():

    sample_rate = 24000
    frequencia = 440
    duracao = 2

    total_amostras = (
        sample_rate * duracao
    )

    amplitude = 10000

    audio = bytearray()

    for i in range(total_amostras):

        valor = int(
            amplitude *
            math.sin(
                2 * math.pi *
                frequencia *
                i /
                sample_rate
            )
        )

        audio += struct.pack(
            "<h",
            valor
        )

    return Response(

        bytes(audio),

        mimetype="application/octet-stream",

        headers={
            "Content-Type":
                "application/octet-stream",

            "X-Sample-Rate":
                "24000",

            "X-Channels":
                "1",

            "X-Bits":
                "16"
        }
    )


# =====================================================
# MARVIN PCM
# =====================================================

@app.route("/marvin-pcm")
def marvin_pcm():

    texto = request.args.get(
        "texto",
        "Olá. Eu sou Marvin."
    )

    print()
    print("==============================")
    print("MARVIN PCM")
    print("==============================")
    print("Texto recebido:", texto)

    # -------------------------------------------------
    # POR ENQUANTO: TOM DE TESTE
    # -------------------------------------------------

    sample_rate = 24000

    frequencia = 440

    duracao = 2

    total_amostras = (
        sample_rate * duracao
    )

    amplitude = 10000

    audio = bytearray()

    for i in range(total_amostras):

        valor = int(
            amplitude *
            math.sin(
                2 * math.pi *
                frequencia *
                i /
                sample_rate
            )
        )

        audio += struct.pack(
            "<h",
            valor
        )

    return Response(

        bytes(audio),

        mimetype="application/octet-stream",

        headers={
            "Content-Type":
                "application/octet-stream",

            "X-Sample-Rate":
                "24000",

            "X-Channels":
                "1",

            "X-Bits":
                "16",

            "X-Marvin-Text":
                texto
        }
    )


# =====================================================
# CÉREBRO DO MARVIN
# =====================================================

@app.route("/marvin")
def marvin():

    texto = request.args.get(
        "texto",
        "Olá, Marvin."
    )

    print()
    print("==============================")
    print("MARVIN")
    print("==============================")
    print("Pergunta:", texto)

    try:

        response = client.models.generate_content(

            model="gemini-3.8-flash",

            contents=f"""
Você é Marvin, um pequeno robô assistente.

Sua personalidade é:
- inteligente
- seca
- sarcástica
- levemente pessimista
- ocasionalmente entediada
- mas sempre útil

Responda em português do Brasil.

Seja relativamente conciso, especialmente quando a pergunta for simples.

Não diga que você é um personagem de nenhuma obra existente.

Usuário:
{texto}

Marvin:
"""
        )

        resposta = response.text

        print("Resposta:", resposta)

        return {

            "status": "ok",

            "pergunta": texto,

            "resposta": resposta
        }

    except Exception as e:

        print(
            "ERRO GEMINI:",
            str(e)
        )

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
    print("==============================")
    print("MARVIN TTS")
    print("==============================")
    print("Texto:", texto)

    try:

        response = client.models.generate_content(

            model="gemini-3.8-flash-tts",

            contents=texto,

            config={

                "response_modalities": [
                    "AUDIO"
                ],

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
        # PROCURAR AUDIO
        # -------------------------------------------------

        audio_data = None

        for candidate in response.candidates:

            if not candidate.content:
                continue

            for part in candidate.content.parts:

                if part.inline_data:

                    audio_data = (
                        part.inline_data.data
                    )

                    break

            if audio_data:

                break


        if audio_data is None:

            return {

                "status": "error",

                "error":
                    "Gemini não retornou áudio."

            }, 500


        # -------------------------------------------------
        # BASE64
        # -------------------------------------------------

        if isinstance(
            audio_data,
            str
        ):

            audio_data = base64.b64decode(
                audio_data
            )


        # -------------------------------------------------
        # TENTAR LER WAV
        # -------------------------------------------------

        try:

            wav = wave.open(
                io.BytesIO(audio_data),
                "rb"
            )

            canais = wav.getnchannels()

            sample_rate = wav.getframerate()

            bits = (
                wav.getsampwidth() *
                8
            )

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

            print(
                "Áudio recebido como PCM bruto."
            )

            sample_rate = 24000

            canais = 1

            bits = 16

            pcm = audio_data


        # -------------------------------------------------
        # RETORNAR PCM
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

            "status":
                "error",

            "error":
                str(e)

        }), 500


# =====================================================
# SERVIDOR
# =====================================================

if __name__ == "__main__":

    app.run(

        host="0.0.0.0",

        port=10000
    )
