import io
import os
import time
import urllib.request
import streamlit as st
import soundfile as sf
from kokoro_onnx import Kokoro

# =========================================================
# CONFIGURACIÓN DE PÁGINA
# =========================================================
st.set_page_config(
    page_title="SonicReader | Studio Audio Engine",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# ESTILOS ENTERPRISE (TIPO NATURALREADER)
# =========================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    #MainMenu, footer, header { visibility: hidden !important; }
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 3rem !important;
        max-width: 1200px !important;
    }

    /* Fondo de la app */
    .stApp {
        background-color: #f7f9fb;
    }

    /* Sidebar refinada */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #eef0f3;
    }

    /* Tarjeta tipo Lienzo / Documento */
    .editor-canvas {
        background: #ffffff;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04), 0 1px 3px rgba(0, 0, 0, 0.02);
        border: 1px solid #e9ecef;
        padding: 30px;
        margin-top: 10px;
    }

    /* Barra Superior de Control */
    .control-bar {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 18px;
        padding: 8px 24px;
        background: #ffffff;
        border-radius: 9999px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        border: 1px solid #eef0f3;
        margin-bottom: 20px;
    }

    /* Botón Play Azul Circular */
    .stButton > button[kind="primary"] {
        background: #0066ff !important;
        border: none !important;
        color: #ffffff !important;
        border-radius: 9999px !important;
        height: 52px !important;
        width: 52px !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 22px !important;
        box-shadow: 0 4px 14px rgba(0, 102, 255, 0.35) !important;
        transition: all 0.15s ease-in-out !important;
        margin: auto;
    }
    .stButton > button[kind="primary"]:hover {
        transform: scale(1.05);
        background: #0052cc !important;
        box-shadow: 0 6px 20px rgba(0, 102, 255, 0.45) !important;
    }

    /* Botones de Chips / Sugerencias */
    .stButton > button[kind="secondary"] {
        background: #ffffff !important;
        color: #495057 !important;
        border: 1px solid #e3e6eb !important;
        border-radius: 9999px !important;
        padding: 6px 16px !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button[kind="secondary"]:hover {
        background: #f1f3f5 !important;
        border-color: #ced4da !important;
        color: #212529 !important;
    }

    /* Editor de texto sin bordes agresivos */
    .stTextArea textarea {
        border: none !important;
        background-color: transparent !important;
        font-size: 1.12rem !important;
        line-height: 1.7 !important;
        color: #2b2f38 !important;
        box-shadow: none !important;
        resize: vertical !important;
    }
    .stTextArea textarea:focus {
        outline: none !important;
        box-shadow: none !important;
    }

    /* Banner inferior */
    .bottom-status-bar {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: #2b303a;
        color: #e9ecef;
        padding: 10px 24px;
        font-size: 0.82rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        z-index: 1000;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# MODELOS Y CACHÉ ULTRA RÁPIDO
# =========================================================
MODEL_FILE = "kokoro-v1.0.int8.onnx"
VOICES_FILE = "voices-v1.0.bin"
MODEL_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.int8.onnx"
VOICES_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"

def download_if_missing(file_path: str, url: str):
    if not os.path.exists(file_path):
        urllib.request.urlretrieve(url, file_path)

@st.cache_resource(show_spinner=False)
def get_tts_pipeline():
    download_if_missing(MODEL_FILE, MODEL_URL)
    download_if_missing(VOICES_FILE, VOICES_URL)
    return Kokoro(MODEL_FILE, VOICES_FILE)

pipeline = get_tts_pipeline()

# Caché de inferencia para velocidad instantánea en textos repetidos
@st.cache_data(show_spinner=False, max_entries=100)
def synthesize_audio_fast(_pipeline, text: str, voice: str, speed: float) -> bytes:
    clean_text = " ".join(text.split())
    samples, _ = _pipeline.create(clean_text, voice=voice, speed=speed, lang="en-us")
    
    buffer = io.BytesIO()
    sf.write(buffer, samples, 24000, format="WAV")
    return buffer.getvalue()

# =========================================================
# CATÁLOGO DE VOCES CON AVATARES
# =========================================================
VOICES = {
    "am_adam": {
        "name": "Adam",
        "desc": "American • Professional",
        "avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&h=100&fit=crop&crop=faces"
    },
    "af_heart": {
        "name": "Heart",
        "desc": "American • Expressive Narrative",
        "avatar": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=100&h=100&fit=crop&crop=faces"
    },
    "af_bella": {
        "name": "Bella",
        "desc": "American • Educational",
        "avatar": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100&h=100&fit=crop&crop=faces"
    },
    "am_michael": {
        "name": "Michael",
        "desc": "American • Conversational",
        "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop&crop=faces"
    },
    "bf_emma": {
        "name": "Emma",
        "desc": "British • Neutral Formal",
        "avatar": "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=100&h=100&fit=crop&crop=faces"
    },
    "bm_george": {
        "name": "George",
        "desc": "British • Deep Narration",
        "avatar": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=100&h=100&fit=crop&crop=faces"
    }
}

# =========================================================
# BARRA LATERAL (ESTILO NATURALREADER)
# =========================================================
with st.sidebar:
    st.markdown("""
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:20px;">
            <div style="background:#0066ff; color:white; border-radius:8px; width:30px; height:30px; display:flex; align-items:center; justify-content:center; font-weight:700;">N</div>
            <span style="font-size:1.15rem; font-weight:700; color:#1e293b;">SonicReader</span>
        </div>
    """, unsafe_allow_html=True)

    st.caption("DOCUMENT")
    st.button("📝 Add Text", use_container_width=True, kind="secondary")
    st.button("📁 Upload Document", use_container_width=True, kind="secondary")
    st.button("📚 Library", use_container_width=True, kind="secondary")

    st.markdown("<br>", unsafe_allow_html=True)
    st.caption("FEATURES")
    st.button("🎙️ Voice Cloning", use_container_width=True, kind="secondary")
    st.button("🎧 AI Audio Studio", use_container_width=True, kind="secondary")

    st.markdown("<br><hr style='border:none; border-top:1px solid #f1f3f5;'><br>", unsafe_allow_html=True)
    st.caption("SYSTEM SPECS")
    st.markdown("""
        <div style="font-size:0.8rem; color:#64748b; line-height:1.6;">
            • Engine: <b>Kokoro 82M INT8</b><br>
            • Latency: <b>Realtime ONNX</b><br>
            • Quality: <b>24 kHz Hi-Fi</b>
        </div>
    """, unsafe_allow_html=True)

# =========================================================
# GESTIÓN DE TEXTO DE ENTRADA
# =========================================================
if "input_text" not in st.session_state:
    st.session_state.input_text = "Natural voice synthesis converts complex text into lifelike speech with real-time speed."

# =========================================================
# BARRA SUPERIOR DE CONTROLES (FLOATING PLAYER BAR)
# =========================================================
c_avatar, c_voice, c_speed, c_play, c_download = st.columns([0.8, 2.2, 1.5, 1, 1.5], vertical_alignment="center")

with c_voice:
    selected_voice_key = st.selectbox(
        "Voice",
        options=list(VOICES.keys()),
        format_func=lambda k: f"{VOICES[k]['name']} ({VOICES[k]['desc'].split('•')[0].strip()})",
        label_visibility="collapsed"
    )

with c_avatar:
    avatar_url = VOICES[selected_voice_key]["avatar"]
    st.markdown(f"""
        <div style="display:flex; justify-content:center; align-items:center;">
            <img src="{avatar_url}" style="width:46px; height:46px; border-radius:50%; object-fit:cover; border:2px solid #0066ff; box-shadow:0 2px 8px rgba(0,0,0,0.08);">
        </div>
    """, unsafe_allow_html=True)

with c_speed:
    speed = st.select_slider(
        "Speed",
        options=[0.75, 1.0, 1.25, 1.5, 2.0],
        value=1.0,
        format_func=lambda x: f"{x}x",
        label_visibility="collapsed"
    )

with c_play:
    # Botón play circular azul
    play_pressed = st.button("▶", type="primary", help="Synthesize & Play")

# =========================================================
# LIENZO / CARD DE EDICIÓN
# =========================================================
st.markdown('<div class="editor-canvas">', unsafe_allow_html=True)

text = st.text_area(
    "Content Editor",
    value=st.session_state.input_text,
    placeholder="Type, paste or edit text here...",
    height=280,
    label_visibility="collapsed"
)

# Sugerencias / Chips inferiores como la referencia
st.markdown("<div style='margin-top:20px; display:flex; gap:10px; flex-wrap:wrap;'>", unsafe_allow_html=True)
p1, p2, p3, p4 = st.columns(4)

with p1:
    if st.button("📖 Read a short story", use_container_width=True, kind="secondary"):
        st.session_state.input_text = "The old lighthouse stood firmly against the crashing waves, guiding ships safely through the storm."
        st.rerun()
with p2:
    if st.button("🎙️ Listen to a Podcast", use_container_width=True, kind="secondary"):
        st.session_state.input_text = "Welcome back to the Tech Frontiers podcast. Today we are diving into quantized on-device neural models."
        st.rerun()
with p3:
    if st.button("🌐 Global Accents", use_container_width=True, kind="secondary"):
        st.session_state.input_text = "Good afternoon! Kokoro supports both American and British standard accents natively."
        st.rerun()
with p4:
    if st.button("⚡ Speed Benchmark", use_container_width=True, kind="secondary"):
        st.session_state.input_text = "Ultra-fast INT8 ONNX models execute speech synthesis at sub-second latencies on standard modern CPUs."
        st.rerun()

st.markdown("</div></div>", unsafe_allow_html=True)

# =========================================================
# LÓGICA DE PROCESAMIENTO Y REPRODUCCIÓN
# =========================================================
if play_pressed:
    clean_text = text.strip()
    if not clean_text:
        st.toast("⚠️ Please enter some text before generating audio.")
    else:
        t0 = time.perf_counter()
        with st.spinner(""):
            audio_bytes = synthesize_audio_fast(pipeline, clean_text, selected_voice_key, speed)
            elapsed = time.perf_counter() - t0

        st.markdown("<br>", unsafe_allow_html=True)
        st.audio(audio_bytes, format="audio/wav", autoplay=True)

        with c_download:
            st.download_button(
                label="⬇ WAV",
                data=audio_bytes,
                file_name=f"speech_{selected_voice_key}.wav",
                mime="audio/wav",
                use_container_width=True
            )

        st.toast(f"Generated in {elapsed:.2f}s", icon="⚡")

# =========================================================
# BANNER INFERIOR DE ESTADO
# =========================================================
st.markdown("""
<div class="bottom-status-bar">
    <span><b>SonicReader Engine</b>: INT8 ONNX Quantized Speech Synthesis</span>
    <span style="color:#94a3b8;">Status: <b>Active & Ready</b></span>
</div>
""", unsafe_allow_html=True)
