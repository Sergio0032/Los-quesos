import streamlit as st
import pandas as pd
import os
import base64


directorio_actual = os.path.dirname(os.path.abspath(__file__))
ruta_logo = os.path.join(directorio_actual, "..", "logo.png")

try:
    with open(ruta_logo, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()

    # 3. Inyectamos el Banner con HTML y CSS
    st.markdown(
        f"""
        <div style="
            width: 100%;
            height: 150px; 
            background-color: #0B132B; /* Color de fondo oscuro. Ajusta este código HEX si no coincide exacto */
            background-image: url('data:image/png;base64,{encoded_string}');
            background-size: contain;
            background-repeat: no-repeat;
            background-position: center;
            border-radius: 10px;
            margin-bottom: 20px;
        "></div>
        """,
        unsafe_allow_html=True
    )
except FileNotFoundError:
    st.error("No se encontró el archivo logo.png")
# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Apuestas",
    layout="wide"
)

# --- 2. ESTILO PROFESIONAL (TONOS EXACTOS DE LAS IMÁGENES) ---
# Sidebar: #EBF2F6 (Gris azulado pálido)
# Títulos: #1D3557 (Azul oscuro institucional)
# Acento: #E63946 (Rojo)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;600;900&display=swap');
    
    /* Fondo blanco para el contenido principal */
    .main {
        background-color: #FFFFFF;
    }
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }

    /* Cabecera: Título y línea azul gruesa */
    .brand-header {
        padding: 20px 0 10px 0;
        background-color: #FFFFFF;
        border-bottom: 5px solid #1D3557; 
        margin-bottom: 40px;
    }
    .brand-title {
        font-size: 50px;
        font-weight: 900;
        letter-spacing: -1.5px;
        color: #333333;
        text-transform: uppercase;
        margin: 0;
    }

    /* BARRA LATERAL: COLOR EXACTO #EBF2F6 */
    [data-testid="stSidebar"] {
        background-color: #EBF2F6 !important;
        border-right: 1px solid #DDE4E9;
    }
    
    /* Ajuste para que todo el contenido del sidebar herede el color */
    [data-testid="stSidebar"] > div:first-child {
        background-color: #EBF2F6 !important;
    }

    /* Etiquetas del Panel de Control en el Sidebar */
    .sidebar-label {
        font-size: 14px;
        font-weight: 800;
        color: #1D3557;
        text-transform: uppercase;
        margin-top: 20px;
        margin-bottom: 5px;
    }

    /* Estilo de los Tabs (Pestañas) con subrayado rojo */
    .stTabs [data-baseweb="tab-list"] {
        gap: 30px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 16px;
        font-weight: 700;
        color: #6C757D !important;
        text-transform: uppercase;
    }
    .stTabs [aria-selected="true"] {
        color: #E63946 !important;
        border-bottom: 4px solid #E63946 !important;
    }

    /* Tarjetas de Cuotas */
    .odds-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        padding: 35px;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .odds-label {
        color: #64748B;
        font-size: 13px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 15px;
    }
    .odds-value {
        color: #D4AF37; 
        font-size: 50px;
        font-weight: 900;
    }

    /* Estilo para los Selectores de Streamlit */
    div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        border: 1px solid #CED4DA !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. BASE DE DATOS (5 GRANDES LIGAS) ---
datos_ligas = {
    "LaLiga (España)": {
        "total": 20, "equipos": {
            "Real Madrid": {"pos": 1, "gf": 82, "gc": 22}, "FC Barcelona": {"pos": 2, "gf": 79, "gc": 25},
            "Atlético de Madrid": {"pos": 3, "gf": 65, "gc": 30}, "Villarreal CF": {"pos": 4, "gf": 60, "gc": 35},
            "Real Sociedad": {"pos": 5, "gf": 55, "gc": 32}, "Athletic Club": {"pos": 6, "gf": 52, "gc": 38},
            "Girona FC": {"pos": 7, "gf": 68, "gc": 45}, "Real Betis": {"pos": 8, "gf": 48, "gc": 42},
            "CA Osasuna": {"pos": 9, "gf": 40, "gc": 40}, "Sevilla FC": {"pos": 10, "gf": 45, "gc": 50}
        }
    },
    "Premier League (Inglaterra)": {
        "total": 20, "equipos": {
            "Manchester City": {"pos": 1, "gf": 94, "gc": 30}, "Arsenal": {"pos": 2, "gf": 88, "gc": 28},
            "Liverpool": {"pos": 3, "gf": 85, "gc": 35}, "Chelsea": {"pos": 4, "gf": 72, "gc": 40},
            "Aston Villa": {"pos": 5, "gf": 70, "gc": 45}, "Tottenham": {"pos": 6, "gf": 74, "gc": 55}
        }
    },
    "Serie A (Italia)": { "total": 20, "equipos": {"Inter Milan": {"pos": 1, "gf": 85, "gc": 20}, "Juventus": {"pos": 2, "gf": 65, "gc": 18}, "AC Milan": {"pos": 3, "gf": 70, "gc": 35}} },
    "Bundesliga (Alemania)": { "total": 18, "equipos": {"Bayer Leverkusen": {"pos": 1, "gf": 88, "gc": 24}, "Bayern Munich": {"pos": 2, "gf": 92, "gc": 30}} },
    "Ligue 1 (Francia)": { "total": 18, "equipos": {"Paris Saint-Germain": {"pos": 1, "gf": 85, "gc": 22}, "Monaco": {"pos": 2, "gf": 68, "gc": 38}} }
}

