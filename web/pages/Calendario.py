import streamlit as st
import pandas as pd
import os
from streamlit_calendar import calendar 

st.set_page_config(page_title="Calendario Mensual", layout="wide", page_icon="📅")

st.title("📅 Calendario Mensual de Partidos")

st.sidebar.header("⚙️ Configuración")
ligas = ["ENG-Premier League", "ESP-La Liga", "GER-Bundesliga", "ITA-Serie A", "FRA-Ligue 1"]
liga_elegida = st.sidebar.selectbox("Selecciona la liga:", ligas)

directorio_actual = os.path.dirname(os.path.abspath(__file__))
directorio_web = os.path.dirname(directorio_actual)
directorio_raiz = os.path.dirname(directorio_web)
nombre_limpio = liga_elegida.replace(" ", "_")

ruta_csv = os.path.join(directorio_raiz, "datos_resultados", f"resultados_{nombre_limpio}_2526.csv")

try:
    df = pd.read_csv(ruta_csv, on_bad_lines='skip')
    
    if 'home_team' in df.columns:
        df = df[df['home_team'] != 'home_team']
    
    def fecha_para_calendario(fecha_str):
        if pd.isna(fecha_str): return pd.NaT 
        try:
            fecha_str = str(fecha_str).strip()
            if '-' in fecha_str:
                return pd.to_datetime(fecha_str, errors='coerce')
            partes = fecha_str.split('/')
            if len(partes) == 2: 
                dia, mes = int(partes[0]), int(partes[1])
                anio = 2025 if mes >= 8 else 2026
                return pd.Timestamp(year=anio, month=mes, day=dia)
            return pd.to_datetime(fecha_str, dayfirst=True, errors='coerce')
        except: return pd.NaT

    df['date'] = pd.to_datetime(df['date'].apply(fecha_para_calendario), errors='coerce')
    df = df.dropna(subset=['date'])

    equipos = pd.concat([df['home_team'], df['away_team']]).dropna().unique()
    equipos = sorted(equipos)
    
    equipo_elegido = st.sidebar.selectbox("Selecciona un equipo:", equipos)
    
    df_equipo = df[(df['home_team'] == equipo_elegido) | (df['away_team'] == equipo_elegido)].copy()

    eventos = []
    for _, row in df_equipo.iterrows():
        fecha_str = row['date'].strftime('%Y-%m-%d')
        marcador = str(row.get('score', '')).strip()
        
        if row['home_team'] == equipo_elegido:
            rival = row['away_team']
            condicion = "🏠 Casa"
            color = "#1f3b73"
        else:
            rival = row['home_team']
            condicion = "✈️ Fuera"
            color = "#d9534f"
            
        if marcador and marcador.lower() not in ['nan', 'none', '']:
            titulo = f"{marcador} vs {rival}"
        else:
            titulo = f"vs {rival}"

        eventos.append({
            "title": titulo,
            "start": fecha_str,
            "color": color,
            "display": "block"
        })

    opciones_calendario = {
        "locale": "es",
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "dayGridMonth,listMonth"
        },
        "initialView": "dayGridMonth",
        "firstDay": 1,
        "height": 700
    }

    st.markdown(f"### Partidos del **{equipo_elegido}**")
    calendario = calendar(events=eventos, options=opciones_calendario)

except FileNotFoundError:
    st.error(f"No se encuentra el archivo de la liga seleccionada.")
    st.info(f"Ruta intentada: {ruta_csv}")
except Exception as e:
    st.error(f"Error inesperado: {e}")