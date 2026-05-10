import os

username = input("Introduce tu 'username' (ej: sergiogarcia): ").strip()
key = input("Introduce tu 'key' (la cadena larga de letras y números): ").strip()

os.environ['KAGGLE_USERNAME'] = username
os.environ['KAGGLE_KEY'] = key

from kaggle.api.kaggle_api_extended import KaggleApi

directorio_actual = os.path.dirname(os.path.abspath(__file__))
carpeta_destino = os.path.join(directorio_actual, '..', 'data_fifa')
carpeta_destino = os.path.abspath(carpeta_destino)

if not os.path.exists(carpeta_destino):
    os.makedirs(carpeta_destino)

print("\nConectando con Kaggle...")
try:
    api = KaggleApi()
    api.authenticate()
    
    dataset = "stefanoleone992/fifa-23-complete-player-dataset"
    print(f"Descargando archivos en {carpeta_destino} (puede tardar un poco)...")
    
    api.dataset_download_files(dataset, path=carpeta_destino, unzip=True)
    
    print(f"\n✅ ¡Éxito! Datos descargados y descomprimidos en: {carpeta_destino}")

except Exception as e:
    print(f"\n❌ Error al descargar: {e}")