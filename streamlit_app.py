import streamlit as st
import random, json, os, time
from datetime import datetime

DATA_FILE = "usuarios_loteria.json"

# ================== DATA ==================
def cargar():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE,"r",encoding="utf8") as f:
            return json.load(f)
    return {}

def guardar(d):
    with open(DATA_FILE,"w",encoding="utf8") as f:
        json.dump(d,f,indent=4)

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

# ================== LOGIN ==================
st.title("🎰 Lotería Dominicana – Simulador")

if st.session_state.user is None:
    tab1, tab2 = st.tabs(["🔐 Login","🆕 Registro"])

    with tab1:
        u = st.text_input("Usuario")
        c = st.text_input("Clave", type="password")
        if st.button("Entrar"):
            d = st.session_state.datos
            if u in d and d[u]["clave"]==c:
                st.session_state.user = u
                st.session_state.saldo = d[u]["saldo"]
                st.session_state.hist = d[u]["historial"]
                st.success("Login correcto")
                st.rerun()
            else:
                st.error("Credenciales incorrectas")

    with tab2:
        ru = st.text_input("Nuevo usuario")
        rc = st.text_input("Clave", type="password")
        rs = st.number_input("Saldo inicial", min_value=1.0)
        if st.button("Crear"):
            if ru not in st.session_state.datos:
                rs *= 1.1
                st.session_state.datos[ru] = {
                    "clave": rc,
                    "saldo": rs,
                    "historial": []
                }
                guardar(st.session_state.datos)
                st.success(f"Usuario creado con ${rs:.2f}")
            else:
                st.error("Usuario existe")

    st.stop()

# ================== UI ==================
st.success(f"👤 {st.session_state.user} | 💰 ${st.session_state.saldo:.2f}")

segundos = max(0, 60 - int(time.time() - st.session_state.inicio_sorteo))
st.subheader(f"⏳ Sorteo en {segundos}s")

# ================== SORTEO ==================
if segundos == 0:
    resultado = [random.randint(0,99) for _ in range(3)]
    st.session_state.inicio_sorteo = time.time()

    total = 0
    for num,m in st.session_state.auto:
        for i,r in enumerate(resultado):
            if num==r:
                mult = [60,8,4][i]
                total += m*mult

    if total>0:
        st.session_state.saldo += total
        st.success(f"🎉 Ganaste ${total:.2f}")

    st.session_state.hist.append(
        f"🎲 Sorteo {resultado} → ${total:.2f}"
    )
    st.session_state.auto = []
    guardar(st.session_state.datos)
    st.rerun()

# ================== APUESTA ==================
num = st.number_input("Número",0,99)
monto = st.number_input("Monto",1.0, step=1.0)

if st.button("🎯 Apostar"):
    if monto <= st.session_state.saldo and segundos>10:
        st.session_state.saldo -= monto
        st.session_state.auto.append((num,monto))
        st.session_state.hist.append(
            f"Apostó {num:02d} por ${monto:.2f}"
        )
        st.session_state.datos[st.session_state.user]["saldo"]=st.session_state.saldo
        guardar(st.session_state.datos)
        st.success("Apuesta registrada")
        st.rerun()
    else:
        st.warning("Saldo insuficiente o tiempo agotado")

# ================== HIST ==================
st.text_area("📜 Historial", "\n".join(st.session_state.hist), height=250)
