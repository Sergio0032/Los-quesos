import asyncio
import aiohttp
import csv
import os
from understat import Understat

async def descargar_temporada(understat, temporada, es_ultima_temporada):
    # Nombres exactos que procesa correctamente la librería Understat
    ligas = {
        'epl': 'Premier League',
        'la liga': 'La Liga',
        'serie a': 'Serie A',
        'bundesliga': 'Bundesliga',
        'ligue 1': 'Ligue 1',
    }

    filename = f"data_clasificaciones/clasificacion_{temporada}.csv"

    # 1. COMPROBACIÓN: Si no es la última y el archivo ya está en el disco, lo saltamos
    if not es_ultima_temporada and os.path.exists(filename):
        print(f"Saltando {temporada}: El archivo ya existe.")
        return
        
    try:
        # 2. RECOPILACIÓN SEGURA: Guardamos en memoria SIN tocar el disco duro todavía
        filas_a_guardar = []
        
        for id_liga, nombre_liga in ligas.items():
            data = await understat.get_league_table(id_liga, str(temporada))
            equipos = data[1:] # Omitimos la primera fila (la cabecera de la API)

            for pos, stats in enumerate(equipos, start=1):
                filas_a_guardar.append([
                    f"{temporada}/{int(temporada)+1}",
                    nombre_liga,
                    pos,
                    stats[0], stats[1], stats[2], stats[3], stats[4], 
                    stats[5], stats[6], stats[7], stats[8]  
                ])
                
        # 3. ESCRITURA: Solo si el bucle terminó al 100% sin errores, creamos el archivo
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            
            # Cabecera
            writer.writerow([
                'Temporada', 'Liga', 'Posicion', 'Equipo', 'Partidos_Jugados', 
                'Ganados', 'Empatados', 'Perdidos', 'Goles_a_favor', 
                'Goles_en_contra', 'Puntos', 'xG_Esperado'
            ])
            
            # Escribimos todos los equipos de golpe
            writer.writerows(filas_a_guardar)
                    
        # 4. CONFIRMACIÓN FINAL
        if es_ultima_temporada:
            print(f"Temporada {temporada} actualizada con los últimos datos.")
        else:
            print(f"Temporada {temporada} guardada por primera vez.")
            
    except Exception as e:
        print(f"Error en temporada {temporada}: {e}")
        # Seguro de vida: Si por un error extraño se llegó a crear un archivo a medias, lo destruimos
        if os.path.exists(filename):
            os.remove(filename)

async def main():
    os.makedirs('data', exist_ok=True)
    
    temporadas = range(2014, 2026) 
    
    ultima_temporada_del_rango = max(temporadas)

    async with aiohttp.ClientSession() as session:
        understat = Understat(session)
        
        for año in temporadas:
            es_ultima = (año == ultima_temporada_del_rango)
            
            await descargar_temporada(understat, año, es_ultima)
            await asyncio.sleep(1)

    print("\n--- Descarga finalizada ---")

if __name__ == "__main__":
    asyncio.run(main())
