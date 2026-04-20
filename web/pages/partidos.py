import streamlit as st
import pandas as pd
import os

st.title("Partidos")
st.subheader("Partidos anteriores")

opciones_temporadas = ["2024/2025","2023/2024", "2022/2023", "2021/2022"]
temporada_elegida = st.selectbox("Selecciona la temporada:", opciones_temporadas)

ligas = ["ENG-Premier League", "ESP-La Liga", "GER-Bundesliga", "ITA-Serie A", "FRA-Ligue 1"]
liga_elegida = st.selectbox("Selecciona la liga:", ligas)
traductor_temporadas = {
    "2021/2022": "2122",
    "2022/2023": "2223",
    "2023/2024": "2324",
    "2024/2025": "2425"
}
codigo_temp = traductor_temporadas[temporada_elegida]

directorio_actual = os.path.dirname(os.path.abspath(__file__))

nombre_limpio = liga_elegida.replace(" ", "_")
nombre_archivo = f"datos_resultados_{nombre_limpio}_{codigo_temp}.csv"
ruta_csv = os.path.join(directorio_actual, "..", "..", "data_resultados", nombre_archivo)

try:
    df = pd.read_csv(ruta_csv)
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
    
    lista_equipos = pd.concat([df['home_team'], df['away_team']]).dropna().unique()
    lista_equipos = sorted(lista_equipos)
    
    lista_equipos.insert(0, "Todos los equipos")
    
    equipo_elegido = st.selectbox("Filtra por equipo:", lista_equipos)
    
    if equipo_elegido != "Todos los equipos":
        df = df[(df['home_team'] == equipo_elegido) | (df['away_team'] == equipo_elegido)]
    
    st.success(f"Archivo cargado: {nombre_archivo}")
    st.write(f"Mostrando partidos de: **{equipo_elegido}**")
    def resaltar_resultados(row):
        estilo_local = ''
        estilo_visitante = ''
        estilo_score = ''
        
        score = str(row['score'])
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
            )
        },
        hide_index=True  
    )

except FileNotFoundError:
    st.error("No se encuentra el archivo.")
    st.info(f"Ruta intentada: {ruta_csv}")
    
except KeyError:
    st.error("Error")