import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go
import base64
from urllib.parse import unquote

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Jugadores", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stDataFrame { border: 1px solid #e6e9ef; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- CAPTURA DE PARÁMETROS DE NAVEGACIÓN ---
params = st.query_params
jugador_enviado = unquote(params.get("player", ""))

# --- BANNER CON LOGO ---
directorio_actual = os.path.dirname(os.path.abspath(__file__))
ruta_logo = os.path.join(directorio_actual, "..", "logo.png")

try:
    with open(ruta_logo, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()

    st.markdown(
        f"""
        <div style="
            width: 100%;
            height: 150px; 
            background-color: #0B132B; 
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

# --- CARGA DE DATOS ---
@st.cache_data
def load_all_data():
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data_jugadores'))
    if not os.path.exists(path): return pd.DataFrame()
    all_files = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.csv')]
    if not all_files: return pd.DataFrame()
    return pd.concat([pd.read_csv(f) for f in all_files], axis=0, ignore_index=True)

@st.cache_data
def load_fifa_data():
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data_fifa', 'fifa_top5_ligas.csv'))
    return pd.read_csv(path) if os.path.exists(path) else pd.DataFrame()

def mostrar_formato_temporada(valor_raw):
    v = str(valor_raw)
    return f"20{v[:2]}-20{v[2:]}" if len(v) == 4 else v

df = load_all_data()
df_fifa = load_fifa_data()

if df.empty:
    st.warning("No hay datos en la carpeta 'data_jugadores'.")
else:
    st.title("Estadísticas de jugadores")
    st.divider()

    # =========================================================
    # 🎯 LÓGICA DE AUTO-FILTRADO (Configura la barra lateral)
    # =========================================================
    temp_idx = 0
    liga_idx = 0
    equipo_idx = 0

    if jugador_enviado:
        # Buscamos al jugador en toda la base de datos
        datos_p = df[df['Jugador'] == jugador_enviado]
        if not datos_p.empty:
            p_temp = datos_p.iloc[0]['Temporada']
            p_liga = datos_p.iloc[0]['Liga']
            p_equipo = datos_p.iloc[0]['Equipo']
            
            # Calculamos índices para los selectbox
            temporadas_list = sorted(df['Temporada'].unique().tolist(), reverse=True)
            if p_temp in temporadas_list:
                temp_idx = temporadas_list.index(p_temp)
            
            # Filtramos temporalmente para encontrar la liga
            df_temp_check = df[df['Temporada'] == p_temp]
            ligas_list = sorted(df_temp_check['Liga'].unique().tolist())
            if p_liga in ligas_list:
                liga_idx = ligas_list.index(p_liga)
            
            # Filtramos para encontrar el equipo
            df_liga_check = df_temp_check[df_temp_check['Liga'] == p_liga]
            equipos_list = ["Ver toda la Liga"] + sorted(df_liga_check['Equipo'].unique().tolist())
            if p_equipo in equipos_list:
                equipo_idx = equipos_list.index(p_equipo)

    # --- SIDEBAR CON ÍNDICES DINÁMICOS ---
    st.sidebar.header("Configuración")
    
    temporadas = sorted(df['Temporada'].unique().tolist(), reverse=True)
    sel_temporada = st.sidebar.selectbox("📅 Temporada", temporadas, index=temp_idx, format_func=mostrar_formato_temporada)
    
    df_temp = df[df['Temporada'] == sel_temporada]
    ligas = sorted(df_temp['Liga'].unique().tolist())
    sel_liga = st.sidebar.selectbox("🏆 Liga", ligas, index=liga_idx)
    
    df_liga = df_temp[df_temp['Liga'] == sel_liga]
    equipos = ["Ver toda la Liga"] + sorted(df_liga['Equipo'].unique().tolist())
    sel_equipo = st.sidebar.selectbox("⚽ Equipo", equipos, index=equipo_idx)

    # DataFrame Final filtrado
    df_final = df_liga if sel_equipo == "Ver toda la Liga" else df_liga[df_liga['Equipo'] == sel_equipo]
    
    if not df_final.empty:
        tab1, tab2 = st.tabs(["📊 Estadísticas Generales", "⚽ Máximos Goleadores"])

        with tab1:
            # Métricas
            m1, m2, m3 = st.columns(3)
            m1.metric("Total Jugadores", len(df_final))
            if 'Goles' in df_final.columns:
                m2.metric("Goles Totales", df_final['Goles'].sum())
                m3.metric("Máximo Goleador", f"{df_final.loc[df_final['Goles'].idxmax(), 'Jugador']}")

            # Tabla
            df_mostrar = df_final.sort_values(by="Goles", ascending=False) if 'Goles' in df_final.columns else df_final
            cols_ok = ['Jugador', 'Equipo', 'Posicion', 'Partidos_Jugados', 'Goles', 'Asistencias']
            df_mostrar = df_mostrar[[c for c in cols_ok if c in df_mostrar.columns]]
            st.dataframe(df_mostrar.astype(str), use_container_width=True, hide_index=True)

            st.divider()
            st.subheader("Perfil del Jugador (Atributos FIFA)")

            # --- SELECTOR DE JUGADOR (Auto-seleccionado) ---
            jugadores_disponibles = df_mostrar['Jugador'].tolist()
            idx_jug_final = 0
            if jugador_enviado in jugadores_disponibles:
                idx_jug_final = jugadores_disponibles.index(jugador_enviado)
                st.success(f"🎯 Perfil de **{jugador_enviado}** cargado desde el mapa.")

            jugador_seleccionado = st.selectbox("Elige un jugador:", jugadores_disponibles, index=idx_jug_final)

            if jugador_seleccionado and not df_fifa.empty:
                # Búsqueda en FIFA
                busqueda_clean = jugador_seleccionado.lower().strip()
                nombres_fifa = df_fifa['short_name'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8').str.lower()
                match = df_fifa[nombres_fifa.str.contains(busqueda_clean, na=False)]

                if not match.empty:
                    datos = match.iloc[0]
                    cats = ['Ritmo', 'Tiro', 'Pase', 'Regate', 'Defensa', 'Físico']
                    vals = [float(datos.get(c, 0)) for c in ['pace', 'shooting', 'passing', 'dribbling', 'defending', 'physic']]
                    
                    fig = go.Figure(go.Scatterpolar(r=vals + [vals[0]], theta=cats + [cats[0]], fill='toself', name=jugador_seleccionado))
                    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No se encontró radar FIFA para este jugador.")

        with tab2:
            st.subheader(f"🏆 Top 3 Goleadores - {sel_liga}")
            # (Aquí va tu código de barras de goleadores que ya tenías)