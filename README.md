## Proyecto estadísticas fútbol
Análisis de las estadísticas generales de equipos y jugadores de las 5 grandes ligas europeas
desde 2010 hasta la actualidad.

### Integrantes

- Sergio González Moya
- Juan Bravo García
- David Castaños Pérez
- Nicolas Pino Urtubia

### Estructura

- src: código
- data: ficheros crudos y trabajados
- notebooks: ficheros de prueba

### Instrucciones

- Virtual env: python -m venv .venv
    -  Activarlo: .venv\Scripts\activate
- Librerías:
    - Datos fútbol: pip install understat
        - Obligatorias para el funcionamiento:
            - pip install aiohttp
            - pip install asyncio
    - Datos partidos recientes/próximos: pip install soccerdata 
    - Web: pip install streamlit
    - Gráficas: pip install pandas

