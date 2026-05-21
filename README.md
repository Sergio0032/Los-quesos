## Proyecto estadísticas fútbol
Análisis de las estadísticas generales de equipos y jugadores de las 5 grandes ligas europeas desde 2014 hasta la actualidad.

### Integrantes
- Sergio González Moya
- Juan Bravo García
- David Castaños Pérez
- Nicolas Pino Urtubia

### Estructura
- src: código
- data/: Ficheros crudos y trabajados (clasificaciones, jugadores, resultados y FIFA).
- web: Archivos de la interfaz interactiva en Streamlit.

### Dockers

1. Nos hemos basado en una arquitectura de 2 contenedores definidos en Docker Compose, adaptada para sortear las medidas de seguridad de las fuentes de datos:

- Contenedor de Descargas (Worker): se encarga de ejecutar los scripts de recolección de datos (src/). Sin embargo, debido a las estrictas políticas anti-bots y bloqueos de IP de plataformas como FBref al detectar tráfico automatizado desde Docker, la extracción de datos se realiza mediante la ejecución manual de los scripts en la máquina local. Por ello, este contenedor se inicializa, notifica que los datos han sido generados externamente y finaliza su proceso de forma limpia (exit code 0) para dar paso a la web.

- Contenedor App Web: Se encarga de levantar y servir la interfaz interactiva desarrollada en Streamlit (web/MENÚ.py), permitiendo al usuario navegar, filtrar y visualizar todas las estadísticas y clasificaciones.

2. Compartición de Ficheros y Persistencia (Volúmenes)
Dado que la descarga de datos se ha delegado a la ejecución manual por parte del usuario, el flujo de información ya no ocurre entre contenedores, sino entre el sistema anfitrión y la aplicación web mediante el uso de volúmenes de Docker.

3. Al ejecutar los scripts localmente, los datos se almacenan en las carpetas físicas del proyecto (data_clasificaciones, data_jugadores, datos_resultados y data_fifa). Estas carpetas físicas están "conectadas" como volúmenes directamente al Contenedor App Web.

4. De esta forma, la interfaz de Streamlit lee en tiempo real los archivos .csv alojados en el ordenador del usuario. Esto garantiza una persistencia total de la información: aunque los contenedores se detengan o se destruyan, los datos recopilados permanecen seguros y disponibles en el disco duro local.

## Instrucciones
1. Abre la terminal en pyhton

2. Instala las librerías necesarias ejecutando en la terminal: pip install -r requirements.txt

3. Ejecuta los archivos de la carpeta src para tener los CSV. 
python src/download_partidos.py
python src/download_clasificaciones.py
python src/download_jugadores.py
python src/download_fifa.py
    *Nota de actualización: Estos scripts extraen la información en tiempo real. Si deseas ver los datos de partidos o clasificaciones más recientes en el futuro, deberás volver a ejecutar estos comandos para sobreescribir los archivos locales. El script de FIFA (download_fifa.py) ya incluye credenciales de Kaggle configuradas internamente, por lo que se ejecutará de forma automática sin requerir la creación de cuentas ni tokens por parte del evaluador.

4. Para el download fifa en config hay unas claves de usuario, no debes hacer nada porque ya se usan solas si tienes el archivo.

5. Haz funcionar los dockers, con los comandos en la terminal de: 
    - docker-compose build --no-cache
    - docker-compose up

6. Cuando la terminal te indique que streamlit ya fuinciona puedes ejecutar http://localhost:8501 para ver la web