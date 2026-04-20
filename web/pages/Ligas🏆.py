import streamlit as st
import pandas as pd
import os

st.title("Ligas")

st.sidebar.header("⚙️ Configuración")

opciones_temporadas = ["2025", "2024", "2023", "2022", "2021", "2020", "2019", "2018", "2017", "2016", "2015", "2014"] 
opciones_ligas = [ "Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1"] 

temporada_elegida = st.sidebar.selectbox("Selecciona la temporada:", opciones_temporadas)
liga_elegida = st.sidebar.selectbox("Selecciona la liga:", opciones_ligas)

tab_clasificacion, tab_goleadores = st.tabs(["📊 Clasificación", "⚽ Goleadores"])


with tab_clasificacion:
    
    
    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    nombre_archivo = f"clasificacion_{temporada_elegida}.csv"
    ruta_csv = os.path.join(directorio_actual, "..", "..", "data_clasificaciones", nombre_archivo)
    
    
    try:
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
            hide_index=True,          
            use_container_width=True,  
            column_config={
                "Puntos": st.column_config.ProgressColumn(
                    "Puntos Obtenidos",  
                    help="Total de puntos conseguidos en la temporada",
                    format="%d",        
                    min_value=0,
                    max_value=114,       
                ),
            }
        )

        # Leyenda
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown("<div style='display: flex; align-items: center;'><div style='width: 20px; height: 20px; background-color: #1f77b4; margin-right: 10px; border-radius: 3px;'></div><span>Champions League</span></div>", unsafe_allow_html=True)
        with col2:
            st.markdown("<div style='display: flex; align-items: center;'><div style='width: 20px; height: 20px; background-color: #ff7f0e; margin-right: 10px; border-radius: 3px;'></div><span>Europa League</span></div>", unsafe_allow_html=True)
        with col3:
            st.markdown("<div style='display: flex; align-items: center;'><div style='width: 20px; height: 20px; background-color: #2ca02c; margin-right: 10px; border-radius: 3px;'></div><span>Conference League</span></div>", unsafe_allow_html=True)
        with col4:
            st.markdown("<div style='display: flex; align-items: center;'><div style='width: 20px; height: 20px; background-color: #d62728; margin-right: 10px; border-radius: 3px;'></div><span>Descenso</span></div>", unsafe_allow_html=True)

    except FileNotFoundError:
        st.warning(f"No se encontró el archivo de clasificación para la temporada {temporada_elegida}.")





with tab_goleadores:
    

    nombre_archivo_goles = f"goleadores_{temporada_elegida}.csv"
    ruta_goles = os.path.join(directorio_actual, "..", "..", "data_clasificaciones", nombre_archivo_goles)
    
    try:
        df_goles = pd.read_csv(ruta_goles)
        
     
        st.markdown(f"### 🇪🇺 BOTA DE ORO EUROPEA ({temporada_elegida})")
        st.caption("Máximos goleadores de todas las competiciones")
        
       
        df_bota_oro = df_goles.sort_values(by='Goles', ascending=False).reset_index(drop=True)
        
        col_oro, col_plata, col_bronce = st.columns(3)
        
        with col_oro:
            st.metric(label="🥇 Bota de Oro", 
                      value=df_bota_oro.iloc[0]['Jugador'], 
                      delta=f"{df_bota_oro.iloc[0]['Goles']} Goles ({df_bota_oro.iloc[0]['Liga']})")
        with col_plata:
            st.metric(label="🥈 Segundo", 
                      value=df_bota_oro.iloc[1]['Jugador'], 
                      delta=f"{df_bota_oro.iloc[1]['Goles']} Goles ({df_bota_oro.iloc[1]['Liga']})")
        with col_bronce:
            st.metric(label="🥉 Tercero", 
                      value=df_bota_oro.iloc[2]['Jugador'], 
                      delta=f"{df_bota_oro.iloc[2]['Goles']} Goles ({df_bota_oro.iloc[2]['Liga']})")
            
        st.markdown("---")
        
      
        if liga_elegida == "Todas":
            st.markdown("### 📊 Top Goleadores Generales")
            df_goles_filtrado = df_bota_oro # Mostramos todos
        else:
            st.markdown(f"### 🎯 Top Goleadores - {liga_elegida}")
          
            df_goles_filtrado = df_goles[df_goles['Liga'] == liga_elegida].sort_values(by='Goles', ascending=False)
        
        subtab_grafico, subtab_tabla = st.tabs(["📊 Gráfico de Barras", "📋 Tabla Detallada"])
        
        with subtab_grafico:
        
            st.bar_chart(df_goles_filtrado.head(10).set_index("Jugador")["Goles"])
            
        with subtab_tabla:
       
            st.dataframe(df_goles_filtrado, hide_index=True, use_container_width=True)

    except FileNotFoundError:
        st.info(f"⏳ Falta subir el archivo de goleadores para la temporada {temporada_elegida} (ej: goleadores_{temporada_elegida}.csv)")