import streamlit as st
import pandas as pd
import os
from streamlit_calendar import calendar # La nueva herramienta

st.set_page_config(page_title="Calendario Mensual", layout="wide", page_icon="📅")

st.title("📅 Calendario Mensual de Partidos")

# 1️⃣ MENÚ LATERAL
st.sidebar.header("⚙️ Configuración")
ligas = ["ENG-Premier League", "ESP-La Liga", "GER-Bundesliga", "ITA-Serie A", "FRA-Ligue 1"]
liga_elegida = st.sidebar.selectbox("Selecciona la liga:", ligas)

# Rutas de doble salto (desde web/pages hasta el inicio del proyecto)
directorio_actual = os.path.dirname(os.path.abspath(__file__))
directorio_web = os.path.dirname(directorio_actual)
directorio_raiz = os.path.dirname(directorio_web)
nombre_limpio = liga_elegida.replace(" ", "_")

# Apuntamos a "data_resultados"
ruta_csv = os.path.join(directorio_raiz, "data_resultados", f"resultados_{nombre_limpio}_2526.csv")

try:
    # 2️⃣ CARGAR DATOS
    df = pd.read_csv(ruta_csv, on_bad_lines='skip')
    
    if 'home_team' in df.columns:
        df = df[df['home_team'] != 'home_team']
    
    # Arreglar Fechas (Transformamos todo a formato AÑO-MES-DÍA estrictamente)
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

    # 3️⃣ FILTRO DE EQUIPO OBLIGATORIO (Para que no se amontone la vista)
    equipos = pd.concat([df['home_team'], df['away_team']]).dropna().unique()
    equipos = sorted(equipos)
    
    equipo_elegido = st.sidebar.selectbox("Selecciona un equipo (Recomendado):", equipos)
    
    # Filtramos la tabla solo para el equipo elegido
    df_equipo = df[(df['home_team'] == equipo_elegido) | (df['away_team'] == equipo_elegido)].copy()

    # 4️⃣ CREAR LOS EVENTOS PARA EL CALENDARIO
    eventos = []
    for _, row in df_equipo.iterrows():
        fecha_str = row['date'].strftime('%Y-%m-%d')
        marcador = str(row.get('score', '')).strip()
        
        # Determinar si juega en casa o fuera
        if row['home_team'] == equipo_elegido:
            rival = row['away_team']
            condicion = "🏠 Casa"
            color = "#1f3b73" # Azul oscuro para partidos en casa
        else:
            rival = row['home_team']
            condicion = "✈️ Fuera"
            color = "#d9534f" # Rojo suave para partidos fuera
            
        # Título que saldrá en la casilla
        if marcador and marcador.lower() not in ['nan', 'none', '']:
            titulo = f"{marcador} vs {rival}"
        else:
            titulo = f"vs {rival}"

        eventos.append({
            "title": titulo,
            "start": fecha_str,
            "color": color,
            "display": "block" # Muestra un bloque de color en el día
        })

    # 5️⃣ CONFIGURACIÓN VISUAL DEL CALENDARIO
    opciones_calendario = {
        "locale": "es", # Lo ponemos en Español (L, M, X, J, V, S, D)
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "dayGridMonth,listMonth" # Permite ver el mes o una lista
        },
        "initialView": "dayGridMonth",
        "firstDay": 1, # La semana empieza en Lunes
        "height": 700
    }

    # Mostrar el calendario
    st.markdown(f"### Partidos del **{equipo_elegido}**")
    calendario = calendar(events=eventos, options=opciones_calendario)

except FileNotFoundError:
    st.error(f"No se encuentra el archivo de la liga seleccionada.")
    st.info(f"Ruta intentada: {ruta_csv}")
except Exception as e:
    st.error(f"Error inesperado: {e}")