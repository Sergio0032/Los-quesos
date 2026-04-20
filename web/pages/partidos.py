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
    "2021/2022": "21-22",
    "2022/2023": "22-23",
    "2023/2024": "23-24",
    "2024/2025": "24-25"
}
codigo_temp = traductor_temporadas[temporada_elegida]

directorio_actual = os.path.dirname(os.path.abspath(__file__))

nombre_limpio = liga_elegida.replace(" ", "_")
nombre_archivo = f"resultados_{nombre_limpio}_{codigo_temp}.csv"

ruta_csv = os.path.join(directorio_actual, "..", "..", "data_resultados", nombre_archivo)

try:
    df = pd.read_csv(ruta_csv)
    
    lista_equipos = pd.concat([df['home_team'], df['away_team']]).dropna().unique()
    lista_equipos = sorted(lista_equipos)
    
    lista_equipos.insert(0, "Todos los equipos")
    
    equipo_elegido = st.selectbox("Filtra por equipo:", lista_equipos)
    
    if equipo_elegido != "Todos los equipos":
        df = df[(df['home_team'] == equipo_elegido) | (df['away_team'] == equipo_elegido)]
    
    st.success(f"Archivo cargado: {nombre_archivo}")
    st.write(f"Mostrando partidos de: **{equipo_elegido}**")
    st.dataframe(df)

except FileNotFoundError:
    st.error("No se encuentra el archivo.")
    st.info(f"Ruta intentada: {ruta_csv}")
    
except KeyError:
    st.error("Error")