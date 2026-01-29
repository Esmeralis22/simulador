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

def rd(valor):
    return f"RD${valor:,.2f}"

# ================== SESSION INIT ==================
if "datos" not in st.session_state:
    st.session_state.datos = cargar()
if "user" not in st.session_state:
    st.session_state.user = None
if "saldo" not in st.session_state:
    st.session_state.saldo = 0.0
if "hist" not in st.session_state:
    st.session_state.hist = []
if "hist_dia" not in st.session_state:
    st.session_state.hist_dia = []
if "resultados_dia" not in st.session_state:
    st.session_state.resultados_dia = []
if "inicio_sorteo" not in st.session_state:
    st.session_state.inicio_sorteo = time.time()
if "auto" not in st.session_state:
    st.session_state.auto = []
if "ultimo_resultado" not in st.session_state:
    st.session_state.ultimo_resultado = ["--", "--", "--"]
if "popup_ganancia" not in st.session_state:
    st.session_state.popup_ganancia = None
if "mostrar_recarga" not in st.session_state:
    st.session_state.mostrar_recarga = False
if "ver_resultados" not in st.session_state:
    st.session_state.ver_resultados = False
if "confirm_delete" not in st.session_state:
    st.session_state.confirm_delete = False

# ================== LOGIN / REGISTRO ==================
st.set_page_config(page_title="🎰 Esteban Loteria", layout="centered")
st.title("🎰 Esteban Loteria")

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
                st.session_state.hist_dia = d[u].get("hist_dia", [])
                st.session_state.resultados_dia = d[u].get("resultados_dia", [])
                st.success("Login correcto")
                st.rerun()
            else:
                st.error("Usuario o clave incorrectos")

    with tab2:
        ru = st.text_input("Nuevo usuario", key="reg_user")
        rc = st.text_input("Clave", type="password", key="reg_pass")
        rs = st.number_input("Saldo inicial", min_value=1.0, step=1.0, key="reg_saldo")
        if st.button("Crear usuario", key="btn_register"):
            rs *= 1.1
            st.session_state.datos[ru] = {
                "clave": rc,
                "saldo": rs,
                "hist_dia": [],
                "resultados_dia": []
            }
            guardar(st.session_state.datos)
            st.success(f"Usuario creado con saldo {rd(rs)}")

    st.stop()

# ================== HEADER ==================
col1, col2 = st.columns([9, 1])
with col1:
    st.success(f"👤 {st.session_state.user} | 💰 {rd(st.session_state.saldo)}")
with col2:
    if st.button("➕", key="btn_recarga"):
        st.session_state.mostrar_recarga = True

# ================== RECARGA ==================
if st.session_state.mostrar_recarga:
    with st.expander("💳 Recargar saldo", expanded=True):
        monto = st.number_input("Monto a recargar", min_value=1.0, step=1.0, key="rec_monto")
        if st.button("Confirmar recarga", key="btn_confirm_recarga"):
            bono = monto * 0.10
            total = monto + bono
            st.session_state.saldo += total
            st.session_state.datos[st.session_state.user]["saldo"] = st.session_state.saldo
            guardar(st.session_state.datos)
            st.success(f"Recargado {rd(monto)} + bono {rd(bono)}")
            st.session_state.mostrar_recarga = False
            st.rerun()

# ================== AUTO REFRESH ==================
st_autorefresh(interval=1000, limit=None)

segundos = max(0, 60 - int(time.time() - st.session_state.inicio_sorteo))
st.subheader(f"⏳ Sorteo en {segundos}s")

# ================== RESULTADO ==================
st.markdown(
    f"<h1 style='text-align:center'>{' '.join(st.session_state.ultimo_resultado)}</h1>",
    unsafe_allow_html=True
)
