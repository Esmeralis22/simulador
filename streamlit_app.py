import streamlit as st
import random, json, os, time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

DATA_FILE = "usuarios_loteria.json"

# ================== DATA ==================
def cargar():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf8") as f:
            return json.load(f)
    return {}

def guardar(d):
    with open(DATA_FILE, "w", encoding="utf8") as f:
        json.dump(d, f, indent=4)

# ================== AUTO REFRESH REAL ==================
st_autorefresh(interval=1000, key="timer")

# ================== SESSION INIT ==================
if "datos" not in st.session_state:
    st.session_state.datos = cargar()
if "user" not in st.session_state:
    st.session_state.user = None
if "saldo" not in st.session_state:
    st.session_state.saldo = 0.0
if "hist" not in st.session_state:
    st.session_state.hist = []
if "inicio_sorteo" not in st.session_state:
    st.session_state.inicio_sorteo = time.time()
if "auto" not in st.session_state:
    st.session_state.auto = []
if "resultado" not in st.session_state:
    st.session_state.resultado = ["--", "--", "--"]

# ================== UI ==================
st.set_page_config(page_title="🎰 Lotería Dominicana", layout="centered")
st.title("🎰 Lotería Dominicana – Simulador")

# ================== LOGIN ==================
if st.session_state.user is None:
    u = st.text_input("Usuario")
    c = st.text_input("Clave", type="password")
    if st.button("Entrar"):
        if u in st.session_state.datos and st.session_state.datos[u]["clave"] == c:
            st.session_state.user = u
            st.session_state.saldo = st.session_state.datos[u]["saldo"]
            st.session_state.hist = st.session_state.datos[u]["historial"]
            st.rerun()
        else:
            st.error("Credenciales incorrectas")
    st.stop()

# ================== HEADER ==================
st.success(f"👤 {st.session_state.user} | 💰 ${st.session_state.saldo:.2f}")

segundos = max(0, 60 - int(time.time() - st.session_state.inicio_sorteo))
st.subheader(f"⏳ Sorteo en {segundos}s")

# ================== BOLOS (HORIZONTALES) ==================
st.markdown(f"""
<div style="display:flex;justify-content:center;gap:20px;margin-top:15px;">
    <div style="width:80px;height:80px;border-radius:50%;background:#ff5722;color:white;
    display:flex;align-items:center;justify-content:center;font-size:32px;font-weight:bold;">
        {st.session_state.resultado[0]}
    </div>
    <div style="width:80px;height:80px;border-radius:50%;background:#ff5722;color:white;
    display:flex;align-items:center;justify-content:center;font-size:32px;font-weight:bold;">
        {st.session_state.resultado[1]}
    </div>
    <div style="width:80px;height:80px;border-radius:50%;background:#ff5722;color:white;
    display:flex;align-items:center;justify-content:center;font-size:32px;font-weight:bold;">
        {st.session_state.resultado[2]}
    </div>
</div>
""", unsafe_allow_html=True)

# ================== SORTEO ==================
if segundos == 0:
    resultado = [f"{random.randint(0,99):02d}" for _ in range(3)]
    st.session_state.resultado = resultado
    st.session_state.inicio_sorteo = time.time()

    total = 0
    for num, monto in st.session_state.auto:
        for pos, res in enumerate(resultado):
            if int(res) == num:
                total += monto * [60, 8, 4][pos]

    if total > 0:
        st.session_state.saldo += total

    st.session_state.hist.append(
        f"🎲 Sorteo {', '.join(resultado)} → ${total:.2f}"
    )

    st.session_state.auto = []
    st.session_state.datos[st.session_state.user]["saldo"] = st.session_state.saldo
    st.session_state.datos[st.session_state.user]["historial"] = st.session_state.hist
    guardar(st.session_state.datos)

# ================== APUESTAS ==================
st.divider()
num = st.number_input("Número", min_value=0, max_value=99)
monto = st.number_input("Monto", min_value=1.0)
if st.button("🎯 Apostar"):
    if segundos <= 10:
        st.warning("No se puede apostar")
    elif monto > st.session_state.saldo:
        st.warning("Saldo insuficiente")
    else:
        st.session_state.saldo -= monto
        st.session_state.auto.append((num, monto))
        st.session_state.hist.append(
            f"🎯 Apostó {num:02d} por ${monto:.2f} ({datetime.now().strftime('%H:%M:%S')})"
        )
        st.session_state.datos[st.session_state.user]["saldo"] = st.session_state.saldo
        st.session_state.datos[st.session_state.user]["historial"] = st.session_state.hist
        guardar(st.session_state.datos)

# ================== HISTORIAL ==================
st.divider()
st.text_area("Historial", "\n".join(st.session_state.hist), height=260)
