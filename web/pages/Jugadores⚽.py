import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Rendimiento de Jugadores", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stDataFrame { border: 1px solid #e6e9ef; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_all_data():
    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(directorio_actual, '..', '..', 'data_jugadores') 
    path = os.path.abspath(path)
    
    if not os.path.exists(path):
        return pd.DataFrame()
    
    all_files = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.csv')]
    if not all_files:
        return pd.DataFrame()
    
    df_list = []
    for filename in all_files:
        df_temp = pd.read_csv(filename)
        df_list.append(df_temp)
    
    return pd.concat(df_list, axis=0, ignore_index=True)

def mostrar_formato_temporada(valor_raw):
    v = str(valor_raw)
    if len(v) == 4:
        return f"20{v[:2]}-20{v[2:]}"
    return v


df = load_all_data()

if df.empty:
    st.warning("No hay datos en la carpeta 'data_jugadores'.")
else:
    st.title("Estadísticas de jugadores")
    st.divider()

    st.sidebar.header("⚙️ Configuración")

    temporadas = sorted(df['Temporada'].unique().tolist(), reverse=True)
    sel_temporada = st.sidebar.selectbox(
        "📅 Temporada", 
        temporadas, 
        format_func=mostrar_formato_temporada
    )

    df_temp = df[df['Temporada'] == sel_temporada]

    ligas = sorted(df_temp['Liga'].unique().tolist())
    sel_liga = st.sidebar.selectbox("🏆 Liga", ligas)

    df_liga = df_temp[df_temp['Liga'] == sel_liga]

    equipos = ["Ver toda la Liga"] + sorted(df_liga['Equipo'].unique().tolist())
    sel_equipo = st.sidebar.selectbox("⚽ Equipo", equipos)

    if sel_equipo == "Ver toda la Liga":
        df_final = df_liga
    else:
        df_final = df_liga[df_liga['Equipo'] == sel_equipo]
    
    if not df_final.empty:
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Jugadores", len(df_final))
        
        if 'Goles' in df_final.columns:
            m2.metric("Goles Totales", df_final['Goles'].sum())
            max_gol_idx = df_final['Goles'].idxmax()
            m3.metric("Máximo Goleador", f"{df_final.loc[max_gol_idx, 'Jugador']}")

        if 'Goles' in df_final.columns:
            df_mostrar = df_final.sort_values(by="Goles", ascending=False)
        else:
            df_mostrar = df_final

        columnas_ok = [
            'Jugador', 'Equipo', 'Posicion', 'Partidos_Jugados', 
            'Goles', 'Asistencias', 'Tarjetas_Amarillas', 'Tarjetas_Rojas'
        ]
        
        cols_finales = [c for c in columnas_ok if c in df_mostrar.columns]
        df_mostrar = df_mostrar[cols_finales]

        df_mostrar = df_mostrar.rename(columns={
            'Partidos_Jugados': 'PJ',
            'Tarjetas_Amarillas': 'Amarillas',
            'Tarjetas_Rojas': 'Rojas'
        })

        st.dataframe(
            df_mostrar.astype(str),
            use_container_width=True,
            hide_index=True
        )
