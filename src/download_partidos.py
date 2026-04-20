import soccerdata as sd
import os

ligas = ["ENG-Premier League", "ESP-La Liga", "GER-Bundesliga", "ITA-Serie A", "FRA-Ligue 1"]
temporadas = ["2122", "2223", "2324", "2425", "2526"]

if not os.path.exists('datos_ligas'):
    os.makedirs('datos_ligas')


for liga in ligas:
    for temporada in temporadas:
        nombre_limpio = liga.replace(" ", "_")
        nombre_archivo = f"datos_ligas/resultados_{nombre_limpio}_{temporada}.csv"
        
        if os.path.exists(nombre_archivo):
            print(f"Saltando {liga} {temporada}: El archivo ya existe.")
            continue  
        try:
            print(f" Descargando: {liga} | Temporada: {temporada}...")
            fbref = sd.FBref(leagues=liga, seasons=temporada)
            resultados = fbref.read_schedule()
            
            resultados.to_csv(nombre_archivo, encoding='utf-8-sig')
            print(f"Guardado correctamente: {nombre_archivo}")
            
        except Exception as e:
            print(f"Error en {liga} {temporada}: {e}")


print(" Proceso finalizado.")