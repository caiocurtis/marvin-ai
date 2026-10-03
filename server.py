from flask import Flask, jsonify, Response
import os
import math
import struct

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
# TESTE DE ÁUDIO
#
# Gera um WAV de 440 Hz diretamente no servidor.
# NÃO USA GEMINI.
# ============================================================

@app.route("/test-audio")
def test_audio():

    try:

        sample_rate = 24000
        duration = 2
        frequency = 440
        amplitude = 10000

        num_samples = sample_rate * duration

        audio_data = bytearray()

        for i in range(num_samples):

            sample = int(
                amplitude *
                math.sin(
                    2 * math.pi *
                    frequency *
                    i /
                    sample_rate
                )
            )

            audio_data.extend(
                struct.pack("<h", sample)
            )

        # ====================================================
        # CABEÇALHO WAV
        # ====================================================

        num_channels = 1
        bits_per_sample = 16

        byte_rate = (
            sample_rate *
            num_channels *
            bits_per_sample //
            8
        )

        block_align = (
            num_channels *
            bits_per_sample //
            8
        )

        data_size = len(audio_data)

        wav = bytearray()

        # RIFF
        wav.extend(b"RIFF")

        wav.extend(
            struct.pack(
                "<I",
                36 + data_size
            )
        )

        wav.extend(b"WAVE")

        # fmt
        wav.extend(b"fmt ")

        wav.extend(
            struct.pack(
                "<I",
                16
            )
        )

        # PCM
        wav.extend(
            struct.pack(
                "<H",
                1
            )
        )

        # Mono
        wav.extend(
            struct.pack(
                "<H",
                num_channels
            )
        )

        # Sample rate
        wav.extend(
            struct.pack(
                "<I",
                sample_rate
            )
        )

        # Byte rate
        wav.extend(
            struct.pack(
                "<I",
                byte_rate
            )
        )

        # Block align
        wav.extend(
            struct.pack(
                "<H",
                block_align
            )
        )

        # Bits
        wav.extend(
            struct.pack(
                "<H",
                bits_per_sample
            )
        )

        # Data
        wav.extend(b"data")

        wav.extend(
            struct.pack(
                "<I",
                data_size
            )
        )

        wav.extend(audio_data)

        print(
            "Áudio de teste gerado:",
            len(wav),
            "bytes"
        )

        return Response(
            bytes(wav),
            status=200,
            mimetype="audio/wav",
            headers={
                "Content-Type": "audio/wav",
                "Content-Length": str(len(wav)),
                "Content-Disposition":
                    "inline; filename=marvin-test.wav",
                "Cache-Control":
                    "no-cache"
            }
        )

    except Exception as e:

        print("ERRO TESTE AUDIO:")
        print(str(e))

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
