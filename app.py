import io
import os
import urllib.request
import streamlit as st
import soundfile as sf
from kokoro_onnx import Kokoro

# =========================================================
# DESCARGA AUTOMÁTICA DE PESOS (Evita problemas con GitHub)
# =========================================================
MODEL_FILE = "kokoro-v1.0.int8.onnx"
VOICES_FILE = "voices-v1.0.bin"

MODEL_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.int8.onnx"
VOICES_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"

def download_if_missing(file_path: str, url: str):
    if not os.path.exists(file_path):
        with st.spinner(f"Descargando {file_path}... (solo la primera vez)"):
            urllib.request.urlretrieve(url, file_path)

# =========================================================
# INICIALIZACIÓN CON CACHÉ DE STREAMLIT
# =========================================================
@st.cache_resource
def load_pipeline():
    download_if_missing(MODEL_FILE, MODEL_URL)
    download_if_missing(VOICES_FILE, VOICES_URL)
    return Kokoro(MODEL_FILE, VOICES_FILE)

# =========================================================
# INTERFAZ DE USUARIO
# =========================================================
st.set_page_config(page_title="Kokoro-82M TTS", page_icon="🎙️", layout="centered")

st.title("🎙️ Generador TTS con Kokoro-82M")
st.write("Genera voz natural a partir de texto en pocos segundos.")

pipeline = load_pipeline()

AVAILABLE_VOICES = [
    "af_heart",
    "af_bella",
    "af_sarah",
    "am_adam",
    "am_michael",
    "bf_emma",
    "bm_george"
]

col1, col2 = st.columns(2)
with col1:
    voice = st.selectbox("Selecciona la voz:", AVAILABLE_VOICES, index=0)
with col2:
    speed = st.slider("Velocidad de reproducción:", min_value=0.5, max_value=2.0, value=1.0, step=0.1)

text = st.text_area(
    "Texto a sintetizar:",
    value="Hello, this is a test using the Kokoro text to speech engine.",
    height=150,
    max_chars=5000
)

if st.button("Generar Audio", type="primary"):
    clean_text = text.strip()
    if not clean_text:
        st.warning("Ingresa un texto antes de generar el audio.")
    else:
        try:
            with st.spinner("Sintetizando audio..."):
                samples, _ = pipeline.create(
                    clean_text,
                    voice=voice,
                    speed=speed,
                    lang="en-us"
                )

                if samples is None or len(samples) == 0:
                    st.error("No se pudo generar el audio para este texto.")
                else:
                    # Empacar audio en búfer WAV a 24 kHz
                    buffer = io.BytesIO()
                    sf.write(buffer, samples, 24000, format="WAV")
                    audio_bytes = buffer.getvalue()

                    st.success("¡Audio generado con éxito!")
                    st.audio(audio_bytes, format="audio/wav")

                    st.download_button(
                        label="Descargar WAV",
                        data=audio_bytes,
                        file_name="tts_output.wav",
                        mime="audio/wav"
                    )

        except Exception as e:
            st.error(f"Error durante la síntesis: {str(e)}")
