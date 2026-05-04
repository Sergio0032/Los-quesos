import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Fútbol Champagne Pro", page_icon="⚽", layout="wide")

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
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #1e2129;
        border-radius: 5px;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

if 'user' not in st.session_state:
    st.session_state.user = "Analista Champagne"
if 'equipo' not in st.session_state:
    st.session_state.equipo = "Real Madrid"

datos_ligas = {
    "LaLiga (España)": {
        "equipos": {
            "Real Madrid": {"pos": 1, "gf": 75, "gc": 22, "valor": "1050M€"},
            "FC Barcelona": {"pos": 2, "gf": 72, "gc": 25, "valor": "950M€"},
            "At. Madrid": {"pos": 3, "gf": 60, "gc": 30, "valor": "480M€"},
            "Valencia": {"pos": 4, "gf": 45, "gc": 38, "valor": "220M€"},
            "Real Sociedad": {"pos": 5, "gf": 48, "gc": 32, "valor": "410M€"},
            "Athletic Club": {"pos": 6, "gf": 46, "gc": 34, "valor": "260M€"},
            "Villarreal": {"pos": 7, "gf": 52, "gc": 40, "valor": "210M€"},
            "Girona": {"pos": 8, "gf": 58, "gc": 42, "valor": "190M€"}
        },
        "goleadores": [
            {"Nombre": "K. Mbappé", "Goles": 21, "Precio": "180M€", "Rating": 9.3},
            {"Nombre": "Robert Lewandowski", "Goles": 19, "Precio": "15M€", "Rating": 8.7},
            {"Nombre": "Lamine Yamal", "Goles": 12, "Precio": "150M€", "Rating": 9.1}
        ],
        "evento": "Real Madrid vs FC Barcelona",
        "total": 20
    },
    "Premier League (Inglaterra)": {
        "equipos": {
            "Manchester City": {"pos": 1, "gf": 82, "gc": 28, "valor": "1250M€"},
            "Liverpool": {"pos": 2, "gf": 78, "gc": 30, "valor": "920M€"},
            "Arsenal": {"pos": 3, "gf": 75, "gc": 24, "valor": "1100M€"},
            "Manchester United": {"pos": 4, "gf": 55, "gc": 45, "valor": "850M€"},
            "Chelsea": {"pos": 5, "gf": 62, "gc": 50, "valor": "960M€"},
            "Tottenham": {"pos": 6, "gf": 65, "gc": 48, "valor": "780M€"},
            "Aston Villa": {"pos": 7, "gf": 60, "gc": 42, "valor": "620M€"},
            "Newcastle": {"pos": 8, "gf": 58, "gc": 44, "valor": "640M€"}
        },
        "goleadores": [
            {"Nombre": "E. Haaland", "Goles": 28, "Precio": "200M€", "Rating": 9.5},
            {"Nombre": "Mohamed Salah", "Goles": 20, "Precio": "60M€", "Rating": 8.9},
            {"Nombre": "Phil Foden", "Goles": 18, "Precio": "150M€", "Rating": 9.2}
        ],
        "evento": "Arsenal vs Manchester City",
        "total": 20
    },
    "Bundesliga (Alemania)": {
        "equipos": {
            "Bayern Múnich": {"pos": 1, "gf": 90, "gc": 30, "valor": "980M€"},
            "Bayer Leverkusen": {"pos": 2, "gf": 85, "gc": 22, "valor": "650M€"},
            "Borussia Dortmund": {"pos": 3, "gf": 70, "gc": 40, "valor": "460M€"},
            "RB Leipzig": {"pos": 4, "gf": 68, "gc": 35, "valor": "500M€"},
            "Stuttgart": {"pos": 5, "gf": 72, "gc": 38, "valor": "280M€"},
            "Eintracht Frankfurt": {"pos": 6, "gf": 55, "gc": 45, "valor": "240M€"}
        },
        "goleadores": [
            {"Nombre": "Harry Kane", "Goles": 32, "Precio": "100M€", "Rating": 9.4},
            {"Nombre": "Florian Wirtz", "Goles": 15, "Precio": "130M€", "Rating": 9.1}
        ],
        "evento": "Bayern Múnich vs Borussia Dortmund",
        "total": 18
    },
    "Serie A (Italia)": {
        "equipos": {
            "Inter Milan": {"pos": 1, "gf": 78, "gc": 20, "valor": "630M€"},
            "AC Milan": {"pos": 2, "gf": 65, "gc": 35, "valor": "550M€"},
            "Juventus": {"pos": 3, "gf": 52, "gc": 25, "valor": "600M€"},
            "Napoli": {"pos": 4, "gf": 58, "gc": 40, "valor": "520M€"},
            "AS Roma": {"pos": 5, "gf": 50, "gc": 38, "valor": "340M€"},
            "Atalanta": {"pos": 6, "gf": 62, "gc": 42, "valor": "430M€"}
        },
        "goleadores": [
            {"Nombre": "Lautaro Martínez", "Goles": 24, "Precio": "110M€", "Rating": 9.0},
            {"Nombre": "Dusan Vlahovic", "Goles": 18, "Precio": "70M€", "Rating": 8.6}
        ],
        "evento": "Inter Milan vs AC Milan",
        "total": 20
    },
    "Ligue 1 (Francia)": {
        "equipos": {
            "PSG": {"pos": 1, "gf": 75, "gc": 28, "valor": "1000M€"},
            "Marsella": {"pos": 2, "gf": 55, "gc": 35, "valor": "300M€"},
            "Lyon": {"pos": 3, "gf": 52, "gc": 45, "valor": "280M€"},
            "Mónaco": {"pos": 4, "gf": 60, "gc": 40, "valor": "350M€"},
            "Lille": {"pos": 5, "gf": 48, "gc": 32, "valor": "260M€"},
            "Lens": {"pos": 6, "gf": 42, "gc": 30, "valor": "220M€"}
        },
        "goleadores": [
            {"Nombre": "Bradley Barcola", "Goles": 14, "Precio": "65M€", "Rating": 8.8},
            {"Nombre": "Jonathan David", "Goles": 16, "Precio": "50M€", "Rating": 8.5}
        ],
        "evento": "PSG vs Marsella",
        "total": 18
    }
}

