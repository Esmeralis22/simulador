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
        if st.button("Entrar"):
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
        ru = st.text_input("Nuevo usuario")
        rc = st.text_input("Clave", type="password")
        rs = st.number_input("Saldo inicial", min_value=1.0, step=1.0)
        if st.button("Crear usuario"):
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
    if st.button("➕"):
        st.session_state.mostrar_recarga = True

# ================== RECARGA ==================
if st.session_state.mostrar_recarga:
    with st.expander("💳 Recargar saldo", expanded=True):
        monto = st.number_input("Monto a recargar", min_value=1.0, step=1.0)
        if st.button("Confirmar recarga"):
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

# ================== SORTEO ==================
if segundos == 0:
    resultado = [random.randint(0, 99) for _ in range(3)]
    st.session_state.ultimo_resultado = [f"{n:02d}" for n in resultado]
    st.session_state.inicio_sorteo = time.time()

    st.session_state.resultados_dia.append(
        f"Sorteo: {'-'.join(st.session_state.ultimo_resultado)}"
    )

    total = 0
    apostado = sum(m for _, m in st.session_state.auto)
    jugadas = [f"{n:02d}" for n, _ in st.session_state.auto]

    for num, monto in st.session_state.auto:
        for pos, res in enumerate(resultado):
            if num == res:
                total += monto * [60, 8, 4][pos]

    if st.session_state.auto:
        if total > 0:
            st.session_state.saldo += total
            st.session_state.popup_ganancia = f"🎉 Ganaste {rd(total)} 🎉"

        registro = (
            f"Apuesta {len(st.session_state.hist_dia)+1}\n"
            f"Tus Jugadas: {', '.join(jugadas)}\n"
            f"Sorteo: {'-'.join(st.session_state.ultimo_resultado)}\n"
            f"Resultado: {'Ganada' if total > 0 else 'Perdida'}\n"
            f"Ganancia: {rd(total)}\n"
            f"Dinero perdido: {rd(apostado if total == 0 else 0)}\n"
            "-----------------------------"
        )

        st.session_state.hist_dia.append(registro)

    st.session_state.datos[st.session_state.user]["saldo"] = st.session_state.saldo
    st.session_state.datos[st.session_state.user]["hist_dia"] = st.session_state.hist_dia
    st.session_state.datos[st.session_state.user]["resultados_dia"] = st.session_state.resultados_dia
    guardar(st.session_state.datos)

    st.session_state.hist.clear()
    st.session_state.auto.clear()
    st.rerun()

# ================== APUESTAS ==================
st.divider()
st.subheader("🎯 Apostar")

num = st.number_input("Número (00–99)", min_value=0, max_value=99)
monto = st.number_input("Monto", min_value=1.0, max_value=1000.0, step=1.0)

if st.button("🎯 Apostar"):
    if monto < 1 or monto > 1000:
        st.error("❌ El monto debe estar entre RD$1.00 y RD$1,000.00")
    elif monto > st.session_state.saldo:
        st.error("❌ Saldo insuficiente para realizar la apuesta")
    else:
        st.session_state.saldo -= monto
        st.session_state.auto.append((num, monto))
        st.session_state.hist.append(f"Apuesta {num:02d} por {rd(monto)}")
        st.session_state.datos[st.session_state.user]["saldo"] = st.session_state.saldo
        guardar(st.session_state.datos)
        st.rerun()

# ================== HISTORIALES ==================
st.divider()
st.subheader("📜 Apuestas del sorteo actual")
st.text_area("", "\n".join(st.session_state.hist), height=150)

with st.expander("📅 Ver historial del día"):
    st.text_area("", "\n".join(st.session_state.hist_dia), height=300)

if st.button("📊 Resultados del día"):
    st.text_area("Resultados", "\n".join(st.session_state.resultados_dia), height=300)

# ================== LOGOUT / ELIMINAR CUENTA ==================
st.divider()
col_logout, col_delete = st.columns(2)
with col_logout:
    if st.button("🚪 Cerrar sesión"):
        st.session_state.clear()
        st.rerun()
with col_delete:
    if not st.session_state.confirm_delete:
        if st.button("🗑️ Eliminar cuenta"):
            st.session_state.confirm_delete = True
    else:
        st.warning("⚠️ ¿Seguro que quieres eliminar tu cuenta? Esta acción no se puede deshacer.")
        confirm, cancel = st.columns(2)
        with confirm:
            if st.button("Sí, eliminar"):
                if st.session_state.user in st.session_state.datos:
                    del st.session_state.datos[st.session_state.user]
                    guardar(st.session_state.datos)
                st.session_state.clear()
                st.success("Cuenta eliminada correctamente")
                st.rerun()
        with cancel:
            if st.button("Cancelar"):
                st.session_state.confirm_delete = False
                st.rerun()  

