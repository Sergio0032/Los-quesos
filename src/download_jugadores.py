import soccerdata as sd
import os
import pandas as pd

def traducir_posicion(pos_understat):
    if pd.isna(pos_understat):
        return "Desconocido"
    
    mapa = {
        'GK': 'Portero',
        'D': 'Defensa',
        'M': 'Centrocampista',
        'F': 'Delantero',
        'S': 'Suplente'
    }
    
    partes = str(pos_understat).split()

    traduccion = [mapa.get(p, p) for p in partes]

    return " / ".join(traduccion)

COLUMNAS = {
    'player': 'Jugador',
    'team': 'Equipo',
    'league': 'Liga',
    'season': 'Temporada',
    'position': 'Posicion',
    'games': 'Partidos_Jugados',
    'goals': 'Goles',
    'assists': 'Asistencias',
    'yellow_cards': 'Tarjetas_Amarillas',
    'red_cards': 'Tarjetas_Rojas',
    'xG': 'xG_Esperado',
    'xA': 'xA_Asistencias_Esperadas'
}

def descargar_estadisticas_jugadores():
    ligas = ["ENG-Premier League", "ESP-La Liga", "ITA-Serie A", "GER-Bundesliga", "FRA-Ligue 1"]
    temporadas = [2021, 2022, 2023, 2024, 2025]
    
    os.makedirs("data_jugadores", exist_ok=True)
    
    for temporada in temporadas:
        filename = f"data_jugadores/jugadores_{temporada}.csv"
        
        if os.path.exists(filename):
            print(f"Saltando {temporada}: El archivo ya existe.")
            continue
            
        try:
            print(f"Descargando datos de la temporada {temporada}...")
            
            understat = sd.Understat(leagues=ligas, seasons=[temporada])
            df = understat.read_player_season_stats()
            

            df = df.reset_index()
            

            columnas_existentes = [col for col in COLUMNAS.keys() if col in df.columns]
            df_final = df[columnas_existentes].rename(columns=COLUMNAS)
            
            df_final.to_csv(filename, index=False, encoding='utf-8')
            
            df_final['Posicion'] = df_final['Posicion'].apply(traducir_posicion)
            
            df_final.to_csv(filename, index=False, encoding='utf-8')
            print(f"Temporada {temporada} guardada.")
            
        except Exception as e:
            print(f"Error en la temporada {temporada}: {e}")

if __name__ == "__main__":
    descargar_estadisticas_jugadores()