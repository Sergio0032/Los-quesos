import streamlit as st
import pandas as pd
import altair as alt
import numpy as np

# --- CONFIGURACIÓN Y ESTILO ---
st.set_page_config(page_title="Fútbol Champagne v2", page_icon="🍾", layout="wide")

# Inicialización de sesión para "Registro"
if 'user_name' not in st.session_state:
    st.session_state.user_name = "Invitado"
if 'fav_team' not in st.session_state:
    st.session_state.fav_team = "Ninguno"

# --- DATOS AMPLIADOS (Incluyendo Fichas y Mercado) ---
datos_ligas = {
    "LaLiga": {
        "equipos": {
            "FC Barcelona": {"pos": 1, "gf": 80, "gc": 29, "valor": "850M€", "estadio": "Camp Nou"},
            "Real Madrid": {"pos": 2, "gf": 64, "gc": 28, "valor": "1000M€", "estadio": "Bernabéu"},
            "Villarreal": {"pos": 3, "gf": 54, "gc": 34, "valor": "210M€", "estadio": "La Cerámica"},
            "At. Madrid": {"pos": 4, "gf": 50, "gc": 30, "valor": "450M€", "estadio": "Metropolitano"}
        },
        "jugadores_top": [
            {"Nombre": "Lamine Yamal", "Equipo": "FC Barcelona", "Precio": "150M€", "Goles": 12, "Asist": 15, "Rating": 8.9},
            {"Nombre": "Vinícius Jr.", "Equipo": "Real Madrid", "Precio": "200M€", "Goles": 18, "Asist": 10, "Rating": 9.1}
        ],
        "total_equipos": 20,
        "evento_dia": "Real Madrid vs FC Barcelona"
    }
    # ... otras ligas se pueden añadir siguiendo este esquema
}

# --- LÓGICA DE APUESTAS "FÚTBOL CHAMPAGNE" ---
def calcular_probabilidades(eq1, eq2, stats_1, stats_2, total_eq):
    """Calcula el % de quién gana basado en fuerza relativa"""
    f1 = (stats_1["gf"] / max(1, stats_1["gc"])) + (total_eq - stats_1["pos"])
    f2 = (stats_2["gf"] / max(1, stats_2["gc"])) + (total_eq - stats_2["pos"])
    
    total_f = f1 + f2 + (total_eq * 0.2) # Factor de empate
    p1 = (f1 / total_f) * 100
    p2 = (f2 / total_f) * 100
    pe = 100 - p1 - p2
    
    return round(p1, 1), round(pe, 1), round(p2, 1)

# --- SIDEBAR: REGISTRO Y CONFIGURACIÓN ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1165/1165187.png", width=100)
    st.header("👤 Perfil de Usuario")
    
    with st.expander("📝 Editar Registro"):
        st.session_state.user_name = st.text_input("Nombre de usuario:", st.session_state.user_name)
        st.session_state.fav_team = st.selectbox("Equipo Favorito:", ["Ninguno", "Real Madrid", "FC Barcelona", "Villarreal"])
    
    st.success(f"Bienvenido, **{st.session_state.user_name}**")
    st.caption(f"Hincha de: {st.session_state.fav_team}")
    st.divider()
    
    liga_activa = st.selectbox("🏆 Competición:", list(datos_ligas.keys()))
    st.divider()
    st.markdown("### ⭐ Partners")
    st.info("**bet365** | **bwin**")

# --- CUERPO PRINCIPAL ---
st.title("🍾 Fútbol Champagne")
st.subheader("Análisis de Élite y Probabilidades Algorítmicas")

tab_center, tab_players, tab_market = st.tabs(["🏟️ Match Center", "👟 Ficha de Jugadores", "💰 Mercado y Valor"])

# -- TAB 1: MATCH CENTER (Con fórmula % y Dibujo de Campo) --
with tab_center:
    st.markdown(f"### ⚔️ {datos_ligas[liga_activa]['evento_dia']}")
    
    eq_l, eq_v = datos_ligas[liga_activa]['evento_dia'].split(" vs ")
    s_l = datos_ligas[liga_activa]['equipos'][eq_l]
    s_v = datos_ligas[liga_activa]['equipos'][eq_v]
    
    prob_l, prob_e, prob_v = calcular_probabilidades(eq_l, eq_v, s_l, s_v, datos_ligas[liga_activa]['total_equipos'])
    
    col_p1, col_pe, col_p2 = st.columns(3)
    col_p1.metric(f"Victoria {eq_l}", f"{prob_l}%")
    col_pe.metric("Empate", f"{prob_e}%")
    col_p2.metric(f"Victoria {eq_v}", f"{prob_v}%")
    
    st.progress(prob_l/100, text=f"Dominio proyectado de {eq_l}")

    # Dibujo del Campo (Simulado con Columnas y Estilo)
    st.markdown("#### 🟢 Disposición Táctica")
    campo = st.container(border=True)
    with campo:
        c1, c2, c3 = st.columns([1, 2, 1])
        c1.button("🧤 GK", use_container_width=True, key="gk")
        c2.button("🛡️ DEF - MID - ATT", use_container_width=True, disabled=True)
        c3.button("🧤 GK", use_container_width=True, key="gk2")
        st.caption("Estrategia basada en el volumen de Goles a Favor (GF)")

# -- TAB 2: FICHA DE JUGADORES (Estadísticas + Precio) --
with tab_players:
    st.markdown("#### 🗂️ Fichas Técnicas Actualizadas")
    for player in datos_ligas[liga_activa]['jugadores_top']:
        with st.container(border=True):
            col_img, col_data, col_stats = st.columns([1, 2, 2])
            with col_img:
                st.write("👤") # Placeholder de Foto
                st.markdown(f"**{player['Nombre']}**")
            with col_data:
                st.markdown(f"**Equipo:** {player['Equipo']}")
                st.markdown(f"**Precio Mercado:** `{player['Precio']}`")
            with col_stats:
                st.write(f"⚽ Goles: {player['Goles']}")
                st.write(f"🎯 Asistencias: {player['Asist']}")
                st.write(f"⭐ Rating: {player['Rating']}")

# -- TAB 3: GRÁFICOS EN TODAS PARTES --
with tab_market:
    st.markdown("#### 📈 Comparativa de Valor de Mercado")
    df_mercado = pd.DataFrame.from_dict(datos_ligas[liga_activa]['equipos'], orient='index').reset_index()
    
    chart = alt.Chart(df_mercado).mark_bar(cornerRadiusTopLeft=10, cornerRadiusTopRight=10).encode(
        x=alt.X('index:N', title='Equipo'),
        y=alt.Y('gf:Q', title='Potencia Ofensiva (GF)'),
        color=alt.Color('index:N', legend=None),
        tooltip=['index', 'valor', 'estadio']
    ).properties(height=400)
    
    st.altair_chart(chart, use_container_width=True)
    st.caption("El valor de mercado influye en el factor de ajuste de las cuotas finales.")

# --- LIMPIEZA GENERAL (Footer) ---
st.divider()
st.markdown("<center>⚽ <i>Fútbol Champagne - Algoritmo de Predicción v2.4</i></center>", unsafe_allow_html=True)