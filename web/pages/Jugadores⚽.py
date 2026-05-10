import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px  # Cambiamos Altair por Plotly para mayor estabilidad

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Fútbol Champagne Pro | Intelligence Suite",
    page_icon="🍾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILOS CSS PERSONALIZADOS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main { background-color: #0e1117; }
    
    /* Tarjetas de Métricas */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #1e2129 0%, #13151a 100%);
        border: 1px solid #31333f;
        padding: 20px !important;
        border-radius: 15px !important;
    }
    
    [data-testid="stMetricValue"] { color: #c9ad60 !important; font-size: 2.2rem !important; }

    /* Contenedor de Calculadora */
    .calc-card {
        background-color: #1e2129;
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #c9ad60;
        margin: 10px 0;
    }

    /* Título Champagne */
    .logo-text {
        font-size: 48px !important;
        font-weight: 800;
        background: -webkit-linear-gradient(#fff, #c9ad60);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DATOS 2026 ---
datos_ligas = {
    "LaLiga (España)": {
        "total": 20,
        "equipos": {
            "Real Madrid": {"pos": 1, "pos_prev": 1, "gf": 78, "gc": 20},
            "FC Barcelona": {"pos": 2, "pos_prev": 2, "gf": 74, "gc": 24},
            "At. Madrid": {"pos": 3, "pos_prev": 4, "gf": 62, "gc": 28},
            "Villarreal": {"pos": 4, "pos_prev": 8, "gf": 55, "gc": 45},
            "Sevilla FC": {"pos": 5, "pos_prev": 14, "gf": 45, "gc": 48},
        }
    },
    "Premier League (Inglaterra)": {
        "total": 20,
        "equipos": {
            "Manchester City": {"pos": 1, "pos_prev": 1, "gf": 85, "gc": 28},
            "Arsenal": {"pos": 2, "pos_prev": 2, "gf": 80, "gc": 25},
            "Liverpool": {"pos": 3, "pos_prev": 3, "gf": 77, "gc": 32},
            "Chelsea": {"pos": 4, "pos_prev": 6, "gf": 63, "gc": 55},
        }
    }
}

# --- FUNCIONES DE CÁLCULO ---
def calcular_fuerza(stats, total_eq):
    ratio = stats["gf"] / max(1, stats["gc"])
    ranking = (total_eq + 1 - stats["pos"]) * 1.2
    return ratio + ranking

# --- HEADER ---
col_logo, col_tit = st.columns([1, 5])
with col_logo:
    st.image("https://cdn-icons-png.flaticon.com/512/5328/5328065.png", width=100)
with col_tit:
    st.markdown('<p class="logo-text">FÚTBOL CHAMPAGNE</p>', unsafe_allow_html=True)
    st.markdown("*Intelligence & Elite Analytics Suite v4.5*")

st.divider()

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Configuración")
    analista = st.text_input("Analista:", "Champagne Master")
    liga_activa = st.selectbox("Competición:", list(datos_ligas.keys()))
    st.divider()
    st.caption("Datos actualizados: Mayo 2026")

# --- CUERPO PRINCIPAL ---
tab1, tab2, tab3 = st.tabs(["🏟️ Match Center", "📊 Análisis Plotly", "📈 Mercado"])

# Tab 1: Simulador
with tab1:
    st.subheader("⚔️ Simulador de Probabilidades")
    c1, c2 = st.columns(2)
    lista = list(datos_ligas[liga_activa]["equipos"].keys())
    
    with c1: loc = st.selectbox("Local:", lista, index=0)
    with c2: vis = st.selectbox("Visitante:", [e for e in lista if e != loc], index=1)
    
    # Lógica de Probabilidad
    s_l, s_v = datos_ligas[liga_activa]["equipos"][loc], datos_ligas[liga_activa]["equipos"][vis]
    f_l = calcular_fuerza(s_l, datos_ligas[liga_activa]["total"])
    f_v = calcular_fuerza(s_v, datos_ligas[liga_activa]["total"])
    
    p_l = (f_l / (f_l + f_v)) * 100
    p_v = (f_v / (f_l + f_v)) * 100
    c_l, c_v = round((100/p_l)*1.1, 2), round((100/p_v)*1.1, 2)

    st.markdown("---")
    m1, m2, m3 = st.columns([1, 0.5, 1])
    m1.metric(loc, f"{p_l:.1f}%", f"Cuota x{c_l}")
    m2.markdown("<h2 style='text-align: center; margin-top: 20px;'>VS</h2>", unsafe_allow_html=True)
    m3.metric(vis, f"{p_v:.1f}%", f"Cuota x{c_v}")
    
    st.progress(p_l/100)

    # Calculadora Inversión
    st.markdown('<div class="calc-card">', unsafe_allow_html=True)
    st.markdown("#### 💰 Calculadora de Retorno")
    inv = st.number_input("Inversión (€):", min_value=1, value=50)
    gan = inv * c_l if st.radio("Apostar por:", [loc, vis]) == loc else inv * c_v
    st.write(f"**Retorno Estimado:** {gan:.2f} € | **Beneficio Neto:** {gan-inv:.2f} €")
    st.markdown('</div>', unsafe_allow_html=True)

# Tab 2: Gráfico Plotly
with tab2:
    st.subheader("📊 Gráfico de Rendimiento Pro")
    df = pd.DataFrame.from_dict(datos_ligas[liga_activa]["equipos"], orient='index').reset_index()
    df.columns = ['Equipo', 'Pos', 'Prev', 'GF', 'GC']
    
    # Crear gráfico Plotly
    fig = px.scatter(df, x="GF", y="GC", text="Equipo", size="GF", color="Equipo",
                     title="Balance Ofensivo vs Defensivo",
                     labels={"GF": "Goles a Favor", "GC": "Goles en Contra"},
                     template="plotly_dark")
    
    fig.update_traces(textposition='top center')
    fig.update_yaxes(autorange="reversed") # Menos goles en contra es mejor
    
    st.plotly_chart(fig, use_container_width=True)
    st.info("💡 El cuadrante inferior derecho representa el verdadero 'Fútbol Champagne'.")

# Tab 3: Mercado
with tab3:
    st.subheader("📈 Tabla de Clasificación Inteligente")
    st.dataframe(df.style.background_gradient(cmap='YlOrBr'), use_container_width=True)

# Footer
st.divider()
st.markdown(f"<center>Analista: <b>{analista}</b> | Fútbol Champagne 2026 | +18 Juega con responsabilidad</center>", unsafe_allow_html=True)