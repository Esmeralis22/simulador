import streamlit as st
import time
import random
from streamlit_autorefresh import st_autorefresh

# ===============================
# CONFIGURACIÓN
# ===============================
DURACION_SORTEO = 30  # segundos

st.set_page_config(page_title="Sorteo en Tiempo Real", layout="centered")

# ===============================
# SESSION STATE
# ===============================
if "inicio" not in st.session_state:
    st.session_state.inicio = time.time()
    st.session_state.historial = []

# ===============================
# AUTO REFRESH (1 segundo)
# ===============================
st_autorefresh(interval=1000, key="refresh")

# ===============================
# TIEMPO RESTANTE
# ===============================
ahora = time.time()
transcurrido = int(ahora - st.session_state.inicio)
restante = max(0, DURACION_SORTEO - transcurrido)

st.title("🎰 Sorteo Automático")
st.subheader("⏳ Tiempo restante")
st.markdown(f"## `{restante} segundos`")

# ===============================
# CUANDO LLEGA A CERO → SORTEO
# ===============================
if restante == 0:
    numero_ganador = random.randint(0, 99)

    st.session_state.historial.insert(0, {
        "hora": time.strftime("%H:%M:%S"),
        "numero": numero_ganador
    })

    # Reiniciar contador
    st.session_state.inicio = time.time()

# ===============================
# HISTORIAL
# ===============================
st.divider()
st.subheader("📜 Historial de sorteos")

if st.session_state.historial:
    for i, s in enumerate(st.session_state.historial[:20], 1):
        st.write(f"{i}. ⏰ {s['hora']} → 🎯 **{s['numero']:02d}**")
else:
    st.info("Aún no hay sorteos")

# ===============================
# BOTÓN MANUAL
# ===============================
st.divider()
if st.button("🎲 Forzar sorteo ahora"):
    numero = random.randint(0, 99)
    st.session_state.historial.insert(0, {
        "hora": time.strftime("%H:%M:%S"),
        "numero": numero
    })
