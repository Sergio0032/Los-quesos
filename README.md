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
    - Gráficas:
            - pip install pandas
            - pip install plotly

### Dockers

- Se utilizan 2 contenedores.
    1.  **Contenedor Worker:** Se encarga exclusivamente de ejecutar los scripts de la carpeta `src/` (como `download_jugadores.py` o `download_partidos.py`). Su función es recopilar la información de internet de forma aislada.
    2.  **Contenedor App Web:** Ejecuta la interfaz interactiva de Streamlit (`web/MENÚ.py`) para que el usuario pueda interactuar y visualizar los datos.

- Orden de ejecución:
    1.  Primero se ejecuta el contenedor **Worker**. Esto asegura que se descargue la información inicial y los CSV no estén vacíos.
    2.  En segundo lugar, se levanta el contenedor **App Web**, que arranca el servidor de la interfaz.

- Compartición de ficheros: 
    Como los contenedores están separados, necesitan una forma de pasarse los datos. Esto se soluciona conectando a las carpetas `data_clasificaciones`, `data_jugadores` y `datos_resultados`. 
    El contenedor *Worker* guarda ahí la información que descarga, y el contenedor *App Web* lee esos mismos archivos en tiempo real para mostrarlos en la pantalla. Así, si alguno de los contenedores se apaga, los datos de los partidos y jugadores nunca se pierden.