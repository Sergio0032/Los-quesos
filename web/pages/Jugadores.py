import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go
import base64
import re
import unicodedata

# CONFIGURACIÓN DE LA PÁGINA 
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

    st.sidebar.header("Configuración")
    sel_temporada = st.sidebar.selectbox(" Temporada", list_temp, index=temp_idx, format_func=mostrar_formato_temporada)
    
    df_temp = df[df['Temporada'] == sel_temporada]
    sel_liga = st.sidebar.selectbox("Liga", sorted(df_temp['Liga'].unique().tolist()), index=liga_idx)
    
    df_liga = df_temp[df_temp['Liga'] == sel_liga]
    equipos = ["Ver toda la Liga"] + sorted(df_liga['Equipo'].unique().tolist())
    sel_equipo = st.sidebar.selectbox(" Equipo", equipos, index=equipo_idx)

    df_final = df_liga if sel_equipo == "Ver toda la Liga" else df_liga[df_liga['Equipo'] == sel_equipo]
    
    if not df_final.empty:
        tab1, tab2, tab3 = st.tabs(["Ficha de Jugador", "Máximos Goleadores", "Comparador de Jugadores"])

        with tab1:
            df_mostrar = df_final.sort_values(by="Goles", ascending=False) if 'Goles' in df_final.columns else df_final
            
            df_mostrar['Goles'] = pd.to_numeric(df_mostrar['Goles'], errors='coerce').fillna(0)
            if 'Asistencias' in df_mostrar.columns:
                df_mostrar['Asistencias'] = pd.to_numeric(df_mostrar['Asistencias'], errors='coerce').fillna(0)
            if 'Tarjetas_Amarillas' in df_mostrar.columns:
                df_mostrar['Tarjetas_Amarillas'] = pd.to_numeric(df_mostrar['Tarjetas_Amarillas'], errors='coerce').fillna(0)
            if 'Tarjetas_Rojas' in df_mostrar.columns:
                df_mostrar['Tarjetas_Rojas'] = pd.to_numeric(df_mostrar['Tarjetas_Rojas'], errors='coerce').fillna(0)
            
            cols_mostrar = [c for c in ['Jugador', 'Equipo', 'Posicion', 'Goles', 'Asistencias', 'Tarjetas_Amarillas', 'Tarjetas_Rojas'] if c in df_mostrar.columns]
            
            max_goles = int(df_mostrar['Goles'].max()) if not df_mostrar.empty and df_mostrar['Goles'].max() > 0 else 30
            max_asist = int(df_mostrar['Asistencias'].max()) if not df_mostrar.empty and 'Asistencias' in df_mostrar.columns and df_mostrar['Asistencias'].max() > 0 else 15

            st.markdown("""
                <style>
                [data-testid="stDataFrame"] {
                    background-color: rgba(15, 15, 15, 0.85);
                    padding: 15px;
                    border-radius: 15px;
                    border: 1px solid #444;
                }
                </style>
            """, unsafe_allow_html=True)

            st.dataframe(
                df_mostrar[cols_mostrar],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Jugador": st.column_config.TextColumn("Jugador", width="medium"),
                    "Goles": st.column_config.ProgressColumn(
                        "Goles", format="%d", min_value=0, max_value=max_goles,
                    ),
                    "Asistencias": st.column_config.ProgressColumn(
                        "Asistencias", format="%d", min_value=0, max_value=max_asist,
                    ),
                    "Tarjetas_Amarillas": st.column_config.NumberColumn(
                        "Amar", format="%d",
                    ),
                    "Tarjetas_Rojas": st.column_config.NumberColumn(
                        "Rojas", format="%d",
                    )
                }
            )


            # FICHA DEL JUGADOR 

            st.divider()
            st.subheader("Ficha del Jugador")

            jugadores_disponibles = df_mostrar['Jugador'].tolist()
            idx_jug_final = jugadores_disponibles.index(jugador_enviado) if jugador_enviado in jugadores_disponibles else 0
            jugador_seleccionado = st.selectbox("Elige un jugador para ver su ficha:", jugadores_disponibles, index=idx_jug_final)

            if jugador_seleccionado and not df_fifa.empty:
                def limpiar_nombre(texto):
                    texto = str(texto).lower()
                    texto = texto.replace('ø', 'o').replace('æ', 'ae').replace('ß', 'ss').replace('đ', 'd').replace('œ', 'oe')
                    texto = "".join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
                    return texto.replace("-", " ").strip()
                
                nombre_buscado = limpiar_nombre(jugador_seleccionado)
                palabras = nombre_buscado.split()
                apellido = palabras[-1] if palabras else ""
                
                long_name_limpio = df_fifa['long_name'].apply(limpiar_nombre)
                short_name_limpio = df_fifa['short_name'].apply(limpiar_nombre)
                
                match = df_fifa[short_name_limpio.str.contains(apellido, na=False) | long_name_limpio.str.contains(apellido, na=False)]
                
                if len(match) > 1 and len(palabras) > 1:
                    inicial = palabras[0][0]
                    match_filtrado = match[short_name_limpio.str.startswith(inicial, na=False) | long_name_limpio.str.startswith(inicial, na=False)]
                    if not match_filtrado.empty:
                        match = match_filtrado

                fila_stats = df_mostrar[df_mostrar['Jugador'] == jugador_seleccionado]
                equipo_forzado = None

                if not match.empty:
                    if 'fifa_version' in match.columns:
                        match = match.sort_values(by='fifa_version', ascending=False)
                        
                    if not fila_stats.empty:
                        equipo_tabla_real = fila_stats['Equipo'].iloc[0]
                        equipo_tabla_limpio = limpiar_nombre(equipo_tabla_real)
                        
                        match_filtrado = match[match['club_name'].astype(str).apply(limpiar_nombre).str.contains(equipo_tabla_limpio, na=False)]
                        
                        if not match_filtrado.empty:
                            match = match_filtrado
                        else:
                            equipo_forzado = equipo_tabla_real

                if not match.empty:
                    datos_fifa = match.iloc[0]
                    nombre_real = datos_fifa.get('short_name', jugador_seleccionado)
                    equipo = equipo_forzado if equipo_forzado else datos_fifa.get('club_name', '')
                   
                    dicc_paises = {'Spain': ('es', 'España'), 'England': ('gb-eng', 'Inglaterra'), 'France': ('fr', 'Francia'), 'Germany': ('de', 'Alemania'), 'Italy': ('it', 'Italia'), 'Brazil': ('br', 'Brasil'), 'Argentina': ('ar', 'Argentina'), 'Portugal': ('pt', 'Portugal'), 'Netherlands': ('nl', 'Países Bajos'), 'Belgium': ('be', 'Bélgica'), 'Norway': ('no', 'Noruega')}
                    nacionalidad_ingles = datos_fifa.get('nationality_name', 'Unknown')
                    if nacionalidad_ingles in dicc_paises:
                        iso, esp = dicc_paises[nacionalidad_ingles]
                        html_pais = f'<img src="https://flagcdn.com/w20/{iso}.png" width="18" style="vertical-align:middle; border-radius:2px; margin-right:5px;"> {esp}'
                    else: html_pais = f'🌍 {nacionalidad_ingles}'

                    try:
                        anyo_temporada = int(sel_temporada.split('-')[0]) 
                        anyo_fifa = 1999 + int(datos_fifa.get('fifa_version', 24))
                        edad_dinamica = int(datos_fifa.get('age', 0)) + (anyo_temporada - anyo_fifa)
                    except: edad_dinamica = datos_fifa.get('age', '-')

                    media = int(datos_fifa.get('overall', 0))
                    color_media = "#ffd700" if media >= 75 else ("#c0c0c0" if media >= 65 else "#cd7f32")
                    pie = "Zurdo" if str(datos_fifa.get('preferred_foot', '')) == "Left" else ("Diestro" if str(datos_fifa.get('preferred_foot', '')) == "Right" else "Ambidiestro")
                    
                    @st.cache_data
                    def buscar_foto_google(nombre_busqueda):
                        try:
                            import requests
                            from bs4 import BeautifulSoup
                            
                            url = f"https://www.google.com/search?q={nombre_busqueda.replace(' ', '+')}+football+player&tbm=isch"
                            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                            
                            respuesta = requests.get(url, headers=headers, timeout=5)
                            soup = BeautifulSoup(respuesta.text, 'html.parser')
                            
                            imagenes = soup.find_all('img')
                            
                            for img in imagenes[1:]:
                                src = img.get('src')
                                if src and src.startswith('http'):
                                    return src
                                    
                            return 'https://upload.wikimedia.org/wikipedia/commons/7/7c/Profile_avatar_placeholder_large.png'
                        except:
                            return 'https://upload.wikimedia.org/wikipedia/commons/7/7c/Profile_avatar_placeholder_large.png'

                    url_foto = buscar_foto_google(f"{nombre_real} {equipo}")
                    
                    valor_mercado = datos_fifa.get('value_eur', 0)
                    str_precio = f"€ {float(valor_mercado) / 1000000:.1f} M" if not pd.isna(valor_mercado) and valor_mercado > 0 else "Desconocido"

                    col_ficha, col_grafico = st.columns([1.2, 1], gap="medium")

                    with col_ficha:
                        goles_f = int(fila_stats['Goles'].iloc[0]) if not fila_stats.empty and pd.notnull(fila_stats['Goles'].iloc[0]) else 0
                        asist_f = int(fila_stats['Asistencias'].iloc[0]) if not fila_stats.empty and 'Asistencias' in fila_stats.columns and pd.notnull(fila_stats['Asistencias'].iloc[0]) else 0

                        st.markdown(f"""
                        <div style="background-color: rgba(15, 15, 15, 0.85); padding: 25px; border-radius: 15px; border: 1px solid #444; box-shadow: 0 4px 15px rgba(0,0,0,0.5);">
                        
                        <div style="display: flex; align-items: center; gap: 20px;">
                            <img src="{url_foto}" style="width: 140px; height: 140px; border-radius: 50%; object-fit: cover; border: 3px solid #1f77b4; background-color: transparent;" onerror="this.src='https://upload.wikimedia.org/wikipedia/commons/7/7c/Profile_avatar_placeholder_large.png'">
                            <div>
                                <h1 style="color: #1f77b4; font-size: 45px; margin: 0; line-height: 1;">{str_precio}</h1>
                                <h2 style="color: white; margin: 0; font-size: 32px; padding-top: 5px;">{nombre_real}</h2>
                                <p style="color: #1f77b4; font-weight: bold; font-size: 18px; margin: 5px 0;">{datos_fifa.get('player_positions', '')}</p>
                                <p style="color: #ccc; margin: 0; font-size: 16px;">{html_pais} &nbsp;|&nbsp; {pie}</p>
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
                                <p style="color: #aaa; margin: 0; font-size: 14px;">Temporada Actual</p>
                                <p style="color: #2ca02c; font-size: 22px; font-weight: bold; margin: 0;">{goles_f} <span style="font-size:16px; color:#aaa; font-weight:normal;">Goles</span> &nbsp;|&nbsp; {asist_f} <span style="font-size:16px; color:#aaa; font-weight:normal;">Asist.</span></p>
                            </div>
                            <div style="text-align: right;">
                                <p style="color: #aaa; margin: 0; font-size: 14px;">Equipo Actual</p>
                                <p style="color: white; font-size: 20px; font-weight: bold; margin: 0;">{equipo}</p>
                            </div>
                        </div>

                        </div>
                        """, unsafe_allow_html=True)

                    with col_grafico:
                        st.markdown("""
                    <div style="background-color: rgba(15, 15, 15, 0.85); padding: 15px; border-radius: 15px; border: 1px solid #444; margin-bottom: 15px;">
                        <h3 style="margin: 0; color: white; border-left: 5px solid #1f77b4; padding-left: 10px;">Rendimiento FIFA</h3>
                    </div>
                        """, unsafe_allow_html=True)
                        
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
                                paper_bgcolor='rgba(0,0,0,0)', 
                                polar=dict(bgcolor='rgba(0,0,0,0)', radialaxis=dict(visible=True, range=[0, 100], gridcolor='#444')),
                                showlegend=False, 
                                height=450, 
                                font=dict(color='white'),
                                margin=dict(t=40, b=40)
                            )
                            st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info(f"No se encontró la ficha detallada para '{jugador_seleccionado}' en la base de datos de FIFA.")

        with tab2:
            col_goles, col_asist = st.columns(2, gap="large")

            with col_goles:
                st.markdown("""
                <div style="background-color: rgba(15,15,15,0.85); padding:25px; border-radius:15px; border:1px solid #444; margin-top:20px;">
                    <h3 style="color: white; border-left: 5px solid #ff4b4b; padding-left: 10px; margin-bottom: 20px;">Top 5 Goleadores</h3>
                """, unsafe_allow_html=True)
                
                if 'Goles' in df_liga.columns:
                    df_goles = df_liga.copy()
                    df_goles['Goles'] = pd.to_numeric(df_goles['Goles'], errors='coerce').fillna(0)
                    top_goles = df_goles[df_goles['Goles'] > 0].sort_values(by="Goles", ascending=False).head(5)

                    if not top_goles.empty:
                        fig_g = go.Figure(go.Bar(
                            x=top_goles['Jugador'], 
                            y=top_goles['Goles'], 
                            text=top_goles['Goles'],
                            textposition='auto',
                            marker_color='#ff4b4b'
                        ))
                        
                        fig_g.update_layout(
                            paper_bgcolor='rgba(0,0,0,0)', 
                            plot_bgcolor='rgba(0,0,0,0)',
                            font=dict(color='white'),
                            yaxis=dict(visible=False), 
                            xaxis=dict(showgrid=False, tickangle=-45), 
                            margin=dict(t=10, b=10, l=0, r=0), 
                            height=380
                        )
                        st.plotly_chart(fig_g, use_container_width=True)
                    else:
                        st.info("Aún no hay goles registrados en esta liga.")
                
                st.markdown('</div>', unsafe_allow_html=True)

            with col_asist:
                st.markdown("""
                <div style="background-color: rgba(15,15,15,0.85); padding:25px; border-radius:15px; border:1px solid #444; margin-top:20px;">
                    <h3 style="color: white; border-left: 5px solid #ff4b4b; padding-left: 10px; margin-bottom: 20px;">Top 5 Asistentes</h3>
                """, unsafe_allow_html=True)
                
                if 'Asistencias' in df_liga.columns:
                    df_asist = df_liga.copy()
                    df_asist['Asistencias'] = pd.to_numeric(df_asist['Asistencias'], errors='coerce').fillna(0)
                    top_asist = df_asist[df_asist['Asistencias'] > 0].sort_values(by="Asistencias", ascending=False).head(5)

                    if not top_asist.empty:
                        fig_a = go.Figure(go.Bar(
                            x=top_asist['Jugador'], 
                            y=top_asist['Asistencias'], 
                            text=top_asist['Asistencias'],
                            textposition='auto',
                            marker_color='#ff4b4b' 
                        ))
                        
                        fig_a.update_layout(
                            paper_bgcolor='rgba(0,0,0,0)', 
                            plot_bgcolor='rgba(0,0,0,0)', 
                            font=dict(color='white'),
                            yaxis=dict(visible=False), 
                            xaxis=dict(showgrid=False, tickangle=-45),
                            margin=dict(t=10, b=10, l=0, r=0), 
                            height=380
                        )
                        st.plotly_chart(fig_a, use_container_width=True)
                    else:
                        st.info("Aún no hay asistencias registradas en esta liga.")
                
                st.markdown('</div>', unsafe_allow_html=True)

        with tab3:
            st.markdown('<div style="background-color: rgba(15,15,15,0.85); padding:15px; border-radius:15px; border:1px solid #444; margin-top:20px; margin-bottom:20px;"><h3 style="color: white; border-left: 5px solid #ff4b4b; padding-left: 10px; margin: 0;">Comparador de Jugadores</h3></div>', unsafe_allow_html=True)
            
            ligas_disponibles = sorted(df['Liga'].unique().tolist())
            idx_liga_base = ligas_disponibles.index(sel_liga) if sel_liga in ligas_disponibles else 0
            
            col_l1, col_l2 = st.columns(2)
            
            with col_l1:
                liga_1 = st.selectbox("🟦 Liga del Jugador 1:", ligas_disponibles, index=idx_liga_base, key="liga1")
                
                df_l1 = df[df['Liga'] == liga_1].copy()
                df_l1['Goles'] = pd.to_numeric(df_l1['Goles'], errors='coerce').fillna(0)
                jugadores_liga1 = df_l1.sort_values(by='Goles', ascending=False)['Jugador'].unique().tolist()
                
                idx_j1 = jugadores_liga1.index(jugador_seleccionado) if jugador_seleccionado in jugadores_liga1 else 0
                j1_nombre = st.selectbox("Selecciona Jugador 1:", jugadores_liga1, index=idx_j1, key="jug1")
                
            with col_l2:
                liga_2 = st.selectbox("🟥 Liga del Jugador 2:", ligas_disponibles, index=0, key="liga2")
                
                df_l2 = df[df['Liga'] == liga_2].copy()
                df_l2['Goles'] = pd.to_numeric(df_l2['Goles'], errors='coerce').fillna(0)
                jugadores_liga2 = df_l2.sort_values(by='Goles', ascending=False)['Jugador'].unique().tolist()
                
                j2_nombre = st.selectbox("Selecciona Jugador 2:", jugadores_liga2, index=0 if len(jugadores_liga2)>0 else 0, key="jug2")
            
            st.divider()

            modo_comparacion = st.radio(
                "Selecciona el modo de comparación:",
                ["Estadísticas Reales", "Estadísticas EA FC"],
                horizontal=True
            )

            datos_reales_j1 = df[(df['Jugador'] == j1_nombre) & (df['Temporada'] == sel_temporada)]
            datos_reales_j2 = df[(df['Jugador'] == j2_nombre) & (df['Temporada'] == sel_temporada)]

            if modo_comparacion == "Estadísticas Reales":
                col_r1, col_r2 = st.columns(2, gap="large")
                
                def pintar_ficha_real(datos, color_borde):
                    if datos.empty:
                        return f"<div style='padding:20px; color:#aaa; border:1px solid #444; border-radius:15px;'>Sin datos reales esta temporada.</div>"
                    d = datos.iloc[0]
                    goles = int(d.get('Goles', 0)) if pd.notnull(d.get('Goles')) else 0
                    asistencias = int(d.get('Asistencias', 0)) if pd.notnull(d.get('Asistencias')) else 0
                    amarillas = int(d.get('Tarjetas_Amarillas', 0)) if pd.notnull(d.get('Tarjetas_Amarillas')) else 0
                    rojas = int(d.get('Tarjetas_Rojas', 0)) if pd.notnull(d.get('Tarjetas_Rojas')) else 0
                    
                    html_str = f"<div style='background-color: rgba(15,15,15,0.85); padding: 25px; border-radius: 15px; border: 2px solid {color_borde}; box-shadow: 0 4px 15px rgba(0,0,0,0.5);'><h2 style='color: white; margin-top:0;'>{d['Jugador']}</h2><p style='color: #aaa; margin-bottom: 20px;'>{d['Equipo']} | {d['Posicion']}</p><div style='display: flex; justify-content: space-between; text-align: center; border-top: 1px solid #333; padding-top: 15px;'><div><p style='color: #aaa; font-size:14px; margin:0;'>Goles</p><h3 style='color:#1f77b4; font-size:26px; margin:0;'>{goles}</h3></div><div><p style='color: #aaa; font-size:14px; margin:0;'>Asistencias</p><h3 style='color:#2ca02c; font-size:26px; margin:0;'>{asistencias}</h3></div><div><p style='color: #aaa; font-size:14px; margin:0;'>Amarillas</p><h3 style='color:#ffd700; font-size:26px; margin:0;'>{amarillas}</h3></div><div><p style='color: #aaa; font-size:14px; margin:0;'>Rojas</p><h3 style='color:#ff4b4b; font-size:26px; margin:0;'>{rojas}</h3></div></div></div>"
                    return html_str

                with col_r1:
                    st.markdown(pintar_ficha_real(datos_reales_j1, "#1f77b4"), unsafe_allow_html=True)
                with col_r2:
                    st.markdown(pintar_ficha_real(datos_reales_j2, "#ff4b4b"), unsafe_allow_html=True)

            else:
                if 'df_fifa' in locals() and not df_fifa.empty:
                    def limpiar_nombre_fifa(texto):
                        texto = str(texto).lower()
                        texto = texto.replace('ø', 'o').replace('æ', 'ae').replace('ß', 'ss').replace('đ', 'd').replace('œ', 'oe')
                        texto = "".join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
                        return texto.replace("-", " ").strip()
                    
                    long_name_limpio = df_fifa['long_name'].apply(limpiar_nombre_fifa)
                    short_name_limpio = df_fifa['short_name'].apply(limpiar_nombre_fifa)
                    
                    def encontrar_jugador_fifa(nombre):
                        pal = limpiar_nombre_fifa(nombre).split()
                        if not pal: return pd.DataFrame()
                        ape = pal[-1]
                        
                        m = df_fifa[short_name_limpio.str.contains(ape, na=False) | long_name_limpio.str.contains(ape, na=False)]
                        if len(m) > 1 and len(pal) > 1:
                            m_fil = m[short_name_limpio.str.startswith(pal[0][0], na=False) | long_name_limpio.str.startswith(pal[0][0], na=False)]
                            if not m_fil.empty: m = m_fil
                        return m
                    
                    m1 = encontrar_jugador_fifa(j1_nombre)
                    m2 = encontrar_jugador_fifa(j2_nombre)
                
                    if not m1.empty and not m2.empty:
                        d_j1 = m1.iloc[0]
                        d_j2 = m2.iloc[0]
                        
                        cats_comp = ['Ritmo', 'Tiro', 'Pase', 'Regate', 'Defensa', 'Físico']
                        stats_c = ['pace', 'shooting', 'passing', 'dribbling', 'defending', 'physic']
                        cols_lower = {c.lower(): c for c in df_fifa.columns}
                        
                        v1_comp = [float(d_j1.get(cols_lower.get(s), 0)) if pd.notnull(d_j1.get(cols_lower.get(s), 0)) else 0 for s in stats_c]
                        v2_comp = [float(d_j2.get(cols_lower.get(s), 0)) if pd.notnull(d_j2.get(cols_lower.get(s), 0)) else 0 for s in stats_c]

                        fig_comp = go.Figure()
                        fig_comp.add_trace(go.Scatterpolar(r=v1_comp+[v1_comp[0]], theta=cats_comp+[cats_comp[0]], fill='toself', name=j1_nombre, line_color='#1f77b4'))
                        fig_comp.add_trace(go.Scatterpolar(r=v2_comp+[v2_comp[0]], theta=cats_comp+[cats_comp[0]], fill='toself', name=j2_nombre, line_color='#ff4b4b'))
                        
                        fig_comp.update_layout(
                            paper_bgcolor='rgba(15,15,15,0.85)', 
                            font=dict(color='white'),
                            polar=dict(bgcolor='rgba(0,0,0,0)', radialaxis=dict(visible=True, range=[0, 100], gridcolor='#444')),
                            height=500,
                            margin=dict(t=30, b=30, l=40, r=40)
                        )
                        st.plotly_chart(fig_comp, use_container_width=True)
                    else:
                        st.warning("No se encontraron los datos de EA FC para uno de los jugadores.")
                        
if 'jugador_enviado' in st.session_state: del st.session_state['jugador_enviado']
if 'temporada_enviada' in st.session_state: del st.session_state['temporada_enviada']