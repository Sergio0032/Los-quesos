import pandas as pd
import os

# Nombre del archivo donde se guardarán los datos
ARCHIVO_CSV = 'usuarios.csv'

def crear_archivo_si_no_existe():
    """Crea el CSV vacío con las columnas si es la primera vez que se ejecuta."""
    if not os.path.exists(ARCHIVO_CSV):
        df = pd.DataFrame(columns=['username', 'password', 'equipo_favorito'])
        df.to_csv(ARCHIVO_CSV, index=False)

def registrar_usuario(user, password, equipo):
    """Guarda un nuevo usuario en el CSV si no existe ya."""
    crear_archivo_si_no_existe()
    df = pd.read_csv(ARCHIVO_CSV)
    
    # Comprobar si el nombre de usuario ya está cogido
    if user in df['username'].values:
        return False # Fallo: El usuario ya existe
        
    # Añadir el nuevo usuario al final de la tabla
    nuevo_usuario = pd.DataFrame([{
        'username': user, 
        'password': str(password), 
        'equipo_favorito': equipo
    }])
    
    df = pd.concat([df, nuevo_usuario], ignore_index=True)
    df.to_csv(ARCHIVO_CSV, index=False)
    
    return True # Éxito: Usuario registrado

def verificar_usuario(user, password):
    """Comprueba si el usuario y la contraseña coinciden. Si es así, devuelve su equipo."""
    if not os.path.exists(ARCHIVO_CSV):
        return None
        
    df = pd.read_csv(ARCHIVO_CSV)
    
    # Buscamos la fila exacta que coincida con usuario Y contraseña
    match = df[(df['username'] == user) & (df['password'] == str(password))]
    
    if not match.empty:
        # Si hay coincidencia, devolvemos el nombre de su equipo favorito
        equipo = match.iloc[0]['equipo_favorito']
        return equipo
        
    return None # Fallo: Usuario o contraseña incorrectos