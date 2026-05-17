from duckduckgo_search import DDGS
import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go
import base64
from urllib.parse import unquote
import re

st.set_page_config(page_title="Rendimiento de Jugadores", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stDataFrame { border: 1px solid #e6e9ef; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- CAPTURA DE MEMORIA (Jugador y Temporada) ---
jugador_enviado = st.session_state.get('jugador_enviado', None)
temporada_enviada = st.session_state.get('temporada_enviada', None)

# --- BANNER CON LOGO ---
directorio_actual = os.path.dirname(os.path.abspath(__file__))
ruta_logo = os.path.join(directorio_actual, "..", "logo.png")

try:
    with open(ruta_logo, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    st.markdown(f"""
        <div style="width: 100%; height: 150px; background-color: #0B132B; 
             background-image: url('data:image/png;base64,{encoded_string}');
             background-size: contain; background-repeat: no-repeat; background-position: center;
             border-radius: 10px; margin-bottom: 20px;">
        </div>
    """, unsafe_allow_html=True)
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
        # ==========================================
        # ZONA NUEVA: FICHA DEL JUGADOR (TIPO CROMO)
        # ==========================================
        st.divider()
        st.subheader("💳 Ficha del Jugador")

        jugadores_disponibles = df_mostrar['Jugador'].tolist()
        jugador_seleccionado = st.selectbox("Elige un jugador para ver su ficha:", jugadores_disponibles)

        if jugador_seleccionado:
            if not df_fifa.empty:
                busqueda = jugador_seleccionado.lower().strip()
                nombres_cortos = df_fifa['short_name'].astype(str).str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8').str.lower()
                
                if 'long_name' in df_fifa.columns:
                    nombres_largos = df_fifa['long_name'].astype(str).str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8').str.lower()
                else:
                    nombres_largos = nombres_cortos
                
                busqueda_limpia = pd.Series([busqueda]).str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8').str.lower()[0]
                match = df_fifa[(nombres_cortos == busqueda_limpia) | (nombres_largos == busqueda_limpia)]

                if match.empty:
                    match = df_fifa[nombres_cortos.str.contains(busqueda_limpia, na=False) | nombres_largos.str.contains(busqueda_limpia, na=False)]

                if match.empty:
                    partes = busqueda_limpia.replace("-", " ").split()
                    for palabra in reversed(partes):
                        if len(palabra) > 3:  
                            match_temp = df_fifa[nombres_cortos.str.contains(palabra, na=False) | nombres_largos.str.contains(palabra, na=False)]
                            if not match_temp.empty:
                                match = match_temp
                                break 

                if not match.empty:
                    datos_fifa = match.iloc[0] 
                    nombre_real = datos_fifa.get('short_name', jugador_seleccionado)
                    
                    # 1. SOLUCIÓN AL ERROR: Extraer ID de forma segura sin que pete el programa
                    # 1. SOLUCIÓN AL ERROR: Extraer ID de forma segura
                    if not match.empty:
                        datos_fifa = match.iloc[0] 
                    nombre_real = datos_fifa.get('short_name', jugador_seleccionado)
                    
                    # ==========================================
                    # 1. BÚSQUEDA DE IMAGEN EN INTERNET EN TIEMPO REAL
                    # 1. BÚSQUEDA DE IMAGEN EN INTERNET EN TIEMPO REAL
                    # ==========================================
                    url_foto = "https://upload.wikimedia.org/wikipedia/commons/7/7c/Profile_avatar_placeholder_large.png"
                    
                    try:
                        equipo = datos_fifa.get('club_name', '')
                        busqueda_web = f"{nombre_real} {equipo} football player"
                        
                        with DDGS() as ddgs:
                            resultados = list(ddgs.images(busqueda_web, max_results=1))
                            if resultados:
                                url_foto = resultados[0]['image']
                    except Exception:
                        pass 

                    # ==========================================
                    # 2. MAQUETACIÓN DE LA FICHA
                    # ==========================================
                    col_foto, col_datos = st.columns([1, 2])
                    
                    with col_foto:
                        st.markdown(f'''
                            <div style="display: flex; flex-direction: column; align-items: center;">
                                <img src="{url_foto}" 
                                     onerror="this.onerror=null;this.src='https://upload.wikimedia.org/wikipedia/commons/7/7c/Profile_avatar_placeholder_large.png';"
                                     style="border-radius: 50%; width: 180px; height: 180px; object-fit: cover; border: 4px solid #1f77b4; box-shadow: 0 4px 8px rgba(0,0,0,0.5); background-color: white;">
                                <h4 style="margin-top: 15px; margin-bottom: 0; color: inherit; text-align: center;">{equipo}</h4>
                                <p style="color: #1f77b4; font-weight: bold; font-size: 18px; margin-top: 5px;">{datos_fifa.get('player_positions', 'Posición')}</p>
                            </div>
                        ''', unsafe_allow_html=True)
                        
                    with col_datos:
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Edad", f"{datos_fifa.get('age', '-')} años")
                        c2.metric("Altura", f"{datos_fifa.get('height_cm', '-')} cm")
                        c3.metric("Peso", f"{datos_fifa.get('weight_kg', '-')} kg")
                        
                        st.divider()
                        
                        valor_mercado = datos_fifa.get('value_eur', 0)
                        if pd.isna(valor_mercado) or valor_mercado == 0:
                            st.markdown("### Precio de Mercado: 💰 Desconocido")
                        else:
                            millones = float(valor_mercado) / 1000000
                            st.markdown(f"### Precio de Mercado: 💰 € {millones:,.1f} M")
                            
                        st.markdown("**Equipo Actual:**")
                        st.info(f"➔ {equipo}")

                    st.divider()

                    if pd.isna(datos_fifa.get('pace')) or pd.isna(datos_fifa.get('shooting')):
                        st.warning(f"⚠️ {nombre_real} no tiene estadísticas de jugador de campo (portero).")
                    else:
                            millones = float(valor_mercado) / 1000000
                            st.markdown(f"### Precio de Mercado: 💰 € {millones:,.1f} M")
                            
                        # AQUÍ ESTÁ EL CAMBIO: Lee la trayectoria de tu CSV
                    st.markdown("**Trayectoria Profesional:**")
                    trayectoria_csv = datos_fifa.get('Trayectoria', 'Sin datos de trayectoria')
                    st.info(trayectoria_csv)

                    st.divider()
                    
                    # 3. El Gráfico de Araña
                    if pd.isna(datos_fifa.get('pace')) or pd.isna(datos_fifa.get('shooting')):
                        st.warning(f"⚠️ {nombre_real} no tiene estadísticas de jugador de campo (portero).")
                    else:
                        categorias = ['Ritmo', 'Tiro', 'Pase', 'Regate', 'Defensa', 'Físico']
                        valores = [
                            float(datos_fifa.get('pace', 0)), float(datos_fifa.get('shooting', 0)),
                            float(datos_fifa.get('passing', 0)), float(datos_fifa.get('dribbling', 0)),
                            float(datos_fifa.get('defending', 0)), float(datos_fifa.get('physic', 0))
                        ]
                        categorias.append(categorias[0])
                        valores.append(valores[0])

                        fig = go.Figure()
                        fig.add_trace(go.Scatterpolar(
                            r=valores, theta=categorias, fill='toself',
                            name=nombre_real, line_color='#1f77b4', fillcolor='rgba(31, 119, 180, 0.4)'
                        ))
                        fig.update_layout(
                            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                            showlegend=False, height=450, margin=dict(t=20, b=20, l=20, r=20)
                        )
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info(f"No hemos encontrado las estadísticas FIFA para '{jugador_seleccionado}'.")
            else:
                st.error("No se ha podido cargar el archivo 'fifa_top5_ligas.csv'.")
