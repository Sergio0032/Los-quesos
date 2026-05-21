import streamlit as st
import pandas as pd
import unicodedata
import os
import base64

st.set_page_config(page_title="Clasificaciones", page_icon="⚽", layout="wide")

def poner_fondo_futbol(nombre_archivo_fondo):
    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    ruta_fondo = os.path.join(directorio_actual, "..", nombre_archivo_fondo)
    
    try:
        with open(ruta_fondo, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-color: transparent;
            }}

            .stApp::before {{
                content: "";
                position: fixed; 
                top: 0;
                left: 0;
                width: 100vw;
                height: 100vh;
                background-image: url("data:image/jpeg;base64,{encoded_string}");
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                opacity: 0.15; 
                z-index: -1;
            }}
            
            [data-testid="stHeader"], [data-testid="stToolbar"] {{
                background-color: rgba(0,0,0,0) !important;
            }}
            
            .odds-card, .report-box, .stDataFrame {{
                background-color: var(--secondary-background-color) !important;
                border: 1px solid var(--divider-color) !important;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
    except FileNotFoundError:
        st.warning(f"No se encontró la imagen de fondo: {nombre_archivo_fondo}")

poner_fondo_futbol("temaa.jpg")

directorio_actual = os.path.dirname(os.path.abspath(__file__))
ruta_logo = os.path.join(directorio_actual, "..", "logo.png")

if os.path.exists(ruta_logo):
    with open(ruta_logo, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    st.markdown(f"""
        <div style="width: 100%; height: 150px; background-color: #0B132B; 
             background-image: url('data:image/png;base64,{data}');
             background-size: contain; background-repeat: no-repeat; background-position: center;
             border-radius: 10px; margin-bottom: 20px;">
        </div>
    """, unsafe_allow_html=True)

st.title("Clasificaciones")
st.divider()

st.markdown("""
    <style>
    [data-testid="stHeader"], footer {visibility: hidden;}
    .stDataFrame { padding-top: 10px; }
    </style>
""", unsafe_allow_html=True)

LOGOS_MAESTROS = {
    # --- ESPAÑA ---
  "real madrid": "541",
    "barcelona": "529",
    "atletico madrid": "530",
    "sevilla": "536",        
    "sevilla fc": "536",      
    "villarreal": "533",
    "real sociedad": "548",
    "athletic club": "531",
    "real betis": "543",
    "valencia": "532",
    "getafe": "546",
    "osasuna": "727",
    "rayo vallecano": "728",
    "girona": "547",
    "celta vigo": "538",
    "alaves": "542",
    "las palmas": "534",
    "granada": "715",
    "cadiz": "724",
    "leganes": "537",
    "valladolid": "712",
    "espanyol": "540",
    "levante": "539",
    "huesca": "714",
    "cordoba": "718",
    "deportivo la coruña": "720",
    "dep la coruna": "720",
    "malaga": "535",
    
    # --- INGLATERRA ---
    "manchester city": "50", "arsenal": "42", "liverpool": "40", "aston villa": "66",
    "tottenham hotspur": "47", "chelsea": "49", "newcastle united": "34", "manchester utd": "33",
    "west ham united": "48", "brighton": "51", "bournemouth": "35", "crystal palace": "52",
    "fulham": "36", "everton": "45", "brentford": "55", "nottingham forest": "65",
    "luton town": "1359", "burnley": "44", "sheffield united": "62", "leicester city": "46",
    "leeds united": "63", "southampton": "41", "wolverhampton": "39", "wolves": "39",
    
    # --- ITALIA ---
    "inter": "505", "milan": "489", "juventus": "496", "atalanta": "499",
    "roma": "497", "lazio": "487", "fiorentina": "502", "napoli": "492",
    "torino": "503", "genoa": "495", "lecce": "867",
    "bologna": "500", "udinese": "494", "verona": "504", "empoli": "511",
    "frosinone": "512", "sassuolo": "488", "cagliari": "490", "parma": "523", "venezia": "517",
    
    # --- ALEMANIA ---
    "bayer leverkusen": "168", "bayern munich": "157", "stuttgart": "172", "rb leipzig": "173",
    "dortmund": "165", "eintracht frankfurt": "169", "hoffenheim": "167", "freiburg": "160",
    "heidenheim": "188", "werder bremen": "162", "wolfsburg": "161", "augsburg": "170",
    "mainz 05": "164", "monchengladbach": "163", "union berlin": "182", "bochum": "176",
    "koeln": "161", "darmstadt 98": "178", "schalke 04": "174", "hertha bsc": "174",

    # --- FRANCIA ---
    "paris saint-germain": "85", "monaco": "91", "lille": "79", "brest": "106",
    "nice": "84", "lyon": "80", "lens": "116", "marseille": "81",
    "reims": "93", "rennes": "94", "toulouse": "96", "montpellier": "82",
    "strasbourg": "95", "nantes": "83", "lorient": "97",
    "metz": "112", "clermont foot": "99"
}

LOGOS_LIGAS = {
    "Premier League": "https://media.api-sports.io/football/leagues/39.png",
    "La Liga": "https://media.api-sports.io/football/leagues/140.png",
    "Bundesliga": "https://media.api-sports.io/football/leagues/78.png",
    "Serie A": "https://media.api-sports.io/football/leagues/135.png",
    "Ligue 1": "https://media.api-sports.io/football/leagues/61.png"
}

COLORES_FILAS = {
    "UCL": "background-color: rgba(0, 82, 160, 0.12);",      
    "UEL": "background-color: rgba(246, 129, 33, 0.12);",    
    "UECL": "background-color: rgba(0, 177, 64, 0.12);",  
    "Playoff_Descenso": "background-color: rgba(255, 193, 7, 0.15);",
    "Descenso": "background-color: rgba(211, 47, 47, 0.12);", 
    "Nada": ""
}

LOGOS_COMPETICIONES = {
    "UCL": "https://media.api-sports.io/football/leagues/2.png",
    "UEL": "https://media.api-sports.io/football/leagues/3.png",
    "UECL": "https://media.api-sports.io/football/leagues/848.png",
    "Playoff_Descenso": "https://cdn-icons-png.flaticon.com/128/6897/6897039.png", 
    "Descenso": "https://cdn-icons-png.flaticon.com/128/9502/9502124.png",
    "Nada": "https://upload.wikimedia.org/wikipedia/commons/c/ca/1x1.png"
}





def obtener_reglas_automaticas(liga, año_inicio):
   
    excepciones = {
# === LA LIGA ===
        ("La Liga", 2015): {"UCL": 4, "UEL": 2, "UECL": 0, "Descenso": 3, "Playoff_Descenso": 0}, 
        ("La Liga", 2016): {"UCL": 4, "UEL": 3, "UECL": 0, "Descenso": 3, "Playoff_Descenso": 0},
        ("La Liga", 2017): {"UCL": 4, "UEL": 3, "UECL": 0, "Descenso": 3, "Playoff_Descenso": 0},
        ("La Liga", 2018): {"UCL": 4, "UEL": 3, "UECL": 0, "Descenso": 3, "Playoff_Descenso": 0},
        ("La Liga", 2019): {"UCL": 4, "UEL": 3, "UECL": 0, "Descenso": 3, "Playoff_Descenso": 0},
        ("La Liga", 2020): {"UCL": 4, "UEL": 2, "UECL": 0, "Descenso": 3, "Playoff_Descenso": 0}, 
        ("La Liga", 2021): {"UCL": 4, "UEL": 2, "UECL": 1, "Descenso": 3, "Playoff_Descenso": 0},
        ("La Liga", 2022): {"UCL": 4, "UEL": 2, "UECL": 1, "Descenso": 3, "Playoff_Descenso": 0}, 
        ("La Liga", 2023): {"UCL": 4, "UEL": 2, "UECL": 1, "Descenso": 3, "Playoff_Descenso": 0}, 
        ("La Liga", 2024): {"UCL": 5, "UEL": 2, "UECL": 1, "Descenso": 3, "Playoff_Descenso": 0},

        # === PREMIER LEAGUE ===
        ("Premier League", 2015): {"UCL": 4, "UEL": 3, "UECL": 0, "Descenso": 3, "Playoff_Descenso": 0},
        ("Premier League", 2016): {"UCL": 4, "UEL": 1, "UECL": 0, "Descenso": 3, "Playoff_Descenso": 0}, 
        ("Premier League", 2017): {"UCL": 4, "UEL": 3, "UECL": 0, "Descenso": 3, "Playoff_Descenso": 0},
        ("Premier League", 2018): {"UCL": 4, "UEL": 3, "UECL": 0, "Descenso": 3, "Playoff_Descenso": 0},
        ("Premier League", 2019): {"UCL": 4, "UEL": 2, "UECL": 0, "Descenso": 3, "Playoff_Descenso": 0},
        ("Premier League", 2020): {"UCL": 4, "UEL": 2, "UECL": 1, "Descenso": 3, "Playoff_Descenso": 0},
        ("Premier League", 2021): {"UCL": 4, "UEL": 2, "UECL": 1, "Descenso": 3, "Playoff_Descenso": 0},
        ("Premier League", 2022): {"UCL": 4, "UEL": 2, "UECL": 1, "Descenso": 3, "Playoff_Descenso": 0}, 
        ("Premier League", 2023): {"UCL": 4, "UEL": 1, "UECL": 1, "Descenso": 3, "Playoff_Descenso": 0},
        ("Premier League", 2024): {"UCL": 5, "UEL": 2, "UECL": 0, "Descenso": 3, "Playoff_Descenso": 0},

        # === SERIE A ===
        ("Serie A", 2015): {"UCL": 3, "UEL": 3, "UECL": 0, "Descenso": 3, "Playoff_Descenso": 0},
        ("Serie A", 2016): {"UCL": 3, "UEL": 3, "UECL": 0, "Descenso": 3, "Playoff_Descenso": 0},
        ("Serie A", 2017): {"UCL": 4, "UEL": 3, "UECL": 0, "Descenso": 3, "Playoff_Descenso": 0},
        ("Serie A", 2018): {"UCL": 4, "UEL": 0, "UECL": 0, "Descenso": 3, "Playoff_Descenso": 0},
        ("Serie A", 2019): {"UCL": 4, "UEL": 3, "UECL": 0, "Descenso": 3, "Playoff_Descenso": 0},
        ("Serie A", 2020): {"UCL": 4, "UEL": 2, "UECL": 1, "Descenso": 3, "Playoff_Descenso": 0},
        ("Serie A", 2021): {"UCL": 4, "UEL": 2, "UECL": 1, "Descenso": 3, "Playoff_Descenso": 0},
        ("Serie A", 2022): {"UCL": 4, "UEL": 2, "UECL": 0, "Descenso": 4, "Playoff_Descenso": 0},
        ("Serie A", 2023): {"UCL": 5, "UEL": 2, "UECL": 1, "Descenso": 3, "Playoff_Descenso": 0}, 
        ("Serie A", 2024): {"UCL": 4, "UEL": 1, "UECL": 1, "Descenso": 3, "Playoff_Descenso": 0},

        # === BUNDESLIGA === (Siempre 18 equipos: 2 descensos directos, 1 playoff)
        ("Bundesliga", 2015): {"UCL": 4, "UEL": 3, "UECL": 0, "Descenso": 2, "Playoff_Descenso": 1},
        ("Bundesliga", 2016): {"UCL": 4, "UEL": 3, "UECL": 0, "Descenso": 2, "Playoff_Descenso": 1},
        ("Bundesliga", 2017): {"UCL": 4, "UEL": 2, "UECL": 0, "Descenso": 2, "Playoff_Descenso": 1},
        ("Bundesliga", 2018): {"UCL": 4, "UEL": 3, "UECL": 0, "Descenso": 2, "Playoff_Descenso": 1},
        ("Bundesliga", 2019): {"UCL": 4, "UEL": 3, "UECL": 0, "Descenso": 2, "Playoff_Descenso": 1},
        ("Bundesliga", 2020): {"UCL": 4, "UEL": 2, "UECL": 1, "Descenso": 2, "Playoff_Descenso": 1},
        ("Bundesliga", 2021): {"UCL": 4, "UEL": 2, "UECL": 1, "Descenso": 2, "Playoff_Descenso": 1}, 
        ("Bundesliga", 2022): {"UCL": 4, "UEL": 2, "UECL": 1, "Descenso": 2, "Playoff_Descenso": 1},
        ("Bundesliga", 2023): {"UCL": 5, "UEL": 2, "UECL": 1, "Descenso": 2, "Playoff_Descenso": 1},

# === LIGUE 1 ===
        ("Ligue 1", 2015): {"UCL": 3, "UEL": 3, "UECL": 0, "Descenso": 3, "Playoff_Descenso": 0},
        ("Ligue 1", 2016): {"UCL": 3, "UEL": 3, "UECL": 0, "Descenso": 2, "Playoff_Descenso": 1},
        ("Ligue 1", 2017): {"UCL": 3, "UEL": 3, "UECL": 0, "Descenso": 2, "Playoff_Descenso": 1},
        ("Ligue 1", 2018): {"UCL": 3, "UEL": 1, "UECL": 0, "Descenso": 2, "Playoff_Descenso": 1},
        ("Ligue 1", 2019): {"UCL": 3, "UEL": 3, "UECL": 0, "Descenso": 2, "Playoff_Descenso": 0},
        ("Ligue 1", 2020): {"UCL": 3, "UEL": 2, "UECL": 1, "Descenso": 2, "Playoff_Descenso": 1},
        ("Ligue 1", 2021): {"UCL": 3, "UEL": 1, "UECL": 1, "Descenso": 2, "Playoff_Descenso": 1},
        ("Ligue 1", 2022): {"UCL": 3, "UEL": 1, "UECL": 1, "Descenso": 4, "Playoff_Descenso": 0}, 
        ("Ligue 1", 2023): {"UCL": 4, "UEL": 2, "UECL": 1, "Descenso": 2, "Playoff_Descenso": 1}, 
        ("Ligue 1", 2024): {"UCL": 4, "UEL": 2, "UECL": 1, "Descenso": 2, "Playoff_Descenso": 1}
    }

   
    return excepciones.get((liga, año_inicio), {"UCL": 4, "UEL": 2, "UECL": 1, "Descenso": 3, "Playoff_Descenso": 0})

def asignar_estatus(pos, reglas, total_equipos):
    if pos <= reglas["UCL"]: return "UCL"
    if pos <= (reglas["UCL"] + reglas["UEL"]): return "UEL"
    if pos <= (reglas["UCL"] + reglas["UEL"] + reglas["UECL"]): return "UECL"
    if pos > (total_equipos - reglas["Descenso"]): return "Descenso"
    if pos > (total_equipos - reglas["Descenso"] - reglas["Playoff_Descenso"]): return "Playoff_Descenso"
    return "Nada"

def normalizar(txt):
    return ''.join((c for c in unicodedata.normalize('NFD', str(txt).lower().strip()) if unicodedata.category(c) != 'Mn'))


with st.sidebar:
    st.title("🏆 Selecciona tu Liga")
    st.caption("Fútbol Estadísticas Históricas")
    temporada = st.selectbox("Temporada", [f"{a}/{a+1}" for a in range(2025, 2014, -1)])
    liga_sel = st.selectbox("Liga", ["La Liga", "Premier League", "Serie A", "Bundesliga", "Ligue 1"])
    
    st.write("---")
    st.subheader("⚙️ Ajustes Extra Manuales")
    st.info("El sistema aplica las plazas reales automáticamente. Usa esto solo para simulaciones o años nuevos futuros.")
    b_ucl = st.number_input("Añadir UCL Extra", 0, 2, 0)
    b_uel = st.number_input("Añadir UEL Extra", 0, 2, 0)
    b_uecl = st.number_input("Añadir UECL Extra", 0, 2, 0)

try:
    año_inicio = int(temporada.split("/")[0])
    
  
    from pathlib import Path
    ruta_csv = Path(__file__).resolve().parent.parent.parent / "data_clasificaciones" / f"clasificacion_{año_inicio}.csv"
    
    df = pd.read_csv(ruta_csv)
    df = df[df['Liga'] == liga_sel].copy().reset_index(drop=True)
    df["Posicion"] = range(1, len(df) + 1)
    # -------------------------------------------
    
    total_equipos = len(df)

    reglas = obtener_reglas_automaticas(liga_sel, año_inicio)

    reglas = obtener_reglas_automaticas(liga_sel, año_inicio)
    
 
  
    reglas["UCL"] += b_ucl
    reglas["UEL"] += b_uel
    reglas["UECL"] += b_uecl  

  
    df["Estatus"] = df["Posicion"].apply(lambda x: asignar_estatus(x, reglas, total_equipos))
    df["Plaza"] = df["Estatus"].map(LOGOS_COMPETICIONES)

    if liga_sel == "La Liga" and año_inicio == 2022:
        df.loc[df["Posicion"] == 11, "Estatus"] = "UCL"
        df.loc[df["Posicion"] == 11, "Plaza"] = LOGOS_COMPETICIONES["UCL"]

 
    if liga_sel == "La Liga" and año_inicio == 2020:
        df.loc[df["Posicion"] == 7, "Estatus"] = "UCL"
        df.loc[df["Posicion"] == 7, "Plaza"] = LOGOS_COMPETICIONES["UCL"]

    if liga_sel == "La Liga" and año_inicio == 2015:
        df.loc[df["Posicion"] == 7, "Estatus"] = "UCL"
        df.loc[df["Posicion"] == 7, "Plaza"] = LOGOS_COMPETICIONES["UCL"]

    if liga_sel == "Premier League" and año_inicio == 2024:
        df.loc[df["Posicion"] == 12, "Estatus"] = "UECL"
        df.loc[df["Posicion"] == 12, "Plaza"] = LOGOS_COMPETICIONES["UECL"]

    if liga_sel == "Premier League" and año_inicio == 2023:
        df.loc[df["Posicion"] == 8, "Estatus"] = "UEL"
        df.loc[df["Posicion"] == 8, "Plaza"] = LOGOS_COMPETICIONES["UEL"]

    if liga_sel == "Premier League" and año_inicio == 2022:
        df.loc[df["Posicion"] == 14, "Estatus"] = "UEL"
        df.loc[df["Posicion"] == 14, "Plaza"] = LOGOS_COMPETICIONES["UEL"]

    if liga_sel == "Premier League" and año_inicio == 2019:
        df.loc[df["Posicion"] == 8, "Estatus"] = "UEL"
        df.loc[df["Posicion"] == 8, "Plaza"] = LOGOS_COMPETICIONES["UEL"]

    if liga_sel == "Premier League" and año_inicio == 2016:
        df.loc[df["Posicion"] == 6, "Estatus"] = "UCL"
        df.loc[df["Posicion"] == 6, "Plaza"] = LOGOS_COMPETICIONES["UCL"]

        
    if liga_sel == "Premier League" and año_inicio == 2016:
        df.loc[df["Posicion"] == 7, "Estatus"] = "UEL"
        df.loc[df["Posicion"] == 7, "Plaza"] = LOGOS_COMPETICIONES["UEL"]

    if liga_sel == "Serie A" and año_inicio == 2024:
        df.loc[df["Posicion"] == 9, "Estatus"] = "UEL"
        df.loc[df["Posicion"] == 9, "Plaza"] = LOGOS_COMPETICIONES["UEL"]

    if liga_sel == "Serie A" and año_inicio == 2022:
        df.loc[df["Posicion"] == 8, "Estatus"] = "UECL"
        df.loc[df["Posicion"] == 8, "Plaza"] = LOGOS_COMPETICIONES["UECL"]

    if liga_sel == "Serie A" and año_inicio == 2018:
        df.loc[df["Posicion"] == 6, "Estatus"] = "UEL"
        df.loc[df["Posicion"] == 6, "Plaza"] = LOGOS_COMPETICIONES["UEL"]

    if liga_sel == "Serie A" and año_inicio == 2018:
        df.loc[df["Posicion"] == 7, "Estatus"] = "UEL"
        df.loc[df["Posicion"] == 7, "Plaza"] = LOGOS_COMPETICIONES["UEL"]

    if liga_sel == "Serie A" and año_inicio == 2018:
        df.loc[df["Posicion"] == 8, "Estatus"] = "UEL"
        df.loc[df["Posicion"] == 8, "Plaza"] = LOGOS_COMPETICIONES["UEL"]

    if liga_sel == "Bundesliga" and año_inicio == 2024:
        df.loc[df["Posicion"] == 9, "Estatus"] = "UEL"
        df.loc[df["Posicion"] == 9, "Plaza"] = LOGOS_COMPETICIONES["UEL"]

    if liga_sel == "Bundesliga" and año_inicio == 2024:
        df.loc[df["Posicion"] == 6, "Estatus"] = "UECL"
        df.loc[df["Posicion"] == 6, "Plaza"] = LOGOS_COMPETICIONES["UECL"]

    if liga_sel == "Bundesliga" and año_inicio == 2017:
        df.loc[df["Posicion"] == 8, "Estatus"] = "UEL"
        df.loc[df["Posicion"] == 8, "Plaza"] = LOGOS_COMPETICIONES["UEL"]

    if liga_sel == "Ligue 1" and año_inicio == 2022:
        df.loc[df["Posicion"] == 13, "Estatus"] = "UEL"
        df.loc[df["Posicion"] == 13, "Plaza"] = LOGOS_COMPETICIONES["UEL"]

    if liga_sel == "Ligue 1" and año_inicio == 2021:
        df.loc[df["Posicion"] == 9, "Estatus"] = "UEL"
        df.loc[df["Posicion"] == 9, "Plaza"] = LOGOS_COMPETICIONES["UEL"]

    if liga_sel == "Ligue 1" and año_inicio == 2018:
        df.loc[df["Posicion"] == 10, "Estatus"] = "UEL"
        df.loc[df["Posicion"] == 10, "Plaza"] = LOGOS_COMPETICIONES["UEL"]

    if liga_sel == "Ligue 1" and año_inicio == 2018:
        df.loc[df["Posicion"] == 11, "Estatus"] = "UEL"
        df.loc[df["Posicion"] == 11, "Plaza"] = LOGOS_COMPETICIONES["UEL"]

    def buscar_escudo(nombre):
        n = normalizar(nombre)
        team_id = LOGOS_MAESTROS.get(n)
        if team_id:
            return f"https://media.api-sports.io/football/teams/{team_id}.png"
        return f"https://ui-avatars.com/api/?name={n[:2].upper()}&background=1A1E26&color=fff"

    df["Club"] = df["Equipo"].apply(buscar_escudo)

    url_logo = LOGOS_LIGAS.get(liga_sel, "")
    

    col_logo, col_titulo = st.columns([1, 12])
    
    with col_logo:
        if url_logo:
            st.image(url_logo, width=80)
            
    with col_titulo:
       
        st.header(liga_sel)
    
    st.caption(f"Temporada {temporada} • {reglas['UCL']} Plazas UCL • {reglas['UEL']} Plazas UEL • {reglas['UECL']} Plazas UECL")
    st.write("")

    df_styled = df.style.apply(lambda r: [COLORES_FILAS.get(r['Estatus'], '')]*len(r), axis=1).format({"xG_Esperado": "{:.2f}"})

    st.dataframe(
        df_styled,
        use_container_width=True,
        hide_index=True,
        height=750,
        column_config={
            "Posicion": st.column_config.NumberColumn("#", width="small"),
            "Plaza": st.column_config.ImageColumn("🏆", width="small"),
            "Club": st.column_config.ImageColumn("Escudo", width="small"),
            "xG_Esperado": st.column_config.NumberColumn("xG")
        },
        column_order=["Posicion", "Plaza", "Club", "Equipo", "Partidos_Jugados", "Ganados", "Empatados", "Perdidos", "Puntos", "xG_Esperado"]
    )

except Exception as e:
    st.error(f"Error al cargar los datos de la clasificación: {e}")
