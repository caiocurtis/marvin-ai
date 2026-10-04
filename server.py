from flask import Flask, Response, request
import math
import struct

app = Flask(__name__)


# =====================================================
# MARVIN
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
# TESTE PCM
# =====================================================

@app.route("/test-pcm")
def test_pcm():

    sample_rate = 24000
    frequencia = 440
    duracao = 2

    total_amostras = sample_rate * duracao

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

        audio += struct.pack("<h", valor)

    return Response(
        bytes(audio),
        mimetype="application/octet-stream"
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

    print("Texto recebido:", texto)

    # -------------------------------------------------
    # POR ENQUANTO, TESTE COM TOM
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
            "X-Sample-Rate": "24000",
            "X-Channels": "1",
            "X-Bits": "16",
            "X-Marvin-Text": texto
        }
    )


# =====================================================
# SERVIDOR
# =====================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=10000
    )
