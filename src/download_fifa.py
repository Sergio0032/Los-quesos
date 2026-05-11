import os

print("--- INICIANDO DESCARGA DE BASE DE DATOS EA FC 24 ---")
print("Ve a tu perfil de Kaggle -> Settings -> 'Create New Token'.")
print("Abre el archivo kaggle.json que se te descarga con el bloc de notas.\n")

username = input("Introduce tu 'username': ").strip()
key = input("Introduce tu 'key' (la cadena larga): ").strip()

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
    
    dataset = "stefanoleone992/ea-sports-fc-24-complete-player-dataset"
    print(f"Descargando archivos en {carpeta_destino}...")
    
    api.dataset_download_files(dataset, path=carpeta_destino, unzip=True)
    
    print(f"\n✅ ¡Éxito! Datos de EA FC 24 descargados en: {carpeta_destino}")

except Exception as e:
    print(f"\n❌ Error al descargar: {e}")