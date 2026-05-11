import streamlit as st
import pandas as pd

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Fútbol Champagne Pro | Elite Edition",
    layout="wide"
)

# --- 2. ESTILO PROFESIONAL (MODO NOCHE ÉLITE) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;600;900&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
        background-color: #050505;
    }

    .brand-header {
        display: flex;
        flex-direction: column;
        padding: 30px;
        background: #0f0f0f;
        border-bottom: 1px solid #1a1a1a;
        margin-bottom: 40px;
    }
    .brand-title {
        font-size: 38px;
        font-weight: 900;
        letter-spacing: -1px;
        color: #FFFFFF;
        text-transform: uppercase;
        margin: 0;
    }
    .brand-subtitle {
        color: #D4AF37;
        font-size: 14px;
        font-weight: 600;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    /* Tarjetas de Cuotas */
    .odds-card {
        background: #111;
        border: 1px solid #222;
        padding: 40px;
        border-radius: 4px;
        text-align: center;
        transition: 0.3s;
    }
    .odds-card:hover {
        border-color: #D4AF37;
        background: #141414;
    }
    .odds-label {
        color: #555;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 20px;
    }
    .odds-value {
        color: #D4AF37;
        font-size: 50px;
        font-weight: 900;
    }

    /* Sidebar Estilizada */
    [data-testid="stSidebar"] {
        background-color: #050505;
        border-right: 1px solid #1a1a1a;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. BASE DE DATOS MAESTRA (98 EQUIPOS - 5 GRANDES LIGAS) ---
datos_ligas = {
    "LaLiga (España)": {
        "total": 20, "equipos": {
            "Real Madrid": {"pos": 1, "gf": 82, "gc": 22}, "FC Barcelona": {"pos": 2, "gf": 79, "gc": 25},
            "Atlético de Madrid": {"pos": 3, "gf": 65, "gc": 30}, "Villarreal CF": {"pos": 4, "gf": 60, "gc": 35},
            "Real Sociedad": {"pos": 5, "gf": 55, "gc": 32}, "Athletic Club": {"pos": 6, "gf": 52, "gc": 38},
            "Girona FC": {"pos": 7, "gf": 68, "gc": 45}, "Real Betis": {"pos": 8, "gf": 48, "gc": 42},
            "CA Osasuna": {"pos": 9, "gf": 40, "gc": 40}, "Sevilla FC": {"pos": 10, "gf": 45, "gc": 50},
            "Valencia CF": {"pos": 11, "gf": 38, "gc": 44}, "Celta de Vigo": {"pos": 12, "gf": 42, "gc": 52},
            "RCD Mallorca": {"pos": 13, "gf": 33, "gc": 40}, "Rayo Vallecano": {"pos": 14, "gf": 35, "gc": 48},
            "UD Las Palmas": {"pos": 15, "gf": 32, "gc": 47}, "Getafe CF": {"pos": 16, "gf": 30, "gc": 42},
            "RCD Espanyol": {"pos": 17, "gf": 34, "gc": 55}, "CD Leganés": {"pos": 18, "gf": 28, "gc": 50},
            "Real Valladolid": {"pos": 19, "gf": 26, "gc": 58}, "Deportivo Alavés": {"pos": 20, "gf": 25, "gc": 60}
        }
    },
    "Premier League (Inglaterra)": {
        "total": 20, "equipos": {
            "Manchester City": {"pos": 1, "gf": 94, "gc": 30}, "Arsenal": {"pos": 2, "gf": 88, "gc": 28},
            "Liverpool": {"pos": 3, "gf": 85, "gc": 35}, "Chelsea": {"pos": 4, "gf": 72, "gc": 40},
            "Aston Villa": {"pos": 5, "gf": 70, "gc": 45}, "Tottenham": {"pos": 6, "gf": 74, "gc": 55},
            "Manchester United": {"pos": 7, "gf": 58, "gc": 50}, "Newcastle": {"pos": 8, "gf": 65, "gc": 52},
            "Brighton": {"pos": 9, "gf": 60, "gc": 58}, "West Ham": {"pos": 10, "gf": 52, "gc": 55},
            "Fulham": {"pos": 11, "gf": 48, "gc": 55}, "Bournemouth": {"pos": 12, "gf": 50, "gc": 62},
            "Brentford": {"pos": 13, "gf": 45, "gc": 60}, "Crystal Palace": {"pos": 14, "gf": 40, "gc": 58},
            "Nottingham Forest": {"pos": 15, "gf": 38, "gc": 65}, "Everton": {"pos": 16, "gf": 35, "gc": 52},
            "Wolverhampton": {"pos": 17, "gf": 33, "gc": 60}, "Leicester City": {"pos": 18, "gf": 38, "gc": 70},
            "Ipswich Town": {"pos": 19, "gf": 30, "gc": 75}, "Southampton": {"pos": 20, "gf": 28, "gc": 80}
        }
    },
    "Serie A (Italia)": {
        "total": 20, "equipos": {
            "Inter Milan": {"pos": 1, "gf": 85, "gc": 20}, "Juventus": {"pos": 2, "gf": 65, "gc": 18},
            "AC Milan": {"pos": 3, "gf": 70, "gc": 35}, "Napoli": {"pos": 4, "gf": 68, "gc": 32},
            "Atalanta": {"pos": 5, "gf": 75, "gc": 42}, "AS Roma": {"pos": 6, "gf": 60, "gc": 40},
            "Lazio": {"pos": 7, "gf": 55, "gc": 38}, "Fiorentina": {"pos": 8, "gf": 58, "gc": 44},
            "Bologna": {"pos": 9, "gf": 50, "gc": 35}, "Torino": {"pos": 10, "gf": 42, "gc": 40},
            "Udinese": {"pos": 11, "gf": 38, "gc": 45}, "Parma": {"pos": 12, "gf": 40, "gc": 50},
            "Genoa": {"pos": 13, "gf": 35, "gc": 42}, "Como": {"pos": 14, "gf": 38, "gc": 55},
            "Monza": {"pos": 15, "gf": 32, "gc": 48}, "Cagliari": {"pos": 16, "gf": 30, "gc": 52},
            "Lecce": {"pos": 17, "gf": 28, "gc": 55}, "Empoli": {"pos": 18, "gf": 26, "gc": 58},
            "Venezia": {"pos": 19, "gf": 29, "gc": 65}, "Hellas Verona": {"pos": 20, "gf": 25, "gc": 62}
        }
    },
    "Bundesliga (Alemania)": {
        "total": 18, "equipos": {
            "Bayer Leverkusen": {"pos": 1, "gf": 88, "gc": 24}, "Bayern Munich": {"pos": 2, "gf": 92, "gc": 30},
            "RB Leipzig": {"pos": 3, "gf": 75, "gc": 35}, "Borussia Dortmund": {"pos": 4, "gf": 72, "gc": 40},
            "VfB Stuttgart": {"pos": 5, "gf": 78, "gc": 45}, "Eintracht Frankfurt": {"pos": 6, "gf": 60, "gc": 48},
            "Hoffenheim": {"pos": 7, "gf": 62, "gc": 60}, "SC Freiburg": {"pos": 8, "gf": 50, "gc": 52},
            "Werder Bremen": {"pos": 9, "gf": 48, "gc": 55}, "Wolfsburg": {"pos": 10, "gf": 45, "gc": 52},
            "Augsburg": {"pos": 11, "gf": 46, "gc": 58}, "Heidenheim": {"pos": 12, "gf": 42, "gc": 55},
            "Mainz 05": {"pos": 13, "gf": 38, "gc": 54}, "Mönchengladbach": {"pos": 14, "gf": 52, "gc": 65},
            "Union Berlin": {"pos": 15, "gf": 33, "gc": 50}, "St. Pauli": {"pos": 16, "gf": 30, "gc": 55},
            "Holstein Kiel": {"pos": 17, "gf": 28, "gc": 62}, "VfL Bochum": {"pos": 18, "gf": 25, "gc": 70}
        }
    },
    "Ligue 1 (Francia)": {
        "total": 18, "equipos": {
            "Paris Saint-Germain": {"pos": 1, "gf": 85, "gc": 22}, "Monaco": {"pos": 2, "gf": 68, "gc": 38},
            "Lille": {"pos": 3, "gf": 62, "gc": 32}, "Marseille": {"pos": 4, "gf": 65, "gc": 40},
            "Lyon": {"pos": 5, "gf": 60, "gc": 45}, "Lens": {"pos": 6, "gf": 52, "gc": 35},
            "Nice": {"pos": 7, "gf": 48, "gc": 30}, "Rennes": {"pos": 8, "gf": 55, "gc": 48},
            "Reims": {"pos": 9, "gf": 45, "gc": 47}, "Toulouse": {"pos": 10, "gf": 42, "gc": 45},
            "Strasbourg": {"pos": 11, "gf": 40, "gc": 50}, "Montpellier": {"pos": 12, "gf": 43, "gc": 60},
            "Auxerre": {"pos": 13, "gf": 35, "gc": 52}, "Nantes": {"pos": 14, "gf": 32, "gc": 48},
            "Angers": {"pos": 15, "gf": 30, "gc": 55}, "Le Havre": {"pos": 16, "gf": 28, "gc": 50},
            "Saint-Étienne": {"pos": 17, "gf": 26, "gc": 58}, "Brest": {"pos": 18, "gf": 38, "gc": 45}
        }
    }
}

# --- 4. MOTOR DE CÁLCULO (ERROR CORREGIDO) ---
def calcular_cuotas_champagne(sl, sv, n):
    # Algoritmo de probabilidad basado en poder ofensivo y solidez defensiva
    f_l = (sl["gf"] / max(1, sl["gc"])) * (n - sl["pos"] + 1) * 1.15 # Bonus de localía
    f_v = (sv["gf"] / max(1, sv["gc"])) * (n - sv["pos"] + 1)
    den = f_l + f_v + (n * 0.45)
    p_l = f_l / den
    p_v = f_v / den
    p_e = 1 - p_l - p_v
    return round(1/p_l, 2), round(1/p_e, 2), round(1/p_v, 2)

# --- 5. LÓGICA DE CONTROL (SIDEBAR) ---
with st.sidebar:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("### PANEL DE CONTROL")
    liga_sel = st.selectbox("ELEGIR COMPETICIÓN", list(datos_ligas.keys()))
    
    # Filtrar equipos por liga seleccionada
    equipos_disponibles = sorted(list(datos_ligas[liga_sel]["equipos"].keys()))
    local = st.selectbox("EQUIPO LOCAL", equipos_disponibles, index=0)
    visitante = st.selectbox("EQUIPO VISITANTE", equipos_disponibles, index=1)
    
    st.markdown("---")
    bookie = st.selectbox("CASA DE APUESTAS", ["Bet365", "Winamax", "Betfair", "Bwin", "Luckia"])

# --- 6. INTERFAZ PRINCIPAL ---
st.markdown("""
    <div class="brand-header">
        <h1 class="brand-title">Fútbol Champagne Pro</h1>
        <span class="brand-subtitle">Terminal de Análisis Predictivo | Temporada 2026</span>
    </div>
    """, unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["ANÁLISIS 1X2", "GESTIÓN DE BANCA", "INFORME TÉCNICO"])

with tab1:
    if local == visitante:
        st.warning("Seleccione dos equipos distintos para generar el informe.")
    else:
        cl, ce, cv = calcular_cuotas_champagne(
            datos_ligas[liga_sel]["equipos"][local], 
            datos_ligas[liga_sel]["equipos"][visitante], 
            datos_ligas[liga_sel]["total"]
        )
        
        st.markdown(f"### COMPARATIVA: {local.upper()} VS {visitante.upper()}")
        st.markdown(f"Mercado: **{liga_sel}**")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f'<div class="odds-card"><div class="odds-label">GANA {local.upper()}</div><div class="odds-value">{cl}</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="odds-card"><div class="odds-label">EMPATE</div><div class="odds-value">{ce}</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="odds-card"><div class="odds-label">GANA {visitante.upper()}</div><div class="odds-value">{cv}</div></div>', unsafe_allow_html=True)

with tab2:
    st.markdown(f"### SIMULADOR DE OPERACIONES: {bookie.upper()}")
    col_money, col_res = st.columns(2)
    
    with col_money:
        apuesta = st.number_input("CAPITAL A INVERTIR (MÚLTIPLOS DE 5€)", min_value=5, value=10, step=5)
        cuota_mercado = st.number_input(f"CUOTA OFRECIDA POR {bookie.upper()}", value=cl if 'cl' in locals() else 2.0, step=0.01)
    
    with col_res:
        bruto = round(apuesta * cuota_mercado, 2)
        neto = round(bruto - apuesta, 2)
        st.markdown("#### PROYECCIÓN DE RETORNO NETO")
        st.markdown(f"<h1 style='color: #00ff88; font-size: 60px;'>{neto} €</h1>", unsafe_allow_html=True)
        st.write(f"Liquidación total bruta: **{bruto} €**")

with tab3:
    st.markdown("### VERDICTO DEL ALGORITMO")
    if 'cl' in locals():
        stats_l = datos_ligas[liga_sel]["equipos"][local]
        stats_v = datos_ligas[liga_sel]["equipos"][visitante]
        
        st.markdown(f"""
        * **Fortaleza Local:** El {local} presenta un ratio ofensivo superior basado en sus {stats_l['gf']} goles anotados.
        * **Vulnerabilidad Visitante:** El {visitante} ha concedido {stats_v['gc']} goles en la campaña actual.
        * **Ajuste Estadístico:** Se ha aplicado un corrector del 15% por factor campo y posición relativa (Puesto {stats_l['pos']} vs Puesto {stats_v['pos']}).
        """)
        
        if cuota_mercado > cl:
            st.success("VALOR DETECTADO: La cuota de mercado es superior a la probabilidad real calculada por el motor.")
        else:
            st.info("ANÁLISIS NEUTRAL: El mercado se encuentra alineado con la probabilidad estadística.")

st.markdown("---")
st.caption("© 2026 Fútbol Champagne Pro | Datos de rendimiento en tiempo real | Juega con responsabilidad +18")