def calcular_probabilidades(f1, f2):
    total = f1 + f2
    return round((f1 / total) * 100, 1), round((f2 / total) * 100, 1)

def calcular_fuerza(stats, total_eq):
    return (stats["gf"] / max(1, stats["gc"])) + ((total_eq + 1 - stats["pos"]) / 2.0)

with st.sidebar:
    st.title("🍾 Menú Champagne")
    st.session_state.user = st.text_input("Usuario:", st.session_state.user)
    st.session_state.equipo = st.selectbox("Hincha de:", ["Real Madrid", "Barça", "Man City", "Arsenal", "Bayern", "Inter"])
    st.divider()
    liga_sel = st.selectbox("Elegir Liga:", list(datos_ligas.keys()))
    st.success(f"Analista: {st.session_state.user}")

st.title(f"⚽ {liga_sel}")

tab1, tab2, tab3 = st.tabs(["🏠 Match Center", "📈 Datos Avanzados", "🗂️ Mercado"])

with tab1:
    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.markdown("#### Simulación Estratégica")
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/Soccer_field_empty.svg/1200px-Soccer_field_empty.svg.png", width=420)
        st.info(f"📍 Evento Destacado: {datos_ligas[liga_sel]['evento']}")
    
    with col_b:
        st.markdown("#### % Probabilidad Victoria")
        partido = datos_ligas[liga_sel]['evento'].split(" vs ")
        e1, e2 = partido[0], partido[1]
        
        f1 = calcular_fuerza(datos_ligas[liga_sel]['equipos'][e1], datos_ligas[liga_sel]['total'])
        f2 = calcular_fuerza(datos_ligas[liga_sel]['equipos'][e2], datos_ligas[liga_sel]['total'])
        p1, p2 = calcular_probabilidades(f1, f2)
        
        st.metric(e1, f"{p1}%")
        st.metric(e2, f"{p2}%")
        st.progress(p1/100)

with tab2:
    df = pd.DataFrame.from_dict(datos_ligas[liga_sel]["equipos"], orient='index').reset_index()
    df.columns = ['Equipo', 'Posición', 'GF', 'GC', 'Valor']
    df['Valor_N'] = df['Valor'].str.replace('M€', '').astype(float)
    
    c_off = alt.Chart(df).mark_bar(cornerRadiusTopLeft=10, cornerRadiusTopRight=10).encode(
        x=alt.X('Equipo', sort='-y'), y='GF', color=alt.Color('GF', scale=alt.Scale(scheme='magma'))
    ).properties(height=300)
    st.altair_chart(c_off, use_container_width=True)
    
    st.divider()
    
    c_val = alt.Chart(df).mark_circle(size=400).encode(
        x='Posición', y='Valor_N', color='Equipo', tooltip=['Equipo', 'Valor', 'GF']
    ).interactive()
    st.altair_chart(c_val, use_container_width=True)

with tab3:
    for j in datos_ligas[liga_sel]["goleadores"]:
        with st.container(border=True):
            f1, f2, f3 = st.columns([1, 2, 2])
            f1.write("⚽")
            f2.markdown(f"**{j['Nombre']}**\n\nPrecio: `{j['Precio']}`")
            f3.metric("Estadística", f"{j['Goles']} Goles", f"⭐ {j['Rating']}")

st.divider()
st.caption(f"Fútbol Champagne v4.0 | Desarrollado para {st.session_state.user} | 2026")