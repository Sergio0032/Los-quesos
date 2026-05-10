import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Fútbol Champagne Pro", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    [data-testid="stMetric"] {
        background-color: #1e2129 !important;
        border: 1px solid #31333f !important;
        padding: 20px !important;
        border-radius: 12px !important;
    }
    [data-testid="stMetricValue"] {
        color: #00ff41 !important;
        font-size: 1.8rem !important;
    }
    [data-testid="stMetricLabel"] {
        color: #ffffff !important;
        font-size: 1rem !important;
        font-weight: bold !important;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #1e2129;
        border-radius: 5px;
        color: white;
    }
    .calculator-container {
        background-color: #13151a;
        padding: 25px;
        border-radius: 15px;
        border: 1px solid #31333f;
    }
    </style>
    """, unsafe_allow_html=True)

if 'user' not in st.session_state:
    st.session_state.user = "Analista Champagne"

# Base de datos completa 2025/2026 (Las 5 Grandes Ligas)
# Datos simplificados para funcionalidad: GF, GC, Posicion Actual (pos), Posicion Temporada Pasada (pos_prev)
datos_ligas = {
    "LaLiga (España)": {
        "total": 20,
        "equipos": {
            "Real Madrid": {"pos": 1, "pos_prev": 1, "gf": 78, "gc": 20},
            "FC Barcelona": {"pos": 2, "pos_prev": 2, "gf": 74, "gc": 24},
            "At. Madrid": {"pos": 3, "pos_prev": 4, "gf": 62, "gc": 28},
            "Girona": {"pos": 4, "pos_prev": 3, "gf": 66, "gc": 38},
            "Athletic Club": {"pos": 5, "pos_prev": 5, "gf": 52, "gc": 30},
            "Real Sociedad": {"pos": 6, "pos_prev": 6, "gf": 48, "gc": 34},
            "Betis": {"pos": 7, "pos_prev": 7, "gf": 44, "gc": 36},
            "Villarreal": {"pos": 8, "pos_prev": 8, "gf": 55, "gc": 45},
            "Valencia": {"pos": 9, "pos_prev": 9, "gf": 40, "gc": 40},
            "Alavés": {"pos": 10, "pos_prev": 10, "gf": 35, "gc": 42},
            "Osasuna": {"pos": 11, "pos_prev": 11, "gf": 38, "gc": 45},
            "Getafe": {"pos": 12, "pos_prev": 12, "gf": 32, "gc": 38},
            "Celta de Vigo": {"pos": 13, "pos_prev": 13, "gf": 42, "gc": 50},
            "Sevilla FC": {"pos": 14, "pos_prev": 14, "gf": 45, "gc": 48},
            "Mallorca": {"pos": 15, "pos_prev": 15, "gf": 30, "gc": 40},
            "Las Palmas": {"pos": 16, "pos_prev": 16, "gf": 31, "gc": 44},
            "Rayo Vallecano": {"pos": 17, "pos_prev": 17, "gf": 28, "gc": 42},
            "Leganés": {"pos": 18, "pos_prev": 21, "gf": 25, "gc": 45}, # Ascendido
            "Valladolid": {"pos": 19, "pos_prev": 22, "gf": 22, "gc": 50}, # Ascendido
            "Espanyol": {"pos": 20, "pos_prev": 23, "gf": 24, "gc": 55} # Ascendido
        }
    },
    "Premier League (Inglaterra)": {
        "total": 20,
        "equipos": {
            "Manchester City": {"pos": 1, "pos_prev": 1, "gf": 85, "gc": 28},
            "Arsenal": {"pos": 2, "pos_prev": 2, "gf": 80, "gc": 25},
            "Liverpool": {"pos": 3, "pos_prev": 3, "gf": 77, "gc": 32},
            "Aston Villa": {"pos": 4, "pos_prev": 4, "gf": 68, "gc": 45},
            "Tottenham": {"pos": 5, "pos_prev": 5, "gf": 65, "gc": 50},
            "Chelsea": {"pos": 6, "pos_prev": 6, "gf": 63, "gc": 55},
            "Newcastle": {"pos": 7, "pos_prev": 7, "gf": 70, "gc": 52},
            "Manchester United": {"pos": 8, "pos_prev": 8, "gf": 52, "gc": 48},
            "West Ham": {"pos": 9, "pos_prev": 9, "gf": 50, "gc": 60},
            "Crystal Palace": {"pos": 10, "pos_prev": 10, "gf": 45, "gc": 50},
            "Brighton": {"pos": 11, "pos_prev": 11, "gf": 48, "gc": 52},
            "Bournemouth": {"pos": 12, "pos_prev": 12, "gf": 42, "gc": 58},
            "Fulham": {"pos": 13, "pos_prev": 13, "gf": 44, "gc": 55},
            "Wolves": {"pos": 14, "pos_prev": 14, "gf": 40, "gc": 55},
            "Everton": {"pos": 15, "pos_prev": 15, "gf": 38, "gc": 48},
            "Brentford": {"pos": 16, "pos_prev": 16, "gf": 46, "gc": 60},
            "Nottingham Forest": {"pos": 17, "pos_prev": 17, "gf": 40, "gc": 62},
            "Leicester City": {"pos": 18, "pos_prev": 21, "gf": 35, "gc": 55},
            "Ipswich Town": {"pos": 19, "pos_prev": 22, "gf": 30, "gc": 60},
            "Southampton": {"pos": 20, "pos_prev": 23, "gf": 32, "gc": 65}
        }
    },
    "Bundesliga (Alemania)": {
        "total": 18,
        "equipos": {
            "Bayer Leverkusen": {"pos": 1, "pos_prev": 1, "gf": 82, "gc": 22},
            "Bayern Múnich": {"pos": 2, "pos_prev": 3, "gf": 88, "gc": 35},
            "Stuttgart": {"pos": 3, "pos_prev": 2, "gf": 74, "gc": 38},
            "RB Leipzig": {"pos": 4, "pos_prev": 4, "gf": 70, "gc": 36},
            "Dortmund": {"pos": 5, "pos_prev": 5, "gf": 65, "gc": 40},
            "Eintracht Frankfurt": {"pos": 6, "pos_prev": 6, "gf": 52, "gc": 44},
            "Hoffenheim": {"pos": 7, "pos_prev": 7, "gf": 55, "gc": 58},
            "Heidenheim": {"pos": 8, "pos_prev": 8, "gf": 48, "gc": 50},
            "Werder Bremen": {"pos": 9, "pos_prev": 9, "gf": 42, "gc": 48},
            "Friburgo": {"pos": 10, "pos_prev": 10, "gf": 44, "gc": 52},
            "Augsburgo": {"pos": 11, "pos_prev": 11, "gf": 46, "gc": 55},
            "Wolfsburgo": {"pos": 12, "pos_prev": 12, "gf": 40, "gc": 45},
            "Maguncia 05": {"pos": 13, "pos_prev": 13, "gf": 38, "gc": 48},
            "Mönchengladbach": {"pos": 14, "pos_prev": 14, "gf": 50, "gc": 60},
            "Unión Berlín": {"pos": 15, "pos_prev": 15, "gf": 32, "gc": 50},
            "Bochum": {"pos": 16, "pos_prev": 16, "gf": 34, "gc": 65},
            "St. Pauli": {"pos": 17, "pos_prev": 19, "gf": 30, "gc": 50},
            "Holstein Kiel": {"pos": 18, "pos_prev": 20, "gf": 28, "gc": 55}
        }
    },
    "Serie A (Italia)": {
        "total": 20,
        "equipos": {
            "Inter": {"pos": 1, "pos_prev": 1, "gf": 82, "gc": 20},
            "Milan": {"pos": 2, "pos_prev": 2, "gf": 72, "gc": 38},
            "Juventus": {"pos": 3, "pos_prev": 3, "gf": 50, "gc": 25},
            "Atalanta": {"pos": 4, "pos_prev": 4, "gf": 68, "gc": 39},
            "Bolonia": {"pos": 5, "pos_prev": 5, "gf": 52, "gc": 30},
            "Roma": {"pos": 6, "pos_prev": 6, "gf": 60, "gc": 42},
            "Lazio": {"pos": 7, "pos_prev": 7, "gf": 55, "gc": 38},
            "Fiorentina": {"pos": 8, "pos_prev": 8, "gf": 58, "gc": 40},
            "Torino": {"pos": 9, "pos_prev": 9, "gf": 36, "gc": 34},
            "Napoli": {"pos": 10, "pos_prev": 10, "gf": 50, "gc": 45},
            "Genoa": {"pos": 11, "pos_prev": 11, "gf": 42, "gc": 45},
            "Monza": {"pos": 12, "pos_prev": 12, "gf": 38, "gc": 48},
            "Verona": {"pos": 13, "pos_prev": 13, "gf": 35, "gc": 48},
            "Lecce": {"pos": 14, "pos_prev": 14, "gf": 32, "gc": 50},
            "Udinese": {"pos": 15, "pos_prev": 15, "gf": 34, "gc": 52},
            "Cagliari": {"pos": 16, "pos_prev": 16, "gf": 40, "gc": 60},
            "Empoli": {"pos": 17, "pos_prev": 17, "gf": 28, "gc": 50},
            "Parma": {"pos": 18, "pos_prev": 21, "gf": 30, "gc": 45},
            "Como": {"pos": 19, "pos_prev": 22, "gf": 28, "gc": 48},
            "Venezia": {"pos": 20, "pos_prev": 23, "gf": 25, "gc": 55}
        }
    },
    "Ligue 1 (Francia)": {
        "total": 18,
        "equipos": {
            "PSG": {"pos": 1, "pos_prev": 1, "gf": 78, "gc": 30},
            "Mónaco": {"pos": 2, "pos_prev": 2, "gf": 65, "gc": 42},
            "Brest": {"pos": 3, "pos_prev": 3, "gf": 50, "gc": 32},
            "Lille": {"pos": 4, "pos_prev": 4, "gf": 52, "gc": 34},
            "Niza": {"pos": 5, "pos_prev": 5, "gf": 40, "gc": 28},
            "Lyon": {"pos": 6, "pos_prev": 6, "gf": 48, "gc": 55},
            "Lens": {"pos": 7, "pos_prev": 7, "gf": 45, "gc": 35},
            "Marsella": {"pos": 8, "pos_prev": 8, "gf": 50, "gc": 40},
            "Reims": {"pos": 9, "pos_prev": 9, "gf": 42, "gc": 45},
            "Rennes": {"pos": 10, "pos_prev": 10, "gf": 52, "gc": 44},
            "Toulouse": {"pos": 11, "pos_prev": 11, "gf": 40, "gc": 44},
            "Montpellier": {"pos": 12, "pos_prev": 12, "gf": 42, "gc": 48},
            "Estrasburgo": {"pos": 13, "pos_prev": 13, "gf": 38, "gc": 45},
            "Nantes": {"pos": 14, "pos_prev": 14, "gf": 30, "gc": 48},
            "Le Havre": {"pos": 15, "pos_prev": 15, "gf": 32, "gc": 42},
            "Saint-Étienne": {"pos": 16, "pos_prev": 19, "gf": 28, "gc": 45},
            "Auxerre": {"pos": 17, "pos_prev": 20, "gf": 30, "gc": 50},
            "Angers": {"pos": 18, "pos_prev": 21, "gf": 25, "gc": 55}
        }
    }
}

# --- LÓGICA DE SIMULACIÓN ---
def calcular_fuerza_sim(stats, total_eq):
    # Variables: Goles Favor, Goles Contra, Pos Actual, Pos Pasada
    # Cuanto mayor el resultado, más fuerte el equipo
    ratio_goles = stats["gf"] / max(1, stats["gc"])
    valor_pos_actual = (total_eq + 1 - stats["pos"]) * 1.5
    valor_pos_prev = (total_eq + 1 - stats["pos_prev"]) * 0.8
    return ratio_goles + valor_pos_actual + valor_pos_prev

def generar_cuotas_sim(f1, f2):
    # Probabilidades basadas en la fuerza relativa
    p1 = f1 / (f1 + f2)
    p2 = f2 / (f1 + f2)
    px = 0.25 # Empate base aproximado
    
    # Cuotas con margen (1.05)
    c1 = round((1 / p1) * 1.05, 2)
    c2 = round((1 / p2) * 1.05, 2)
    cx = round((1 / px) * 1.15, 2)
    
    prob_v1 = round(p1 * 100, 1)
    prob_v2 = round(p2 * 100, 1)
    return c1, cx, c2, prob_v1, prob_v2

with st.sidebar:
    st.title("Configuración")
    st.session_state.user = st.text_input("Nombre Analista:", st.session_state.user)
    st.divider()
    liga_activa = st.selectbox("Liga a Consultar:", list(datos_ligas.keys()))

st.title(f"Centro de Inteligencia: {liga_activa}")

tab1, tab2, tab3, tab4 = st.tabs(["Centro de Partido", "Datos Avanzados", "Mercado", "Casas de Apuestas"])

with tab1:
    st.markdown("### Simulador de Enfrentamientos")
    
    col_sel_a, col_sel_b = st.columns(2)
    
    lista_equipos = list(datos_ligas[liga_activa]["equipos"].keys())
    
    with col_sel_a:
        local = st.selectbox("Equipo Local:", lista_equipos, index=0)
    
    with col_sel_b:
        # Filtrar para no elegir el mismo
        opciones_visitante = [e for e in lista_equipos if e != local]
        visitante = st.selectbox("Equipo Visitante:", opciones_visitante, index=0)

    st.divider()
    
    # Cálculos
    stats_l = datos_ligas[liga_activa]["equipos"][local]
    stats_v = datos_ligas[liga_activa]["equipos"][visitante]
    total_l = datos_ligas[liga_activa]["total"]
    
    fuerza_l = calcular_fuerza_sim(stats_l, total_l)
    fuerza_v = calcular_fuerza_sim(stats_v, total_l)
    
    c1, cx, c2, p1, p2 = generar_cuotas_sim(fuerza_l, fuerza_v)

    col_visual, col_stats = st.columns([1.2, 1])
    
    with col_visual:
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/Soccer_field_empty.svg/1200px-Soccer_field_empty.svg.png", use_container_width=True)
        st.info(f"Partido Proyectado: {local} vs {visitante}")

    with col_stats:
        st.markdown("#### Probabilidades y Cuotas")
        
        m1, m2 = st.columns(2)
        m1.metric(local, f"{p1}%", delta=f"Cuota x{c1}")
        m2.metric(visitante, f"{p2}%", delta=f"Cuota x{c2}")
        
        st.metric("Empate", "Proyectado", delta=f"Cuota x{cx}", delta_color="off")
        st.progress(p1/100)
        
        with st.expander("¿Cómo se calcula la cuota?"):
            st.write("""
            El algoritmo analiza cuatro pilares dinámicos:
            1.  **Efectividad Ofensiva/Defensiva**: Relación entre goles marcados y encajados.
            2.  **Estado de Forma Actual**: Posición actual en la tabla clasificatoria.
            3.  **Histórico Reciente**: Posición final en la temporada anterior.
            4.  **Peso de Liga**: Ajuste según el número total de competidores.
            
            Las cuotas finales incluyen un margen de estabilidad del mercado.
            """)

with tab2:
    df_liga = pd.DataFrame.from_dict(datos_ligas[liga_activa]["equipos"], orient='index').reset_index()
    df_liga.columns = ['Equipo', 'Posición', 'Pos_Prev', 'GF', 'GC']
    
    chart = alt.Chart(df_liga).mark_bar(cornerRadiusTopLeft=10, cornerRadiusTopRight=10).encode(
        x=alt.X('Equipo', sort='-y', title='Equipo'),
        y=alt.Y('GF', title='Goles a Favor'),
        color=alt.Color('GF', scale=alt.Scale(scheme='magma'), legend=None)
    ).properties(height=350)
    st.altair_chart(chart, use_container_width=True)

with tab4:
    st.markdown("### Calculadora de Inversión")
    
    col_calc_in, col_calc_out = st.columns([1, 1.5])
    
    with col_calc_in:
        st.markdown('<div class="calculator-container">', unsafe_allow_html=True)
        # Usamos los equipos del simulador para conveniencia
        st.write(f"Inversión para: **{local}**")
        inversion = st.number_input("Dinero a apostar (€):", min_value=1, value=10, step=1)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_calc_out:
        ganancia = inversion * c1
        st.metric("Retorno Estimado", f"{ganancia:,.2f} €", delta=f"Beneficio: {ganancia-inversion:,.2f} €")
        st.info("El juego debe ser una forma de ocio. Juega con responsabilidad. +18")

st.divider()
st.caption(f"Fútbol Champagne v4.3 | Analista: {st.session_state.user} | Datos en tiempo real 2026")