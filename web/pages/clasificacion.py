import streamlit as st
import pandas as pd
import os

st.title("CLASIFICACIONES")



opciones_temporadas = ["2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025" ] 
opciones_ligas = [ "Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1"] 


col1, col2 = st.columns(2)


with col1:
    temporada_elegida = st.selectbox("Selecciona la temporada que quieres ver:", opciones_temporadas)


with col2:
    liga_elegida = st.selectbox("Selecciona la liga:", opciones_ligas)

directorio_actual = os.path.dirname(os.path.abspath(__file__))

nombre_archivo = f"clasificacion_{temporada_elegida}.csv"

ruta_csv = os.path.join(directorio_actual, "..", "..", "data_clasificaciones", nombre_archivo)

df = pd.read_csv(ruta_csv)

if liga_elegida != "Todas":
    df = df[df['Liga'] == liga_elegida]


    
st.markdown("### 🏆 Resumen de la Temporada")


if not df.empty:
    campeon = df.iloc[0]['Equipo']
  
    puntos_campeon = df.iloc[0]['Puntos'] 
    
   
    st.metric(label=f"👑 Campeón ({liga_elegida})", value=campeon, delta=f"{puntos_campeon} Puntos")

st.markdown("---") 


   
def colorear_posiciones(df_a_colorear):
    
    colores = pd.DataFrame('', index=df_a_colorear.index, columns=df_a_colorear.columns)
    
   
    total_equipos = len(df_a_colorear)
    
    for i in range(total_equipos):
        if i < 4:
           
            estilo = 'background-color: #1f77b4; color: white;'
        elif i < 6:
           
            estilo = 'background-color: #ff7f0e; color: white;'
        elif i == 6:
          
            estilo = 'background-color: #2ca02c; color: white;'
        elif i >= total_equipos - 3:
           
            estilo = 'background-color: #d62728; color: white;'
        else:
           
            estilo = ''
            
      
        colores.iloc[i] = estilo
        
    return colores


df = df.reset_index(drop=True)


tabla_estilada = df.style.apply(colorear_posiciones, axis=None)

st.dataframe(
    tabla_estilada,
    hide_index=True,           # Oculta los números grises de la izquierda
    use_container_width=True,  # Hace que la tabla ocupe todo el ancho de la pantalla
    column_config={
        # OJO: "Puntos" debe ser el nombre exacto de la columna en tu CSV
        "Puntos": st.column_config.ProgressColumn(
            "Puntos Obtenidos",  # Nombre que se mostrará en la cabecera
            help="Total de puntos conseguidos en la temporada",
            format="%d",         # %d significa que mostrará números enteros
            min_value=0,
            max_value=114,       # 114 es el máximo de puntos (38 partidos x 3)
        ),
    }
)




col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        "<div style='display: flex; align-items: center;'>"
        "<div style='width: 20px; height: 20px; background-color: #1f77b4; margin-right: 10px; border-radius: 3px;'></div>"
        "<span>Champions League</span>"
        "</div>", 
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        "<div style='display: flex; align-items: center;'>"
        "<div style='width: 20px; height: 20px; background-color: #ff7f0e; margin-right: 10px; border-radius: 3px;'></div>"
        "<span>Europa League</span>"
        "</div>", 
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        "<div style='display: flex; align-items: center;'>"
        "<div style='width: 20px; height: 20px; background-color: #2ca02c; margin-right: 10px; border-radius: 3px;'></div>"
        "<span>Conference League</span>"
        "</div>", 
        unsafe_allow_html=True
    )

with col4:
    st.markdown(
        "<div style='display: flex; align-items: center;'>"
        "<div style='width: 20px; height: 20px; background-color: #d62728; margin-right: 10px; border-radius: 3px;'></div>"
        "<span>Descenso</span>"
        "</div>", 
        unsafe_allow_html=True
    )
