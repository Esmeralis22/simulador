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

    # 🔒 Blindaje de estructura
    d.setdefault("usuarios", {})
    d.setdefault("recargas", [])
    d.setdefault("retiros", [])
    d.setdefault("bloqueados", [])
    d.setdefault("congelados", [])

    return d

def guardar(d):
    with open(DATA_FILE, "w", encoding="utf8") as f:
        json.dump(d, f, indent=4, ensure_ascii=False)

def rd(v): 
    return f"RD${v:,.2f}"

datos = cargar()

# ================== SESSION ==================
if "user" not in st.session_state:
    st.session_state.user = None
if "saldo" not in st.session_state:
    st.session_state.saldo = 0.0
if "confirm_delete" not in st.session_state:
    st.session_state.confirm_delete = False

# ================== CONFIG ==================
st.set_page_config("🎰 Esteban Loteria", layout="centered")
st.title("🎰 Esteban Loteria")

# ================== LOGIN ==================
if st.session_state.user is None:
    u = st.text_input("Usuario")
    c = st.text_input("Clave", type="password")

    if st.button("Entrar"):
        if u == "admin" and c == "admin123":
            st.session_state.user = "admin"
            st.rerun()

        if u in datos["usuarios"] and datos["usuarios"][u]["clave"] == c:
            if u in datos["bloqueados"]:
                st.error("🚫 Usuario bloqueado")
            else:
                st.session_state.user = u
                st.session_state.saldo = datos["usuarios"][u]["saldo"]
                st.rerun()
        else:
            st.error("Credenciales incorrectas")

    st.divider()
    st.subheader("Registro")

    ru = st.text_input("Nuevo usuario")
    rc = st.text_input("Clave nueva", type="password")

    if st.button("Crear usuario"):
        datos["usuarios"][ru] = {
            "clave": rc,
            "saldo": 0.0,
            "historial": []
        }
        guardar(datos)
        st.success("Usuario creado con saldo RD$0.00")

    st.stop()

# ================== ADMIN ==================
if st.session_state.user == "admin":
    st.subheader("🛠️ Panel Admin")

    st.markdown("### 💳 Recargas pendientes")
    for r in datos["recargas"]:
        if r["estado"] == "pendiente":
            if st.button(f"Aprobar {r['usuario']} {rd(r['monto'])}"):
                datos["usuarios"][r["usuario"]]["saldo"] += r["monto"]
                r["estado"] = "aprobado"

    st.markdown("### 💸 Retiros pendientes")
    for r in datos["retiros"]:
        if r["estado"] == "pendiente":
            if st.button(f"Aprobar retiro {r['usuario']} {rd(r['monto'])}"):
                r["estado"] = "aprobado"

    st.markdown("### 👥 Usuarios")
    for u in datos["usuarios"]:
        col1, col2, col3 = st.columns(3)
        col1.write(u)
        if col2.button("Bloquear", key="b"+u):
            datos["bloqueados"].append(u)
        if col3.button("Multa -100", key="m"+u):
            datos["usuarios"][u]["saldo"] -= 100

    guardar(datos)
    if st.button("Cerrar admin"):
        st.session_state.clear()
        st.rerun()
    st.stop()

# ================== HEADER ==================
st.success(f"👤 {st.session_state.user} | 💰 {rd(st.session_state.saldo)}")

# ================== RECARGA ==================
with st.expander("💳 Solicitar recarga"):
    monto = st.number_input("Monto", min_value=1.0)
    if st.button("Enviar solicitud"):
        datos["recargas"].append({
            "usuario": st.session_state.user,
            "monto": monto,
            "fecha": str(datetime.now()),
            "estado": "pendiente"
        })
        guardar(datos)
        st.success("⏳ Recarga pendiente de aprobación")

# ================== RETIRO ==================
with st.expander("💸 Solicitar retiro"):
    monto = st.number_input("Monto a retirar", min_value=1.0)
    banco = st.text_input("Banco")
    cuenta = st.text_input("Cuenta")
    if st.button("Solicitar retiro"):
        datos["retiros"].append({
            "usuario": st.session_state.user,
            "monto": monto,
            "banco": banco,
            "cuenta": cuenta,
            "fecha": str(datetime.now()),
            "estado": "pendiente"
        })
        guardar(datos)
        st.info("⏳ Retiro pendiente")

# ================== LOGOUT ==================
if st.button("Cerrar sesión"):
    st.session_state.clear()
    st.rerun()





