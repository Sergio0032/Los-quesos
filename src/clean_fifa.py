import pandas as pd
import os

# 1. Definimos las rutas
directorio_actual = os.path.dirname(os.path.abspath(__file__))
carpeta_fifa = os.path.join(directorio_actual, '..', 'data_fifa')

# Buscamos los archivos específicos de EA FC 24
archivo_origen = os.path.join(carpeta_fifa, 'male_players.csv')
if not os.path.exists(archivo_origen):
    archivo_origen = os.path.join(carpeta_fifa, 'player_24.csv')
if not os.path.exists(archivo_origen):
    archivo_origen = os.path.join(carpeta_fifa, 'players_24.csv')

archivo_destino = os.path.join(carpeta_fifa, 'fifa_top5_ligas.csv')

print("⏳ Cargando los datos de EA FC 24...")

try:
    df = pd.read_csv(archivo_origen, low_memory=False)
    print(f"📊 Datos originales cargados: {len(df)} jugadores encontrados.")

    # 2. Filtrar las 5 grandes ligas
    ligas_top = [
        'Premier League', 'English Premier League', 
        'Spain Primera Division', 'LaLiga', 'Primera Division',
        'Italian Serie A', 'Serie A',
        'German 1. Bundesliga', 'Bundesliga',
        'French Ligue 1', 'Ligue 1'
    ]

    if 'league_name' in df.columns:
        df_limpio = df[df['league_name'].isin(ligas_top)]
    else:
        print("⚠️ No encuentro la columna 'league_name'.")
        df_limpio = df

    # 3. Limpiar columnas inútiles
    columnas_interesantes = [
        'short_name', 'player_positions', 'club_name', 'league_name', 'nationality_name',
        'overall', 'potential', 'pace', 'shooting', 'passing', 'dribbling', 'defending', 'physic'
    ]
    
    cols_finales = [c for c in columnas_interesantes if c in df_limpio.columns]
    df_limpio = df_limpio[cols_finales]

    # 4. Guardar el archivo limpio y ligero
    df_limpio.to_csv(archivo_destino, index=False)
    
    print(f"\n✅ ¡Limpieza de FC 24 completada!")
    print(f"📉 Hemos pasado de {len(df)} jugadores a solo {len(df_limpio)}.")
    print(f"📁 Tu archivo final está en: {archivo_destino}")

except FileNotFoundError:
    print(f"\n❌ No encuentro el archivo de FC 24. Comprueba qué se ha descargado exactamente en tu carpeta data_fifa.")