import pandas as pd
import os

directorio_actual = os.path.dirname(os.path.abspath(__file__))
carpeta_fifa = os.path.join(directorio_actual, '..', 'data_fifa')


archivo_origen = os.path.join(carpeta_fifa, 'male_players.csv')
if not os.path.exists(archivo_origen):
    archivo_origen = os.path.join(carpeta_fifa, 'players_23.csv')
2
archivo_destino = os.path.join(carpeta_fifa, 'fifa_top5_ligas.csv')

print("⏳ Cargando el mastodonte de datos de la FIFA...")

try:
    
    df = pd.read_csv(archivo_origen, low_memory=False)
    
    print(f"📊 Datos originales cargados: {len(df)} jugadores encontrados.")

    
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
        print("⚠️ No encuentro la columna 'league_name'. Revisa el nombre de las columnas en tu CSV.")
        df_limpio = df

  
    columnas_interesantes = [
        'short_name', 'player_positions', 'club_name', 'league_name', 'nationality_name',
        'overall', 'potential', 'pace', 'shooting', 'passing', 'dribbling', 'defending', 'physic'
    ]
    
    columnas_finales = [c for c in columnas_interesantes if c in df_limpio.columns]
    df_limpio = df_limpio[columnas_finales]

    df_limpio.to_csv(archivo_destino, index=False)
    
    print(f"\n✅ ¡Limpieza completada!")
    print(f"📉 Hemos pasado de {len(df)} jugadores a solo {len(df_limpio)}.")
    print(f"📁 Tu archivo final está en: {archivo_destino}")

except FileNotFoundError:
    print(f"\n❌ No encuentro el archivo {archivo_origen}. Comprueba cómo se llama exactamente dentro de tu carpeta data_fifa.")