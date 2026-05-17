from duckduckgo_search import DDGS
import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go
import base64
import re

# CONFIGURACIÓN DE PÁGINA 
st.set_page_config(page_title="Jugadores", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stDataFrame { border: 1px solid #e6e9ef; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

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
    pass 

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
    if os.path.exists(path): return pd.read_csv(path)
    return pd.DataFrame()

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

    temp_idx, liga_idx, equipo_idx = 0, 0, 0
    
    list_temp = sorted(df['Temporada'].unique().tolist(), reverse=True)

    if temporada_enviada and temporada_enviada in list_temp:
        temp_idx = list_temp.index(temporada_enviada)
        p_temp = temporada_enviada
    elif jugador_enviado:
        datos_p = df[df['Jugador'] == jugador_enviado]
        p_temp = datos_p.iloc[0]['Temporada'] if not datos_p.empty else list_temp[0]
        if p_temp in list_temp: temp_idx = list_temp.index(p_temp)
    else:
        p_temp = list_temp[0]

    if jugador_enviado:
        datos_p = df[(df['Jugador'] == jugador_enviado) & (df['Temporada'] == p_temp)]
        if not datos_p.empty:
            p_liga, p_equipo = datos_p.iloc[0]['Liga'], datos_p.iloc[0]['Equipo']
            
            list_liga = sorted(df[df['Temporada'] == p_temp]['Liga'].unique().tolist())
            if p_liga in list_liga: liga_idx = list_liga.index(p_liga)
            
            list_equi = ["Ver toda la Liga"] + sorted(df[(df['Temporada'] == p_temp) & (df['Liga'] == p_liga)]['Equipo'].unique().tolist())
            if p_equipo in list_equi: equipo_idx = list_equi.index(p_equipo)

    # --- SIDEBAR ---
    st.sidebar.header("Configuración")
    sel_temporada = st.sidebar.selectbox("📅 Temporada", list_temp, index=temp_idx, format_func=mostrar_formato_temporada)
    
    df_temp = df[df['Temporada'] == sel_temporada]
    sel_liga = st.sidebar.selectbox("🏆 Liga", sorted(df_temp['Liga'].unique().tolist()), index=liga_idx)
    
    df_liga = df_temp[df_temp['Liga'] == sel_liga]
    equipos = ["Ver toda la Liga"] + sorted(df_liga['Equipo'].unique().tolist())
    sel_equipo = st.sidebar.selectbox("⚽ Equipo", equipos, index=equipo_idx)

    df_final = df_liga if sel_equipo == "Ver toda la Liga" else df_liga[df_liga['Equipo'] == sel_equipo]
    
    if not df_final.empty:
        tab1, tab2 = st.tabs(["📊 Estadísticas Generales", "⚽ Máximos Goleadores"])

        with tab1:
            # --- TABLA Y MÉTRICAS BÁSICAS ---
            m1, m2, m3 = st.columns(3)
            m1.metric("Total Jugadores", len(df_final))
            if 'Goles' in df_final.columns:
                m2.metric("Goles Totales", int(df_final['Goles'].sum()))
                m3.metric("Máximo Goleador", f"{df_final.loc[df_final['Goles'].idxmax(), 'Jugador']}")

            df_mostrar = df_final.sort_values(by="Goles", ascending=False) if 'Goles' in df_final.columns else df_final
            cols_ok = ['Jugador', 'Equipo', 'Posicion', 'Partidos_Jugados', 'Goles', 'Asistencias']
            st.dataframe(df_mostrar[[c for c in cols_ok if c in df_mostrar.columns]].astype(str), use_container_width=True, hide_index=True)

            # FICHA DEL JUGADOR 

            st.divider()
            st.subheader("💳 Ficha del Jugador")

            jugadores_disponibles = df_mostrar['Jugador'].tolist()
            idx_jug_final = jugadores_disponibles.index(jugador_enviado) if jugador_enviado in jugadores_disponibles else 0
            jugador_seleccionado = st.selectbox("Elige un jugador para ver su ficha:", jugadores_disponibles, index=idx_jug_final)

            if jugador_seleccionado and not df_fifa.empty:
                # Búsqueda en el CSV de FIFA
                busqueda_clean = jugador_seleccionado.lower().strip()
                match = pd.DataFrame()
                cols_texto = df_fifa.select_dtypes(include=['object', 'string']).columns
                
                partes = re.split(r'[\s\-]+', busqueda_clean)
                palabras_clave = sorted([p for p in partes if len(p) > 3], key=len, reverse=True)

                for col in cols_texto:
                    col_limpia = df_fifa[col].astype(str).str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8').str.lower()
                    temp_match = df_fifa[col_limpia.str.contains(busqueda_clean, na=False)]
                    if not temp_match.empty:
                        match = temp_match
                        break

                if match.empty:
                    for palabra in palabras_clave:
                        for col in cols_texto:
                            col_limpia = df_fifa[col].astype(str).str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8').str.lower()
                            temp_match = df_fifa[col_limpia.str.contains(palabra, na=False)]
                            if not temp_match.empty:
                                match = temp_match
                                break
                        if not match.empty: break

                # Si encontramos al jugador, maquetamos la ficha
                if not match.empty:
                    datos_fifa = match.iloc[0]
                    nombre_real = datos_fifa.get('short_name', jugador_seleccionado)
                    equipo = datos_fifa.get('club_name', '')
                    
                    # Búsqueda de imagen
                    url_foto = "https://upload.wikimedia.org/wikipedia/commons/7/7c/Profile_avatar_placeholder_large.png"
                    try:
                        busqueda_web = f"{nombre_real} {equipo} football player"
                        with DDGS() as ddgs:
                            resultados = list(ddgs.images(busqueda_web, max_results=1))
                            if resultados:
                                url_foto = resultados[0]['image']
                    except Exception:
                        pass 

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
                            
                        st.markdown("**Trayectoria Profesional:**")
                        trayectoria_csv = datos_fifa.get('Trayectoria', 'Sin datos de trayectoria')
                        st.info(trayectoria_csv)

                    st.divider()

                    # Gráfico de Araña / Radar
                    columnas_csv_lower = {c.lower(): c for c in df_fifa.columns}
                    cats = ['Ritmo', 'Tiro', 'Pase', 'Regate', 'Defensa', 'Físico']
                    stats_campo = ['pace', 'shooting', 'passing', 'dribbling', 'defending', 'physic']
                    
                    valores = []
                    for stat in stats_campo:
                        nombre_col_real = columnas_csv_lower.get(stat)
                        if nombre_col_real:
                            val = datos_fifa.get(nombre_col_real, 0)
                            try: valores.append(float(val) if pd.notnull(val) else 0.0)
                            except: valores.append(0.0)
                        else: 
                            valores.append(0.0)

                    if sum(valores) == 0:
                        st.warning(f"⚠️ **{nombre_real}** es portero o no tiene estadísticas de jugador de campo en FIFA.")
                    else:
                        fig = go.Figure(go.Scatterpolar(
                            r=valores + [valores[0]], 
                            theta=cats + [cats[0]], 
                            fill='toself', 
                            line_color='#1f77b4', 
                            name=nombre_real
                        ))
                        fig.update_layout(
                            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                            showlegend=False, 
                            height=450, 
                            margin=dict(t=40, b=40)
                        )
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info(f"No se encontró la ficha detallada para '{jugador_seleccionado}' en la base de datos de FIFA.")

        with tab2:
            # TOP 3 GOLEADORES 
            st.subheader(f"🏆 Top 3 Goleadores - {sel_liga}")
            if 'Goles' in df_liga.columns:
                df_goles = df_liga.dropna(subset=['Goles']).copy()
                df_goles['Goles'] = pd.to_numeric(df_goles['Goles'], errors='coerce').fillna(0)
                top_3 = df_goles.sort_values(by="Goles", ascending=False).head(3)
                if not top_3.empty:
                    fig_bar = go.Figure(go.Bar(
                        x=top_3['Jugador'], y=top_3['Goles'], text=top_3['Goles'],
                        textposition='auto', marker_color=['#FFD700', '#C0C0C0', '#CD7F32'][:len(top_3)]
                    ))
                    fig_bar.update_layout(xaxis_title="Jugador", yaxis_title="Goles", height=450, plot_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig_bar, use_container_width=True)

# Limpieza de memoria
if 'jugador_enviado' in st.session_state: del st.session_state['jugador_enviado']
if 'temporada_enviada' in st.session_state: del st.session_state['temporada_enviada']