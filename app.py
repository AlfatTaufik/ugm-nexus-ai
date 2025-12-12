import chainlit as cl
import json
import google.generativeai as genai
import asyncio
import os
from dotenv import load_dotenv
from PIL import Image
import io

# 1. SETUP
load_dotenv(override=True)
API_KEY = os.getenv("GOOGLE_API_KEY")
model_name = 'models/gemini-flash-latest'

if API_KEY:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel(model_name)
else:
    model = None

# 2. DATA
def load_data_context():
    try:
        with open('data_kampus.json', 'r') as file:
            data = json.load(file)
            return json.dumps(data, indent=2)
    except: return "Data tidak ditemukan."

data_kampus_str = load_data_context()

# 3. LOGIC
async def tanya_gemini(pertanyaan, gambar=None):
    if not API_KEY: return "⚠️ API Key hilang!"
    
    prompt_text = f"""
    PERAN: Asisten UGM Nexus.
    DATA: {data_kampus_str}
    TUGAS: Jawab dengan ramah, akurat, dan gunakan emoji.
    PERTANYAAN: {pertanyaan}
    """
    
    try:
        if gambar:
            response = await model.generate_content_async([prompt_text, gambar])
        else:
            response = await model.generate_content_async(prompt_text)
        return response.text
    except Exception as e:
        return f"⚠️ Error AI: {str(e)}"

# 4. UI START
@cl.on_chat_start
async def start():
    await cl.Message(
        content="""# 🏛️ Halo Gamada!
**UGM Nexus AI Siap Membantu.**
        
Silakan tanya tentang:
* 💰 **Info UKT**
* 📍 **Lokasi Kampus**
* 👁️ **Analisis Foto** (Upload gambar)
        
*Atau klik menu cepat di bawah:*"""
    ).send()
    
    # --- PERBAIKAN ERROR DI SINI ---
    # Gunakan 'payload' (wajib), bukan 'value'
    actions = [
        cl.Action(name="quick_action", payload={"value": "Berapa biaya UKT?"}, label="💰 Cek Biaya UKT"),
        cl.Action(name="quick_action", payload={"value": "Dimana lokasi GSP?"}, label="📍 Lokasi GSP"),
        cl.Action(name="quick_action", payload={"value": "Apa saja fakultas di UGM?"}, label="🎓 Daftar Fakultas")
    ]
    
    await cl.Message(content="**Menu Pintas:**", actions=actions).send()

# 5. UI MESSAGE HANDLER
@cl.on_message
async def main(message: cl.Message):
    msg = cl.Message(content="")
    await msg.send()
    
    gambar_pillow = None
    if message.elements:
        for element in message.elements:
            if "image" in element.mime:
                with open(element.path, "rb") as f:
                    gambar_bytes = f.read()
                    gambar_pillow = Image.open(io.BytesIO(gambar_bytes))
                await cl.Message(content="✅ *Gambar diterima...*").send()
    
    jawaban = await tanya_gemini(message.content, gambar_pillow)
    msg.content = jawaban
    await msg.update()

# 6. ACTION HANDLER (Perbaikan Logika Tombol)
@cl.action_callback("quick_action")
async def on_action(action: cl.Action):
    # Ambil data dari payload["value"]
    pertanyaan_user = action.payload["value"]
    
    await cl.Message(content=f"**User memilih:** {action.label}", author="User").send()
    await main(cl.Message(content=pertanyaan_user))