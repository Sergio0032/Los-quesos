import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go

st.set_page_config(page_title="Rendimiento de Jugadores", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stDataFrame { border: 1px solid #e6e9ef; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- CARGA DE DATOS REALES ---
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

# --- CARGA DE DATOS FIFA ---
@st.cache_data
def load_fifa_data():
    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(directorio_actual, '..', '..', 'data_fifa', 'fifa_top5_ligas.csv') 
    path = os.path.abspath(path)
    
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()

def mostrar_formato_temporada(valor_raw):
    v = str(valor_raw)
    if len(v) == 4:
        return f"20{v[:2]}-20{v[2:]}"
    return v

# --- INICIO DE LA APLICACIÓN ---
df = load_all_data()
df_fifa = load_fifa_data()

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
        
        csv = df_final.to_csv(index=False).encode('utf-8')
        st.download_button("Descargar CSV", csv, "jugadores.csv", "text/csv")

        # ==========================================
        # ZONA NUEVA: GRÁFICO DE ARAÑA (FIFA)
        # ==========================================
        st.divider()
        st.subheader("🕸️ Perfil del Jugador (Atributos FIFA)")

        # Desplegable para elegir jugador
        jugadores_disponibles = df_mostrar['Jugador'].tolist()
        jugador_seleccionado = st.selectbox("Elige un jugador para ver su gráfico:", jugadores_disponibles)

        if jugador_seleccionado:
            if not df_fifa.empty:
                busqueda = jugador_seleccionado.lower().strip()
                
                # 1. Quitamos tildes de los nombres del FIFA y de la búsqueda para igualar el terreno
                nombres_fifa_limpios = df_fifa['short_name'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8').str.lower()
                busqueda_limpia = pd.Series([busqueda]).str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8').str.lower()[0]

                # Búsqueda 1: Nombre completo exacto
                match = df_fifa[nombres_fifa_limpios.str.contains(busqueda_limpia, na=False)]

                # Búsqueda 2: Palabras sueltas (de atrás hacia adelante, ideal para apellidos compuestos)
                if match.empty:
                    partes = busqueda_limpia.replace("-", " ").split()
                    
                    for palabra in reversed(partes):
                        if len(palabra) > 3:  
                            match_temp = df_fifa[nombres_fifa_limpios.str.contains(palabra, na=False)]
                            if not match_temp.empty:
                                match = match_temp
                                break 

                if not match.empty:
                    datos_fifa = match.iloc[0] 

                    # Nombres de las categorías y sus valores desde el CSV del FIFA
                    categorias = ['Ritmo', 'Tiro', 'Pase', 'Regate', 'Defensa', 'Físico']
                    valores = [
                        float(datos_fifa.get('pace', 0)),
                        float(datos_fifa.get('shooting', 0)),
                        float(datos_fifa.get('passing', 0)),
                        float(datos_fifa.get('dribbling', 0)),
                        float(datos_fifa.get('defending', 0)),
                        float(datos_fifa.get('physic', 0))
                    ]

                    # Cerramos el polígono repitiendo el primer valor al final
                    categorias.append(categorias[0])
                    valores.append(valores[0])

                    # Construimos el gráfico
                    fig = go.Figure()
                    fig.add_trace(go.Scatterpolar(
                        r=valores,
                        theta=categorias,
                        fill='toself',
                        name=jugador_seleccionado,
                        line_color='#1f77b4',
                        fillcolor='rgba(31, 119, 180, 0.4)'
                    ))

                    # La escala ahora es fija del 0 al 100
                    fig.update_layout(
                        polar=dict(
                            radialaxis=dict(
                                visible=True,
                                range=[0, 100]
                            )
                        ),
                        showlegend=False,
                        height=500
                    )

                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info(f"No hemos encontrado las estadísticas FIFA para '{jugador_seleccionado}'. A veces los nombres están muy cambiados en el juego.")
            else:
                st.error("No se ha podido cargar el archivo 'fifa_top5_ligas.csv'. Comprueba que está en la carpeta 'data_fifa'.")