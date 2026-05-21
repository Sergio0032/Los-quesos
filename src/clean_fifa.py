import pandas as pd

input_file = "data_fifa/male_players.csv"
output_file = "data_fifa/fifa_top5_ligas.csv"

print("Cargando la base de datos...")
df = pd.read_csv(input_file, low_memory=False)

# 1. Filtrar las temporadas: desde la 20/21 (FIFA 21) hasta la 23/24 (FIFA 24)
if 'fifa_version' in df.columns:
    df['fifa_version'] = df['fifa_version'].astype(str).str.split('.').str[0].astype(int)
    df = df[df['fifa_version'].isin([21, 22, 23, 24])]

# 2. Filtrar estricto por las 5 grandes ligas (incluyendo todos los nombres de patrocinadores en estos 4 años)
top5_ligas = [
    'Spain Primera Division', 'LaLiga Santander', 'LaLiga EA SPORTS', 'La Liga',
    'English Premier League', 'Premier League',
    'French Ligue 1', 'Ligue 1 Uber Eats', 'Ligue 1',
    'German 1. Bundesliga', 'Bundesliga',
    'Italian Serie A', 'Serie A TIM', 'Serie A'
]
df = df[df['league_name'].isin(top5_ligas)]

# 3. Renombramos el ID para que las fotos sigan funcionando en tu web
if 'player_id' in df.columns:
    df = df.rename(columns={'player_id': 'sofifa_id'})

# Guardamos el archivo final súper limpio
df.to_csv(output_file, index=False)
print(f"✅ ¡Hecho! Guardados {len(df)} jugadores de las 5 grandes ligas (Temporadas 20/21 a la 23/24).")