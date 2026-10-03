from flask import Flask, Response
import math
import struct

app = Flask(__name__)


@app.route("/")
def home():
    return {
        "status": "online",
        "name": "Marvin"
    }


@app.route("/health")
def health():
    return {
        "status": "ok"
    }


@app.route("/test-pcm")
def test_pcm():

    # -----------------------------------------
    # CONFIGURAÇÃO DO ÁUDIO
    # -----------------------------------------

    sample_rate = 24000
    frequencia = 440
    duracao = 2

    total_amostras = sample_rate * duracao

    amplitude = 10000

    audio = bytearray()

    # -----------------------------------------
    # GERAR TOM 440 Hz
    # -----------------------------------------

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

    # -----------------------------------------
    # RETORNAR PCM PURO
    # -----------------------------------------

    return Response(
        bytes(audio),
        mimetype="application/octet-stream",
        headers={
            "Content-Type": "application/octet-stream",
            "X-Sample-Rate": str(sample_rate),
            "X-Channels": "1",
            "X-Bits": "16"
        }
    )


if __name__ == "__main__":
    app.run()
