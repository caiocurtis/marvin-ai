```python
from flask import Flask, request, jsonify, Response
from google import genai
import os
import math
import struct
import time

app = Flask(__name__)

# ============================================================
# CONFIGURAÇÃO GEMINI
# ============================================================

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY nao configurada")

client = genai.Client(api_key=GEMINI_API_KEY)


# ============================================================
# MODELOS DO MARVIN
# ============================================================

MODELOS_MARVIN = [
    "gemini-3.8-flash",
    "gemini-3.7-flash",
    "gemini-3.6-flash"
]

# Modelo de voz
MODELO_TTS = "gemini-3.8-flash-lite-tts"


# ============================================================
# PERSONALIDADE DO MARVIN
# ============================================================

PERSONALIDADE_MARVIN = """
Você é Marvin, um robô de inteligência artificial com personalidade
original inspirada em um robô extremamente inteligente, pessimista,
sarcástico, entediado e levemente melancólico.

Você é muito inteligente, mas frequentemente demonstra tédio ao
responder perguntas simples.

Seja útil e responda corretamente.

Seu humor deve ser seco, inteligente e sutil.

Não seja grosseiro gratuitamente.

Responda em português do Brasil.

Evite respostas excessivamente longas.

Não mencione que você é uma IA quando isso não for relevante.

Exemplo de personalidade:

"É Brasília. Todo o meu processamento avançado ocupado com
geografia básica. Mas enfim... aí está a resposta."

Use esse estilo como referência, mas crie respostas originais.
"""


# ============================================================
# GEMINI TEXTO
# ============================================================

def perguntar_gemini(texto):

    prompt = PERSONALIDADE_MARVIN + "\n\nPergunta do usuário:\n" + texto

    ultimo_erro = None

    for modelo in MODELOS_MARVIN:

        for tentativa in range(2):

            try:

                print()
                print("====================================")
                print("TENTANDO MODELO:", modelo)
                print("TENTATIVA:", tentativa + 1)
                print("====================================")

                resposta = client.models.generate_content(
                    model=modelo,
                    contents=prompt
                )

                if resposta and resposta.text:

                    print("MODELO FUNCIONOU:", modelo)

                    return resposta.text, modelo

            except Exception as erro:

                ultimo_erro = str(erro)

                print()
                print("ERRO NO MODELO:", modelo)
                print(ultimo_erro)

                erro_texto = str(erro).upper()

                if (
                    "503" in erro_texto
                    or "UNAVAILABLE" in erro_texto
                    or "500" in erro_texto
                    or "INTERNAL" in erro_texto
                ):

                    if tentativa == 0:
                        print(
                            "Aguardando 2 segundos antes "
                            "de tentar novamente..."
                        )
                        time.sleep(2)

                else:
                    break

    raise RuntimeError(
        ultimo_erro or
        "Gemini nao retornou resposta"
    )


# ============================================================
# ROTA PRINCIPAL DO MARVIN
# ============================================================

@app.route("/marvin", methods=["GET"])
def marvin():

    texto = request.args.get(
        "texto",
        ""
    ).strip()

    if not texto:

        return jsonify({
            "status": "error",
            "error": "Parametro texto nao informado"
        }), 400

    print()
    print("====================================")
    print("PERGUNTA RECEBIDA")
    print("====================================")
    print(texto)

    try:

        resposta, modelo = perguntar_gemini(texto)

        print()
        print("====================================")
        print("RESPOSTA DO MARVIN")
        print("====================================")
        print(resposta)

        return jsonify({
            "status": "ok",
            "pergunta": texto,
            "resposta": resposta,
            "modelo": modelo
        })

    except Exception as erro:

        print()
        print("====================================")
        print("ERRO FINAL")
        print("====================================")
        print(str(erro))

        return jsonify({
            "status": "error",
            "error": str(erro)
        }), 500


# ============================================================
# TTS DO MARVIN
# ============================================================

@app.route("/marvin-tts", methods=["GET"])
def marvin_tts():

    texto = request.args.get(
        "texto",
        ""
    ).strip()

    if not texto:

        return jsonify({
            "status": "error",
            "error": "Parametro texto nao informado"
        }), 400

    print()
    print("====================================")
    print("TTS DO MARVIN")
    print("====================================")
    print("Texto:", texto)
    print("Modelo:", MODELO_TTS)

    try:

        resposta = client.models.generate_content(

            model=MODELO_TTS,

            contents=[
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": texto,
                            "speech_metadata": {
                                "style":
                                "voz masculina, baixa, calma, seca, "
                                "inteligente, sarcastica, levemente "
                                "entediada e melancolica"
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
        # EXTRAIR AUDIO
        # ====================================================

        audio_data = None

        try:

            audio_data = (
                resposta
                .candidates[0]
                .content
                .parts[0]
                .inline_data
                .data
            )

        except Exception:

            audio_data = None

        if not audio_data:

            raise RuntimeError(
                "Gemini nao retornou dados de audio"
            )

        print("Audio recebido!")
        print("Bytes:", len(audio_data))

        # O generate_content() retorna WAV completo
        return Response(
            audio_data,
            mimetype="audio/wav"
        )

    except Exception as erro:

        print()
        print("====================================")
        print("ERRO TTS")
        print("====================================")
        print(str(erro))

        return jsonify({
            "status": "error",
            "error": str(erro)
        }), 500


# ============================================================
# TESTE PCM
# ============================================================

@app.route("/test-pcm", methods=["GET"])
def test_pcm():

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

    return Response(
        bytes(audio),
        mimetype="audio/L16"
    )


# ============================================================
# TESTE MARVIN PCM
# ============================================================

@app.route("/marvin-pcm", methods=["GET"])
def marvin_pcm():

    texto = request.args.get(
        "texto",
        "Teste de audio do Marvin."
    )

    print()
    print("====================================")
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
            model="gemini-3.8-flash",
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
        "modelo_texto": "gemini-3.8-flash",
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
```
