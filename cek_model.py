import google.generativeai as genai
import os
from dotenv import load_dotenv

# Paksa baca file .env yang baru
load_dotenv(override=True)
API_KEY = os.getenv("GOOGLE_API_KEY")

print("🔍 SEDANG MEMERIKSA API KEY...")
print(f"🔑 Key Terbaca: {str(API_KEY)[:5]}... (Cek apakah ini key baru?)")

if not API_KEY:
    print("❌ ERROR: File .env kosong/tidak terbaca!")
else:
    genai.configure(api_key=API_KEY)
    
    print("\n📋 DAFTAR MODEL YANG TERSEDIA UNTUK ANDA:")
    print("==========================================")
    try:
        count = 0
        for m in genai.list_models():
            # Kita cari model yang bisa generate text (chat)
            if 'generateContent' in m.supported_generation_methods:
                print(f"✅ {m.name}")
                count += 1
        
        if count == 0:
            print("⚠️ Aneh, tidak ada model yang tersedia. Coba update library.")
            
    except Exception as e:
        print(f"❌ GAGAL KONEKSI: {e}")