import streamlit as st
import pandas as pd
import os
import glob
from datetime import datetime

# 1. CONFIGURACIÓN: PANTALLA COMPLETA Y TÍTULO
st.set_page_config(page_title="App Fútbol Total", layout="wide", page_icon="⚽")

# CSS exclusivo para la estética de las cabeceras de la portada
st.markdown("""
    <style>
    .liga-header { background-color: #1f3b73; color: white; padding: 8px 15px; border-radius: 5px; margin-bottom: 10px; font-weight: bold; }
    h4 { margin-bottom: 0px; padding-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 2. GESTIÓN DE RUTAS
directorio_actual = os.path.dirname(os.path.abspath(__file__))
ruta_base = directorio_actual if os.path.exists(os.path.join(directorio_actual, "data_clasificaciones")) else os.path.join(directorio_actual, "..")


# ==========================================
# SECCIÓN A: PORTADA REAL-TIME (PARTE SUPERIOR)
# ==========================================

@st.cache_data(ttl=60) # Refresca el caché cada 60 segundos por si hay datos nuevos
def load_data_2025():
    try:
        df_c = pd.read_csv(os.path.join(ruta_base, "data_clasificaciones", "clasificacion_2025.csv"))
    except: 
        df_c = pd.DataFrame()
    
    try:
        archivos = glob.glob(os.path.join(ruta_base, "datos_resultados", "*_2526.csv"))
        archivos = list(set(archivos)) 
        if archivos:
            df_r = pd.concat([pd.read_csv(f) for f in archivos], ignore_index=True)
            df_r['date'] = pd.to_datetime(df_r['date'], dayfirst=True, errors='coerce')
        else:
            df_r = pd.DataFrame()
    except: 
        df_r = pd.DataFrame()
    
    return df_c, df_r

df_clasif, df_partidos = load_data_2025()

st.title("⚽ PORTADA REAL-TIME 2025")
st.markdown("---")

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

hoy = datetime.now()

for liga in ligas:
    if not df_clasif.empty:
        equipos_liga = df_clasif[df_clasif['Liga'] == liga['id']]['Equipo'].tolist()
        
        if equipos_liga:
            st.markdown(f"<div class='liga-header'>{liga['icon']} {liga['name']}</div>", unsafe_allow_html=True)
            c_rec, c_cla, c_pro = st.columns(3)

            # Últimos resultados
            with c_rec:
                if not df_partidos.empty:
                    m_rec = df_partidos[(df_partidos['date'] <= hoy) & (df_partidos['home_team'].isin(equipos_liga))].sort_values('date', ascending=False).head(2)
                    if not m_rec.empty:
                        for _, r in m_rec.iterrows():
                            st.markdown(f"**{r['home_team']}** <span style='color:red;'>{r['score']}</span> **{r['away_team']}**", unsafe_allow_html=True)
                    else: st.caption("No hay resultados recientes")
                else: st.caption("Sin datos de partidos")

            # Top 3 Clasificación
            with c_cla:
                top3 = df_clasif[df_clasif['Liga'] == liga['id']].head(3)
                for i, row in enumerate(top3.itertuples(), 1):
                    st.write(f"{i}. {row.Equipo} **{row.Puntos} pts**")

            # Próximos Partidos
            with c_pro:
                if not df_partidos.empty and 'score' in df_partidos.columns:
                    m_prox = df_partidos[
                        (df_partidos['home_team'].isin(equipos_liga)) & 
                        (df_partidos['score'].isna())
                    ].sort_values('date', ascending=True).drop_duplicates(subset=['home_team', 'away_team']).head(2)

                    if not m_prox.empty:
                        for _, p in m_prox.iterrows():
                            f_str = p['date'].strftime('%d/%m') if pd.notna(p['date']) else "TBD"
                            hora = f" | {p['time']}" if 'time' in p and pd.notna(p['time']) else ""
                            
                            st.write(f"📅 {f_str}{hora} - {p['home_team']} vs {p['away_team']}")
                    else: 
                        st.caption("No hay partidos futuros")
                else:
                    st.caption("Sin datos de calendario")
            
            st.markdown("<br>", unsafe_allow_html=True)

st.markdown("<br><br><br>", unsafe_allow_html=True) # Espacio visual entre secciones


