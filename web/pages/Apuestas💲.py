import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Fútbol Champagne Pro",
    page_icon="🍾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. INYECCIÓN DE ESTILO (El "Look" Champagne) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@700;800&display=swap');
    
    .main { background-color: #0e1117; }

    /* Estilo del Título Principal */
    .header-container {
        display: flex;
        align-items: center;
        margin-bottom: 20px;
    }
    
    .logo-text {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 52px !important;
        font-weight: 800;
        background: linear-gradient(135deg, #ffffff 0%, #c9ad60 50%, #866d2d 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -1px;
        margin: 0;
        line-height: 1.1;
    }

    .subtitle-text {
        color: #9ea4b0;
        font-size: 18px;
        font-weight: 400;
        margin-top: -5px;
    }

    /* Tarjetas de Métricas */
    [data-testid="stMetric"] {
        background: #1e2129;
        border: 1px solid #31333f;
        padding: 15px !important;
        border-radius: 12px !important;
    }
    
    [data-testid="stMetricValue"] { color: #c9ad60 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATOS DE EJEMPLO ---
datos_ligas = {
    "LaLiga (España)": {
        "total": 20,
        "equipos": {
            "Real Madrid": {"pos": 1, "gf": 78, "gc": 20},
            "FC Barcelona": {"pos": 2, "gf": 74, "gc": 24},
            "At. Madrid": {"pos": 3, "gf": 62, "gc": 28}
        }
    }
}

# --- 4. IMPLEMENTACIÓN DEL TÍTULO (ENCABEZADO) ---
# Usamos una columna estrecha para el logo y una ancha para el texto
col_icon, col_title = st.columns([0.6, 5])

<<<<<<< Updated upstream
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
=======
with col_icon:
    # Logo temático elegante
    st.image("https://cdn-icons-png.flaticon.com/512/5328/5328065.png", width=100)

with col_title:
    st.markdown('<p class="logo-text">FÚTBOL CHAMPAGNE</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle-text">Elite Football Intelligence & Data Analytics</p>', unsafe_allow_html=True)
>>>>>>> Stashed changes

st.divider()

# --- 5. SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Panel")
    liga_activa = st.selectbox("Competición:", list(datos_ligas.keys()))
    st.info("Algoritmo v4.5 - May 2026")

# --- 6. CUERPO PRINCIPAL ---
tab1, tab2 = st.tabs(["🏟️ Simulador", "📊 Análisis"])

with tab1:
    st.subheader("⚔️ Match Center")
    c1, c2, c3 = st.columns([2, 1, 2])
    
    equipos = list(datos_ligas[liga_activa]["equipos"].keys())
    with c1: loc = st.selectbox("Local", equipos, index=0)
    with c2: st.markdown("<h1 style='text-align: center; color: #31333f;'>VS</h1>", unsafe_allow_html=True)
    with c3: vis = st.selectbox("Visitante", equipos, index=1)
    
    # Simulación rápida
    stats_l = datos_ligas[liga_activa]["equipos"][loc]
    stats_v = datos_ligas[liga_activa]["equipos"][vis]
    
    p_l = (stats_l["gf"] / (stats_l["gf"] + stats_v["gf"])) * 100
    
    st.metric(f"Probabilidad {loc}", f"{p_l:.1f}%")
    st.progress(p_l/100)

with tab2:
    st.subheader("📊 Visualización de Datos")
    df = pd.DataFrame.from_dict(datos_ligas[liga_activa]["equipos"], orient='index').reset_index()
    df.columns = ['Equipo', 'Pos', 'GF', 'GC']
    
    # Gráfico Plotly seguro
    fig = px.bar(df, x="Equipo", y="GF", color="Equipo", 
                 title="Goles a Favor por Equipo",
                 template="plotly_dark",
                 color_discrete_sequence=['#c9ad60', '#866d2d', '#4d3f1a'])
    
    st.plotly_chart(fig, use_container_width=True)

# --- 7. FOOTER ---
st.divider()
st.caption("© 2026 Fútbol Champagne Pro | El análisis de datos nunca fue tan sofisticado.")