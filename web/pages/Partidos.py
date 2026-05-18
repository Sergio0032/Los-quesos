import streamlit as st
import pandas as pd
import os
import streamlit.components.v1 as components
from streamlit_calendar import calendar 
import base64

directorio_actual = os.path.dirname(os.path.abspath(__file__))
ruta_logo = os.path.join(directorio_actual, "..", "logo.png")

try:
    with open(ruta_logo, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()

    st.markdown(
        f"""
        <div style="
            width: 100%;
            height: 150px; 
            background-color: #0B132B; 
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

st.set_page_config(page_title="Partidos", layout="wide")
st.title("Partidos")

equipo_fav = st.session_state.get('equipo', None)

@st.cache_data
def obtener_liga_de_equipo(equipo):
    if not equipo: return None
    ruta_clasif = os.path.abspath(os.path.join(directorio_actual, "..", "..", "data_clasificaciones", "clasificacion_2025.csv"))
    try:
        df_c = pd.read_csv(ruta_clasif)
        fila = df_c[df_c['Equipo'] == equipo]
        if not fila.empty:
            return fila.iloc[0]['Liga']
    except:
        pass
    return None

mapa_ligas = {
    "Premier League": "ENG-Premier League",
    "La Liga": "ESP-La Liga",
    "Bundesliga": "GER-Bundesliga",
    "Serie A": "ITA-Serie A",
    "Ligue 1": "FRA-Ligue 1"
}

ligas = ["ENG-Premier League", "ESP-La Liga", "GER-Bundesliga", "ITA-Serie A", "FRA-Ligue 1"]
index_liga_fav = 0

if equipo_fav:
    liga_base = obtener_liga_de_equipo(equipo_fav)
    if liga_base in mapa_ligas:
        liga_formateada = mapa_ligas[liga_base]
        if liga_formateada in ligas:
            index_liga_fav = ligas.index(liga_formateada)

# --- SIDEBAR (Configuración Global) ---
st.sidebar.header("⚙️ Configuración")

liga_elegida = st.sidebar.selectbox("Selecciona la liga:", ligas, index=index_liga_fav)
nombre_limpio = liga_elegida.replace(" ", "_")

# Extraemos la lista de equipos leyendo el archivo de la liga seleccionada
lista_equipos = ["Todos los equipos"]
ruta_base_csv = os.path.join(directorio_actual, "..", "..", "datos_resultados", f"resultados_{nombre_limpio}_2526.csv")
try:
    df_base = pd.read_csv(ruta_base_csv, on_bad_lines='skip')
    if 'home_team' in df_base.columns:
        df_base = df_base[df_base['home_team'] != 'home_team']
        equipos_unicos = pd.concat([df_base['home_team'], df_base['away_team']]).dropna().unique()
        equipos_unicos = sorted(equipos_unicos)
        lista_equipos.extend(equipos_unicos)
except:
    pass

# Seleccionamos el equipo automáticamente si está logueado
index_equipo_fav = 0
if equipo_fav and equipo_fav in lista_equipos:
    index_equipo_fav = lista_equipos.index(equipo_fav)
    
equipo_elegido = st.sidebar.selectbox("Filtra por equipo:", lista_equipos, index=index_equipo_fav)

# Definimos el diccionario de temporadas
traductor_temporadas = {
    "2021/2022": "2122", "2022/2023": "2223", "2023/2024": "2324",
    "2024/2025": "2425", "2025/2026": "2526"
}


st.write("")
vista = st.radio("Selecciona qué deseas ver:", ["📊 Tabla de Partidos", "📅 Calendario Mensual"], horizontal=True, label_visibility="collapsed")
st.divider()

if vista == "📊 Tabla de Partidos":
    opciones_temporadas = ["2025/2026", "2024/2025","2023/2024", "2022/2023", "2021/2022"]
    temporada_elegida = st.selectbox("Selecciona la temporada para la tabla:", opciones_temporadas)
    
    codigo_temp = traductor_temporadas[temporada_elegida]
    nombre_archivo = f"resultados_{nombre_limpio}_{codigo_temp}.csv"
    ruta_csv = os.path.join(directorio_actual, "..", "..", "datos_resultados", nombre_archivo)

    try:
        df = pd.read_csv(ruta_csv)
        
        columnas_deseadas = ['date', 'time', 'home_team', 'score', 'away_team', 'attendance', 'venue', 'referee', 'match_report']
        columnas_finales = [c for c in columnas_deseadas if c in df.columns]
        df = df[columnas_finales]

        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.strftime('%d/%m')

        if 'match_report' in df.columns:
            def limpiar_enlace(url):
                texto = str(url)
                if texto.startswith('=HYPERLINK'): return texto.split('"')[1] 
                elif texto.startswith('/'): return f"https://fbref.com{texto}"
                return None if texto in ['Sin reporte', 'nan'] or pd.isna(url) else texto
            df['match_report'] = df['match_report'].apply(limpiar_enlace)
        
        # Aplicamos el filtro elegido en la barra lateral
        if equipo_elegido != "Todos los equipos":
            df = df[(df['home_team'] == equipo_elegido) | (df['away_team'] == equipo_elegido)]
        
        def resaltar_resultados(row):
            estilo_local = estilo_visitante = estilo_score = ''
            score = str(row.get('score', ''))
            sep = '–' if '–' in score else '-'
            if sep in score:
                try:
                    goles = score.split(sep)
                    g_l, g_v = int(goles[0]), int(goles[1])
                    if g_l > g_v: estilo_local, estilo_visitante = 'background-color: #d4edda; color: #155724', 'background-color: #f8d7da; color: #721c24'
                    elif g_v > g_l: estilo_local, estilo_visitante = 'background-color: #f8d7da; color: #721c24', 'background-color: #d4edda; color: #155724'
                    else: estilo_local = estilo_visitante = 'background-color: #fff3cd; color: #856404'
                    estilo_score = 'font-weight: bold'
                except: pass
            return [estilo_local if col == 'home_team' else estilo_visitante if col == 'away_team' else estilo_score if col == 'score' else '' for col in row.index]

        st.dataframe(df.style.apply(resaltar_resultados, axis=1), column_config={"match_report": st.column_config.LinkColumn("Reporte", display_text="Ver"), "attendance": st.column_config.NumberColumn("Asistencia", format="%d")}, hide_index=True)

    except FileNotFoundError:
        st.error(f"No se encuentra el archivo: {nombre_archivo}")

else:
    st.subheader("📅 Calendario Mensual")
    
    temp_fija = "2025/2026"
    codigo_temp_cal = "2526"
    ruta_csv_cal = os.path.join(directorio_actual, "..", "..", "datos_resultados", f"resultados_{nombre_limpio}_{codigo_temp_cal}.csv")

    try:
        df_cal = pd.read_csv(ruta_csv_cal, on_bad_lines='skip')
        if 'home_team' in df_cal.columns: df_cal = df_cal[df_cal['home_team'] != 'home_team']
        
        def fecha_para_calendario(fecha_str):
            if pd.isna(fecha_str): return pd.NaT 
            try:
                fecha_str = str(fecha_str).strip()
                if '-' in fecha_str: return pd.to_datetime(fecha_str, errors='coerce')
                partes = fecha_str.split('/')
                if len(partes) == 2: 
                    dia, mes = int(partes[0]), int(partes[1])
                    anio = 2025 if mes >= 7 else 2026
                    return pd.Timestamp(year=anio, month=mes, day=dia)
                return pd.to_datetime(fecha_str, dayfirst=True, errors='coerce')
            except: return pd.NaT

        df_cal['date'] = pd.to_datetime(df_cal['date'].apply(fecha_para_calendario), errors='coerce')
        df_cal = df_cal.dropna(subset=['date'])

        if equipo_elegido != "Todos los equipos":
            df_equipo = df_cal[(df_cal['home_team'] == equipo_elegido) | (df_cal['away_team'] == equipo_elegido)].copy()
            eventos = []
            for _, row in df_equipo.iterrows():
                fecha_str = row['date'].strftime('%Y-%m-%d')
                marcador, hora_raw = str(row.get('score', '')).strip(), str(row.get('time', '')).strip()
                color = "#1f3b73" if row['home_team'] == equipo_elegido else "#d9534f"
                rival = row['away_team'] if row['home_team'] == equipo_elegido else row['home_team']
                titulo = f"{marcador} vs {rival}" if marcador and marcador.lower() != 'nan' else f"vs {rival}"

                start_full, es_todo_el_dia = fecha_str, True
                if hora_raw and hora_raw.lower() != 'nan':
                    hora_l = hora_raw[:5]
                    if len(hora_l) == 5 and ":" in hora_l:
                        start_full, es_todo_el_dia = f"{fecha_str}T{hora_l}:00", False

                eventos.append({"title": titulo, "start": start_full, "allDay": es_todo_el_dia, "color": color, "display": "block"})

            calendar(events=eventos, options={"locale": "es", "headerToolbar": {"left": "prev,next today", "center": "title", "right": "dayGridMonth,listMonth"}, "initialView": "dayGridMonth", "firstDay": 1, "height": 700})
        else:
            st.info("👆 Selecciona un equipo en el panel lateral para ver su calendario 25/26.")
    except:
        st.warning("No hay datos de calendario disponibles para la temporada actual.")