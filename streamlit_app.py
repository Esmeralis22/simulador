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
if "recargas_pendientes" not in st.session_state:
    st.session_state.recargas_pendientes = {}

# ================== CONFIG ==================
ADMIN_USER = "admin"
ADMIN_PASS = "admin123"

# ================== LOGIN ==================
st.set_page_config(page_title="🎰 Lotería Dominicana", layout="centered")
st.title("🎰 Lotería Dominicana – Simulador")

if st.session_state.user is None:
    st.subheader("🔐 Login")
    u = st.text_input("Usuario", key="login_user")
    c = st.text_input("Clave", type="password", key="login_pass")
    if st.button("Entrar"):
        if u == ADMIN_USER and c == ADMIN_PASS:
            st.session_state.user = ADMIN_USER
            st.success("Bienvenido Admin")
            st.rerun()
        else:
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

    st.subheader("🆕 Registro")
    ru = st.text_input("Nuevo usuario")
    rc = st.text_input("Clave", type="password")
    if st.button("Crear usuario"):
        if ru in st.session_state.datos:
            st.error("Usuario ya existe")
        else:
            st.session_state.datos[ru] = {
                "clave": rc,
                "saldo": 0.0,  # no hay saldo inicial
                "hist_dia": [],
                "resultados_dia": [],
                "recargas_pendientes": {}
            }
            guardar(st.session_state.datos)
            st.success("Usuario creado con saldo RD$0.00")
    st.stop()  # detiene la ejecución hasta login exitoso

# ================== ADMIN ==================
if st.session_state.user == ADMIN_USER:
    st.subheader("🔧 Panel de Administrador")

    # 1️⃣ Ver todos los usuarios
    st.write("**1️⃣ Usuarios registrados:**")
    for usr, info in st.session_state.datos.items():
        st.write(f"- {usr} | Saldo: {rd(info.get('saldo',0))}")

    st.divider()

    # 2️⃣ Historial global del día
    st.write("**2️⃣ Historial global del día:**")
    for usr, info in st.session_state.datos.items():
        for r in info.get("hist_dia", []):
            st.text_area(f"{usr}", r, height=50)

    st.divider()

    # 3️⃣ Resultados oficiales del día
    st.write("**3️⃣ Resultados del día:**")
    for usr, info in st.session_state.datos.items():
        for r in info.get("resultados_dia", []):
            st.text_area(f"{usr}", r, height=30)

    st.divider()

    # 4️⃣ Aprobar recargas y editar saldo
st.write("**4️⃣ Recargas pendientes y edición de saldo:**")
for usr, info in st.session_state.datos.items():
    recs = info.get("recargas_pendientes", {})
    # iteramos sobre una copia de los items
    for key, monto in list(recs.items()):
        col1, col2 = st.columns([3,1])
        with col1:
            st.write(f"{usr} solicitó: {rd(monto)}")
        with col2:
            if st.button(f"Aprobar {usr}-{key}"):
                bono = monto*0.10
                total = monto + bono
                st.session_state.datos[usr]["saldo"] += total
                # eliminamos la recarga aprobada
                del st.session_state.datos[usr]["recargas_pendientes"][key]
                guardar(st.session_state.datos)
                st.success(f"Aprobado {rd(monto)} + bono {rd(bono)} a {usr}")
                st.experimental_rerun()  # recarga la página para que desaparezca de la lista


    # 5️⃣ Bloquear / desbloquear usuarios
    st.write("**5️⃣ Bloquear / desbloquear usuarios**")
    for usr in st.session_state.datos.keys():
        estado = st.session_state.datos[usr].get("bloqueado", False)
        if st.button(f"{'Desbloquear' if estado else 'Bloquear'} {usr}"):
            st.session_state.datos[usr]["bloqueado"] = not estado
            guardar(st.session_state.datos)
            st.experimental_rerun()

    st.divider()

    # 6️⃣ Estadísticas del sistema
    st.write("**6️⃣ Estadísticas:**")
    total_users = len(st.session_state.datos)
    total_saldo = sum(info.get("saldo",0) for info in st.session_state.datos.values())
    st.write(f"Usuarios: {total_users} | Saldo total: {rd(total_saldo)}")

    st.divider()

    # 7️⃣ Reset diario
    if st.button("7️⃣ Reset diario (historial del día)"):
        for usr in st.session_state.datos.keys():
            st.session_state.datos[usr]["hist_dia"] = []
            st.session_state.datos[usr]["resultados_dia"] = []
        guardar(st.session_state.datos)
        st.success("Historial del día reseteado")

    st.divider()

    # 8️⃣ Modo solo lectura
    st.write("**8️⃣ Modo solo lectura:**")
    st.write("No se pueden modificar apuestas ni recargas mientras esté activo.")
    st.stop()

# ================== HEADER USUARIOS ==================
col1, col2 = st.columns([9, 1])
with col1:
    st.success(f"👤 {st.session_state.user} | 💰 {rd(st.session_state.saldo)}")
with col2:
    if st.button("➕"):
        st.session_state.mostrar_recarga = True

# ================== RECARGA ==================
if st.session_state.mostrar_recarga:
    with st.expander("💳 Solicitar recarga", expanded=True):
        monto = st.number_input("Monto a recargar", min_value=1.0, step=1.0)
        if st.button("Solicitar recarga"):
            key = str(time.time())
            st.session_state.datos[st.session_state.user].setdefault("recargas_pendientes", {})[key] = monto
            guardar(st.session_state.datos)
            st.success(f"Recarga de {rd(monto)} solicitada para aprobación del admin")
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

# ================== POPUP GANANCIA ==================
if st.session_state.popup_ganancia:
    st.success(st.session_state.popup_ganancia)
    st.session_state.popup_ganancia = None

# ================== LOGOUT ==================
st.divider()
if st.button("🚪 Cerrar sesión"):
    st.session_state.clear()
    st.rerun()

