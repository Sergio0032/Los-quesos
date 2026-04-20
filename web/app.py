import streamlit as st
import pandas as pd
import os

st.title("Futbol champagne")
st.subheader("Clasificaciones")

opciones_temporadas = ["2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"]
temporada_elegida = st.selectbox("Selecciona la temporada que quieres ver:", opciones_temporadas)

opciones_ligas = ["Todas", "Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1"]
liga_elegida = st.selectbox("Selecciona la liga:", opciones_ligas)

directorio_actual = os.path.dirname(os.path.abspath(__file__))

nombre_archivo = f"clasificacion_{temporada_elegida}.csv"

ruta_csv = os.path.join(directorio_actual, "..", "data_clasificaciones", nombre_archivo)

df = pd.read_csv(ruta_csv)

if liga_elegida != "Todas":
    df = df[df['Liga'] == liga_elegida]

st.dataframe(df)