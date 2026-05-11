from pathlib import Path
import pandas as pd
import streamlit as st
import urllib.parse
import unicodedata
import os
import base64


directorio_actual = os.path.dirname(os.path.abspath(__file__))
ruta_logo = os.path.join(directorio_actual, "..", "logo.png")

try:
    with open(ruta_logo, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()

    # 3. Inyectamos el Banner con HTML y CSS
    st.markdown(
        f"""
        <div style="
            width: 100%;
            height: 150px; 
            background-color: #0B132B; /* Color de fondo oscuro. Ajusta este código HEX si no coincide exacto */
            background-image: url('data:image/png;base64,{encoded_string}');
            background-size: contain;
            background-repeat: no-repeat;
            background-position: center;
            border-radius: 10px;
            margin-bottom: 20px;
        "></div>
        """,
        unsafe_allow_html=True
    )
except FileNotFoundError:
    st.error("No se encontró el archivo logo.png")
# =========================================================================
# 1. CONFIGURACIÓN CORE
# =========================================================================
st.set_page_config(page_title="Ligas", layout="wide")

st.markdown("""
<style>
    [data-testid="stHeader"], footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# =========================================================================
# 2. ACTIVOS VISUALES (Logos Ligas y MAPEO MAESTRO API-SPORTS)
# =========================================================================
LOGOS_LIGAS = {
    "Premier League": "https://media.api-sports.io/football/leagues/39.png",
    "La Liga": "https://media.api-sports.io/football/leagues/140.png",
    "Bundesliga": "https://media.api-sports.io/football/leagues/78.png",
    "Serie A": "https://media.api-sports.io/football/leagues/135.png",
    "Ligue 1": "https://media.api-sports.io/football/leagues/61.png"
}

# Diccionario Maestro (Regresamos a los IDs estables de API-Sports)
LOGOS_CLUBES = {
    # --- LA LIGA ---
    "real madrid": "541", "barcelona": "529", "atletico madrid": "530", 
    "villarreal": "533", "real betis": "543", "celta vigo": "538", 
    "getafe": "546", "real sociedad": "548", "osasuna": "727", 
    "athletic club": "531", "athletic bilbao": "531", "rayo vallecano": "728", 
    "valencia": "532", "elche": "730", "sevilla": "536", 
    "espanyol": "540", "mallorca": "534", "alaves": "542", 
    "granada": "715", "cadiz": "724", "levante": "539", 
    "real valladolid": "712", "valladolid": "712", "eibar": "537", 
    "girona": "547", "las palmas": "535", "almeria": "733", 
    "leganes": "745", "malaga": "723", "deportivo la coruna": "720", 
    "deportivo": "720", "sporting gijon": "732", "huesca": "714",
    
    # --- PREMIER LEAGUE ---
    "arsenal": "42", "manchester city": "50", "liverpool": "40", 
    "manchester united": "33", "chelsea": "49", "tottenham": "47", 
    "aston villa": "66", "newcastle united": "34", "newcastle": "34",
    "brighton": "51", "west ham": "48", "everton": "45", 
    "crystal palace": "52", "fulham": "36", "brentford": "55", 
    "nottingham forest": "65", "bournemouth": "35", "wolves": "39", 
    "wolverhampton": "39", "leicester": "46", "southampton": "41", 
    "leeds": "63", "burnley": "44", "sheffield united": "62", 
    "sunderland": "73", 
    
    # --- SERIE A ---
    "juventus": "496", "inter": "505", "ac milan": "489", "milan": "489",
    "napoli": "492", "roma": "497", "lazio": "487", "atalanta": "499",
    "fiorentina": "502", "torino": "503", "sassuolo": "488", "udinese": "494",
    "genoa": "495", "sampdoria": "498", "bologna": "500", "cagliari": "490",
    
    # --- BUNDESLIGA ---
    "bayern munich": "157", "borussia dortmund": "165", "bayer leverkusen": "168",
    "rb leipzig": "173", "leipzig": "173", "eintracht frankfurt": "169", "frankfurt": "169",
    "wolfsburg": "161", "hoffenheim": "167", "freiburg": "160", "union berlin": "182",
    "stuttgart": "172", "mainz 05": "164", "mainz": "164",
    
    # --- LIGUE 1 ---
    "paris saint germain": "85", "psg": "85", "marseille": "81", "lyon": "80",
    "monaco": "91", "lille": "79", "rennes": "94", "nice": "84", "lens": "116",
    "strasbourg": "95", "montpellier": "82", "reims": "93", "toulouse": "96"
}

COLORES_FILAS = {
    "UCL": "background-color: rgba(0, 82, 160, 0.15);",      
    "UEL": "background-color: rgba(246, 129, 33, 0.15);",    
    "UECL": "background-color: rgba(0, 177, 64, 0.15);",     
    "Descenso": "background-color: rgba(211, 47, 47, 0.15);", 
    "Nada": ""
}

# =========================================================================
# 3. LÓGICA DE DATOS AVANZADA
# =========================================================================
def normalizar_nombre(nombre):
    """Limpia el texto: elimina mayúsculas, tildes y espacios extra."""
    nombre = str(nombre).strip().lower()
    nombre = ''.join((c for c in unicodedata.normalize('NFD', nombre) if unicodedata.category(c) != 'Mn'))
    return nombre

def obtener_escudo(equipo):
    """Busca el equipo normalizado y devuelve el PNG de la API estable."""
    equipo_norm = normalizar_nombre(equipo)
    
    if equipo_norm in LOGOS_CLUBES:
        id_api = LOGOS_CLUBES[equipo_norm]
        return f"https://media.api-sports.io/football/teams/{id_api}.png"
        
    # Si falta algún equipo (ej. uno de 2ª división muy raro), crea un logo con iniciales
    nombre_seguro = urllib.parse.quote(str(equipo).strip())
    return f"https://ui-avatars.com/api/?name={nombre_seguro}&background=1A1E26&color=FFFFFF&bold=true&length=2&font-size=0.4"

def asignar_estatus(pos, reglas):
    if pos <= reglas["UCL"]: return "UCL"
    if pos <= reglas["UCL"] + reglas["UEL"]: return "UEL"
    if pos <= reglas["UCL"] + reglas["UEL"] + reglas["UECL"]: return "UECL"
    if pos > (20 - reglas["Descenso"]): return "Descenso"
    return "Nada"

@st.cache_data
def cargar_datos_historicos(temporada, liga_seleccionada):
    try:
        año = temporada.split("/")[0]
        ruta_raiz = Path(__file__).resolve().parent.parent.parent
        ruta_archivo = ruta_raiz / "data_clasificaciones" / f"clasificacion_{año}.csv"
        
        df = pd.read_csv(ruta_archivo)
        df_liga = df[df['Liga'] == liga_seleccionada].copy()
        df_liga = df_liga.sort_values(by="Puntos", ascending=False).reset_index(drop=True)
        df_liga["Posicion"] = range(1, len(df_liga) + 1)
        
        # Elimina columnas feas de siglas si existen
        if "Club" in df_liga.columns:
            df_liga = df_liga.drop(columns=["Club"])
        
        reglas = {"UCL": 4, "UEL": 2, "UECL": 1, "Descenso": 3} 
        df_liga["Estatus"] = df_liga["Posicion"].apply(lambda x: asignar_estatus(x, reglas))
        
        # Asignación visual
        df_liga["Escudo"] = df_liga["Equipo"].apply(obtener_escudo)
        logos_plaza = {"UCL": "🔵", "UEL": "🟠", "UECL": "🟢", "Descenso": "🔴", "Nada": "⚫"}
        df_liga["Plaza"] = df_liga["Estatus"].map(logos_plaza)
        
        return df_liga, reglas
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        return pd.DataFrame(), {}

def colorear_filas(row):
    color = COLORES_FILAS.get(row['Estatus'], '')
    return [color] * len(row)

# =========================================================================
# 4. FRONTEND (INTERFAZ)
# =========================================================================
temporadas_disponibles = [f"{año}/{año+1}" for año in range(2025, 2014, -1)]

with st.sidebar:
    st.title("⚽ StatsPro")
    temp_sel = st.selectbox("Temporada", temporadas_disponibles)
    liga_sel = st.selectbox("Torneo", ["La Liga", "Premier League", "Serie A", "Bundesliga", "Ligue 1"])

# --- CABECERA ---
col_logo, col_titulo = st.columns([0.8, 8])
with col_logo:
    st.image(LOGOS_LIGAS.get(liga_sel, ""), width=100)
with col_titulo:
    st.markdown(f"<h1 style='margin-bottom: 0; padding-bottom: 0;'>{liga_sel}</h1>", unsafe_allow_html=True)
    st.caption(f"Temporada {temp_sel} • Clasificación General Histórica")

st.write("---")

# --- RENDERIZADO DE TABLA ---
df, reglas_actuales = cargar_datos_historicos(temp_sel, liga_sel)

if not df.empty:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Líder de la Liga", df.iloc[0]["Equipo"], f"{int(df.iloc[0]['Puntos'])} PTS")
    c2.metric("Mejor xG", df.sort_values("xG_Esperado", ascending=False).iloc[0]["Equipo"])
    c3.metric("Plazas Champions", reglas_actuales.get("UCL", 4))
    c4.metric("Plazas Descenso", reglas_actuales.get("Descenso", 3))
    
    st.write("")

    cols_mostrar = ["Posicion", "Plaza", "Escudo", "Equipo", "Partidos_Jugados", "Ganados", 
                    "Empatados", "Perdidos", "Goles_a_favor", "Goles_en_contra", 
                    "Puntos", "xG_Esperado"]
    
    df_styled = df.style.apply(colorear_filas, axis=1).format({
        "xG_Esperado": "{:.2f}"
    })

    st.dataframe(
        df_styled,
        use_container_width=True,
        hide_index=True,
        height=700,
        column_config={
            "Posicion": st.column_config.NumberColumn("#", width="small"),
            "Plaza": st.column_config.TextColumn("Plaza", width="small"),
            "Escudo": st.column_config.ImageColumn("Club", width="small"), 
            "Equipo": st.column_config.TextColumn("Equipo", width="medium"),
            "Partidos_Jugados": st.column_config.NumberColumn("PJ"),
            "Ganados": st.column_config.NumberColumn("G"),
            "Empatados": st.column_config.NumberColumn("E"),
            "Perdidos": st.column_config.NumberColumn("P"),
            "Goles_a_favor": st.column_config.NumberColumn("GF"),
            "Goles_en_contra": st.column_config.NumberColumn("GC"),
            "Puntos": st.column_config.NumberColumn("PTS"),
            "xG_Esperado": st.column_config.NumberColumn("xG", width="small")
        },
        column_order=cols_mostrar 
    )