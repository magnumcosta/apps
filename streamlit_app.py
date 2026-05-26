import streamlit as st

# -----------------------------------
# CONFIGURACIÓN
# -----------------------------------

st.set_page_config(
    page_title="Cerrador Pro",
    page_icon="💰",
    layout="wide"
)

# -----------------------------------
# ESTILOS
# -----------------------------------

st.markdown("""
<style>

.main {
    background-color: #f7f9fc;
}

.box {
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 10px;
}

.aprobado {
    background-color: #d4edda;
    color: #155724;
}

.denegado {
    background-color: #f8d7da;
    color: #721c24;
}

.comision {
    background-color: #fff3cd;
    color: #856404;
    font-size: 22px;
    font-weight: bold;
}

.destino {
    background-color: #e0f7fa;
    color: #006064;
    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)

st.title("💰 Cerrador Pro - Vacaciones Tropicales")

# -----------------------------------
# BASE DE DATOS
# -----------------------------------

zonas = {
    "California": "Costa Oeste",
    "Texas": "Zona Central",
    "Florida": "Costa Este",
    "New York": "Costa Este",
    "Puerto Rico": "Puerto Rico"
}

hoteles = {
    "Orlando": ["Avanti", "Buena Vista Suites"],
    "Vegas": ["Tuscany Suites"],
    "Cancún": ["Oasis Palm Lite", "Villa del Palmar"],
    "Punta Cana": ["Ancora"]
}

horarios = {
    "Costa Oeste": "6 AM - 2 PM",
    "Zona Central": "7 AM - 4 PM",
    "Costa Este": "9 AM - 5 PM",
    "Puerto Rico": "10 AM - 5 PM"
}

# -----------------------------------
# SIDEBAR
# -----------------------------------

st.sidebar.header("📋 Datos")

estado = st.sidebar.selectbox(
    "Estado",
    list(zonas.keys())
)

estado_civil = st.sidebar.selectbox(
    "Estado Civil",
    [
        "Casado / Convive",
        "Mujer Soltera",
        "Hombre Soltero"
    ]
)

edad = st.sidebar.number_input(
    "Edad",
    18,
    100,
    35
)

residencia = st.sidebar.selectbox(
    "¿Residente USA/Canadá?",
    ["Sí", "No"]
)

porcentaje = st.sidebar.radio(
    "Comisión",
    [6, 8]
) / 100

ventas = st.sidebar.number_input(
    "Cantidad de paquetes",
    1,
    20,
    1
)

# -----------------------------------
# LÓGICA
# -----------------------------------

zona = zonas[estado]

califica = False
paquete = "MIX & MATCH"
motivo = ""
vigencia = "24 meses"

if residencia == "Sí":

    if estado_civil == "Casado / Convive":

        if 25 <= edad <= 79:
            califica = True
            paquete = "VDL"
            vigencia = "18 meses"

    elif estado_civil == "Mujer Soltera":

        if 25 <= edad <= 72:
            califica = True
            paquete = "HÍBRIDO"
            vigencia = "18 meses"

    elif estado_civil == "Hombre Soltero":

        if 35 <= edad <= 59:
            califica = True
            paquete = "VDL"
            vigencia = "18 meses"

if not califica:
    motivo = "No cumple los requisitos"

# -----------------------------------
# INTERFAZ
# -----------------------------------

col1, col2 = st.columns(2)

# -------- COLUMNA 1 --------

with col1:

    st.subheader("📦 Resultado")

    if califica:
        st.markdown(f"""
        <div class="box aprobado">
        ✅ CALIFICA PARA {paquete}
        <br>
        Vigencia: {vigencia}
        </div>
        """, unsafe_allow_html=True)

    else:
        st.markdown(f"""
        <div class="box denegado">
        ❌ ENVIAR A MIX & MATCH
        <br>
        {motivo}
        </div>
        """, unsafe_allow_html=True)

    st.subheader("🌴 Destinos")

    destinos = list(hoteles.keys())

    for destino in destinos:

        st.markdown(f"""
        <div class="box destino">
        {destino}
        </div>
        """, unsafe_allow_html=True)

        for hotel in hoteles[destino]:
            st.write("🏨", hotel)

# -------- COLUMNA 2 --------

with col2:

    st.subheader("🗺️ Zona")

    st.info(f"""
    Zona detectada: {zona}

    Horario:
    {horarios[zona]}
    """)

    st.subheader("💰 Comisión")

    deducible = st.number_input(
        "Monto deducible",
        150,
        500,
        399
    )

    ganancia = deducible * porcentaje
    total = ganancia * ventas

    st.markdown(f"""
    <div class="box comision">

    ${total:,.2f} USD

    <br><br>

    • Ganancia unidad:
    ${ganancia:,.2f}

    </div>
    """, unsafe_allow_html=True)

    st.subheader("🗣️ Speech")

    if paquete in ["VDL", "HÍBRIDO"]:

        st.success("""
        Hola, ganó unas vacaciones...
        solo debe cubrir el deducible.
        """)

    else:

        st.warning("""
        Incluye crucero Bahamas
        con vigencia de 24 meses.
        """)
