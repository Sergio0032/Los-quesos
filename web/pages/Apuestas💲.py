import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import altair as alt

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

    .header-container {
        display: flex;
        align-items: center;
        margin-bottom: 20px;
        background: #1e2129;
        padding: 25px;
        border-radius: 20px;
        border-bottom: 4px solid #c9ad60;
    }
    
    .logo-text {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 48px !important;
        font-weight: 800;
        background: linear-gradient(135deg, #ffffff 0%, #c9ad60 50%, #866d2d 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -1px;
        margin: 0;
    }

    .subtitle-text {
        color: #9ea4b0;
        font-size: 16px;
        font-weight: 400;
        margin-top: -5px;
    }

    [data-testid="stMetric"] {
        background: #1e2129;
        border: 1px solid #31333f;
        padding: 15px !important;
        border-radius: 12px !important;
    }
    
    [data-testid="stMetricValue"] { color: #c9ad60 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LÓGICA DE CÁLCULO (Mejorada según notas) ---
def calcular_probabilidades_premium(local_stats, visita_stats, total_equipos):
    ventaja_local = 1.10
    f_l = (local_stats["gf"] / max(1, local_stats["gc"])) * ventaja_local * (total_equipos - local_stats["pos"] + 1)
    f_v = (visita_stats["gf"] / max(1, visita_stats["gc"])) * (total_equipos - visita_stats["pos"] + 1)
    
    total = f_l + f_v + (total_equipos * 0.2) # Factor empate
    p_l = (f_l / total) * 100
    p_v = (f_v / total) * 100
    p_e = 100 - p_l - p_v
    
    # Generar cuotas basadas en probabilidad con margen de casa (7%)
    c_l = round((100 / p_l) * 1.07, 2) if p_l > 0 else 0
    c_e = round((100 / p_e) * 1.07, 2) if p_e > 0 else 0
    c_v = round((100 / p_v) * 1.07, 2) if p_v > 0 else 0
    
    return p_l, p_e, p_v, c_l, c_e, c_v

# --- 4. DATOS ---
if 'user_name' not in st.session_state: st.session_state.user_name = "Analista Pro"

datos_ligas = {
    "LaLiga (España)": {
        "total": 20,
        "equipos": {
            "Real Madrid": {"pos": 1, "gf": 78, "gc": 20, "valor": "1000M€"},
            "FC Barcelona": {"pos": 2, "gf": 74, "gc": 24, "valor": "850M€"},
            "Villarreal": {"pos": 3, "gf": 58, "gc": 30, "valor": "210M€"},
            "At. Madrid": {"pos": 4, "gf": 62, "gc": 28, "valor": "450M€"}
        }
    }
}

# --- 5. ENCABEZADO ---
col_logo, col_info = st.columns([1, 4])
with col_logo:
    st.image("https://cdn-icons-png.flaticon.com/512/5328/5328065.png", width=120)
with col_info:
    st.markdown('<p class="logo-text">FÚTBOL CHAMPAGNE</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle-text">Elite Intelligence by Tivale Analytics</p>', unsafe_allow_html=True)

# --- 6. SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Configuración")
    st.session_state.user_name = st.text_input("Analista:", st.session_state.user_name)
    liga_activa = st.selectbox("Competición:", list(datos_ligas.keys()))
    st.divider()
    st.success(f"Sesión: {st.session_state.user_name}")

# --- 7. CUERPO PRINCIPAL ---
tab1, tab2, tab3 = st.tabs(["🏟️ Match Center", "📊 Análisis Avanzado", "💰 Calculadora de Valor"])

with tab1:
    st.subheader("⚔️ Simulador de Probabilidades")
    c1, c2, c3 = st.columns([2, 1, 2])
    
    lista_eq = list(datos_ligas[liga_activa]["equipos"].keys())
    with c1: loc = st.selectbox("Local", lista_eq, index=0)
    with c2: st.markdown("<h1 style='text-align: center; padding-top: 20px;'>VS</h1>", unsafe_allow_html=True)
    with c3: vis = st.selectbox("Visitante", lista_eq, index=1)
    
    # Ejecutar lógica de apuestas
    p_l, p_e, p_v, cuota_l, cuota_e, cuota_v = calcular_probabilidades_premium(
        datos_ligas[liga_activa]["equipos"][loc],
        datos_ligas[liga_activa]["equipos"][vis],
        datos_ligas[liga_activa]["total"]
    )
    
    m1, m2, m3 = st.columns(3)
    m1.metric(f"Prob. {loc}", f"{p_l:.1f}%", f"Cuota x{cuota_l}")
    m2.metric("Empate", f"{p_e:.1f}%", f"Cuota x{cuota_e}", delta_color="off")
    m3.metric(f"Prob. {vis}", f"{p_v:.1f}%", f"Cuota x{cuota_v}")
    
    st.progress(p_l/100, text=f"Dominio Proyectado de {loc}")
    
    # Pizarra Táctica
    st.markdown("#### 🟢 Disposición Táctica Estimada")
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/Soccer_field_empty.svg/1200px-Soccer_field_empty.svg.png", use_container_width=True)

with tab2:
    st.subheader("📊 Comparativa Ofensiva (GF)")
    df = pd.DataFrame.from_dict(datos_ligas[liga_activa]["equipos"], orient='index').reset_index()
    df.columns = ['Equipo', 'Pos', 'GF', 'GC', 'Valor']
    
    fig = px.bar(df, x="Equipo", y="GF", color="GF", 
                 color_continuous_scale="Viridis",
                 template="plotly_dark",
                 title="Goles a Favor por Escuadra")
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("💰 Calculadora de Inversión (Smart Betting)")
    col_in, col_res = st.columns([1, 1])
    
    with col_in:
        st.info(f"Escenario seleccionado: {loc} (Victoria)")
        inversion = st.number_input("Cantidad a invertir (€):", min_value=1, value=100)
        cuota_act = st.number_input("Cuota de tu casa de apuestas:", value=cuota_l)
    
    with col_res:
        retorno = inversion * cuota_act
        beneficio = retorno - inversion
        st.metric("Retorno Estimado", f"{retorno:.2f} €", f"Beneficio: {beneficio:.2f} €")
        
        # Alerta de valor
        if cuota_act > cuota_l:
            st.success("🔥 ¡VALOR DETECTADO! Tu cuota es superior a la probabilidad real del algoritmo.")
        else:
            st.warning("⚠️ CUOTA BAJA. El riesgo es mayor al beneficio estadístico sugerido.")

# --- 8. FOOTER ---
st.divider()
st.caption(f"© 2026 Fútbol Champagne Pro | {st.session_state.user_name} | Juega con responsabilidad +18")