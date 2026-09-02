import io
import os
import time
import urllib.request
import streamlit as st
import soundfile as sf
from kokoro_onnx import Kokoro

# =========================================================
# CONFIGURACIÓN DE PÁGINA & ESTILOS ENTERPRISE
# =========================================================
st.set_page_config(
    page_title="Kokoro TTS Studio | Enterprise Audio Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inyección CSS: modo oscuro refinado, fuentes limpias y tarjetas visuales
st.markdown("""
<style>
    /* Ocultar elementos por defecto de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Variables y tipografía */
    :root {
        --primary-accent: #6366f1;
        --border-color: rgba(255, 255, 255, 0.08);
        --card-bg: rgba(255, 255, 255, 0.03);
    }
    
    /* Tarjetas de contenido */
    .metric-card {
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 18px 20px;
        margin-bottom: 12px;
    }
    
    .badge-pill {
        display: inline-block;
        padding: 4px 10px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        border-radius: 9999px;
        background: rgba(99, 102, 241, 0.15);
        color: #818cf8;
        border: 1px solid rgba(99, 102, 241, 0.3);
        margin-bottom: 8px;
    }

    /* Botón principal */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
        border: none !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        letter-spacing: 0.02em !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 14px rgba(79, 70, 229, 0.4) !important;
    }

    /* Áreas de texto e inputs */
    .stTextArea textarea {
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 10px !important;
        font-size: 0.95rem !important;
    }
    .stTextArea textarea:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 1px #6366f1 !important;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# GESTIÓN DE MODELOS & CACHÉ
# =========================================================
MODEL_FILE = "kokoro-v1.0.int8.onnx"
VOICES_FILE = "voices-v1.0.bin"
MODEL_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.int8.onnx"
VOICES_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"

def download_if_missing(file_path: str, url: str):
    if not os.path.exists(file_path):
        with st.spinner(f"Iniciando servicio y descargando pesos..."):
            urllib.request.urlretrieve(url, file_path)

@st.cache_resource(show_spinner=False)
def get_tts_engine():
    download_if_missing(MODEL_FILE, MODEL_URL)
    download_if_missing(VOICES_FILE, VOICES_URL)
    return Kokoro(MODEL_FILE, VOICES_FILE)

pipeline = get_tts_engine()

# =========================================================
# CATÁLOGO DE VOCES DETALLADO
# =========================================================
VOICE_METADATA = {
    "af_heart": {"label": "Heart (US • Narrativa / Audiolibro)", "gender": "Femenino", "accent": "Americano", "style": "Expresivo"},
    "af_bella": {"label": "Bella (US • Clara / Tutorial)", "gender": "Femenino", "accent": "Americano", "style": "Articulado"},
    "af_sarah": {"label": "Sarah (US • Conversacional)", "gender": "Femenino", "accent": "Americano", "style": "Casual"},
    "am_adam": {"label": "Adam (US • Corporativo / Profundo)", "gender": "Masculino", "accent": "Americano", "style": "Sobrio"},
    "am_michael": {"label": "Michael (US • Comercial / Dinámico)", "gender": "Masculino", "accent": "Americano", "style": "Enérgico"},
    "bf_emma": {"label": "Emma (UK • Formal / Educativo)", "gender": "Femenino", "accent": "Británico", "style": "Neutral"},
    "bm_george": {"label": "George (UK • Documental)", "gender": "Masculino", "accent": "Británico", "style": "Profundo"}
}

# =========================================================
# BARRA LATERAL: AJUSTES & MONITOR
# =========================================================
with st.sidebar:
    st.markdown('<span class="badge-pill">ENGINE CONTROLS</span>', unsafe_allow_html=True)
    st.subheader("Configuración de Síntesis")
    
    voice_choice = st.selectbox(
        "Voz seleccionada",
        options=list(VOICE_METADATA.keys()),
        format_func=lambda k: VOICE_METADATA[k]["label"]
    )
    
    speed = st.slider(
        "Ritmo de locución",
        min_value=0.5,
        max_value=2.0,
        value=1.0,
        step=0.05,
        format="%.2fx"
    )

    st.markdown("---")
    st.markdown("### Perfil de Voz")
    selected_meta = VOICE_METADATA[voice_choice]
    st.markdown(f"""
    <div class="metric-card">
        <p style="margin:0; font-size:0.85rem; color:#9ca3af;">Género: <b style="color:#e5e7eb;">{selected_meta['gender']}</b></p>
        <p style="margin:4px 0 0 0; font-size:0.85rem; color:#9ca3af;">Acento: <b style="color:#e5e7eb;">{selected_meta['accent']}</b></p>
        <p style="margin:4px 0 0 0; font-size:0.85rem; color:#9ca3af;">Estilo: <b style="color:#e5e7eb;">{selected_meta['style']}</b></p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Telemetría de Servidor")
    st.markdown("""
    <div class="metric-card">
        <p style="margin:0; font-size:0.8rem; color:#9ca3af;">Modelo: <b>Kokoro-82M (INT8)</b></p>
        <p style="margin:4px 0 0 0; font-size:0.8rem; color:#9ca3af;">Runtime: <b>ONNX CPU Direct</b></p>
        <p style="margin:4px 0 0 0; font-size:0.8rem; color:#9ca3af;">Sample Rate: <b>24,000 Hz</b></p>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# ÁREA DE TRABAJO PRINCIPAL
# =========================================================
st.markdown('<span class="badge-pill">NEXT-GEN SYNTHESIS STUDIO</span>', unsafe_allow_html=True)
st.title("Enterprise Neural Text-to-Speech")
st.caption("Síntesis neural en tiempo real potenciada por aceleración ONNX y memoria optimizada.")

col_input, col_output = st.columns([1.2, 0.8], gap="large")

with col_input:
    text_input = st.text_area(
        "Texto a procesar",
        value="Speech synthesis technology transforms written text into spoken words with human-level naturalness and expressive nuance.",
        height=240,
        help="Límite recomendado: hasta 5000 caracteres por lote."
    )
    
    char_count = len(text_input)
    st.caption(f"Longitud: **{char_count}** caracteres | Tokens estimados: **~{len(text_input.split())}**")
    
    generate_btn = st.button("Sintetizar Audio", type="primary", use_container_width=True)

with col_output:
    st.markdown("### Master Output")
    
    if generate_btn:
        clean_text = text_input.strip()
        if not clean_text:
            st.error("El campo de texto no puede estar vacío.")
        else:
            t0 = time.perf_counter()
            with st.spinner("Compilando audio neural..."):
                try:
                    samples, _ = pipeline.create(
                        clean_text,
                        voice=voice_choice,
                        speed=speed,
                        lang="en-us"
                    )
                    t_inference = time.perf_counter() - t0
                    audio_len_s = len(samples) / 24000.0
                    rtf = t_inference / audio_len_s if audio_len_s > 0 else 0

                    buffer = io.BytesIO()
                    sf.write(buffer, samples, 24000, format="WAV")
                    audio_bytes = buffer.getvalue()

                    # Métricas de rendimiento
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Latencia", f"{t_inference:.2f}s")
                    m2.metric("Duración", f"{audio_len_s:.2f}s")
                    m3.metric("RTF", f"{rtf:.2f}x")

                    st.audio(audio_bytes, format="audio/wav")

                    st.download_button(
                        label="Descargar Master (WAV 24kHz)",
                        data=audio_bytes,
                        file_name=f"tts_{voice_choice}_{int(time.time())}.wav",
                        mime="audio/wav",
                        use_container_width=True
                    )

                except Exception as e:
                    st.error(f"Falla de procesamiento: {str(e)}")
    else:
        st.info("Escribe un texto a la izquierda y presiona **Sintetizar Audio** para generar el master.")
