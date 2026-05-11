import sys
import os
from pathlib import Path
import streamlit as st
import pandas as pd
import glob
from datetime import datetime
import streamlit as st
import os
import base64

directorio_actual = os.path.dirname(os.path.abspath(__file__))
ruta_logo = os.path.join(directorio_actual, "logo.png")

try:
    with open(ruta_logo, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()

    st.markdown(
        f"""
        <div style="
            width: 100%;
            height: 150px; 
            background-color: #0B132B; /* Color de fondo oscuro. Ajusta este código HEX si no coincide exacto */
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


root_path = str(Path(__file__).resolve().parent.parent)
if root_path not in sys.path:
    sys.path.append(root_path)

from src.database import crear_tabla, registrar_usuario, verificar_usuario

st.set_page_config(page_title="Futbol Champagne", layout="wide", page_icon="⚽")
crear_tabla()

st.markdown("""
    <style>
    .liga-header { background-color: #1f3b73; color: white; padding: 8px 15px; border-radius: 5px; margin-bottom: 10px; font-weight: bold; }
    .fav-header { background-color: #FFD700; color: #1f3b73; padding: 15px; border-radius: 10px; margin-bottom: 20px; border: 2px solid #1f3b73; text-align: center; font-weight: bold; }
    h4 { margin-bottom: 0px; padding-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

if 'logueado' not in st.session_state:
    st.session_state.logueado = False
    st.session_state.user = ""
    st.session_state.equipo = ""

directorio_actual = os.path.dirname(os.path.abspath(__file__))
ruta_base = directorio_actual if os.path.exists(os.path.join(directorio_actual, "data_clasificaciones")) else os.path.join(directorio_actual, "..")

@st.cache_data(ttl=15)
def load_data_2025():
    df_c = pd.DataFrame()
    df_r = pd.DataFrame()
    
    ruta_c = os.path.join(ruta_base, "data_clasificaciones", "clasificacion_2025.csv")
    if os.path.exists(ruta_c):
        try: df_c = pd.read_csv(ruta_c)
        except: pass

    archivos = glob.glob(os.path.join(ruta_base, "datos_resultados", "*_2526.csv"))
    if archivos:
        columnas_nombres = ['date', 'time', 'home_team', 'score', 'away_team', 'attendance', 'stadium', 'referee', 'link']
        lista_dfs = []
        for f in archivos:
            try:
                temp_df = pd.read_csv(f, header=None, names=columnas_nombres, on_bad_lines='skip')
                temp_df = temp_df[temp_df['home_team'] != 'home_team'] 
                lista_dfs.append(temp_df)
            except: continue
        if lista_dfs:
            df_r = pd.concat(lista_dfs, ignore_index=True)
            def arreglar_fecha(fecha_str):
                if pd.isna(fecha_str): return pd.NaT 
                try:
                    fecha_str = str(fecha_str).strip()
                    if '-' in fecha_str: return pd.to_datetime(fecha_str, errors='coerce')
                    partes = fecha_str.split('/')
                    if len(partes) == 2: 
                        dia, mes = int(partes[0]), int(partes[1])
                        anio = 2025 if mes >= 8 else 2026
                        return pd.Timestamp(year=anio, month=mes, day=dia)
                    return pd.to_datetime(fecha_str, dayfirst=True, errors='coerce')
                except: return pd.NaT
            df_r['date'] = pd.to_datetime(df_r['date'].apply(arreglar_fecha), errors='coerce')
            if 'score' in df_r.columns:
                df_r['score'] = df_r['score'].astype(str).str.strip()
    return df_c, df_r

df_clasif, df_partidos = load_data_2025()

with st.sidebar:
    st.title("Área de Usuario")
    if not st.session_state.logueado:
        opcion = st.radio("Acceso", ["Iniciar Sesión", "Registrarse"])
        if opcion == "Iniciar Sesión":
            with st.form("login"):
                u = st.text_input("Usuario")
                p = st.text_input("Pass", type="password")
                if st.form_submit_button("Entrar", use_container_width=True):
                    res = verificar_usuario(u, p)
                    if res:
                        st.session_state.logueado = True
                        st.session_state.user = u
                        st.session_state.equipo = res[0]
                        st.rerun()
                    else: st.error("Fallo")
        else:
            with st.form("reg"):
                new_u = st.text_input("Nuevo Usuario")
                new_p = st.text_input("Contraseña", type="password")
                lista_eq = sorted(df_clasif['Equipo'].unique().tolist()) if not df_clasif.empty else ["Real Madrid"]
                fav_e = st.selectbox("Tu Equipo", lista_eq)
                if st.form_submit_button("Registrar", use_container_width=True):
                    if registrar_usuario(new_u, new_p, fav_e): st.success("OK")
                    else: st.error("Ya existe")
    else:
        st.success(f"Hola, {st.session_state.user}")
        st.info(f"Fan del {st.session_state.equipo}")
        if st.button("Cerrar Sesión"):
            st.session_state.logueado = False
            st.rerun()

st.title("Inicio")

if st.session_state.logueado:
    st.markdown(f"<div class='fav-header'> SEGUIMIENTO ESPECIAL: {st.session_state.equipo.upper()} </div>", unsafe_allow_html=True)

st.markdown("---")

if df_clasif.empty:
    st.warning("No hay datos disponibles en los CSV.")
else:
    hoy = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    ligas = [
        {"name": "La Liga", "icon": "🇪🇸", "id": "La Liga"},
        {"name": "Premier League", "icon": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "id": "Premier League"},
        {"name": "Bundesliga", "icon": "🇩🇪", "id": "Bundesliga"},
        {"name": "Serie A", "icon": "🇮🇹", "id": "Serie A"},
        {"name": "Ligue 1", "icon": "🇫🇷", "id": "Ligue 1"}
    ]

    h1, h2, h3 = st.columns(3)
    h1.markdown("<h4 style='text-align:center; background-color:#f0f2f6; border-radius:5px;'>RESULTADOS</h4>", unsafe_allow_html=True)
    h2.markdown("<h4 style='text-align:center; background-color:#f0f2f6; border-radius:5px;'>TOP 3</h4>", unsafe_allow_html=True)
    h3.markdown("<h4 style='text-align:center; background-color:#f0f2f6; border-radius:5px;'>PRÓXIMOS</h4>", unsafe_allow_html=True)

    mask_jugado = pd.Series(False, index=df_partidos.index)
    if not df_partidos.empty:
        mask_jugado = (df_partidos['score'].notna() & (df_partidos['score'] != '') & (df_partidos['score'].str.lower() != 'nan'))

    for liga in ligas:
        equipos_liga = df_clasif[df_clasif['Liga'] == liga['id']]['Equipo'].tolist()
        if equipos_liga:
            st.markdown(f"<div class='liga-header'>{liga['icon']} {liga['name']}</div>", unsafe_allow_html=True)
            c_rec, c_cla, c_pro = st.columns(3)

            with c_rec:
                m_rec = df_partidos[(df_partidos['home_team'].isin(equipos_liga)) & mask_jugado].sort_values(['date'], ascending=False)
                if not m_rec.empty:
                    for _, r in m_rec.head(2).iterrows():
                        f = r['date'].strftime('%d/%m') if pd.notna(r['date']) else "--"
                        st.markdown(f"<small>{f}</small> | **{r['home_team']}** <span style='color:red;'>{r['score']}</span> **{r['away_team']}**", unsafe_allow_html=True)
                else: st.caption("Sin datos")

            with c_cla:
                top3 = df_clasif[df_clasif['Liga'] == liga['id']].head(3)
                for i, row in enumerate(top3.itertuples(), 1):
                    st.write(f"{i}. {row.Equipo} **{row.Puntos} pts**")

            with c_pro:
                m_pro = df_partidos[(df_partidos['home_team'].isin(equipos_liga)) & ~mask_jugado & (df_partidos['date'] >= hoy)].sort_values('date')
                if not m_pro.empty:
                    for _, p in m_pro.head(2).iterrows():
                        f = p['date'].strftime('%d/%m') if pd.notna(p['date']) else "--"
                        st.write(f"{f} - {p['home_team']} vs {p['away_team']}")
                else: st.caption("No hay próximos")
            st.markdown("<br>", unsafe_allow_html=True)