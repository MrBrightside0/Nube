import os
from openai import OpenAI
from dotenv import load_dotenv

print("🚀 Iniciando diagnóstico de conexión con OpenAI...\n")

# 1️⃣ Cargar variables desde .env
if not load_dotenv():
    print("⚠️ No se encontró archivo .env o no se pudo cargar.")
else:
    print("✅ Archivo .env cargado correctamente.")

# 2️⃣ Verificar que la API key esté presente
api_key = "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"

if not api_key:
    print("❌ No se encontró la variable OPENAI_API_KEY en el entorno.")
    print("👉 Asegúrate de tener un archivo .env en la carpeta backend con:")
    print("   OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\n")
    exit()
else:
    print(f"✅ API Key detectada: {api_key[:10]}... (ocultando el resto por seguridad)")

# 3️⃣ Crear cliente
try:
    client = OpenAI(api_key=api_key)
    print("✅ Cliente OpenAI inicializado correctamente.")
except Exception as e:
    print(f"❌ Error al inicializar cliente OpenAI: {e}")
    exit()

# 4️⃣ Probar una solicitud simple
try:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Hola, ¿puedes confirmar que estás funcionando?"}],
        max_tokens=50,
    )
    print("\n✅ Solicitud exitosa.")
    print("🧠 Respuesta del modelo:")
    print("────────────────────────────────────────────")
    print(response.choices[0].message.content.strip())
    print("────────────────────────────────────────────")
except Exception as e:
    print(f"\n❌ Error al conectar con OpenAI:")
    print(e)
    print("\n👉 Revisa tu conexión a internet, la API key o el límite de créditos.")
