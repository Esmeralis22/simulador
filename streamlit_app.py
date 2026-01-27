import streamlit as st
import random, json, os, time
from datetime import datetime

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
if "resultado" not in st.session_state:
    st.session_state.resultado = ["--", "--", "--"]
if "recargar" not in st.session_state:
    st.session_state.recargar = False

# ================== CONFIG ==================
st.set_page_config(page_title="🎰 Lotería Dominicana", layout="centered")
st.title("🎰 Lotería Dominicana – Simulador")

# ================== AUTO REFRESH REAL
st.markdown("""
<script>
setTimeout(function(){
    window.location.reload();
}, 1000);
</script>
""", unsafe_allow_html=True)

# ================== LOGIN ==================
if st.session_state.user is None:
    tab1, tab2 = st.tabs(["🔐 Login", "🆕 Registro"])

    with tab1:
        u = st.text_input("Usuario", key="lu")
        c = st.text_input("Clave", type="password", key="lp")
        if st.button("Entrar"):
            if u in st.session_state.datos and st.session_state.datos[u]["clave"] == c:
                st.session_state.user = u
                st.session_state.saldo = st.session_state.datos[u]["saldo"]
                st.session_state.hist = st.session_state.datos[u]["historial"]
                st.rerun()
            else:
                st.error("Credenciales incorrectas")

    with tab2:
        ru = st.text_input("Nuevo usuario")
        rc = st.text_input("Clave nueva", type="password")
        rs = st.number_input("Saldo inicial", min_value=1.0)
        if st.button("Crear usuario"):
            if ru and rc and ru not in st.session_state.datos:
                rs *= 1.1
                st.session_state.datos[ru] = {
                    "clave": rc,
                    "saldo": rs,
                    "historial": []
                }
                guardar(st.session_state.datos)
                st.success("Usuario creado")
    st.stop()

# ================== HEADER + SALDO ==================
c1, c2 = st.columns([4, 1])
with c1:
    st.success(f"👤 {st.session_state.user} | 💰 ${st.session_state.saldo:.2f}")
with c2:
    if st.button("➕"):
        st.session_state.recargar = not st.session_state.recargar

if st.session_state.recargar:
    monto = st.number_input("Monto a recargar", min_value=1.0)
    if st.button("Confirmar"):
        bono = monto * 0.10
        st.session_state.saldo += monto + bono
        st.session_state.datos[st.session_state.user]["saldo"] = st.session_state.saldo
        guardar(st.session_state.datos)
        st.session_state.recargar = False
        st.success(f"Recarga ${monto:.2f} + bono ${bono:.2f}")
        st.rerun()

# ================== COUNTDOWN ==================
seg = max(0, 60 - int(time.time() - st.session_state.inicio_sorteo))
st.subheader(f"⏳ Sorteo en {seg}s")

# ================== BOLOS ==================
def bolo(n):
    return f"""
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

st.markdown(
    "<div style='display:flex;gap:20px;justify-content:center;margin:20px;'>"
    + "".join(bolo(n) for n in st.session_state.resultado)
    + "</div>",
    unsafe_allow_html=True
)

# ================== SORTEO ==================
if seg == 0:
    res = [f"{random.randint(0,99):02d}" for _ in range(3)]
    st.session_state.resultado = res
    st.session_state.inicio_sorteo = time.time()

    total = 0
    for n, m in st.session_state.auto:
        for p, r in enumerate(res):
            if f"{n:02d}" == r:
                total += m * [60,8,4][p]

    if total > 0:
        st.session_state.saldo += total
        st.success(f"🎉 Ganaste ${total:.2f}")

    st.session_state.hist.append(
        f"🎲 Sorteo {', '.join(res)} → ${total:.2f}"
    )

    st.session_state.auto = []
    st.session_state.datos[st.session_state.user]["saldo"] = st.session_state.saldo
    st.session_state.datos[st.session_state.user]["historial"] = st.session_state.hist
    guardar(st.session_state.datos)

# ================== APUESTAS ==================
st.divider()
num = st.number_input("Número (00–99)", 0, 99)
monto = st.number_input("Monto", min_value=1.0)

if st.button("🎯 Apostar"):
    if seg <= 10:
        st.warning("Cerrado")
    elif monto > st.session_state.saldo:
        st.warning("Saldo insuficiente")
    else:
        st.session_state.saldo -= monto
        st.session_state.auto.append((num, monto))
        st.session_state.hist.append(
            f"🎯 Apostó {num:02d} por ${monto:.2f}"
        )
        guardar(st.session_state.datos)
        st.rerun()

# ================== HISTORIAL ==================
st.divider()
st.text_area("Historial", "\n".join(st.session_state.hist), height=260)

# ================== LOGOUT ==================
if st.button("🚪 Cerrar sesión"):
    st.session_state.clear()
    st.rerun()
