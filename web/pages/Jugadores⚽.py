import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go
import base64

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Jugadores", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stDataFrame { border: 1px solid #e6e9ef; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

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

    # --- SIDEBAR: CONFIGURACIÓN ---
    st.sidebar.header("Configuración")

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
        
        # CREACIÓN DE PESTAÑAS
        tab1, tab2 = st.tabs(["📊 Estadísticas Generales", "⚽ Máximos Goleadores"])

        # PESTAÑA 1: TABLA Y GRÁFICO DE ARAÑA
        with tab1:
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

            st.divider()
            st.subheader("Perfil del Jugador (Atributos FIFA)")

            jugadores_disponibles = df_mostrar['Jugador'].tolist()
            jugador_seleccionado = st.selectbox("Elige un jugador para ver su gráfico:", jugadores_disponibles)

            if jugador_seleccionado:
                if not df_fifa.empty:
                    busqueda = jugador_seleccionado.lower().strip()
                    
                    nombres_fifa_limpios = df_fifa['short_name'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8').str.lower()
                    busqueda_limpia = pd.Series([busqueda]).str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8').str.lower()[0]

                    match = df_fifa[nombres_fifa_limpios.str.contains(busqueda_limpia, na=False)]

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

                        categorias = ['Ritmo', 'Tiro', 'Pase', 'Regate', 'Defensa', 'Físico']
                        valores = [
                            float(datos_fifa.get('pace', 0)),
                            float(datos_fifa.get('shooting', 0)),
                            float(datos_fifa.get('passing', 0)),
                            float(datos_fifa.get('dribbling', 0)),
                            float(datos_fifa.get('defending', 0)),
                            float(datos_fifa.get('physic', 0))
                        ]

                        categorias.append(categorias[0])
                        valores.append(valores[0])

                        fig = go.Figure()
                        fig.add_trace(go.Scatterpolar(
                            r=valores,
                            theta=categorias,
                            fill='toself',
                            name=jugador_seleccionado,
                            line_color='#1f77b4',
                            fillcolor='rgba(31, 119, 180, 0.4)'
                        ))

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

        #  MÁXIMOS GOLEADORES
        with tab2:
            st.subheader(f"🏆 Top 3 Goleadores - {sel_liga}")
            
            if 'Goles' in df_liga.columns:
                # Cogemos siempre df_liga para mostrar los de la liga entera, sin importar si filtró un equipo
                df_goles = df_liga.dropna(subset=['Goles'])
                df_goles['Goles'] = pd.to_numeric(df_goles['Goles'], errors='coerce').fillna(0)
                
                # Ordenamos y sacamos los 3 primeros
                top_3 = df_goles.sort_values(by="Goles", ascending=False).head(3)
                
                if not top_3.empty:
                    # Colores tipo Oro, Plata, Bronce para que visualmente se entienda rápido
                    colores = ['#FFD700', '#C0C0C0', '#CD7F32'] 
                    
                    fig_bar = go.Figure(data=[
                        go.Bar(
                            x=top_3['Jugador'],
                            y=top_3['Goles'],
                            text=top_3['Goles'],
                            textposition='auto', # Pone el número dentro o justo encima de la barra
                            marker_color=colores[:len(top_3)], 
                            hovertemplate="<b>%{x}</b><br>Goles: %{y}<extra></extra>"
                        )
                    ])
                    
                    fig_bar.update_layout(
                        xaxis_title="Jugador",
                        yaxis_title="Goles",
                        height=500,
                        plot_bgcolor='rgba(0,0,0,0)', # Fondo transparente para que quede más limpio
                        yaxis=dict(showgrid=True, gridcolor='#e6e9ef')
                    )
                    
                    st.plotly_chart(fig_bar, use_container_width=True)
                else:
                    st.info("No hay datos de goles suficientes para mostrar el Top 3.")
            else:
                st.warning("La columna 'Goles' no existe en los datos de esta liga.")