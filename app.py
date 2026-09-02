import io
import os
import time
import urllib.request
import streamlit as st
import soundfile as sf
from kokoro_onnx import Kokoro

# =========================================================
# 1. CONFIGURACIÓN DEL CORE (DEBE IR PRIMERO)
# =========================================================
st.set_page_config(
    page_title="SonicReader | AI Voice Studio",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# 2. INYECCIÓN CSS NIVEL ENTERPRISE (FORZANDO LIGHT THEME)
# =========================================================
st.markdown("""
<style>
    /* Importar fuente premium (Inter) */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Reset y tipografía global */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        color: #0f172a !important;
    }

    /* Ocultar basura de Streamlit */
    #MainMenu, footer, header { visibility: hidden !important; }
    
    /* Forzar fondo claro en toda la app */
    .stApp {
        background-color: #f8fafc !important; 
    }

    /* Ajustar el contenedor principal */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 5rem !important;
        max-width: 1000px !important;
    }

    /* =======================================
       SIDEBAR (Menú lateral limpio)
       ======================================= */
    section[data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e2e8f0 !important;
    }
    /* Estilo de los botones del Sidebar (como enlaces de menú) */
    section[data-testid="stSidebar"] .stButton > button {
        background: transparent !important;
        border: none !important;
        color: #475569 !important;
        justify-content: flex-start !important;
        padding: 10px 16px !important;
        font-weight: 500 !important;
        border-radius: 8px !important;
        box-shadow: none !important;
        width: 100% !important;
        transition: all 0.2s ease !important;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: #f1f5f9 !important;
        color: #0f172a !important;
    }

    /* =======================================
       BARRA DE CONTROLES SUPERIOR
       ======================================= */
    .control-bar-container {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 12px 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        margin-bottom: 24px;
    }
    
    /* Selectores y Sliders limpios */
    div[data-testid="stSelectbox"] > div > div {
        background-color: #f8fafc !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
        color: #0f172a !important;
    }
    
    /* BOTÓN PLAY (El Hero Button) */
    div[data-testid="column"]:nth-child(4) .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
        border: none !important;
        color: #ffffff !important;
        border-radius: 50% !important;
        height: 56px !important;
        width: 56px !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 24px !important;
        box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.3) !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease !important;
        margin-top: 15px; /* Alineación visual */
    }
    div[data-testid="column"]:nth-child(4) .stButton > button:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 10px 25px -3px rgba(37, 99, 235, 0.5) !important;
    }

    /* =======================================
       EDITOR DE TEXTO (El Lienzo Principal)
       ======================================= */
    div[data-testid="stTextArea"] textarea {
        background-color: #ffffff !important;
        color: #0f172a !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 16px !important;
        padding: 24px !important;
        font-size: 1.15rem !important;
        line-height: 1.7 !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02) !important;
        height: 350px !important;
        resize: none !important;
    }
    div[data-testid="stTextArea"] textarea:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2) !important;
        outline: none !important;
    }

    /* =======================================
       CHIPS (Botones inferiores de sugerencias)
       ======================================= */
    .chip-container .stButton > button {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        color: #64748b !important;
        border-radius: 999px !important;
        font-size: 0.85rem !important;
        padding: 6px 16px !important;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05) !important;
    }
    .chip-container .stButton > button:hover {
        background: #f8fafc !important;
        border-color: #cbd5e1 !important;
        color: #0f172a !important;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 3. MOTOR TTS: DESCARGA Y CACHÉ EXTREMO (0.00s Latencia repetida)
# =========================================================
MODEL_FILE = "kokoro-v1.0.int8.onnx"
VOICES_FILE = "voices-v1.0.bin"
MODEL_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.int8.onnx"
VOICES_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"

@st.cache_resource(show_spinner="Iniciando motor neural por primera vez...")
def get_engine():
    if not os.path.exists(MODEL_FILE):
        urllib.request.urlretrieve(MODEL_URL, MODEL_FILE)
    if not os.path.exists(VOICES_FILE):
        urllib.request.urlretrieve(VOICES_URL, VOICES_FILE)
    return Kokoro(MODEL_FILE, VOICES_FILE)

pipeline = get_engine()

@st.cache_data(show_spinner=False, max_entries=50)
def synthesize(_pipeline, text: str, voice: str, speed: float) -> bytes:
    clean_text = " ".join(text.split())
    samples, _ = _pipeline.create(clean_text, voice=voice, speed=speed, lang="en-us")
    buffer = io.BytesIO()
    sf.write(buffer, samples, 24000, format="WAV")
    return buffer.getvalue()

# =========================================================
# 4. VOCES PREMIUM
# =========================================================
VOICES = {
    "af_heart":   {"name": "Heart", "tag": "American Narrative"},
    "am_adam":    {"name": "Adam", "tag": "American Professional"},
    "af_bella":   {"name": "Bella", "tag": "American Clear"},
    "am_michael": {"name": "Michael", "tag": "American Dynamic"},
    "bf_emma":    {"name": "Emma", "tag": "British Formal"},
    "bm_george":  {"name": "George", "tag": "British Deep"}
}

# =========================================================
# 5. CONSTRUCCIÓN DE LA UI (SIDEBAR)
# =========================================================
with st.sidebar:
    st.markdown("""
        <div style="display:flex; align-items:center; gap:12px; margin-bottom:30px; padding: 10px 0;">
            <div style="background: linear-gradient(135deg, #3b82f6, #2563eb); color:white; border-radius:10px; width:36px; height:36px; display:flex; align-items:center; justify-content:center; font-weight:700; font-size: 18px; box-shadow: 0 4px 6px -1px rgba(37,99,235,0.2);">S</div>
            <span style="font-size:1.25rem; font-weight:700; color:#0f172a; letter-spacing: -0.5px;">SonicReader</span>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<p style='font-size: 0.75rem; font-weight: 600; color: #94a3b8; margin-bottom: 8px; letter-spacing: 1px;'>WORKSPACE</p>", unsafe_allow_html=True)
    st.button("📝 Editor", use_container_width=True)
    st.button("📁 Documents", use_container_width=True)
    st.button("🎧 Audio Library", use_container_width=True)

    st.markdown("<br><p style='font-size: 0.75rem; font-weight: 600; color: #94a3b8; margin-bottom: 8px; letter-spacing: 1px;'>PRO FEATURES</p>", unsafe_allow_html=True)
    st.button("🎙️ Voice Cloning", use_container_width=True)
    st.button("🌐 Translation", use_container_width=True)

    st.markdown("<div style='position:absolute; bottom:20px; width:100%;'><hr style='border-color:#e2e8f0;'><p style='font-size: 0.75rem; color: #64748b;'>Engine: Kokoro-82M ONNX<br>Status: <span style='color:#10b981;'>● Online</span></p></div>", unsafe_allow_html=True)

# =========================================================
# 6. ESTADO DEL TEXTO
# =========================================================
if "input_text" not in st.session_state:
    st.session_state.input_text = "Speech synthesis has evolved. Our neural engine transforms text into incredibly lifelike audio in real-time, completely reshaping how we consume written content."

# =========================================================
# 7. MAIN APP: BARRA SUPERIOR DE CONTROLES
# =========================================================
st.markdown('<div class="control-bar-container">', unsafe_allow_html=True)
c_voice, c_speed, c_space, c_play, c_download = st.columns([2, 1.5, 0.5, 1, 1], vertical_alignment="center")

with c_voice:
    selected_voice = st.selectbox(
        "Speaker Profile",
        options=list(VOICES.keys()),
        format_func=lambda k: f"👤 {VOICES[k]['name']} ({VOICES[k]['tag']})"
    )

with c_speed:
    speed = st.select_slider(
        "Pacing (Speed)",
        options=[0.75, 0.9, 1.0, 1.1, 1.25, 1.5],
        value=1.0,
        format_func=lambda x: f"{x}x"
    )

with c_play:
    # Este botón está estilizado por CSS como el Play azul gigante
    play_pressed = st.button("▶")

st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# 8. MAIN APP: EDITOR DE TEXTO (LIENZO)
# =========================================================
text = st.text_area(
    "Editor",
    value=st.session_state.input_text,
    placeholder="Start typing or paste your document here...",
    label_visibility="collapsed"
)

# =========================================================
# 9. MAIN APP: CHIPS DE TEMPLATES
# =========================================================
st.markdown('<div class="chip-container">', unsafe_allow_html=True)
ch1, ch2, ch3, ch4 = st.columns(4)
with ch1:
    if st.button("📖 Storytelling"): 
        st.session_state.input_text = "The old clock tower chimed midnight. Rain lashed against the cobblestones as a lone figure emerged from the fog, pulling their coat tight against the bitter wind."
        st.rerun()
with ch2:
    if st.button("🎙️ Podcast Intro"): 
        st.session_state.input_text = "Welcome back to Tech Frontiers! In today's episode, we're diving deep into the world of quantized neural networks and how they're bringing AI directly to your devices."
        st.rerun()
with ch3:
    if st.button("💼 Corporate"): 
        st.session_state.input_text = "Our Q3 earnings report indicates a twenty-five percent increase in year-over-year revenue, driven primarily by our new enterprise software solutions."
        st.rerun()
with ch4:
    if st.button("⚡ Fast Benchmark"): 
        st.session_state.input_text = "This is a speed test to demonstrate sub-second audio generation capabilities using INT8 precision models."
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# 10. LÓGICA DE GENERACIÓN Y REPRODUCTOR
# =========================================================
if play_pressed:
    clean_text = text.strip()
    if not clean_text:
        st.toast("⚠️ Please enter text to synthesize.", icon="✍️")
    else:
        t0 = time.perf_counter()
        
        # Generación ultrarrápida (con caché)
        with st.spinner("Synthesizing..."):
            audio_bytes = synthesize(pipeline, clean_text, selected_voice, speed)
        
        elapsed = time.perf_counter() - t0
        
        # Notificación elegante
        st.toast(f"Audio generated in {elapsed:.2f} seconds", icon="⚡")
        
        # Reproductor nativo limpio y botón de descarga
        st.markdown("<br>", unsafe_allow_html=True)
        st.audio(audio_bytes, format="audio/wav", autoplay=True)
        
        with c_download:
            st.download_button(
                label="⬇️ Export WAV",
                data=audio_bytes,
                file_name=f"sonicreader_{selected_voice}.wav",
                mime="audio/wav",
                use_container_width=True
            )
