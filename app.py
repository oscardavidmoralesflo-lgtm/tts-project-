import io
import os
import time
import urllib.request
import streamlit as st
import soundfile as sf
from kokoro_onnx import Kokoro

# =========================================================
# CONFIGURACIÓN DEL CORE
# =========================================================
st.set_page_config(
    page_title="SonicReader | Neural Audio",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Limpieza básica de la UI de Streamlit (sin romper el DOM)
st.markdown("""
<style>
    #MainMenu, header, footer {visibility: hidden !important;}
    .block-container {padding-top: 2rem !important; padding-bottom: 2rem !important; max-width: 1050px !important;}
    
    /* Pequeño ajuste para que el reproductor de audio se integre mejor */
    audio {
        width: 100%;
        border-radius: 8px;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# MOTOR TTS Y CACHÉ ULTRA RÁPIDO
# =========================================================
MODEL_FILE = "kokoro-v1.0.int8.onnx"
VOICES_FILE = "voices-v1.0.bin"
MODEL_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.int8.onnx"
VOICES_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"

@st.cache_resource(show_spinner="Initializing neural engine (INT8)...")
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
    return buffer.getvalue(), len(samples) / 24000.0  # Retorna audio y duración

# =========================================================
# CATÁLOGO DE VOCES
# =========================================================
VOICES = {
    "af_heart":   {"name": "Heart", "desc": "American • Narrative", "icon": "🎙️"},
    "af_bella":   {"name": "Bella", "desc": "American • Clear", "icon": "👩"},
    "am_adam":    {"name": "Adam", "desc": "American • Deep", "icon": "👨"},
    "am_michael": {"name": "Michael", "desc": "American • Dynamic", "icon": "👨‍💼"},
    "bf_emma":    {"name": "Emma", "desc": "British • Formal", "icon": "👑"},
    "bm_george":  {"name": "George", "desc": "British • Documentary", "icon": "🎩"}
}

# =========================================================
# ESTADO DE LA SESIÓN
# =========================================================
if "text_input" not in st.session_state:
    st.session_state.text_input = "Speech synthesis has evolved. Our neural engine transforms text into incredibly lifelike audio in real-time, completely reshaping how we interact with digital content."

# =========================================================
# UI: SIDEBAR (CONTROLES)
# =========================================================
with st.sidebar:
    st.markdown("### ⚡ SonicReader Pro")
    st.caption("Enterprise Audio Studio")
    
    st.divider()
    
    st.markdown("#### Voice Settings")
    selected_voice = st.selectbox(
        "Speaker",
        options=list(VOICES.keys()),
        format_func=lambda k: f"{VOICES[k]['icon']} {VOICES[k]['name']} ({VOICES[k]['desc']})",
        label_visibility="collapsed"
    )
    
    speed = st.slider(
        "Pacing (Speed)",
        min_value=0.75,
        max_value=1.5,
        value=1.0,
        step=0.05,
        format="%.2fx"
    )
    
    st.divider()
    
    st.markdown("#### Engine Status")
    st.markdown(
        """
        <div style='font-size: 0.85rem; color: #a1a1aa; line-height: 1.6;'>
            <span style='color:#10b981;'>●</span> Model: <b>Kokoro 82M</b><br>
            <span style='color:#10b981;'>●</span> Precision: <b>INT8 Quantized</b><br>
            <span style='color:#10b981;'>●</span> Sample Rate: <b>24,000 Hz</b>
        </div>
        """, 
        unsafe_allow_html=True
    )

# =========================================================
# UI: ÁREA PRINCIPAL (STUDIO)
# =========================================================
st.title("Neural Synthesis Studio")
st.markdown("Transform written text into broadcast-quality speech instantly.")

# Contenedor del Editor (Nativo de Streamlit, perfecto para Dark Mode)
with st.container(border=True):
    # Botones de sugerencias como "Pestañas"
    col_t1, col_t2, col_t3, col_t4 = st.columns(4)
    with col_t1:
        if st.button("📖 Story", use_container_width=True): st.session_state.text_input = "The neon lights flickered in the rain-soaked streets of Neo-Kyoto. He pulled his collar up, knowing they were already tracking his signal."
    with col_t2:
        if st.button("🎙️ Podcast", use_container_width=True): st.session_state.text_input = "Welcome to the Daily Tech Rundown. Today we're discussing the latest breakthroughs in local machine learning models."
    with col_t3:
        if st.button("💼 Corporate", use_container_width=True): st.session_state.text_input = "Our primary objective for Q3 is to streamline deployment pipelines and enhance our cloud infrastructure."
    with col_t4:
        if st.button("🧹 Clear", use_container_width=True): st.session_state.text_input = ""

    text = st.text_area(
        "Script Editor",
        value=st.session_state.text_input,
        height=250,
        placeholder="Type or paste your script here...",
        label_visibility="collapsed"
    )
    
    char_count = len(text)
    st.caption(f"Length: {char_count} characters")

# Fila de Acción (Botón y reproductor)
action_col1, action_col2 = st.columns([1, 2], vertical_alignment="center")

with action_col1:
    generate_btn = st.button("Generate Audio", type="primary", use_container_width=True)

with action_col2:
    if generate_btn:
        if not text.strip():
            st.warning("Please enter some text to synthesize.")
        else:
            t0 = time.perf_counter()
            with st.spinner("Compiling neural audio..."):
                try:
                    audio_bytes, duration = synthesize(pipeline, text, selected_voice, speed)
                    elapsed = time.perf_counter() - t0
                    rtf = elapsed / duration if duration > 0 else 0
                    
                    st.audio(audio_bytes, format="audio/wav", autoplay=True)
                    
                    # Mostrar métricas de rendimiento en la misma fila
                    st.success(f"⚡ Ready in {elapsed:.2f}s | RTF: {rtf:.2f}x")
                    
                    st.download_button(
                        label="Download WAV",
                        data=audio_bytes,
                        file_name=f"sonicreader_{selected_voice}_{int(time.time())}.wav",
                        mime="audio/wav"
                    )
                except Exception as e:
                    st.error(f"Synthesis failed: {str(e)}")
