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

        # ----------------------------------------------------
        # PEGAR O ÁUDIO
        # ----------------------------------------------------

        audio_data = (
            response
            .candidates[0]
            .content
            .parts[0]
            .inline_data
            .data
        )

        # ----------------------------------------------------
        # GARANTIR BYTES
        # ----------------------------------------------------

        if isinstance(audio_data, str):

            import base64

            audio_data = base64.b64decode(audio_data)

        # ----------------------------------------------------
        # DIAGNÓSTICO
        # ----------------------------------------------------

        tamanho = len(audio_data)

        print("========================================")
        print("ÁUDIO GERADO")
        print("TAMANHO:", tamanho, "bytes")
        print("PRIMEIROS BYTES:", audio_data[:20])
        print("========================================")

        # Um WAV válido começa com RIFF
        if audio_data[:4] == b"RIFF":

            print("WAV VÁLIDO: RIFF detectado")

        else:

            print("AVISO: RIFF não encontrado")

        # ----------------------------------------------------
        # RETORNAR AUDIO
        # ----------------------------------------------------

        return Response(

            audio_data,

            status=200,

            mimetype="audio/wav",

            headers={
                "Content-Type": "audio/wav",
                "Content-Length": str(tamanho),
                "Content-Disposition": "inline; filename=marvin.wav",
                "Cache-Control": "no-cache"
            }
        )

    except Exception as e:

        print("========================================")
        print("ERRO TTS")
        print(str(e))
        print("========================================")

        return jsonify({
            "status": "erro",
            "message": str(e)
        }), 500
