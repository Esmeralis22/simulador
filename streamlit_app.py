import streamlit as st
import random, json, os, time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

DATA_FILE = "usuarios_loteria.json"

# ================== DATA ==================
def cargar():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf8") as f:
            d = json.load(f)
    else:
        d = {}

    d.setdefault("recargas", [])
    d.setdefault("retiros", [])
    d.setdefault("bloqueados", [])

    return d

def guardar(d):
    with open(DATA_FILE, "w", encoding="utf8") as f:
        json.dump(d, f, indent=4, ensure_ascii=False)

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
if "confirm_delete" not in st.session_state:
    st.session_state.confirm_delete = False

# ================== LOGIN / REGISTRO ==================
st.set_page_config(page_title="🎰 Esteban Loteria", layout="centered")
st.title("🎰 Esteban Loteria")

# ---------- ADMIN LOGIN ----------
if st.session_state.user is None:
    tab1, tab2 = st.tabs(["🔐 Login", "🆕 Registro"])

    with tab1:
        u = st.text_input("Usuario")
        c = st.text_input("Clave", type="password")

        if st.button("Entrar"):
            if u == "admin" and c == "admin123":
                st.session_state.user = "admin"
                st.rerun()

            d = st.session_state.datos
            if u in d and d[u]["clave"] == c:
                if u in d["bloqueados"]:
                    st.error("🚫 Usuario bloqueado")
                else:
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

        if st.button("Crear usuario"):
            st.session_state.datos[ru] = {
                "clave": rc,
                "saldo": 0.0,
                "hist_dia": [],
                "resultados_dia": []
            }
            guardar(st.session_state.datos)
            st.success("Usuario creado con saldo RD$0.00")

    st.stop()

# ================== MODO ADMIN ==================
if st.session_state.user == "admin":
    st.subheader("🛠️ Panel Administrador")

    st.markdown("### 💳 Recargas pendientes")
    for r in st.session_state.datos["recargas"]:
        if r["estado"] == "pendiente":
            if st.button(f"Aprobar {r['usuario']} {rd(r['monto'])}", key="rec"+r["usuario"]+r["fecha"]):
                st.session_state.datos[r["usuario"]]["saldo"] += r["monto"]
                r["estado"] = "aprobado"
                guardar(st.session_state.datos)
                st.rerun()

    st.markdown("### 💸 Retiros pendientes")
    for r in st.session_state.datos["retiros"]:
        if r["estado"] == "pendiente":
            if st.button(f"Aprobar retiro {r['usuario']} {rd(r['monto'])}", key="ret"+r["usuario"]+r["fecha"]):
                r["estado"] = "aprobado"
                guardar(st.session_state.datos)
                st.rerun()

    st.divider()
    st.markdown("### 👥 Bloquear / Desbloquear usuarios")

    for u in st.session_state.datos:
        if u in ["recargas", "retiros", "bloqueados"]:
            continue

        col1, col2 = st.columns([6, 2])
        col1.write(u)

        if u in st.session_state.datos["bloqueados"]:
            if col2.button("🔓 Desbloquear", key="unb"+u):
                st.session_state.datos["bloqueados"].remove(u)
                guardar(st.session_state.datos)
                st.rerun()
        else:
            if col2.button("🚫 Bloquear", key="bl"+u):
                st.session_state.datos["bloqueados"].append(u)
                guardar(st.session_state.datos)
                st.rerun()

    st.divider()
    st.markdown("### 📊 Historial por usuario")

    usuario_sel = st.selectbox(
        "Usuario",
        [u for u in st.session_state.datos if u not in ["recargas","retiros","bloqueados"]]
    )

    st.markdown("#### 💳 Recargas")
    for r in st.session_state.datos["recargas"]:
        if r["usuario"] == usuario_sel:
            st.write(f"{r['fecha']} | {rd(r['monto'])} | {r['estado']}")

    st.markdown("#### 💸 Retiros")
    for r in st.session_state.datos["retiros"]:
        if r["usuario"] == usuario_sel:
            st.write(f"{r['fecha']} | {rd(r['monto'])} | {r['banco']} | {r['estado']}")

    if st.button("Cerrar sesión"):
        st.session_state.clear()
        st.rerun()

    st.stop()

# ================== HEADER USUARIO ==================
st.success(f"👤 {st.session_state.user} | 💰 {rd(st.session_state.saldo)}")

# ================== RECARGA ==================
with st.expander("💳 Solicitar recarga"):
    monto = st.number_input("Monto", min_value=1.0)
    if st.button("Enviar recarga"):
        st.session_state.datos["recargas"].append({
            "usuario": st.session_state.user,
            "monto": monto,
            "fecha": str(datetime.now()),
            "estado": "pendiente"
        })
        guardar(st.session_state.datos)
        st.info("⏳ Recarga pendiente de aprobación")

# ================== RETIRO ==================
with st.expander("💸 Solicitar retiro"):
    monto = st.number_input("Monto a retirar", min_value=1.0)
    banco = st.text_input("Banco")
    cuenta = st.text_input("Cuenta")
    if st.button("Solicitar retiro"):
        st.session_state.datos["retiros"].append({
            "usuario": st.session_state.user,
            "monto": monto,
            "banco": banco,
            "cuenta": cuenta,
            "fecha": str(datetime.now()),
            "estado": "pendiente"
        })
        guardar(st.session_state.datos)
        st.info("⏳ Retiro pendiente")

# ================== AQUÍ SIGUE TU JUEGO ORIGINAL SIN TOCAR ==================
