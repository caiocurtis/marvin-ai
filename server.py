    print("MARVIN PCM")
    print("====================================")
    print("Texto recebido:", texto)

    sample_rate = 24000
    duracao = 2
    frequencia = 440

    audio = bytearray()

    total_amostras = (
        sample_rate *
        duracao
    )

    for i in range(total_amostras):

        valor = int(
            12000 *
            math.sin(
                2 *
                math.pi *
                frequencia *
                i /
                sample_rate
            )
        )

        audio.extend(
            struct.pack(
                "<h",
                valor
            )
        )

    resposta = Response(
        bytes(audio),
        mimetype="audio/L16"
    )

    resposta.headers[
        "X-Marvin-Text"
    ] = texto

    return resposta


# ============================================================
# TESTE GEMINI
# ============================================================

@app.route("/test-gemini", methods=["GET"])
def test_gemini():

    try:

        resposta = client.models.generate_content(
            model=MODELOS_MARVIN[0],
            contents=(
                "Responda apenas: "
                "Olá, eu sou Marvin."
            )
        )

        return jsonify({
            "status": "ok",
            "response": resposta.text
        })

    except Exception as erro:

        return jsonify({
            "status": "error",
            "error": str(erro)
        }), 500


# ============================================================
# HOME
# ============================================================

@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "status": "online",
        "servidor": "Marvin AI",
        "modelo_texto": MODELOS_MARVIN[0],
        "modelo_tts": MODELO_TTS
    })


# ============================================================
# INICIALIZAÇÃO
# ============================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=int(
            os.environ.get(
                "PORT",
                10000
            )
        )
    )
