import soccerdata as sd
import os
import pandas as pd

nombre_carpeta = 'datos_resultados'

ligas = ["ENG-Premier League", "ESP-La Liga", "GER-Bundesliga", "ITA-Serie A", "FRA-Ligue 1"]
temporadas = ["2122", "2223", "2324", "2425", "2526"]

if not os.path.exists(nombre_carpeta):
    os.makedirs(nombre_carpeta)

columnas_deseadas = [
    'date', 
    'time', 
    'home_team', 
    'score', 
    'away_team', 
    'attendance', 
    'venue', 
    'referee', 
    'match_report'
]

for liga in ligas:
    for temporada in temporadas:
        nombre_limpio = liga.replace(" ", "_")
        nombre_archivo = f"{nombre_carpeta}/resultados_{nombre_limpio}_{temporada}.csv"
        
        if os.path.exists(nombre_archivo) and temporada != "2526":
                    print(f" Saltando {liga} {temporada}: El archivo ya existe.")
                    continue
            
        try:
            print(f" Descargando: {liga} | Temporada: {temporada}...")
            fbref = sd.FBref(leagues=liga, seasons=temporada)
            resultados = fbref.read_schedule()

            columnas_finales = [c for c in columnas_deseadas if c in resultados.columns]
            resultados_limpios = resultados[columnas_finales].copy()
            if 'date' in resultados_limpios.columns:

                resultados_limpios['date'] = pd.to_datetime(resultados_limpios['date'], errors='coerce')
                resultados_limpios['date'] = resultados_limpios['date'].dt.strftime('%d/%m')

            if 'match_report' in resultados_limpios.columns:
                def crear_enlace_directo(url):
                    if pd.isna(url) or url == '':
                        return 'Sin reporte'
                    
                    url_str = str(url)
                    
                    if url_str.startswith('/'):
                        return 'https://fbref.com' + url_str
                        
                    return url_str 
                

                resultados_limpios['match_report'] = resultados_limpios['match_report'].apply(crear_enlace_directo)
            
            resultados_limpios.to_csv(nombre_archivo, encoding='utf-8-sig', index=False)
            print(f" Guardado correctamente: {nombre_archivo}")
            
        except Exception as e:
            print(f" Error en {liga} {temporada}: {e}")

print(" Proceso finalizado.")