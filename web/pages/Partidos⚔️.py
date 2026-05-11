import streamlit as st
import pandas as pd
import os
import streamlit.components.v1 as components
from streamlit_calendar import calendar 

st.title("Partidos")

st.sidebar.header("⚙️ Configuración")

opciones_temporadas = ["2025/2026", "2024/2025","2023/2024", "2022/2023", "2021/2022"]
temporada_elegida = st.sidebar.selectbox("Selecciona la temporada:", opciones_temporadas)

ligas = ["ENG-Premier League", "ESP-La Liga", "GER-Bundesliga", "ITA-Serie A", "FRA-Ligue 1"]
liga_elegida = st.sidebar.selectbox("Selecciona la liga:", ligas)
traductor_temporadas = {
    "2021/2022": "2122",
    "2022/2023": "2223",
    "2023/2024": "2324",
    "2024/2025": "2425",
    "2025/2026": "2526"
}
codigo_temp = traductor_temporadas[temporada_elegida]

directorio_actual = os.path.dirname(os.path.abspath(__file__))

nombre_limpio = liga_elegida.replace(" ", "_")
nombre_archivo = f"resultados_{nombre_limpio}_{codigo_temp}.csv"
ruta_csv = os.path.join(directorio_actual, "..", "..", "datos_resultados", nombre_archivo)


try:
    df = pd.read_csv(ruta_csv)
    
    columnas_deseadas = [
        'date', 'time', 'home_team', 'score', 'away_team', 
        'attendance', 'venue', 'referee', 'match_report'
    ]
    columnas_finales = [c for c in columnas_deseadas if c in df.columns]
    df = df[columnas_finales]

    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.strftime('%d/%m')

    # LIMPIAR EL ENLACE DEL REPORTE
    if 'match_report' in df.columns:
        def limpiar_enlace(url):
            texto = str(url)
            if texto.startswith('=HYPERLINK'):
                return texto.split('"')[1] 
            elif texto.startswith('/'):
                return f"https://fbref.com{texto}"
            elif texto == 'Sin reporte' or texto.lower() == 'nan' or pd.isna(url):
                return None
            return texto
        df['match_report'] = df['match_report'].apply(limpiar_enlace)
    
    # FILTRAR POR EQUIPO 
    lista_equipos = pd.concat([df['home_team'], df['away_team']]).dropna().unique()
    lista_equipos = sorted(lista_equipos)
    lista_equipos.insert(0, "Todos los equipos")
    
    equipo_elegido = st.sidebar.selectbox("Filtra por equipo:", lista_equipos)    

    if equipo_elegido != "Todos los equipos":
        df = df[(df['home_team'] == equipo_elegido) | (df['away_team'] == equipo_elegido)]
    
    # COLORES
    def resaltar_resultados(row):
        estilo_local = ''
        estilo_visitante = ''
        estilo_score = ''
        
        score = str(row.get('score', ''))
        if '–' in score or '-' in score:
            sep = '–' if '–' in score else '-'
            try:
                goles = score.split(sep)
                g_local = int(goles[0])
                g_visitante = int(goles[1])

                if g_local > g_visitante:
                    estilo_local = 'background-color: #d4edda; color: #155724'   # Verde
                    estilo_visitante = 'background-color: #f8d7da; color: #721c24' # Rojo
                elif g_visitante > g_local:
                    estilo_local = 'background-color: #f8d7da; color: #721c24'   # Rojo
                    estilo_visitante = 'background-color: #d4edda; color: #155724' # Verde
                else:
                    estilo_local = estilo_visitante = 'background-color: #fff3cd; color: #856404' # Naranja
                
                estilo_score = 'font-weight: bold'
            except ValueError:
                pass

        return [estilo_local if col == 'home_team' else 
                estilo_visitante if col == 'away_team' else 
                estilo_score if col == 'score' else '' for col in row.index]

    df_display = df.style.apply(resaltar_resultados, axis=1)
    st.dataframe(
        df_display,
        column_config={
            "match_report": st.column_config.LinkColumn(
                "Reporte",          
                display_text="Ver" 
            ), 
            "attendance": st.column_config.NumberColumn(
                "Asistencia",
                format="%d"  
            )
        },
        hide_index=True  
    )

except FileNotFoundError:
    st.error("No se encuentra el archivo.")
    st.info(f"Ruta intentada: {ruta_csv}")
    
except Exception as e:
    st.error(f"Error inesperado: {e}")


st.divider() 
st.title("Calendario Mensual")
try:
    # Volvemos a cargar el csv limpio
    df_cal = pd.read_csv(ruta_csv, on_bad_lines='skip')
    
    if 'home_team' in df_cal.columns:
        df_cal = df_cal[df_cal['home_team'] != 'home_team']
    
    def fecha_para_calendario(fecha_str):
        if pd.isna(fecha_str): return pd.NaT 
        try:
            fecha_str = str(fecha_str).strip()
            if '-' in fecha_str:
                return pd.to_datetime(fecha_str, errors='coerce')
            partes = fecha_str.split('/')
            if len(partes) == 2: 
                dia, mes = int(partes[0]), int(partes[1])
                anio_inicio = int(temporada_elegida[:4])
                anio_fin = int(temporada_elegida[5:])
                anio = anio_inicio if mes >= 7 else anio_fin
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
            marcador = str(row.get('score', '')).strip()
            hora_raw = str(row.get('time', '')).strip() 
            
            if row['home_team'] == equipo_elegido:
                rival = row['away_team']
                color = "#1f3b73"
            else:
                rival = row['home_team']
                color = "#d9534f"
                
            if marcador and marcador.lower() not in ['nan', 'none', '']:
                titulo = f"{marcador} vs {rival}"
            else:
                titulo = f"vs {rival}"

            # --- LÓGICA DE HORA ROBUSTA ---
            if hora_raw and hora_raw.lower() not in ['nan', 'none', '']:
                # Cogemos los primeros 5 caracteres (por si viene algo como "16:15 h")
                hora_limpia = hora_raw[:5] 
                # Validamos que tenga estrictamente el formato XX:XX
                if len(hora_limpia) == 5 and ":" in hora_limpia:
                    start_full = f"{fecha_str}T{hora_limpia}:00"
                    es_todo_el_dia = False
                else:
                    start_full = fecha_str
                    es_todo_el_dia = True
            else:
                start_full = fecha_str
                es_todo_el_dia = True

            eventos.append({
                "title": titulo,
                "start": start_full,
                "allDay": es_todo_el_dia, 
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
        
    else:
        st.info(" Por favor, selecciona un equipo específico en el menú de la izquierda para poder ver su calendario.")

except Exception as e:
    st.error(f"Error renderizando el calendario: {e}")