import streamlit as st
import pandas as pd

st.title("Futbol Champagne")

st.subheader("Clasificación grandes 5 ligas temporada 2024-2025")

df = pd.read_csv("../data/clasificacion_2024.csv")

st.dataframe(df)