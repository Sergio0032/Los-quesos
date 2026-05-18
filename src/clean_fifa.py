import pandas as pd

input_file = "data_fifa/male_players.csv"
output_file = "data_fifa/fifa_top5_ligas.csv"

print("Cargando datos masivos...")
df = pd.read_csv(input_file, low_memory=False)

# 1. NOS QUEDAMOS SOLO CON FC 24
if 'fifa_version' in df.columns:
    df['fifa_version'] = df['fifa_version'].astype(str).str.split('.').str[0]
    df = df[df['fifa_version'] == '24']

# 2. BORRAMOS DUPLICADOS (Por si hay cartas repetidas del mismo jugador)
id_col = 'player_id' if 'player_id' in df.columns else 'sofifa_id'
df = df.sort_values(by='age', ascending=False)
df = df.drop_duplicates(subset=[id_col], keep='first')

# 3. RENOMBRAMOS LA COLUMNA ID (Para que las fotos de tu web funcionen)
if 'player_id' in df.columns:
    df = df.rename(columns={'player_id': 'sofifa_id'})

# 4. GUARDAMOS TODOS LOS JUGADORES (Sin borrar a los de Portugal u otras ligas)
df.to_csv(output_file, index=False)
print(f"✅ CSV Machacado. Se han guardado {len(df)} jugadores en la base de datos.")