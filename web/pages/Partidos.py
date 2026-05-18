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

    # 3. Inyectamos el Banner con HTML y CSS
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

st.set_page_config(page_title="Partidos", layout="wide")

st.title("Partidos")

# --- SIDEBAR (Solo cosas generales: Liga y Equipo) ---
st.sidebar.header("⚙️ Configuración")

ligas = ["ENG-Premier League", "ESP-La Liga", "GER-Bundesliga", "ITA-Serie A", "FRA-Ligue 1"]
liga_elegida = st.sidebar.selectbox("Selecciona la liga:", ligas)

# Definimos el diccionario de temporadas aquí para que ambos apartados puedan usarlo
traductor_temporadas = {
    "2021/2022": "2122", "2022/2023": "2223", "2023/2024": "2324",
    "2024/2025": "2425", "2025/2026": "2526"
}

directorio_actual = os.path.dirname(os.path.abspath(__file__))
nombre_limpio = liga_elegida.replace(" ", "_")

tab_tabla, tab_calendario = st.tabs(["📊 Tabla de Partidos", "📅 Calendario Mensual"])


with tab_tabla:
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

            df = df.rename(columns={
                'date': 'Fecha',
                'time': 'Hora',
                'home_team': 'Local',
                'score': 'Resultado',
                'away_team': 'Visitante',
                'attendance': 'Asistencia',
                'venue': 'Estadio',
                'referee': 'Árbitro',
                'match_report': 'Reporte'
            })
        lista_equipos = pd.concat([df['Local'], df['Visitante']]).dropna().unique()
        lista_equipos = sorted(lista_equipos)
        lista_equipos.insert(0, "Todos los equipos")
        
        equipo_elegido = st.sidebar.selectbox("Filtra por equipo:", lista_equipos)    

        if equipo_elegido != "Todos los equipos":
            df = df[(df['Local'] == equipo_elegido) | (df['Visitante'] == equipo_elegido)]
        
        def resaltar_resultados(row):
            estilo_local = estilo_visitante = estilo_score = ''
            score = str(row.get('Resultado', '')) 
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
            
            return [estilo_local if col == 'Local' else estilo_visitante if col == 'Visitante' else estilo_score if col == 'Resultado' else '' for col in row.index]

        st.dataframe(df.style.apply(resaltar_resultados, axis=1), column_config={"Reporte": st.column_config.LinkColumn("Reporte", display_text="Ver"), "Asistencia": st.column_config.NumberColumn("Asistencia", format="%d")}, hide_index=True)


    except FileNotFoundError:
        st.error(f"No se encuentra el archivo: {nombre_archivo}")


with tab_calendario:
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

        if 'equipo_elegido' in locals() and equipo_elegido != "Todos los equipos":
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