
import asyncio
import aiohttp
import csv
import os
from understat import Understat

async def descargar_temporada(understat, temporada):
    ligas = {
        'EPL': 'Premier League',
        'La_Liga': 'La Liga',
        'Serie_A': 'Serie A',
        'Bundesliga': 'Bundesliga',
        'Ligue_1': 'Ligue 1',
    }

    filename = f"data/clasificacion_{temporada}.csv"

    if os.path.exists(filename):
        print(f"Saltando {temporada}: El archivo ya existe.")
        return
    try:
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([
                'Temporada', 'Liga', 'Posicion', 'Equipo', 'Partidos_Jugados', 
                'Ganados', 'Empatados', 'Perdidos', 'Goles_a_favor', 
                'Goles_en_contra', 'Puntos', 'xG_Esperado'
            ])

            for id_liga, nombre_liga in ligas.items():
                data = await understat.get_league_table(id_liga, str(temporada))
                equipos = data[1:]

                for pos, stats in enumerate(equipos, start=1):
                    writer.writerow([
                        f"{temporada}/{int(temporada)+1}",
                        nombre_liga,
                        pos,
                        stats[0], 
                        stats[1], 
                        stats[2], 
                        stats[3], 
                        stats[4], 
                        stats[5], 
                        stats[6], 
                        stats[7], 
                        stats[8]  
                    ])
        print(f"Temporada {temporada} guardada.")
    except Exception as e:
        print(f"Error en temporada {temporada}: {e}")

async def main():
    os.makedirs('data', exist_ok=True)
    
    temporadas = range(2014, 2026) 

    async with aiohttp.ClientSession() as session:
        understat = Understat(session)
        
        for año in temporadas:
            await descargar_temporada(understat, año)
            await asyncio.sleep(1)

    print("\n--- Descarga finalizada ---")

if __name__ == "__main__":
    asyncio.run(main())