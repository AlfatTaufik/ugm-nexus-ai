import streamlit as st
import json
import requests
from streamlit_lottie import st_lottie
from thefuzz import process, fuzz
import time

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="UGM AI Nexus", page_icon="🧬", layout="wide", initial_sidebar_state="collapsed")

# --- FUNGSI LOAD LOTTIE (ANIMASI) ---
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200: return None
    return r.json()

# --- 1. SETUP & CONFIG ---
st.set_page_config(
    page_title="UGM AI Next-Gen",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed" # Sidebar disembunyikan agar lebih clean
)

# --- 2. THE DESIGNER'S CSS (ADVANCED) ---
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap" rel="stylesheet">
<style>
    /* --- ANIMASI --- */
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    @keyframes slideInUp {
        from { transform: translateY(20px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }

    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(0, 255, 136, 0.4); }
        70% { box-shadow: 0 0 0 10px rgba(0, 255, 136, 0); }
        100% { box-shadow: 0 0 0 0 rgba(0, 255, 136, 0); }
    }

            
    div.stButton > button {
    height: 100%;
    padding-top: 20px;
    padding-bottom: 25px;
}
            
    /* --- GLOBAL SETTINGS --- */
    :root {
        --glass: rgba(255, 255, 255, 0.05);
        --glass-border: rgba(255, 255, 255, 0.1);
        --neon: #00ffa3;
        --primary-gradient: linear-gradient(135deg, #00ffa3 0%, #00d2ff 100%);
    }

    [data-testid="stAppViewContainer"] {
        background: linear-gradient(-45deg, #0f0c29, #302b63, #24243e);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        font-family: 'Poppins', sans-serif;
    }
    
    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stSidebar"] { 
        background-color: rgba(15, 12, 41, 0.95); 
        border-right: 1px solid var(--glass-border);
    }

    /* --- HEADER TITLE --- */
    .hero-title {
        font-size: 3rem;
        font-weight: 700;
        background: var(--primary-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-top: 40px;
        letter-spacing: -1px;
    }
    .hero-subtitle {
        color: rgba(255,255,255,0.7);
        text-align: center;
        font-weight: 300;
        margin-bottom: 50px;
    }

    /* --- CHAT AREA --- */
    .chat-container {
        max-width: 800px;
        margin: 0 auto 100px auto;
        padding: 20px;
    }

    .bubble-row {
        display: flex;
        margin-bottom: 25px;
        animation: slideInUp 0.4s ease-out forwards; /* Efek muncul dari bawah */
    }

    /* --- USER BUBBLE (GLASS + NEON) --- */
    .row-user { justify-content: flex-end; }
    .bubble-user {
        background: rgba(0, 255, 163, 0.15); /* Hijau Transparan */
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 255, 163, 0.3);
        color: white;
        padding: 15px 25px;
        border-radius: 25px 25px 5px 25px;
        max-width: 70%;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    }
    .avatar-user {
        width: 45px; height: 45px;
        background: var(--primary-gradient);
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        margin-left: 15px;
        box-shadow: 0 0 15px rgba(0, 255, 163, 0.5);
        font-size: 20px;
    }

    /* --- BOT BUBBLE (FROSTED GLASS) --- */
    .row-bot { justify-content: flex-start; }
    .bubble-bot {
        background: var(--glass);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid var(--glass-border);
        color: #e0e0e0;
        padding: 15px 25px;
        border-radius: 25px 25px 25px 5px;
        max-width: 70%;
        line-height: 1.6;
    }
    .avatar-bot {
        width: 45px; height: 45px;
        background: rgba(255,255,255,0.1);
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        margin-right: 15px;
        font-size: 22px;
    }

    /* --- FLOATING INPUT BAR --- */
    .stTextInput {
        position: fixed;
        bottom: 40px;
        left: 50%;
        transform: translateX(-50%);
        width: 50%;
        min-width: 320px;
        z-index: 999;
    }
    
    .stTextInput > div > div > input {
        background: rgba(15, 12, 41, 0.8) !important;
        backdrop-filter: blur(15px);
        color: white !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 50px !important;
        padding: 15px 25px !important;
        font-size: 16px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.5);
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--neon) !important;
        box-shadow: 0 0 20px rgba(0, 255, 163, 0.3), 0 10px 40px rgba(0,0,0,0.5);
        transform: scale(1.02);
    }
    
    /* HIDE FOOTER */
    footer {display: none;}
    .stDeployButton {display:none;}
    
</style>
""", unsafe_allow_html=True)

# --- 3. LOGIC ---
@st.cache_data
def load_data():
    try:
        with open('data_kampus.json', 'r') as file: return json.load(file)
    except: return {}

def cari_jawaban(pertanyaan, data):
    if not data: return "⚠️ Error: Database 404."
    hasil = process.extractOne(pertanyaan, list(data.keys()), scorer=fuzz.token_set_ratio)
    if hasil and hasil[1] > 60: return data[hasil[0]]
    return "Maaf, data tidak ditemukan di memori saya. Coba kata kunci yang lebih spesifik."

# --- 4. MAIN INTERFACE ---
def main():
    # Sidebar Minimalis
    with st.sidebar:
        st.header("⚙️ Control Hub")
        if st.button("Reset Memory", type="primary"):
            st.session_state.messages = []
            st.rerun()
        st.info("System v4.0 - Glassmorphism UI")

    # Hero Section (Hanya muncul jika chat kosong)
    if "messages" not in st.session_state: st.session_state.messages = []
    
    if not st.session_state.messages:
        st.markdown('<h1 class="hero-title">UGM AI Nexus</h1>', unsafe_allow_html=True)
        st.markdown('<p class="hero-subtitle">Artificial Intelligence Assistant for Gadjah Mada University</p>', unsafe_allow_html=True)
        
        # Tombol Suggestion Transparan
        col1, col2, col3 = st.columns([1,1,1])
        with col2:
             st.markdown("""
             <div style="display:flex; justify-content:center; gap:10px; opacity:0.6;">
                <small>Try: 'Biaya UKT'</small>
                <small>•</small>
                <small>Try: 'Lokasi GSP'</small>
             </div>
             """, unsafe_allow_html=True)

    # Render Chat History
    data_pengetahuan = load_data()
    chat_html = '<div class="chat-container">'
    
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            chat_html += f"""
            <div class="bubble-row row-user">
                <div class="bubble-user">{msg['content']}</div>
                <div class="avatar-user">👤</div>
            </div>
            """
        else:
            chat_html += f"""
            <div class="bubble-row row-bot">
                <div class="avatar-bot">🧬</div>
                <div class="bubble-bot">{msg['content']}</div>
            </div>
            """
            
    chat_html += '</div>'
    st.markdown(chat_html, unsafe_allow_html=True)

    # Input Logic with "Thinking" simulation
    st.markdown("<br><br>", unsafe_allow_html=True) # Spacer
    
    if prompt := st.chat_input("Ask me anything..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Simulasi "Bot is typing..." (UX Trick)
        with st.spinner('Processing...'):
            time.sleep(0.4) # Delay buatan agar terasa natural
            jawaban = cari_jawaban(prompt, data_pengetahuan)
            
        st.session_state.messages.append({"role": "assistant", "content": jawaban})
        st.rerun()

if __name__ == "__main__":
    main()