import requests
import csv
import os
from config import API_KEY

api_key = API_KEY
temporada = 2024 

ligas = {
    'Premier_League': 39,
    'La_Liga': 140,
    'Serie_A': 135,
    'Bundesliga': 78,
    'Ligue_1': 61
}

headers = {
    'x-apisports-key': api_key
}

url = "https://v3.football.api-sports.io/standings"

os.makedirs('data', exist_ok=True)

for nombre_liga, liga_id in ligas.items():
    datos = {
        'league': liga_id,
        'season': temporada
    }

    response = requests.get(url, headers=headers, params=datos)
    

    data = response.json()
        
    if data['response']:
        clasificacion = data['response'][0]['league']['standings'][0]
            
        f444ilename = f"data/clasificacion_{nombre_liga}_{temporada}.csv"            
        44
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
                
            writer.writerow([
                'Posicion', 'Equipo', 'Puntos', 'Partidos_Jugados', 
                'Ganados', 'Empatados', 'Perdidos', 'Goles a favor', 'Goles en contra', 'Diferencia de goles'
            ])
                
            for estadisticas_equipo in clasificacion:
                writer.writerow([
                    estadisticas_equipo['rank'],
                    estadisticas_equipo['team']['name'],
                    estadisticas_equipo['points'],
                    estadisticas_equipo['all']['played'],
                    estadisticas_equipo['all']['win'],
                    estadisticas_equipo['all']['draw'],
                    estadisticas_equipo['all']['lose'],
                    estadisticas_equipo['all']['goals']['for'],
                    estadisticas_equipo['all']['goals']['against'],
                    estadisticas_equipo['goalsDiff']
                ])

        print(f"Archivo guardado correctamente: {filename}")
    else:
        print(f" La API no devolvió datos para {nombre_liga} en el año {temporada}.")


