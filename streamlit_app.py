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
if "ultimo_resultado" not in st.session_state:
    st.session_state.ultimo_resultado = ["--", "--", "--"]

# ================== LOGIN / REGISTRO ==================
st.set_page_config(page_title="🎰 Lotería Dominicana", layout="centered")
st.title("🎰 Lotería Dominicana – Simulador")

if st.session_state.user is None:
    tab1, tab2 = st.tabs(["🔐 Login", "🆕 Registro"])

    with tab1:
        u = st.text_input("Usuario", key="login_user")
        c = st.text_input("Clave", type="password", key="login_pass")
        if st.button("Entrar", key="btn_login"):
            d = st.session_state.datos
            if u in d and d[u]["clave"] == c:
                st.session_state.user = u
                st.session_state.saldo = d[u]["saldo"]
                st.session_state.hist = d[u]["historial"]
                st.success("Login correcto")
                st.rerun()
            else:
                st.error("Usuario o clave incorrectos")

    with tab2:
        ru = st.text_input("Nuevo usuario", key="reg_user")
        rc = st.text_input("Clave", type="password", key="reg_pass")
        rs = st.number_input("Saldo inicial", min_value=1.0, step=1.0, key="reg_saldo")
        if st.button("Crear usuario", key="btn_reg"):
            if ru and rc and ru not in st.session_state.datos:
                rs *= 1.1
                st.session_state.datos[ru] = {
                    "clave": rc,
                    "saldo": rs,
                    "historial": []
                }
                guardar(st.session_state.datos)
                st.success(f"Usuario creado con saldo ${rs:.2f}")
            else:
                st.error("Datos inválidos o usuario ya existe")

    st.stop()

# ================== HEADER ==================
st.success(f"👤 {st.session_state.user} | 💰 ${st.session_state.saldo:.2f}")

# ================== AUTO REFRESH ==================
st_autorefresh(interval=1000, limit=None, key="timer_refresh")

segundos = max(0, 60 - int(time.time() - st.session_state.inicio_sorteo))
st.subheader(f"⏳ Sorteo en {segundos}s")

# ================== BOLOS (CORRECCIÓN ÚNICA) ==================
bolos_html = """
<div style="
    display:flex;
    justify-content:center;
    gap:20px;
    margin-top:15px;
">
"""

for n in st.session_state.ultimo_resultado:
    bolos_html += f"""
    <div style="
        width:80px;height:80px;
        border-radius:50%;
        background:#ff5722;
        color:white;
        display:flex;
        align-items:center;
        justify-content:center;
        font-size:32px;
        font-weight:bold;
    ">
        {n}
    </div>
    """

bolos_html += "</div>"

st.markdown(bolos_html, unsafe_allow_html=True)

# ================== SORTEO ==================
if segundos == 0:
    resultado = [random.randint(0, 99) for _ in range(3)]
    st.session_state.ultimo_resultado = [f"{n:02d}" for n in resultado]
    st.session_state.inicio_sorteo = time.time()

    total = 0
    for num, monto in st.session_state.auto:
        for pos, res in enumerate(resultado):
            if num == res:
                mult = [60, 8, 4][pos]
                total += monto * mult

    if total > 0:
        st.session_state.saldo += total
        st.success(f"🎉 Ganaste ${total:.2f}")

    registro = f"🎲 Sorteo {', '.join(f'{n:02d}' for n in resultado)} → ${total:.2f}"
    st.session_state.hist.append(registro)

    st.session_state.auto = []
    st.session_state.datos[st.session_state.user]["saldo"] = st.session_state.saldo
    st.session_state.datos[st.session_state.user]["historial"] = st.session_state.hist
    guardar(st.session_state.datos)

    st.rerun()

# ================== APUESTAS ==================
st.divider()
st.subheader("🎯 Apostar")

num = st.number_input("Número (00–99)", min_value=0, max_value=99, key="bet_num")
monto = st.number_input("Monto", min_value=1.0, step=1.0, key="bet_monto")

if st.button("🎯 Apostar", key="btn_bet"):
    if segundos <= 10:
        st.warning("No se puede apostar con 10 segundos o menos")
    elif monto > st.session_state.saldo:
        st.warning("Saldo insuficiente")
    else:
        st.session_state.saldo -= monto
        st.session_state.auto.append((num, monto))
        registro = f"🎯 Apostó {num:02d} por ${monto:.2f} ({datetime.now().strftime('%H:%M:%S')})"
        st.session_state.hist.append(registro)

        st.session_state.datos[st.session_state.user]["saldo"] = st.session_state.saldo
        st.session_state.datos[st.session_state.user]["historial"] = st.session_state.hist
        guardar(st.session_state.datos)

        st.success("Apuesta registrada")
        st.rerun()

# ================== HISTORIAL ==================
st.divider()
st.subheader("📜 Historial")
st.text_area(
    "Historial de apuestas",
    "\n".join(st.session_state.hist),
    height=260,
    key="hist_area"
)

# ================== LOGOUT ==================
st.divider()
if st.button("🚪 Cerrar sesión", key="logout"):
    st.session_state.clear()
    st.rerun()
