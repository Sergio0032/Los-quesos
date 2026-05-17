import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Fútbol Champagne Pro | 25-26",
    layout="wide"
)

# ESTILO
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;600;900&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
        background-color: #FFFFFF;
        color: #333333;
    }

    .brand-header {
        padding: 40px 0 10px 0;
        border-bottom: 5px solid #1D3557; 
        margin-bottom: 40px;
    }
    .brand-title {
        font-size: 52px;
        font-weight: 900;
        letter-spacing: -1.5px;
        color: #333333;
        text-transform: uppercase;
        margin: 0;
    }

    /* BARRA LATERAL: COLOR #EBF2F6 */
    [data-testid="stSidebar"] {
        background-color: #EBF2F6 !important;
        border-right: 1px solid #DDE4E9;
    }
    [data-testid="stSidebar"] > div:first-child {
        background-color: #EBF2F6 !important;
    }

    .sidebar-label {
        font-size: 15px;
        font-weight: 800;
        color: #1D3557;
        text-transform: uppercase;
        margin-top: 15px;
        margin-bottom: 5px;
    }

    .stTabs [data-baseweb="tab-list"] { gap: 30px; }
    .stTabs [data-baseweb="tab"] {
        font-size: 17px;
        font-weight: 700;
        color: #6C757D !important;
        text-transform: uppercase;
    }
    .stTabs [aria-selected="true"] {
        color: #E63946 !important;
        border-bottom: 4px solid #E63946 !important;
    }

    .odds-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        padding: 40px;
        border-radius: 8px;
        text-align: center;
    }
    .odds-value {
        color: #D4AF37; 
        font-size: 54px;
        font-weight: 900;
    }

    .report-box {
        background-color: #F8FAFC;
        border-left: 6px solid #1D3557;
        padding: 25px;
        border-radius: 4px;
    }
    </style>
    """, unsafe_allow_html=True)

datos_ligas = {
    "Premier League": {
        "total": 20, "equipos": {
            "Arsenal": {"pos": 1, "gf": 67, "gc": 26}, "Manchester City": {"pos": 2, "gf": 72, "gc": 32},
            "Manchester United": {"pos": 3, "gf": 63, "gc": 48}, "Liverpool": {"pos": 4, "gf": 60, "gc": 48},
            "Aston Villa": {"pos": 5, "gf": 48, "gc": 44}, "Bournemouth": {"pos": 6, "gf": 56, "gc": 52},
            "Brighton": {"pos": 7, "gf": 52, "gc": 42}, "Brentford": {"pos": 8, "gf": 52, "gc": 49},
            "Chelsea": {"pos": 9, "gf": 55, "gc": 49}, "Everton": {"pos": 10, "gf": 44, "gc": 44},
            "Fulham": {"pos": 11, "gf": 44, "gc": 50}, "Sunderland": {"pos": 12, "gf": 37, "gc": 46},
            "Newcastle United": {"pos": 13, "gf": 49, "gc": 51}, "Leeds": {"pos": 14, "gf": 47, "gc": 52},
            "Crystal Palace": {"pos": 15, "gf": 36, "gc": 42}, "Nottingham Forest": {"pos": 16, "gf": 44, "gc": 46},
            "Tottenham": {"pos": 17, "gf": 45, "gc": 54}, "West Ham": {"pos": 18, "gf": 42, "gc": 61},
            "Burnley": {"pos": 19, "gf": 35, "gc": 71}, "Wolverhampton Wanderers": {"pos": 20, "gf": 25, "gc": 66}
        }
    },
    "La Liga": {
        "total": 20, "equipos": {
            "Barcelona": {"pos": 1, "gf": 89, "gc": 31}, "Real Madrid": {"pos": 2, "gf": 70, "gc": 31},
            "Villarreal": {"pos": 3, "gf": 64, "gc": 39}, "Atletico Madrid": {"pos": 4, "gf": 58, "gc": 38},
            "Real Betis": {"pos": 5, "gf": 54, "gc": 43}, "Celta Vigo": {"pos": 6, "gf": 49, "gc": 44},
            "Real Sociedad": {"pos": 7, "gf": 54, "gc": 55}, "Getafe": {"pos": 8, "gf": 28, "gc": 36},
            "Athletic Club": {"pos": 9, "gf": 40, "gc": 50}, "Osasuna": {"pos": 10, "gf": 42, "gc": 45},
            "Rayo Vallecano": {"pos": 11, "gf": 35, "gc": 41}, "Sevilla": {"pos": 12, "gf": 43, "gc": 56},
            "Elche": {"pos": 13, "gf": 46, "gc": 54}, "Valencia": {"pos": 14, "gf": 37, "gc": 50},
            "Espanyol": {"pos": 15, "gf": 38, "gc": 53}, "Mallorca": {"pos": 16, "gf": 42, "gc": 51},
            "Girona": {"pos": 17, "gf": 36, "gc": 51}, "Alaves": {"pos": 18, "gf": 41, "gc": 54},
            "Levante": {"pos": 19, "gf": 41, "gc": 57}, "Real Oviedo": {"pos": 20, "gf": 26, "gc": 54}
        }
    },
    "Serie A": {
        "total": 20, "equipos": {
            "Inter": {"pos": 1, "gf": 85, "gc": 31}, "Napoli": {"pos": 2, "gf": 52, "gc": 33},
            "Juventus": {"pos": 3, "gf": 59, "gc": 30}, "AC Milan": {"pos": 4, "gf": 48, "gc": 29},
            "Roma": {"pos": 5, "gf": 52, "gc": 29}, "Como": {"pos": 6, "gf": 59, "gc": 28},
            "Atalanta": {"pos": 7, "gf": 47, "gc": 32}, "Lazio": {"pos": 8, "gf": 39, "gc": 37},
            "Udinese": {"pos": 9, "gf": 45, "gc": 46}, "Bologna": {"pos": 10, "gf": 42, "gc": 41},
            "Sassuolo": {"pos": 11, "gf": 44, "gc": 46}, "Torino": {"pos": 12, "gf": 41, "gc": 59},
            "Parma Calcio 1913": {"pos": 13, "gf": 25, "gc": 42}, "Genoa": {"pos": 14, "gf": 40, "gc": 48},
            "Fiorentina": {"pos": 15, "gf": 38, "gc": 49}, "Cagliari": {"pos": 16, "gf": 36, "gc": 51},
            "Lecce": {"pos": 17, "gf": 24, "gc": 48}, "Cremonese": {"pos": 18, "gf": 27, "gc": 53},
            "Verona": {"pos": 19, "gf": 24, "gc": 57}, "Pisa": {"pos": 20, "gf": 25, "gc": 63}
        }
    },
    "Bundesliga": {
        "total": 18, "equipos": {
            "Bayern Munich": {"pos": 1, "gf": 117, "gc": 35}, "Borussia Dortmund": {"pos": 2, "gf": 68, "gc": 34},
            "RB Leipzig": {"pos": 3, "gf": 65, "gc": 43}, "VfB Stuttgart": {"pos": 4, "gf": 69, "gc": 47},
            "Hoffenheim": {"pos": 5, "gf": 65, "gc": 48}, "Bayer Leverkusen": {"pos": 6, "gf": 67, "gc": 46},
            "Freiburg": {"pos": 7, "gf": 45, "gc": 53}, "Eintracht Frankfurt": {"pos": 8, "gf": 59, "gc": 63},
            "Augsburg": {"pos": 9, "gf": 45, "gc": 57}, "Mainz 05": {"pos": 10, "gf": 41, "gc": 50},
            "Borussia M.Gladbach": {"pos": 11, "gf": 38, "gc": 53}, "Hamburger SV": {"pos": 12, "gf": 36, "gc": 51},
            "Union Berlin": {"pos": 13, "gf": 37, "gc": 57}, "FC Cologne": {"pos": 14, "gf": 47, "gc": 55},
            "Werder Bremen": {"pos": 15, "gf": 37, "gc": 58}, "Wolfsburg": {"pos": 16, "gf": 42, "gc": 68},
            "St. Pauli": {"pos": 17, "gf": 28, "gc": 57}, "FC Heidenheim": {"pos": 18, "gf": 38, "gc": 69}
        }
    },
    "Ligue 1": {
        "total": 18, "equipos": {
            "Paris Saint Germain": {"pos": 1, "gf": 70, "gc": 27}, "Lens": {"pos": 2, "gf": 62, "gc": 33},
            "Lyon": {"pos": 3, "gf": 52, "gc": 34}, "Lille": {"pos": 4, "gf": 51, "gc": 35},
            "Rennes": {"pos": 5, "gf": 56, "gc": 46}, "Monaco": {"pos": 6, "gf": 56, "gc": 48},
            "Marseille": {"pos": 7, "gf": 59, "gc": 44}, "Strasbourg": {"pos": 8, "gf": 50, "gc": 41},
            "Lorient": {"pos": 9, "gf": 44, "gc": 49}, "Toulouse": {"pos": 10, "gf": 45, "gc": 45},
            "Paris FC": {"pos": 11, "gf": 44, "gc": 47}, "Brest": {"pos": 12, "gf": 41, "gc": 51},
            "Angers": {"pos": 13, "gf": 27, "gc": 46}, "Le Havre": {"pos": 14, "gf": 30, "gc": 43},
            "Nice": {"pos": 15, "gf": 36, "gc": 58}, "Auxerre": {"pos": 16, "gf": 30, "gc": 43},
            "Nantes": {"pos": 17, "gf": 29, "gc": 52}, "Metz": {"pos": 18, "gf": 32, "gc": 72}
        }
    }
}

def calcular_cuotas_Champagne(sl, sv, n):
    p_pos_l = (n - sl["pos"] + 1) / n
    p_pos_v = (n - sv["pos"] + 1) / n
    eff_l = sl["gf"] / max(1, sl["gc"])
    eff_v = sv["gf"] / max(1, sv["gc"])
    
    f_l = (p_pos_l * 0.65 + eff_l * 0.35) * 1.12
    f_v = (p_pos_v * 0.65 + eff_v * 0.35)
    
    total = f_l + f_v
    prob_l_base = f_l / total
    prob_v_base = f_v / total
    
    dif = abs(prob_l_base - prob_v_base)
    prob_e = 0.28 - (dif * 0.10)
    
    p_l = prob_l_base * (1.0 - prob_e)
    p_v = prob_v_base * (1.0 - prob_e)
    
    return round(1/p_l, 2), round(1/prob_e, 2), round(1/p_v, 2)

with st.sidebar:
    st.markdown('<p class="sidebar-label">PANEL DE CONTROL</p>', unsafe_allow_html=True)
    liga_sel = st.selectbox("LIGA", list(datos_ligas.keys()))
    equipos = sorted(list(datos_ligas[liga_sel]["equipos"].keys()))
    loc = st.selectbox("LOCAL", equipos, index=0)
    vis = st.selectbox("VISITANTE", equipos, index=min(1, len(equipos)-1))
    st.markdown("---")

# INTERFAZ PRINCIPAL 
st.markdown('<div class="brand-header"><h1 class="brand-title">Fútbol Champagne Pro</h1></div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["ANÁLISIS 1X2", "GESTIÓN DE BANCA", "INFORME TÉCNICO"])

if loc != vis:
    cl, ce, cv = calcular_cuotas_Champagne(datos_ligas[liga_sel]["equipos"][loc], datos_ligas[liga_sel]["equipos"][vis], datos_ligas[liga_sel]["total"])

with tab1:
    if loc == vis:
        st.warning("Seleccione equipos distintos.")
    else:
        st.markdown(f"<h3 style='color: #1D3557;'>TEMPORADA 25/26: {loc.upper()} VS {vis.upper()}</h3>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="odds-card"><div style="color:#6C757D; font-weight:800; font-size:13px; margin-bottom:15px; text-transform:uppercase;">GANA {loc.upper()}</div><div class="odds-value">{cl}</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="odds-card"><div style="color:#6C757D; font-weight:800; font-size:13px; margin-bottom:15px; text-transform:uppercase;">EMPATE</div><div class="odds-value">{ce}</div></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="odds-card"><div style="color:#6C757D; font-weight:800; font-size:13px; margin-bottom:15px; text-transform:uppercase;">GANA {vis.upper()}</div><div class="odds-value">{cv}</div></div>', unsafe_allow_html=True)

with tab2:
    st.markdown(f"<h3 style='color: #1D3557;'>SIMULADOR DE OPERACIONES</h3>", unsafe_allow_html=True)
    col_m, col_r = st.columns(2)
    with col_m:
        apuesta = st.number_input("CANTIDAD A INVERTIR (PASOS DE 5€)", min_value=5, value=10, step=5)
        st.markdown(f"**CUOTA FIJA:** {cl}")
    with col_r:
        neto = round((apuesta * cl) - apuesta, 2)
        st.markdown("#### GANANCIA NETA ESTIMADA")
        st.markdown(f"<h1 style='color: #1D3557; font-size: 60px;'>{neto} €</h1>", unsafe_allow_html=True)

with tab3:
    st.markdown("<h2 style='color: #1D3557;'>DETALLES DE LA CUOTA</h2>", unsafe_allow_html=True)
    if 'cl' in locals():
        st.markdown(f"""
        <div class="report-box">
            <p>La cuota de <b>{cl}</b> se establece bajo los siguientes criterios de la temporada actual:</p>
            <ul>
                <li><b>Clasificación (65%):</b> Ponderación de la posición del <b>{loc}</b> (Puesto {datos_ligas[liga_sel]['equipos'][loc]['pos']}) frente al rival.</li>
                <li><b>Efectividad (35%):</b> Análisis de los {datos_ligas[liga_sel]['equipos'][loc]['gf']} goles anotados frente a la defensa contraria.</li>
                <li><b>Factor Campo:</b> Ajuste positivo de localía del 12%.</li>
                <li><b>Paridad:</b> Ajuste dinámico de empate para reflejar la realidad del mercado profesional.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")
st.caption("© 2026 Fútbol Champagne Pro | Temporada 2025/2026 | +18 Juega con responsabilidad")