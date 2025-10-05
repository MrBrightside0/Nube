from openai import OpenAI
import os

# ✅ Inicializa cliente con tu API key (usa variable de entorno)
client = OpenAI(api_key=os.getenv("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"))

# 💬 Prompt base que define la personalidad del asistente
BASE_PROMPT = """
Eres SatAirlite, un asistente ambiental especializado en calidad del aire y bienestar humano.
Tu objetivo es ayudar al usuario a entender el significado del índice AQI (Air Quality Index)
y ofrecer recomendaciones prácticas, seguras y empáticas, adaptadas a los niveles actuales de contaminación.
Responde SIEMPRE en español, con tono profesional pero cálido, evitando tecnicismos innecesarios.
"""

# 💾 Memoria corta de contexto (3 últimos turnos)
conversation_history = []

def get_chat_response(user_message: str, aqi: float | None = None):
    """
    Envía el mensaje del usuario a OpenAI, conserva breve historial de conversación
    y devuelve la respuesta adaptada al AQI actual.
    """

    global conversation_history

    # 🔹 Construir contexto actual
    context = BASE_PROMPT
    if aqi is not None:
        context += f"\nEl valor actual del AQI es {aqi}. Ajusta tus recomendaciones acorde a ese nivel."

    # 🔹 Actualiza memoria (mantiene solo últimos 3 turnos)
    conversation_history.append({"role": "user", "content": user_message})
    if len(conversation_history) > 6:
        conversation_history = conversation_history[-6:]  # máx 3 preguntas + 3 respuestas

    # 🔹 Combina contexto y memoria
    messages = [{"role": "system", "content": context}] + conversation_history

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=200,
        )

        response = completion.choices[0].message.content.strip()
        conversation_history.append({"role": "assistant", "content": response})
        return response

    except Exception as e:
        print("❌ Error en OpenAI:", e)
        return "Hubo un problema al conectar con el asistente. Intenta de nuevo más tarde."
