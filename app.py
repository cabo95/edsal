import streamlit as st
import sqlite3
from datetime import datetime

# Función para conectar con la base de datos
def conectar_bd():
    return sqlite3.connect("produccion.db")

# Función para crear las tablas si no existen
def crear_tablas():
    conn = conectar_bd()
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        numero_empleado TEXT UNIQUE NOT NULL,
        nombre TEXT NOT NULL,
        contraseña TEXT NOT NULL
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS produccion (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        fecha TEXT NOT NULL,
        turno TEXT NOT NULL,
        medida TEXT NOT NULL,
        piezas_producidas INTEGER NOT NULL,
        piezas_defectuosas INTEGER NOT NULL,
        piezas_buenas INTEGER NOT NULL,
        frames_descartados INTEGER NOT NULL,
        FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS scarl_post (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        fecha TEXT NOT NULL,
        motivo TEXT NOT NULL,
        tiempo_detenido INTEGER NOT NULL,
        FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
    )''')

    conn.commit()
    conn.close()

# Función para registrar producción
def registrar_produccion(usuario_id, turno, medida, piezas_producidas, piezas_defectuosas, frames_descartados):
    piezas_buenas = piezas_producidas - piezas_defectuosas
    conn = conectar_bd()
    cursor = conn.cursor()
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO produccion (usuario_id, fecha, turno, medida, piezas_producidas, piezas_defectuosas, piezas_buenas, frames_descartados) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                   (usuario_id, fecha_actual, turno, medida, piezas_producidas, piezas_defectuosas, piezas_buenas, frames_descartados))
    conn.commit()
    conn.close()

# Función para registrar paradas del robot (Scarl Post)
def registrar_scarl_post(usuario_id, motivo, tiempo_detenido):
    conn = conectar_bd()
    cursor = conn.cursor()
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO scarl_post (usuario_id, fecha, motivo, tiempo_detenido) VALUES (?, ?, ?, ?)",
                   (usuario_id, fecha_actual, motivo, tiempo_detenido))
    conn.commit()
    conn.close()

# Crear las tablas si no existen
crear_tablas()

# Diseño de la aplicación
st.title("📊 Registro de Producción - Empresa")

# Sección para ingresar datos de producción
st.subheader("🛠 Ingresar Producción")
usuario_id = st.text_input("Número de Empleado")
turno = st.selectbox("Turno", ["Turno Noche", "Turno Día"])
medida = st.text_input("Medida en Trabajo")
piezas_producidas = st.number_input("Piezas Producidas", min_value=0, step=1)
piezas_defectuosas = st.number_input("Piezas Defectuosas", min_value=0, step=1)
frames_descartados = st.number_input("Frames Descartados", min_value=0, step=1)

if st.button("✅ Registrar Producción"):
    if usuario_id:
        registrar_produccion(usuario_id, turno, medida, piezas_producidas, piezas_defectuosas, frames_descartados)
        st.success("✅ Producción registrada correctamente.")
    else:
        st.warning("⚠️ Debes ingresar tu número de empleado.")

# Sección para ingresar Scarl Post (paradas del robot)
st.subheader("⚠️ Registro de Paradas del Robot (Scarl Post)")
motivo = st.text_input("Motivo de la Parada")
tiempo_detenido = st.number_input("Tiempo Detenido (minutos)", min_value=0, step=1)

if st.button("⏸ Registrar Parada"):
    if usuario_id and motivo:
        registrar_scarl_post(usuario_id, motivo, tiempo_detenido)
        st.success("✅ Parada registrada correctamente.")
    else:
        st.warning("⚠️ Debes ingresar el número de empleado y el motivo.")

# Mostrar registros recientes
st.subheader("📋 Últimos Registros de Producción")
conn = conectar_bd()
cursor = conn.cursor()
cursor.execute("SELECT fecha, turno, medida, piezas_producidas, piezas_defectuosas, piezas_buenas, frames_descartados FROM produccion ORDER BY fecha DESC LIMIT 5")
produccion_data = cursor.fetchall()
conn.close()

for row in produccion_data:
    st.write(f"📅 {row[0]} - {row[1]} | {row[2]} - Producción: {row[3]} piezas (Defectuosas: {row[4]} | Buenas: {row[5]}) | Frames descartados: {row[6]}")

st.subheader("🔍 Últimos Registros de Paradas del Robot")
conn = conectar_bd()
cursor = conn.cursor()
cursor.execute("SELECT fecha, motivo, tiempo_detenido FROM scarl_post ORDER BY fecha DESC LIMIT 5")
scarl_data = cursor.fetchall()
conn.close()

for row in scarl_data:
    st.write(f"📅 {row[0]} | Motivo: {row[1]} | ⏳ Tiempo detenido: {row[2]} minutos")