# --- 4. MOTOR DE CÁLCULO ---
def calcular_cuotas_champagne(sl, sv, n):
    f_l = (sl["gf"] / max(1, sl["gc"])) * (n - sl["pos"] + 1) * 1.15
    f_v = (sv["gf"] / max(1, sv["gc"])) * (n - sv["pos"] + 1)
    den = f_l + f_v + (n * 0.45)
    p_l = f_l / den
    p_v = f_v / den
    p_e = 1 - p_l - p_v
    return round(1/p_l, 2), round(1/p_e, 2), round(1/p_v, 2)

# --- 5. PANEL DE CONTROL (SIDEBAR #EBF2F6) ---
with st.sidebar:
    st.markdown('<p style="font-size: 18px; font-weight: 900; color: #1D3557; margin-bottom: 20px;">MENU</p>', unsafe_allow_html=True)
    st.markdown("""
        <div style="color: #457B9D; font-weight: 600; line-height: 2.5;">
            Apuestas 💸<br>Calendario<br>Jugadores ⚽<br>Ligas 🏆<br>Partidos ⚔️
        </div>
        <hr style="border-top: 1px solid #DDE4E9;">
    """, unsafe_allow_html=True)
    
    st.markdown('<p class="sidebar-label">PANEL DE CONTROL</p>', unsafe_allow_html=True)
    
    st.markdown('<p class="sidebar-label">ELEGIR COMPETICIÓN</p>', unsafe_allow_html=True)
    liga_sel = st.selectbox("", list(datos_ligas.keys()), label_visibility="collapsed")
    
    equipos_disponibles = sorted(list(datos_ligas[liga_sel]["equipos"].keys()))
    
    st.markdown('<p class="sidebar-label">EQUIPO LOCAL</p>', unsafe_allow_html=True)
    local = st.selectbox("L", equipos_disponibles, index=0, label_visibility="collapsed")
    
    st.markdown('<p class="sidebar-label">EQUIPO VISITANTE</p>', unsafe_allow_html=True)
    visitante = st.selectbox("V", equipos_disponibles, index=1, label_visibility="collapsed")
    
    st.markdown("---")
    st.markdown('<p class="sidebar-label">CASA DE APUESTAS</p>', unsafe_allow_html=True)
    bookie = st.selectbox("B", ["Bet365", "Winamax", "Betfair", "Bwin", "Luckia"], label_visibility="collapsed")

# --- 6. INTERFAZ PRINCIPAL ---
st.markdown("""
    <div class="brand-header">
        <h1 class="brand-title">Fútbol Champagne Pro</h1>
    </div>
    """, unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["ANÁLISIS 1X2", "GESTIÓN DE BANCA", "INFORME TÉCNICO"])

with tab1:
    if local == visitante:
        st.warning("Seleccione dos equipos distintos para proceder.")
    else:
        cl, ce, cv = calcular_cuotas_champagne(
            datos_ligas[liga_sel]["equipos"][local], 
            datos_ligas[liga_sel]["equipos"][visitante], 
            datos_ligas[liga_sel]["total"]
        )
        
        st.markdown(f"<h3 style='color: #1D3557;'>COMPARATIVA: {local.upper()} VS {visitante.upper()}</h3>", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f'<div class="odds-card"><div class="odds-label">GANA {local.upper()}</div><div class="odds-value">{cl}</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="odds-card"><div class="odds-label">EMPATE</div><div class="odds-value">{ce}</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="odds-card"><div class="odds-label">GANA {visitante.upper()}</div><div class="odds-value">{cv}</div></div>', unsafe_allow_html=True)

with tab2:
    st.markdown(f"<h3 style='color: #1D3557;'>SIMULADOR DE BANCA: {bookie.upper()}</h3>", unsafe_allow_html=True)
    col_money, col_res = st.columns(2)
    
    with col_money:
        apuesta = st.number_input("CANTIDAD A INVERTIR (DE 5€ EN 5€)", min_value=5, value=10, step=5)
        cuota_mercado = st.number_input(f"CUOTA ACTUAL EN {bookie.upper()}", value=cl if 'cl' in locals() else 2.0, step=0.01)
    
    with col_res:
        neto = round((apuesta * cuota_mercado) - apuesta, 2)
        st.markdown("#### BENEFICIO NETO PROYECTADO")
        st.markdown(f"<h1 style='color: #1D3557; font-size: 60px;'>{neto} €</h1>", unsafe_allow_html=True)

with tab3:
    st.markdown("<h2 style='color: #1D3557;'>VERDICTO DEL ALGORITMO</h2>", unsafe_allow_html=True)
    if 'cl' in locals():
        st.markdown(f"""
        <div style="background-color: #F8FAFC; border-left: 6px solid #1D3557; padding: 25px; border-radius: 4px;">
            <ul style="color: #334155; line-height: 1.8;">
                <li><b>Localía:</b> Se ha aplicado un corrector positivo al {local}.</li>
                <li><b>Goles:</b> Basado en los goles marcados y recibidos de ambos conjuntos.</li>
                <li><b>Mercado:</b> La cuota matemática pura es de {cl}.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")
st.caption("© 2026 Fútbol Champagne Pro | Datos en tiempo real | +18 Juega con responsabilidad")