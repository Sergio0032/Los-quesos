import streamlit as st
import pandas as pd
import os
import glob
from datetime import datetime

st.set_page_config(page_title="Futbol Champagne", layout="wide", page_icon="⚽")

st.markdown("""
    <style>
    .liga-header { background-color: #1f3b73; color: white; padding: 8px 15px; border-radius: 5px; margin-bottom: 10px; font-weight: bold; }
    h4 { margin-bottom: 0px; padding-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

directorio_actual = os.path.dirname(os.path.abspath(__file__))
ruta_base = directorio_actual if os.path.exists(os.path.join(directorio_actual, "data_clasificaciones")) else os.path.join(directorio_actual, "..")

@st.cache_data(ttl=10) 
@st.cache_data(ttl=15)
def load_data_2025():
    df_c = pd.DataFrame()
    df_r = pd.DataFrame()
    
    ruta_c = os.path.join(ruta_base, "data_clasificaciones", "clasificacion_2025.csv")
    if os.path.exists(ruta_c):
        try:
            df_c = pd.read_csv(ruta_c)
        except: pass

    archivos = glob.glob(os.path.join(ruta_base, "datos_resultados", "*_2526.csv"))
    archivos = list(set(archivos)) 
    
    if archivos:
        columnas_nombres = ['date', 'time', 'home_team', 'score', 'away_team', 'attendance', 'stadium', 'referee', 'link']
        
        lista_dfs = []
        for f in archivos:
            try:
                temp_df = pd.read_csv(f, header=None, names=columnas_nombres, on_bad_lines='skip')
                lista_dfs.append(temp_df)
            except: continue
        
        if lista_dfs:
            df_r = pd.concat(lista_dfs, ignore_index=True)
            
            def arreglar_fecha(fecha_str):
                if pd.isna(fecha_str): return pd.NaT 
                try:
                    fecha_str = str(fecha_str).strip()
                    partes = fecha_str.split('/')
                    if len(partes) == 2: 
                        dia, mes = int(partes[0]), int(partes[1])
                        anio = 2025 if mes >= 8 else 2026
                        return pd.Timestamp(year=anio, month=mes, day=dia)
                    return pd.to_datetime(fecha_str, dayfirst=True, errors='coerce')
                except: return pd.NaT

            df_r['date'] = df_r['date'].apply(arreglar_fecha)
            
            if 'score' in df_r.columns:
                df_r['score'] = df_r['score'].astype(str).str.strip()
        
    return df_c, df_r

df_clasif, df_partidos = load_data_2025()

df_clasif, df_partidos = load_data_2025()

st.title("⚽ PORTADA REAL-TIME 2025")
st.markdown("---")

if df_partidos.empty:
    st.info("ℹ️ La tabla de partidos está vacía. Si no ves errores en rojo arriba, es que el CSV no tiene datos válidos.")
if df_clasif.empty:
    st.info("ℹ️ La tabla de clasificaciones está vacía.")

hoy = datetime.now()

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

for liga in ligas:
    if not df_clasif.empty:
        equipos_liga = df_clasif[df_clasif['Liga'] == liga['id']]['Equipo'].tolist()
        
        if equipos_liga:
            st.markdown(f"<div class='liga-header'>{liga['icon']} {liga['name']}</div>", unsafe_allow_html=True)
            c_rec, c_cla, c_pro = st.columns(3)

            hoy_solo_fecha = hoy.replace(hour=0, minute=0, second=0, microsecond=0)

            with c_rec:
                if not df_partidos.empty:
                    m_rec = df_partidos[
                        (df_partidos['home_team'].isin(equipos_liga)) & 
                        (df_partidos['date'] < hoy_solo_fecha)
                    ].sort_values('date', ascending=False) 

                    if not m_rec.empty:
                        for _, r in m_rec.head(2).iterrows():
                            fecha_f = r['date'].strftime('%d/%m')
                            
                            val_score = str(r.get('score', '')).strip()

                            if not val_score or val_score.lower() in ['nan', 'none', 'null', '']:
                                marcador = "vs"
                            else:
                                marcador = val_score
                                
                            st.markdown(f"<small>{fecha_f}</small> | **{r['home_team']}** <span style='color:red;'>{marcador}</span> **{r['away_team']}**", unsafe_allow_html=True)
                    else: st.caption("Sin resultados anteriores")

            with c_cla:
                top3 = df_clasif[df_clasif['Liga'] == liga['id']].head(3)
                for i, row in enumerate(top3.itertuples(), 1):
                    st.write(f"{i}. {row.Equipo} **{row.Puntos} pts**")

            with c_pro:
                if not df_partidos.empty:
                    m_prox = df_partidos[
                        (df_partidos['home_team'].isin(equipos_liga)) & 
                        (df_partidos['date'] >= hoy_solo_fecha)
                    ].sort_values(['date', 'time'], ascending=True)

                    mask_proximos = (
                        m_prox['score'].isna() | 
                        (m_prox['score'].astype(str).str.strip() == '') | 
                        (m_prox['score'].astype(str).str.strip().str.lower() == 'nan')
                    )
                    m_prox = m_prox[mask_proximos]

                    if not m_prox.empty:
                        for _, p in m_prox.head(2).iterrows():
                            f_str = p['date'].strftime('%d/%m')
                            hora = f" | {p['time']}" if 'time' in p and pd.notna(p['time']) else ""
                            st.write(f"📅 {f_str}{hora} - {p['home_team']} vs {p['away_team']}")
                    else: st.caption("No hay partidos programados")
            
            st.markdown("<br>", unsafe_allow_html=True)