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

# ================== AUTO REFRESH ==================
st.markdown("""
<script>
setTimeout(() => {
    window.location.reload();
}, 1000);
</script>
""", unsafe_allow_html=True)

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
                st.success("Usuario creado")
            else:
                st.error("Error en registro")
    st.stop()

# ================== HEADER ==================
col1, col2 = st.columns([4,1])
with col1:
    st.success(f"👤 {st.session_state.user} | 💰 ${st.session_state.saldo:.2f}")
with col2:
    if st.button("➕"):
        rec = st.number_input("Recargar", min_value=1.0, step=1.0)
        if st.button("Confirmar recarga"):
            rec *= 1.1
            st.session_state.saldo += rec
            st.session_state.datos[st.session_state.user]["saldo"] = st.session_state.saldo
            guardar(st.session_state.datos)
            st.rerun()

segundos = max(0, 60 - int(time.time() - st.session_state.inicio_sorteo))
st.subheader(f"⏳ Sorteo en {segundos}s")

# ================== BOLOS (CORREGIDO) ==================
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
                total += monto * [60,8,4][pos]

    if total > 0:
        st.session_state.saldo += total

    st.session_state.hist.append(
        f"🎲 Sorteo {', '.join(resultado)} → ${total:.2f}"
    )

    st.session_state.auto = []
    st.session_state.datos[st.session_state.user]["saldo"] = st.session_state.saldo
    st.session_state.datos[st.session_state.user]["historial"] = st.session_state.hist
    guardar(st.session_state.datos)
    st.rerun()

# ================== APUESTAS ==================
st.divider()
num = st.number_input("Número", min_value=0, max_value=99)
monto = st.number_input("Monto", min_value=1.0)
if st.button("🎯 Apostar"):
    if segundos <= 10:
        st.warning("Cerrado")
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
        st.rerun()

# ================== HISTORIAL ==================
st.divider()
st.text_area("Historial", "\n".join(st.session_state.hist), height=260)

# ================== LOGOUT ==================
st.divider()
if st.button("🚪 Cerrar sesión"):
    st.session_state.clear()
    st.rerun()
