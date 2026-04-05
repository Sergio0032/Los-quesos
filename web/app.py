import streamlit as st
import pandas as pd

st.title("Futbol champagne")

st.subheader("Clasificacion grandes 5 ligas temprada 2024-2025")

# 1. Guarda los datos en la memoria
df = pd.read_csv("../data/clasificacion_2024.csv")

# 2. Dibuja los datos en la pantalla
st.dataframe(df)


