import streamlit as st
import pandas as pd
import unicodedata
import os
import base64


st.set_page_config(page_title="StatsPro", page_icon="⚽", layout="wide")
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

st.title("Ligas")
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



def normalizar(txt):
    import unicodedata
    return ''.join((c for c in unicodedata.normalize('NFD', str(txt).lower().strip()) if unicodedata.category(c) != 'Mn'))

def obtener_reglas(liga, b_ucl, b_uel):
    reglas = {"UCL": 4, "UEL": 2, "UECL": 1, "Descenso": 3, "Playoff_Descenso": 0}
    
    if liga == "Ligue 1": 
        reglas["UCL"] = 3
        reglas["Descenso"] = 2
        reglas["Playoff_Descenso"] = 1
    elif liga == "Bundesliga":
        reglas["Descenso"] = 2
        reglas["Playoff_Descenso"] = 1
        
    reglas["UCL"] += b_ucl
    reglas["UEL"] += b_uel
    return reglas

def asignar_estatus(pos, reglas, total_equipos):
    if pos <= reglas["UCL"]: return "UCL"
    if pos <= (reglas["UCL"] + reglas["UEL"]): return "UEL"
    if pos <= (reglas["UCL"] + reglas["UEL"] + reglas["UECL"]): return "UECL"
    
   
    if pos > (total_equipos - reglas["Descenso"]): 
        return "Descenso"
    if pos > (total_equipos - reglas["Descenso"] - reglas["Playoff_Descenso"]): 
        return "Playoff_Descenso"
        
    return "Nada"


with st.sidebar:
    st.title("🏆 Selecciona tu Liga")
    temporada = st.selectbox("Temporada", [f"{a}/{a+1}" for a in range(2025, 2014, -1)])
    liga_sel = st.selectbox("Liga", ["La Liga", "Premier League", "Serie A", "Bundesliga", "Ligue 1"])
    st.write("---")
    bonus_ucl = st.number_input("Bonus Champions", 0, 2, 0)
    bonus_uel = st.number_input("Bonus Europa League", 0, 2, 0)


try:
    año = temporada.split("/")[0]
    from pathlib import Path
    ruta_csv = Path(__file__).resolve().parent.parent.parent / "data_clasificaciones" / f"clasificacion_{año}.csv"
    
    df = pd.read_csv(ruta_csv)
    df = df[df['Liga'] == liga_sel].copy().reset_index(drop=True)
    df["Posicion"] = range(1, len(df) + 1)

    # Lógica de Plazas
    reglas = obtener_reglas(liga_sel, bonus_ucl, bonus_uel)
    total_equipos = len(df)
    df["Estatus"] = df["Posicion"].apply(lambda x: asignar_estatus(x, reglas, total_equipos))

    def buscar_escudo(nombre):
        n = normalizar(nombre)
        team_id = LOGOS_MAESTROS.get(n)
        if team_id:
            return f"https://media.api-sports.io/football/teams/{team_id}.png"
        return f"https://ui-avatars.com/api/?name={n[:2].upper()}&background=1A1E26&color=fff"

    df["Club"] = df["Equipo"].apply(buscar_escudo)


    url_logo = LOGOS_LIGAS.get(liga_sel, "")
    
    
    st.markdown(f"""
        <div style="display: flex; align-items: center; margin-bottom: 5px;">
            <img src="{url_logo}" width="80" style="margin-right: 15px;">
            <h1 style="margin: 0; padding: 0; font-size: 2.5rem;">{liga_sel}</h1>
        </div>
    """, unsafe_allow_html=True)
    
    st.caption(f"Temporada {temporada} • Configuración de plazas manual")
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
    st.error(f"Error al cargar los datos: {e}")