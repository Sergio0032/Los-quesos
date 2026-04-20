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

df = load_all_data()

if df.empty:
    st.warning("No hay datos disponibles en 'data_jugadores'.")
else:
    st.title("Estadísticas Completas de Jugadores")

    st.divider()

    c1, c2, c3 = st.columns(3)

    with c1:
        temporadas = sorted(df['Temporada'].unique().tolist(), reverse=True)
        sel_temporada = st.selectbox("Temporada", temporadas)

    df_temp = df[df['Temporada'] == sel_temporada]

    with c2:
        ligas = sorted(df_temp['Liga'].unique().tolist())
        sel_liga = st.selectbox("Liga", ligas)

    df_liga = df_temp[df_temp['Liga'] == sel_liga]

    with c3:
        equipos = ["Ver toda la Liga"] + sorted(df_liga['Equipo'].unique().tolist())
        sel_equipo = st.selectbox("Equipo", equipos)

    if sel_equipo == "Ver toda la Liga":
        df_final = df_liga
    else:
        df_final = df_liga[df_liga['Equipo'] == sel_equipo]

    st.divider()
    
    if not df_final.empty:
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Jugadores", len(df_final))
        
        if 'Goles' in df_final.columns:
            m2.metric("Goles Totales", df_final['Goles'].sum())
            max_gol_idx = df_final['Goles'].idxmax()
            m3.metric("Máximo Goleador", f"{df_final.loc[max_gol_idx, 'Jugador']}")
        else:
            m2.metric("Goles Totales", "No hay col. 'Goles'")
            m3.metric("Máximo Goleador", "No hay col. 'Goles'")

        if 'Goles' in df_final.columns:
            df_mostrar = df_final.sort_values(by="Goles", ascending=False)
        else:
            df_mostrar = df_final

      
        df_mostrar = df_mostrar.drop(columns=['Liga', 'Temporada'], errors='ignore')

        st.dataframe(
            df_mostrar.astype(str),
            use_container_width=True,
            hide_index=True
        )

        csv = df_final.to_csv(index=False).encode('utf-8')
        st.download_button("Descargar Estadísticas (CSV)", csv, "estadisticas_jugadores.csv", "text/csv")
    else:
        st.error("No se encontraron datos para la selección actual.")