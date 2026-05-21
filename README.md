### Proyecto estadísticas fútbol
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

### Instrucciones
ALERTA: RECOMENDAMOS NO ELIMINAR LOS CSV DE CLASIFICACIÓN YA QUE LA API PUEDE DETECTARTE COMO BOT Y NO DEJARTE DESCARGARLO, 
ES PROBABLE Q LA PRIMERA VEZ DEJE PERO NO ES SEGURO, RECOMENDAMOS POR SI ACASO NO ELIMINAR LOS CSV, Y SI SE QUIERRE COMPROBAR 
PROBARLO PERO TENERLOS GUARDADOS POR SI DIERA FALLO PARA Q LA WEB CONTINUE FUNCIONANDO

1. Abre la terminal en pyhton

2. Prepara el entorno virtual en la versión requerida con: 
- py -3.11 -m venv env
- .\env\Scripts\activate
(Sabrá que el entorno está activo cuando vea el prefijo (env) al inicio de la línea en su terminal).

    ⚠️ Requisito Previo Obligatorio: Instalar Python 3.11

    Para garantizar la correcta ejecución de los scripts de recolección de datos y evitar conflictos de compilación de C++ con las librerías, es estrictamente necesario utilizar Python 3.11. Versiones superiores (como 3.12 o 3.13) generarán errores con las librerías

    Si no tiene esta versión instalada, siga estos pasos:
    - Vaya a la página oficial y descargue el instalador de Python 3.11: [Descargar Python 3.11.9](https://www.python.org/downloads/release/python-3119/)
    - Instalación: Al ejecutar el instalador en Windows, asegúrese de marcar la casilla **Add python.exe to PATH**

2. Instala las librerías necesarias ejecutando en la terminal: python -m pip install -r requirements.txt

3. Ejecuta los archivos de la carpeta src para tener los CSV, en este orden(pudes hacerlo copiando estos códgios en la termianl o dandole al play en cada archivo)
python src/download_partidos.py
python src/download_clasificaciones.py
python src/download_jugadores.py
python src/download_fifa.py
python src/clean_fifa.py
python src/añadir_jugadoresU18.py

    *Nota de actualización: Estos scripts extraen la información en tiempo real. Si deseas ver los datos de partidos o clasificaciones más recientes en el futuro, deberás volver a ejecutar estos comandos para sobreescribir los archivos locales.

4. Para el download fifa en el archivo config.py hay unas claves de usuario que tendrás que meter o sino te puedes crear unas en KAGGLE

5. Haz funcionar los dockers, con los comandos en la terminal de: 
    - docker-compose build --no-cache
    - docker-compose up
    *Es necesario tener instalado y abierto docker desktop para este paso.

6. Cuando la terminal te indique que streamlit ya fuinciona puedes ejecutar http://localhost:8501 para ver la web