import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go
import numpy as np
from urllib.parse import quote
import base64

st.set_page_config(page_title="Táctica de Equipo", layout="wide")

st.markdown("<style>.main { }</style>", unsafe_allow_html=True)

directorio_actual = os.path.dirname(os.path.abspath(__file__))
ruta_logo = os.path.join(directorio_actual, "..", "logo.png")

if os.path.exists(ruta_logo):
    with open(ruta_logo, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    st.markdown(f"""
        <div style="width: 100%; height: 150px; background-color: #0B132B; 
             background-image: url('data:image/png;base64,{data}');
             background-size: contain; background-repeat: no-repeat; background-position: center;
             border-radius: 10px; margin-bottom: 20px;">
        </div>
    """, unsafe_allow_html=True)

st.title("Disposición Táctica")
st.divider()

@st.cache_data
def load_all_data():
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data_jugadores'))
    if not os.path.exists(path): return pd.DataFrame()
    all_files = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.csv')]
    if not all_files: return pd.DataFrame()
    
    df_list = []
    for f in all_files:
        temp_df = pd.read_csv(f)
        temp_df.columns = temp_df.columns.str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8').str.lower().str.replace(' ', '_')
        df_list.append(temp_df)
    return pd.concat(df_list, axis=0, ignore_index=True)

@st.cache_data
def load_fifa_data():
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data_fifa', 'fifa_top5_ligas.csv'))
    if os.path.exists(path): return pd.read_csv(path)
    return pd.DataFrame()

df = load_all_data()
df_fifa = load_fifa_data()

# --- CÁLCULO DE MEDIAS DEL EQUIPO TITULAR (FIFA) ---
def calcular_radar_equipo(df_fifa, equipo):
    col_equipo = 'team' if 'team' in df_fifa.columns else 'club_name'
    df_equipo = df_fifa[df_fifa[col_equipo].astype(str).str.contains(equipo, case=False, na=False)]
    
    if df_equipo.empty:
        return 0, 0, 0
        
    pos_ataque = ['ST', 'CF', 'RW', 'LW', 'RS', 'LS', 'RF', 'LF', 'ATTACK']
    pos_medio = ['CAM', 'CM', 'CDM', 'RM', 'LM', 'MIDFIELDER']
    pos_defensa = ['CB', 'RB', 'LB', 'RWB', 'LWB', 'DEFENSE', 'DEFENDER']
    
    col_pos = 'position' if 'position' in df_equipo.columns else 'player_positions'
    col_media = 'overallRating' if 'overallRating' in df_equipo.columns else 'overall'
    
    ataque, medio, defensa = [], [], []
    
    for _, row in df_equipo.iterrows():
        pos = str(row.get(col_pos, '')).upper()
        media = row.get(col_media, 0)
        
        try: media = float(media)
        except: continue
        
        if pd.isna(media) or media == 0: continue
        
        if any(p in pos for p in pos_ataque): ataque.append(media)
        elif any(p in pos for p in pos_medio): medio.append(media)
        elif any(p in pos for p in pos_defensa): defensa.append(media)
            
    ata = int(sum(sorted(ataque, reverse=True)[:4]) / 4) if len(ataque) >= 4 else (int(sum(ataque)/len(ataque)) if ataque else 0)
    med = int(sum(sorted(medio, reverse=True)[:4]) / 4) if len(medio) >= 4 else (int(sum(medio)/len(medio)) if medio else 0)
    dfn = int(sum(sorted(defensa, reverse=True)[:5]) / 5) if len(defensa) >= 5 else (int(sum(defensa)/len(defensa)) if defensa else 0)
    
    return ata, med, dfn


if not df.empty:

    st.sidebar.header("⚙️ Configuración")

    temporadas_disponibles = [f"{año}/{año+1}" for año in range(2025, 2014, -1)]

    sel_temp = st.sidebar.selectbox("🗓️ Temporada", temporadas_disponibles)
    temp_corto = sel_temp[2:4] + sel_temp[7:9]
    df_temp = df[(df['temporada'] == temp_corto) | (df['temporada'] == int(temp_corto))]
    
    #  AUTO-SELECCIÓN DE LIGA Y EQUIPO
    equipo_fav = st.session_state.get('equipo', None)
    lista_ligas = sorted(df_temp['liga'].unique().tolist())
    
    index_liga = 0
    if equipo_fav:
        # Buscamos en qué liga juega el equipo favorito esta temporada
        ligas_del_equipo = df_temp[df_temp['equipo'] == equipo_fav]['liga'].unique()
        if len(ligas_del_equipo) > 0:
            liga_fav = ligas_del_equipo[0]
            if liga_fav in lista_ligas:
                index_liga = lista_ligas.index(liga_fav)

    sel_liga = st.sidebar.selectbox("🏆 Liga", lista_ligas, index=index_liga)
    df_liga = df_temp[df_temp['liga'] == sel_liga]

    lista_equipos = sorted(df_liga['equipo'].unique().tolist())
    index_equipo = 0
    if equipo_fav and equipo_fav in lista_equipos:
        index_equipo = lista_equipos.index(equipo_fav)

    sel_equipo = st.sidebar.selectbox("🛡️ Equipo", lista_equipos, index=index_equipo)
        
    df_equipo = df_liga[df_liga['equipo'] == sel_equipo].copy()

    if not df_equipo.empty:
        st.subheader(f"Táctica del {sel_equipo}")
        
        # ASIGNACIÓN DE COORDENADAS
        def asignar_x(pos):
            pos = str(pos).lower()
            if any(p in pos for p in ['port', 'gk', 'arq']): return 10
            elif any(p in pos for p in ['def', 'df', 'cb', 'lat']): return 30
            elif any(p in pos for p in ['cen', 'med', 'mf', 'piv']): return 60
            else: return 85 

        df_equipo['coord_x'] = df_equipo['posicion'].apply(asignar_x).astype(float)
        df_equipo['coord_y'] = 50.0
        
        for x_val in df_equipo['coord_x'].unique():
            indices = df_equipo[df_equipo['coord_x'] == x_val].index
            n = len(indices)
            if n == 1:
                y_coords = [50.0]
            else:
                spread = min(38, n * 5)
                y_coords = np.linspace(50 - spread, 50 + spread, n)
            for i, idx in enumerate(indices):
                df_equipo.at[idx, 'coord_y'] = float(y_coords[i])

        # DIBUJO DEL CAMPO
        fig = go.Figure()

        # Campo
        fig.add_shape(type="rect", x0=0, y0=0, x1=100, y1=100, line=dict(color="white", width=2), fillcolor="#2b7a2b", layer="below")
        fig.add_shape(type="line", x0=50, y0=0, x1=50, y1=100, line=dict(color="white", width=2), layer="below")
        fig.add_shape(type="circle", x0=40, y0=40, x1=60, y1=60, line=dict(color="white", width=2), layer="below")
        fig.add_shape(type="rect", x0=0, y0=20, x1=15, y1=80, line=dict(color="white", width=2), layer="below")
        fig.add_shape(type="rect", x0=85, y0=20, x1=100, y1=80, line=dict(color="white", width=2), layer="below")

        fig.add_trace(go.Scatter(
            x=df_equipo['coord_x'], 
            y=df_equipo['coord_y'],
            mode='markers+text',
            text=df_equipo['jugador'],
            customdata=df_equipo['jugador'],
            textposition="top center",
            marker=dict(size=18, color="white", line=dict(width=2, color="black")),
            textfont=dict(size=12, family="Arial Black", color="white"),
            hoverinfo="text",
            hovertext=df_equipo['posicion']
        ))

        fig.update_layout(
            xaxis=dict(visible=False, range=[-5, 105]),
            yaxis=dict(visible=False, range=[-5, 105]),
            margin=dict(l=0, r=0, t=0, b=0),
            height=600,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            showlegend=False,
            clickmode='event+select'
        )

        st.info(" **Haz clic directamente en el punto o nombre del jugador** sobre el césped para ver su Radar FIFA.")

        evento = st.plotly_chart(fig, use_container_width=True, on_select="rerun")

        if not df_fifa.empty:
            ata, med, dfn = calcular_radar_equipo(df_fifa, sel_equipo)
            
            if ata > 0 or med > 0 or dfn > 0:
                st.divider()
                st.subheader(f"Nivel de Plantilla del {sel_equipo} (FIFA)")
                
                c_izq, c_cen, c_der = st.columns([1, 2, 1])
                
                with c_cen:
                    categorias = ['Ataque', 'Centro del Campo', 'Defensa', 'Ataque']
                    valores = [ata, med, dfn, ata]
                    
                    fig_radar = go.Figure()
                    fig_radar.add_trace(go.Scatterpolar(
                        r=valores,
                        theta=categorias,
                        fill='toself',
                        line_color='#1f77b4',
                        fillcolor='rgba(31, 119, 180, 0.4)',
                        name='Valoración Equipo'
                    ))
                    
                    fig_radar.update_layout(
                        polar=dict(
                            radialaxis=dict(visible=True, range=[50, 100]) 
                        ),
                        showlegend=False,
                        height=400,
                        margin=dict(t=40, b=40, l=40, r=40),
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                    )
                    st.plotly_chart(fig_radar, use_container_width=True)
                    
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Ataque", f"{ata}")
                    m2.metric("Medio", f"{med}")
                    m3.metric("Defensa", f"{dfn}")

        if evento and len(evento.selection.get("points", [])) > 0:
            jugador_clicado = evento.selection["points"][0]["customdata"]
            st.session_state['jugador_enviado'] = jugador_clicado
            st.session_state['temporada_enviada'] = sel_temp
            st.switch_page("pages/Jugadores.py")