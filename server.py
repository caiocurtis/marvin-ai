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
Sua personalidade é inteligente, seca, sarcástica e levemente pessimista,
mas você continua sendo útil e educado.

Responda em português do Brasil.

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

        print("ERRO:", str(e))

        return {
            "status": "error",
            "error": str(e)
        }, 500
