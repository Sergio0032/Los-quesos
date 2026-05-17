import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go
import numpy as np
from urllib.parse import quote
import base64

st.set_page_config(page_title="Táctica de Equipo", layout="wide")
st.markdown("<style>.main { background-color: #ffffff; }</style>", unsafe_allow_html=True)

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

# CARGA Y LIMPIEZA DE DATOS 
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

df = load_all_data()

if not df.empty:

    st.sidebar.header("⚙️ Configuración")

    temporadas_disponibles = [f"{año}/{año+1}" for año in range(2025, 2014, -1)]

    sel_temp = st.sidebar.selectbox("🗓️ Temporada", temporadas_disponibles)
    temp_corto = sel_temp[2:4] + sel_temp[7:9]
    df_temp = df[(df['temporada'] == temp_corto) | (df['temporada'] == int(temp_corto))]
    sel_liga = st.sidebar.selectbox("🏆 Liga", sorted(df_temp['liga'].unique().tolist()))
    df_liga = df_temp[df_temp['liga'] == sel_liga]

    sel_equipo = st.sidebar.selectbox("🛡️ Equipo", sorted(df_liga['equipo'].unique().tolist()))
        
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

        # IMPORTANTE: Metemos el nombre del jugador en 'customdata' para que Plotly 
        # sepa exactamente a quién estamos pinchando en secreto.
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
            clickmode='event+select' # Activamos el modo clic
        )

        st.info(" **Haz clic directamente en el punto o nombre del jugador** sobre el césped para ver su Radar FIFA.")


        evento = st.plotly_chart(fig, use_container_width=True, on_select="rerun")

        # SALTO AUTOMÁTICO 
        if evento and len(evento.selection.get("points", [])) > 0:
            
            jugador_clicado = evento.selection["points"][0]["customdata"]
            
            st.session_state['jugador_enviado'] = jugador_clicado
            st.session_state['temporada_enviada'] = sel_temp
            
            st.switch_page("pages/Jugadores⚽.py")