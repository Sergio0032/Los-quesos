import pandas as pd
import os

directorio_actual = os.path.dirname(os.path.abspath(__file__))
carpeta_fifa = os.path.join(directorio_actual, '..', 'data_fifa')
archivo_destino = os.path.join(carpeta_fifa, 'fifa_top5_ligas.csv')

# Busca el archivo gigante que te descargaste
archivo_origen = os.path.join(carpeta_fifa, 'male_players.csv')
if not os.path.exists(archivo_origen): archivo_origen = os.path.join(carpeta_fifa, 'player_24.csv')
if not os.path.exists(archivo_origen): archivo_origen = os.path.join(carpeta_fifa, 'players_24.csv')

try:
    df = pd.read_csv(archivo_origen, low_memory=False)

    # --- EL ARREGLO ESTÁ AQUÍ ---
    # Renombramos la columna de FC 24 para recuperar los IDs perdidos
    if 'player_id' in df.columns:
        df = df.rename(columns={'player_id': 'sofifa_id'})

    # 1. ORDEN ESTRICTO DE COLUMNAS (19 en total, empezando por sofifa_id)
    columnas = [
        'sofifa_id', 'short_name', 'long_name', 'player_positions', 
        'club_name', 'league_name', 'nationality_name', 
        'age', 'height_cm', 'weight_kg', 'value_eur', 
        'overall', 'potential', 'pace', 'shooting', 
        'passing', 'dribbling', 'defending', 'physic'
    ]

    # 2. Filtrar ligas
    ligas_top = ['Premier League', 'English Premier League', 'Spain Primera Division', 'LaLiga', 'Primera Division', 'Italian Serie A', 'Serie A', 'German 1. Bundesliga', 'Bundesliga', 'French Ligue 1', 'Ligue 1']
    
    if 'league_name' in df.columns:
        df_limpio = df[df['league_name'].isin(ligas_top)]
    else:
        df_limpio = df

    # 3. Guardar solo las columnas exactas
    cols_finales = [c for c in columnas if c in df_limpio.columns]
    df_limpio = df_limpio[cols_finales]

    df_limpio.to_csv(archivo_destino, index=False)
    print("✅ CSV creado con los IDs de los jugadores recuperados correctamente.")

except Exception as e:
    print(f"❌ Error: {e}")