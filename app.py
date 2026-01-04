import chainlit as cl
import json
import google.generativeai as genai
import asyncio
import os
from dotenv import load_dotenv
from PIL import Image
import io
from pypdf import PdfReader 

# 1. SETUP
load_dotenv(override=True)
API_KEY = os.getenv("GOOGLE_API_KEY")
model_name = 'models/gemini-flash-latest'

if API_KEY:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel(model_name)
else:
    model = None
def load_data_context():
    try:
        with open('data_kampus.json', 'r') as file:
            data = json.load(file)
            return json.dumps(data, indent=2)
    except: return "Data dasar tidak ditemukan."

data_kampus_str = load_data_context()

# 3. HELPER:PDF
def extract_pdf_text(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages[:20]: 
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error membaca PDF: {str(e)}"

async def tanya_gemini(pertanyaan, gambar=None, konteks_tambahan=""):
    if not API_KEY: return "⚠️ API Key hilang!"
    
    prompt_text = f"""
    PERAN: Talky.
    
    SUMBER PENGETAHUAN:
    1. DATA KAMPUS (JSON): {data_kampus_str}
    2. DOKUMEN TAMBAHAN (PDF USER): {konteks_tambahan}
    
    TUGAS:
    Jawab pertanyaan user dengan ramah, akurat, dan gunakan emoji.
    Jika ada info dari PDF user, prioritaskan itu.
    
    PERTANYAAN USER: {pertanyaan}
    """
    
    try:
        if gambar:
            response = await model.generate_content_async([prompt_text, gambar])
        else:
            response = await model.generate_content_async(prompt_text)
        return response.text
    except Exception as e:
        return f"⚠️ Error AI: {str(e)}"

@cl.on_chat_start
async def start():
    cl.user_session.set("pdf_content", "")
    
    await cl.Message(
        content="""# 🏛️ Halo Gamada!
**Talky siap membantu kamu.**
        
Silakan tanya tentang:
* 💰 **Info UKT & Admisi**
* 📍 **Lokasi & Fasilitas Kampus**
* 👁️ **Analisis Foto** (Upload gambar gedung/soal)
* 📄 **Bedah Dokumen** (Upload PDF Panduan/Jadwal)
        
*Atau klik menu cepat di bawah:*"""
    ).send()
    
    actions = [
        cl.Action(name="quick_action", payload={"value": "Berapa biaya UKT?"}, label="💰 Cek Biaya UKT"),
        cl.Action(name="quick_action", payload={"value": "Dimana lokasi GSP?"}, label="📍 Lokasi GSP"),
        cl.Action(name="quick_action", payload={"value": "Apa saja fakultas di UGM?"}, label="🎓 Daftar Fakultas")
    ]
    
    await cl.Message(content="**Menu Pintas:**", actions=actions).send()

@cl.on_message
async def main(message: cl.Message):
    msg = cl.Message(content="")
    await msg.send()
    
    gambar_pillow = None
    pdf_text_baru = ""
    
    if message.elements:
        for element in message.elements:
            
            # KASUS 1: Jika GAMBAR
            if "image" in element.mime:
                with open(element.path, "rb") as f:
                    gambar_bytes = f.read()
                    gambar_pillow = Image.open(io.BytesIO(gambar_bytes))
                await cl.Message(content="✅ *Menerima Gambar...*").send()
            
            # KASUS 2: Jika PDF (FITUR BARU)
            elif "pdf" in element.mime:
                await cl.Message(content=f"📖 *Membaca dokumen: {element.name}...*").send()
                
                # Ekstrak teks
                text_isi = extract_pdf_text(element.path)
                pdf_text_baru += f"\n[ISI DOKUMEN {element.name}]:\n{text_isi}\n"
                
                # Simpan ke memori sesi
                current_pdf = cl.user_session.get("pdf_content")
                cl.user_session.set("pdf_content", current_pdf + pdf_text_baru)
                
                await cl.Message(content="✅ *Dokumen terbaca! Silakan tanya isinya.*").send()

    # Ambil konteks PDF dari memori
    konteks_pdf = cl.user_session.get("pdf_content")
    
    # Jawaban
    jawaban = await tanya_gemini(message.content, gambar_pillow, konteks_pdf)
    msg.content = jawaban
    await msg.update()

# 7. ACTION HANDLER
@cl.action_callback("quick_action")
async def on_action(action: cl.Action):
    pertanyaan_user = action.payload["value"]
    await cl.Message(content=f"**User memilih:** {action.label}", author="User").send()
    await main(cl.Message(content=pertanyaan_user))