import streamlit as st
import pandas as pd
import os

# 1. Configuración de la página
st.set_page_config(page_title="Top Scorer Dashboard", page_icon="⚽", layout="wide")

# Estilo personalizado para mejorar la visualización
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stDataFrame {
        border: 1px solid #e6e9ef;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Función para cargar y unir todos los CSVs (Rutas Absolutas)
@st.cache_data
def load_all_data():
    # 1. Detecta dónde está app.py (dentro de la carpeta 'web' o 'src')
    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    
    # 2. Sube un nivel ('..') y luego entra en 'data_jugadores'
    path = os.path.join(directorio_actual, '..', 'data_jugadores')
    
    # 3. Limpia la ruta para que sea perfecta para tu sistema operativo
    path = os.path.abspath(path)
    
    # Comprobamos si la carpeta existe
    if not os.path.exists(path):
        print(f"Error: Intenté buscar los datos en {path} pero no encontré la carpeta.")
        return pd.DataFrame()
    
    # Buscamos todos los archivos en la carpeta que terminen en .csv
    all_files = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.csv')]
    
    if not all_files:
        return pd.DataFrame()
    
    df_list = []
    for filename in all_files:
        df_temp = pd.read_csv(filename)
        df_list.append(df_temp)
    
    full_df = pd.concat(df_list, axis=0, ignore_index=True)
    return full_df

# 3. Carga de datos inicial
df = load_all_data()

if df.empty:
    st.error("No se encontraron archivos CSV en la carpeta 'data_jugadores'. Revisa la terminal para ver la ruta exacta donde los está buscando.")
else:
    # --- TÍTULO Y MÉTRICAS ---
    st.title("⚽ Dashboard de Máximos Goleadores")
    st.subheader("Análisis de las 5 Grandes Ligas Europeas")

    # --- FILTROS EN EL SIDEBAR ---
    st.sidebar.header("Filtros de Búsqueda")

    # Filtro de Temporada
    temporadas_disponibles = sorted(df['Temporada'].unique().tolist(), reverse=True)
    sel_temporada = st.sidebar.multiselect("Selecciona Temporada(s)", temporadas_disponibles, default=temporadas_disponibles[0])

    # Filtro de Liga
    ligas_disponibles = sorted(df['Liga'].unique().tolist())
    sel_liga = st.sidebar.multiselect("Selecciona Liga(s)", ligas_disponibles, default=ligas_disponibles)

    # Filtrado intermedio para que el filtro de equipo sea dinámico
    df_filtrado = df[
        (df['Temporada'].isin(sel_temporada)) & 
        (df['Liga'].isin(sel_liga))
    ]

    # Filtro de Equipo
    equipos_disponibles = sorted(df_filtrado['Equipo'].unique().tolist())
    sel_equipo = st.sidebar.multiselect("Selecciona Equipo(s)", equipos_disponibles)

    # Aplicar filtro de equipo si hay selección
    if sel_equipo:
        df_filtrado = df_filtrado[df_filtrado['Equipo'].isin(sel_equipo)]

    # --- LÓGICA DE VISUALIZACIÓN ---
    
    # Ordenar por goles (Top Goleadores)
    df_ranking = df_filtrado.sort_values(by="Goles", ascending=False)

    # Mostrar métricas rápidas arriba
    col1, col2, col3 = st.columns(3)
    if not df_ranking.empty:
        top_player = df_ranking.iloc[0]
        col1.metric("Pichichi Actual", top_player['Jugador'], f"{top_player['Goles']} Goles")
        col2.metric("Total Jugadores", len(df_ranking))
        col3.metric("Media de Goles xG", round(df_ranking['xG_Esperado'].mean(), 2))

    st.divider()

    # --- TABLA PRINCIPAL ---
    st.write(f"### Clasificación: {', '.join(map(str, sel_temporada))}")
    
    # Formatear la tabla para que se vea mejor
    st.dataframe(
        df_ranking,
        column_config={
            "Goles": st.column_config.NumberColumn("Goles", format="%d"),
            "xG_Esperado": st.column_config.NumberColumn(" xG", format="%.2f"),
            "Asistencias": st.column_config.NumberColumn("Asist.", format="%d"),
            "Partidos_Jugados": st.column_config.NumberColumn("PJ", format="%d"),
            "Posicion": "Rol",
            "Temporada": st.column_config.TextColumn("Año")
        },
        use_container_width=True,
        hide_index=True
    )

    # --- BOTÓN DE DESCARGA ---
    csv = df_ranking.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar esta tabla en CSV",
        data=csv,
        file_name='mi_ranking_personalizado.csv',
        mime='text/csv',
    )