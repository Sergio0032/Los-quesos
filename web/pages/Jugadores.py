import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go
import base64
import re
import unicodedata

# CONFIGURACIÓN DE PÁGINA 
st.set_page_config(page_title="Jugadores", layout="wide")

def poner_fondo_futbol(nombre_archivo_fondo):
    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    ruta_fondo = os.path.join(directorio_actual, "..", nombre_archivo_fondo)
    
    try:
        with open(ruta_fondo, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-color: transparent;
            }}

            .stApp::before {{
                content: "";
                position: fixed; 
                top: 0;
                left: 0;
                width: 100vw;
                height: 100vh;
                background-image: url("data:image/jpeg;base64,{encoded_string}");
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                opacity: 0.15; 
                z-index: -1;
            }}
            
            [data-testid="stHeader"], [data-testid="stToolbar"] {{
                background-color: rgba(0,0,0,0) !important;
            }}
            
            .odds-card, .report-box, .stDataFrame {{
                background-color: var(--secondary-background-color) !important;
                border: 1px solid var(--divider-color) !important;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
    except FileNotFoundError:
        st.warning(f"No se encontró la imagen de fondo: {nombre_archivo_fondo}")

poner_fondo_futbol("temaa.jpg")

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
    sel_temporada = st.sidebar.selectbox(" Temporada", list_temp, index=temp_idx, format_func=mostrar_formato_temporada)
    
    df_temp = df[df['Temporada'] == sel_temporada]
    sel_liga = st.sidebar.selectbox("Liga", sorted(df_temp['Liga'].unique().tolist()), index=liga_idx)
    
    df_liga = df_temp[df_temp['Liga'] == sel_liga]
    equipos = ["Ver toda la Liga"] + sorted(df_liga['Equipo'].unique().tolist())
    sel_equipo = st.sidebar.selectbox(" Equipo", equipos, index=equipo_idx)

    df_final = df_liga if sel_equipo == "Ver toda la Liga" else df_liga[df_liga['Equipo'] == sel_equipo]
    
    if not df_final.empty:
        tab1, tab2 = st.tabs([" Estadísticas Generales", " Máximos Goleadores"])

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
            st.subheader("Ficha del Jugador")

            jugadores_disponibles = df_mostrar['Jugador'].tolist()
            idx_jug_final = jugadores_disponibles.index(jugador_enviado) if jugador_enviado in jugadores_disponibles else 0
            jugador_seleccionado = st.selectbox("Elige un jugador para ver su ficha:", jugadores_disponibles, index=idx_jug_final)

            if jugador_seleccionado and not df_fifa.empty:
                # Búsqueda definitiva a prueba de segundos nombres
                def limpiar_string(t):
                    return "".join(c for c in unicodedata.normalize('NFD', str(t)) if unicodedata.category(c) != 'Mn').lower().replace("-", " ").strip()
                
                nombre_buscado = limpiar_string(jugador_seleccionado)
                palabras = nombre_buscado.split()
                
                long_name_limpio = df_fifa['long_name'].astype(str).str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8').str.lower().str.replace("-", " ")
                short_name_limpio = df_fifa['short_name'].astype(str).str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8').str.lower().str.replace("-", " ")
                
                # 1. Filtramos que el nombre contenga todas las palabras buscadas
                match = df_fifa.copy()
                for p in palabras:
                    match = match[long_name_limpio.str.contains(p, na=False) | short_name_limpio.str.contains(p, na=False)]
                    
                # 2. Si falla por nombres muy raros, busca solo por el apellido
                if match.empty and len(palabras) > 0:
                    apellido = palabras[-1]
                    match = df_fifa[long_name_limpio.str.contains(apellido, na=False) | short_name_limpio.str.contains(apellido, na=False)]
                    
                # # 3. Sincronizamos con el equipo y cogemos el año correcto
                fila_stats = df_mostrar[df_mostrar['Jugador'] == jugador_seleccionado]
                equipo_forzado = None

                if not match.empty:
                    # Ordenamos para que la versión de FC 24 (más reciente) quede arriba por defecto
                    if 'fifa_version' in match.columns:
                        match = match.sort_values(by='fifa_version', ascending=False)
                        
                    if not fila_stats.empty:
                        equipo_tabla_real = fila_stats['Equipo'].iloc[0]
                        equipo_tabla_limpio = limpiar_string(equipo_tabla_real)
                        
                        match_filtrado = match[match['club_name'].astype(str).apply(limpiar_string).str.contains(equipo_tabla_limpio, na=False)]
                        
                        if not match_filtrado.empty:
                            match = match_filtrado
                        else:
                            # Si no coincide (fichaje inventado), nos quedamos con el FC 24 pero forzamos vuestro equipo
                            equipo_forzado = equipo_tabla_real

                # Si encontramos al jugador, maquetamos la ficha
                if not match.empty:
                    datos_fifa = match.iloc[0]
                    nombre_real = datos_fifa.get('short_name', jugador_seleccionado)
                    equipo = equipo_forzado if equipo_forzado else datos_fifa.get('club_name', '')
                   
                                            # --- DATOS LÓGICOS PREVIOS ---
                    # 1. Banderas
                    dicc_paises = {'Spain': ('es', 'España'), 'England': ('gb-eng', 'Inglaterra'), 'France': ('fr', 'Francia'), 'Germany': ('de', 'Alemania'), 'Italy': ('it', 'Italia'), 'Brazil': ('br', 'Brasil'), 'Argentina': ('ar', 'Argentina'), 'Portugal': ('pt', 'Portugal'), 'Netherlands': ('nl', 'Países Bajos'), 'Belgium': ('be', 'Bélgica'), 'Norway': ('no', 'Noruega')}
                    nacionalidad_ingles = datos_fifa.get('nationality_name', 'Unknown')
                    if nacionalidad_ingles in dicc_paises:
                        iso, esp = dicc_paises[nacionalidad_ingles]
                        html_pais = f'<img src="https://flagcdn.com/w20/{iso}.png" width="18" style="vertical-align:middle; border-radius:2px; margin-right:5px;"> {esp}'
                    else: html_pais = f'🌍 {nacionalidad_ingles}'

                    # 2. Datos dinámicos
                    try:
                        anyo_temporada = int(sel_temporada.split('-')[0]) 
                        anyo_fifa = 1999 + int(datos_fifa.get('fifa_version', 24))
                        edad_dinamica = int(datos_fifa.get('age', 0)) + (anyo_temporada - anyo_fifa)
                    except: edad_dinamica = datos_fifa.get('age', '-')

                    media = int(datos_fifa.get('overall', 0))
                    color_media = "#ffd700" if media >= 75 else ("#c0c0c0" if media >= 65 else "#cd7f32")
                    pie = "Zurdo" if str(datos_fifa.get('preferred_foot', '')) == "Left" else ("Diestro" if str(datos_fifa.get('preferred_foot', '')) == "Right" else "Ambidiestro")
                    
                    # 3. Foto y Precio
                    sofifa_id_raw = datos_fifa.get('sofifa_id', 0)
                    url_foto = f"https://cdn.sofifa.net/players/{str(int(sofifa_id_raw)).zfill(6)[:3]}/{str(int(sofifa_id_raw)).zfill(6)[3:]}/24_120.png"
                    valor_mercado = datos_fifa.get('value_eur', 0)
                    str_precio = f"€ {float(valor_mercado) / 1000000:.1f} M" if not pd.isna(valor_mercado) and valor_mercado > 0 else "Desconocido"

                    # --- MAQUETACIÓN VISUAL ---
                    col_ficha, col_grafico = st.columns([1.2, 1], gap="medium")

                    with col_ficha:
                        # TODO EL HTML EN UN SOLO BLOQUE (Caja negra al 85% de opacidad para que se lea perfecto)
                        st.markdown(f"""
                        <div style="background-color: rgba(15, 15, 15, 0.85); padding: 25px; border-radius: 15px; border: 1px solid #444; box-shadow: 0 4px 15px rgba(0,0,0,0.5);">
                        
                        <div style="display: flex; align-items: center; gap: 20px;">
                            <img src="{url_foto}" style="width: 140px; height: 140px; border-radius: 50%; object-fit: cover; border: 3px solid {color_media}; background-color: transparent;" onerror="this.src='https://upload.wikimedia.org/wikipedia/commons/7/7c/Profile_avatar_placeholder_large.png'">
                            <div>
                                <h1 style="color: {color_media}; font-size: 55px; margin: 0; line-height: 1;">{media} <span style="font-size: 20px; color: white;">OVR</span></h1>
                                <h2 style="color: white; margin: 0; font-size: 32px; padding-top: 5px;">{nombre_real}</h2>
                                <p style="color: #1f77b4; font-weight: bold; font-size: 18px; margin: 5px 0;">{datos_fifa.get('player_positions', '')}</p>
                                <p style="color: #ccc; margin: 0; font-size: 16px;">{html_pais} &nbsp;|&nbsp; 👟 {pie}</p>
                            </div>
                        </div>

                        <hr style="border-top: 1px solid #444; margin: 25px 0;">

                        <div style="display: flex; justify-content: space-between; text-align: center;">
                            <div style="width: 30%;"><p style="color: #aaa; margin: 0; font-size: 14px;">Edad</p><p style="color: white; font-size: 20px; font-weight: bold; margin: 0;">{edad_dinamica} años</p></div>
                            <div style="width: 30%;"><p style="color: #aaa; margin: 0; font-size: 14px;">Altura</p><p style="color: white; font-size: 20px; font-weight: bold; margin: 0;">{datos_fifa.get('height_cm', '-')} cm</p></div>
                            <div style="width: 30%;"><p style="color: #aaa; margin: 0; font-size: 14px;">Peso</p><p style="color: white; font-size: 20px; font-weight: bold; margin: 0;">{datos_fifa.get('weight_kg', '-')} kg</p></div>
                        </div>

                        <hr style="border-top: 1px solid #444; margin: 25px 0;">

                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <p style="color: #aaa; margin: 0; font-size: 14px;">Valor de Mercado</p>
                                <p style="color: #1f77b4; font-size: 24px; font-weight: bold; margin: 0;">{str_precio}</p>
                            </div>
                            <div style="text-align: right;">
                                <p style="color: #aaa; margin: 0; font-size: 14px;">Equipo Actual</p>
                                <p style="color: white; font-size: 20px; font-weight: bold; margin: 0;">{equipo}</p>
                            </div>
                        </div>

                        </div>
                        """, unsafe_allow_html=True)

                    with col_grafico:
                        # Título del radar en su propia cajita negra
                        st.markdown("""
                    <div style="background-color: rgba(15, 15, 15, 0.85); padding: 15px; border-radius: 15px; border: 1px solid #444; margin-bottom: 15px;">
                        <h3 style="margin: 0; color: white; border-left: 5px solid #1f77b4; padding-left: 10px;">Rendimiento FIFA</h3>
                    </div>
                        """, unsafe_allow_html=True)
                        
                        # --- AQUÍ DEBAJO TIENE QUE ESTAR TU CÓDIGO DEL RADAR ---                        # ...
                                

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
                            st.warning(f" **{nombre_real}** es portero o no tiene estadísticas de jugador de campo en FIFA.")
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
            st.subheader(f"Top 3 Goleadores - {sel_liga}")
            if 'Goles' in df_liga.columns:
                df_goles = df_liga.dropna(subset=['Goles']).copy()
                df_goles['Goles'] = pd.to_numeric(df_goles['Goles'], errors='coerce').fillna(0)
                top_3 = df_goles.sort_values(by="Goles", ascending=False).head(3)
                if not top_3.empty:
                    fig_bar = go.Figure(go.Bar(
                        x=top_3['Jugador'], y=top_3['Goles'], text=top_3['Goles'],
                        textposition='auto', marker_color=['#FFD700', "#C0C0C0", '#CD7F32'][:len(top_3)]
                    ))
                    fig_bar.update_layout(xaxis_title="Jugador", yaxis_title="Goles", height=450, plot_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig_bar, use_container_width=True)

# Limpieza de memoria
if 'jugador_enviado' in st.session_state: del st.session_state['jugador_enviado']
if 'temporada_enviada' in st.session_state: del st.session_state['temporada_enviada']