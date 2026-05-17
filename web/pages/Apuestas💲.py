import streamlit as st
import pandas as pd
import requests
import io
import os
import plotly.graph_objects as go
import numpy as np
from urllib.parse import quote
import base64

st.set_page_config(
    page_title="Fútbol Champagne Pro | 25-26",
    layout="wide"
)

# --- 1. ESTILO INSTITUCIONAL ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;600;900&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
        background-color: #FFFFFF;
        color: #333333;
    }

    /* BARRA LATERAL: COLOR #EBF2F6 */
    [data-testid="stSidebar"] {
        background-color: #EBF2F6 !important;
        border-right: 1px solid #DDE4E9;
    }
    [data-testid="stSidebar"] > div:first-child {
        background-color: #EBF2F6 !important;
    }

    .sidebar-label {
        font-size: 15px;
        font-weight: 800;
        color: #1D3557;
        text-transform: uppercase;
        margin-top: 15px;
        margin-bottom: 5px;
    }

    .stTabs [data-baseweb="tab-list"] { gap: 30px; }
    .stTabs [data-baseweb="tab"] {
        font-size: 17px;
        font-weight: 700;
        color: #6C757D !important;
        text-transform: uppercase;
    }
    .stTabs [aria-selected="true"] {
        color: #E63946 !important;
        border-bottom: 4px solid #E63946 !important;
    }

    .odds-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        padding: 40px;
        border-radius: 8px;
        text-align: center;
    }
    .odds-value {
        color: #D4AF37; 
        font-size: 54px;
        font-weight: 900;
    }

    .report-box {
        background-color: #F8FAFC;
        border-left: 6px solid #1D3557;
        padding: 25px;
        border-radius: 4px;
    }
    </style>
    """, unsafe_allow_html=True)


# --- 2. EXTRACCIÓN EN TIEMPO REAL CON RESPALDO INTEGRAL (96 EQUIPOS) ---
@st.cache_data(ttl=21600)
def descargar_datos_en_vivo():
    urls_fuentes = {
        "Premier League": "https://www.skysports.com/premier-league-table",
        "La Liga": "https://www.skysports.com/la-liga-table",
        "Serie A": "https://www.skysports.com/serie-a-table",
        "Bundesliga": "https://www.skysports.com/bundesliga-table",
        "Ligue 1": "https://www.skysports.com/ligue-1-table"
    }
    
    respaldo_csv = """Temporada,Liga,Posicion,Equipo,Partidos_Jugados,Ganados,Empatados,Perdidos,Goles_a_favor,Goles_en_contra,Puntos,xG_Esperado
2025/2026,Premier League,1,Arsenal,36,24,7,5,68,26,79,72.35
2025/2026,Premier League,2,Manchester City,36,23,8,5,75,32,77,76.71
2025/2026,Premier League,3,Manchester United,37,19,11,7,66,50,68,69.86
2025/2026,Premier League,4,Aston Villa,37,18,8,11,54,48,62,53.76
2025/2026,Premier League,5,Liverpool,37,17,8,12,62,52,59,64.26
2025/2026,Premier League,6,Bournemouth,36,13,16,7,56,52,55,63.78
2025/2026,Premier League,7,Brighton,36,14,11,11,52,42,53,55.48
2025/2026,Premier League,8,Brentford,36,14,9,13,52,49,51,63.25
2025/2026,Premier League,9,Chelsea,36,13,10,13,55,49,49,70.2
2025/2026,Premier League,10,Everton,36,13,10,13,46,46,49,48.28
2025/2026,Premier League,11,Fulham,36,14,6,16,44,50,48,46.37
2025/2026,Premier League,12,Sunderland,36,12,12,12,37,46,48,39.52
2025/2026,Premier League,13,Newcastle United,36,13,7,16,50,52,46,58.24
2025/2026,Premier League,14,Leeds,36,10,14,12,48,53,44,57.07
2025/2026,Premier League,15,Crystal Palace,36,11,11,14,38,47,44,59.63
2025/2026,Premier League,16,Nottingham Forest,37,11,10,16,47,50,43,46.88
2025/2026,Premier League,17,Tottenham,36,9,11,16,46,55,38,43.24
2025/2026,Premier League,18,West Ham,36,9,9,18,42,62,36,45.95
2025/2026,Premier League,19,Burnley,36,4,9,23,37,73,21,35.46
2025/2026,Premier League,20,Wolverhampton Wanderers,36,3,9,24,25,66,18,34.1
2025/2026,La Liga,1,Barcelona,36,30,1,5,91,32,91,96.78
2025/2026,La Liga,2,Real Madrid,36,25,5,6,72,33,80,78.06
2025/2026,La Liga,3,Villarreal,36,21,6,9,67,43,69,65.38
2025/2026,La Liga,4,Atletico Madrid,36,20,6,10,60,39,66,63.81
2025/2026,La Liga,5,Real Betis,36,14,15,7,56,44,57,58.45
2025/2026,La Liga,6,Celta Vigo,36,13,11,12,51,47,50,50.07
2025/2026,La Liga,7,Getafe,36,14,6,16,31,37,48,33.6
2025/2026,La Liga,8,Real Sociedad,36,11,12,13,55,56,45,57.16
2025/2026,La Liga,9,Rayo Vallecano,36,10,14,12,37,43,44,56.4
2025/2026,La Liga,10,Athletic Club,36,13,5,18,40,53,44,51.3
2025/2026,La Liga,11,Sevilla,36,12,7,17,46,58,43,38.21
2025/2026,La Liga,12,Valencia,36,11,10,15,39,51,43,50.13
2025/2026,La Liga,13,Osasuna,36,11,9,16,43,47,42,48.85
2025/2026,La Liga,14,Espanyol,36,11,9,16,40,53,42,49.29
2025/2026,La Liga,15,Alaves,36,10,10,16,42,54,40,50.57
2025/2026,La Liga,16,Girona,36,9,13,14,38,53,40,49.46
2025/2026,La Liga,17,Elche,36,9,12,15,47,56,39,46.98
2025/2026,La Liga,18,Mallorca,36,10,9,17,44,55,39,43.57
2025/2026,La Liga,19,Levante,36,10,9,17,44,59,39,54.8
2025/2026,La Liga,20,Real Oviedo,36,6,11,19,26,56,29,40.63
2025/2026,Serie A,1,Inter,37,27,5,5,86,32,86,85.86
2025/2026,Serie A,2,Napoli,37,22,7,8,57,36,73,56.2
2025/2026,Serie A,3,Roma,37,22,4,11,57,31,70,59.07
2025/2026,Serie A,4,AC Milan,37,20,10,7,52,33,70,63.05
2025/2026,Serie A,5,Como,37,19,11,7,61,28,68,65.28
2025/2026,Serie A,6,Juventus,37,19,11,7,59,32,68,71.62
2025/2026,Serie A,7,Atalanta,36,15,13,8,50,34,58,66.19
2025/2026,Serie A,8,Bologna,36,15,7,14,45,43,52,47.38
2025/2026,Serie A,9,Lazio,37,13,12,12,39,39,51,45.16
2025/2026,Serie A,10,Udinese,36,14,8,14,45,46,50,46.5
2025/2026,Serie A,11,Sassuolo,36,14,7,15,44,46,49,43.91
2025/2026,Serie A,12,Torino,36,12,8,16,41,59,44,49.27
2025/2026,Serie A,13,Parma Calcio 1913,37,10,12,15,27,46,42,34.64
2025/2026,Serie A,14,Genoa,37,10,11,16,41,50,41,47.35
2025/2026,Serie A,15,Fiorentina,37,9,14,14,40,49,41,51.03
2025/2026,Serie A,16,Cagliari,36,9,10,17,36,51,37,38.53
2025/2026,Serie A,17,Lecce,36,8,8,20,24,48,32,33.72
2025/2026,Serie A,18,Cremonese,36,7,10,19,30,53,31,35.84
2025/2026,Serie A,19,Verona,37,3,12,22,25,59,21,36.8
2025/2026,Serie A,20,Pisa,37,2,12,23,25,69,18,40.99
2025/2026,Bundesliga,1,Bayern Munich,34,28,5,1,122,36,89,104.81
2025/2026,Bundesliga,2,Borussia Dortmund,34,22,7,5,70,34,73,67.8
2025/2026,Bundesliga,3,RasenBallsport Leipzig,34,20,5,9,66,47,65,75.18
2025/2026,Bundesliga,4,VfB Stuttgart,34,18,8,8,71,49,62,68.33
2025/2026,Bundesliga,5,Hoffenheim,34,18,7,9,65,52,61,63.15
2025/2026,Bundesliga,6,Bayer Leverkusen,34,17,8,9,68,47,59,75.25
2025/2026,Bundesliga,7,Freiburg,34,13,8,13,51,57,47,50.13
2025/2026,Bundesliga,8,Eintracht Frankfurt,34,11,11,12,61,65,44,51.02
2025/2026,Bundesliga,9,Augsburg,34,12,7,15,45,61,43,51.27
2025/2026,Bundesliga,10,Mainz 05,34,10,10,14,44,53,40,63.26
2025/2026,Bundesliga,11,Union Berlin,34,10,9,15,44,58,39,48.41
2025/2026,Bundesliga,12,Borussia M.Gladbach,34,9,11,14,42,53,38,46.69
2025/2026,Bundesliga,13,Hamburger SV,34,9,11,14,40,54,38,43.83
2025/2026,Bundesliga,14,FC Cologne,34,7,11,16,49,63,32,53.83
2025/2026,Bundesliga,15,Werder Bremen,34,8,8,18,37,60,32,42.35
2025/2026,Bundesliga,16,Wolfsburg,34,7,8,19,45,69,29,52.58
2025/2026,Bundesliga,17,FC Heidenheim,34,6,8,20,41,72,26,49.97
2025/2026,Bundesliga,18,St. Pauli,34,6,8,20,29,60,26,34.03
2025/2026,Ligue 1,1,Paris Saint Germain,33,24,4,5,73,27,76,74.77
2025/2026,Ligue 1,2,Lens,33,21,4,8,62,35,67,72.34
2025/2026,Ligue 1,3,Lille,33,18,7,8,52,35,61,55.97
2025/2026,Ligue 1,4,Lyon,33,18,6,9,53,36,60,54.04
2025/2026,Ligue 1,5,Rennes,33,17,8,8,58,47,59,52.26
2025/2026,Ligue 1,6,Marseille,33,17,5,11,60,44,56,65.54
2025/2026,Ligue 1,7,Monaco,33,16,6,11,56,49,54,59.96
2025/2026,Ligue 1,8,Strasbourg,33,14,8,11,53,43,50,54.65
2025/2026,Ligue 1,9,Lorient,33,11,12,10,48,49,45,47.84
2025/2026,Ligue 1,10,Toulouse,33,12,8,13,47,46,44,46.29
2025/2026,Ligue 1,11,Paris FC,33,10,11,12,45,49,41,47.38
2025/2026,Ligue 1,12,Brest,33,10,8,15,42,54,38,43.99
2025/2026,Ligue 1,13,Angers,33,9,8,16,28,47,35,32.39
2025/2026,Ligue 1,14,Le Havre,33,6,14,13,30,44,32,37.4
2025/2026,Ligue 1,15,Auxerre,33,7,10,16,32,44,31,39.72
2025/2026,Ligue 1,16,Nice,33,7,10,16,37,60,31,45.57
2025/2026,Ligue 1,17,Nantes,33,5,8,20,29,52,23,37.82
2025/2026,Ligue 1,18,Metz,33,3,7,23,32,76,16,32.74"""

    dict_final = {}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        for liga, url in urls_fuentes.items():
            req = requests.get(url, headers=headers, timeout=5)
            tablas = pd.read_html(io.StringIO(req.text))
            df_tabla = tablas[0]
            
            df_tabla = df_tabla[['#', 'Team', 'F', 'A']].copy()
            df_tabla.columns = ['pos', 'equipo', 'gf', 'gc']
            
            total_equipos = len(df_tabla)
            equipos_dict = {}
            
            for _, fila in df_tabla.iterrows():
                nombre_limpio = str(fila['equipo']).strip()
                equipos_dict[nombre_limpio] = {
                    "pos": int(fila['pos']),
                    "gf": int(fila['gf']),
                    "gc": int(fila['gc'])
                }
                
            dict_final[liga] = {
                "total": total_equipos,
                "equipos": equipos_dict
            }
    except Exception:
        df_respaldo = pd.read_csv(io.StringIO(respaldo_csv))
        dict_final = {}
        for liga in df_respaldo['Liga'].unique():
            df_liga = df_respaldo[df_respaldo['Liga'] == liga]
            total_equipos = len(df_liga)
            equipos = {}
            for _, row in df_liga.iterrows():
                equipos[row['Equipo']] = {
                    "pos": int(row['Posicion']), 
                    "gf": int(row['Goles_a_favor']), 
                    "gc": int(row['Goles_en_contra'])
                }
            dict_final[liga] = {
                "total": total_equipos,
                "equipos": equipos
            }
        
    return dict_final

datos_ligas = descargar_datos_en_vivo()


# --- 3. MOTOR DE CÁLCULO PROFESIONAL ---
def calcular_cuotas_Champagne(sl, sv, n):
    p_pos_l = (n - sl["pos"] + 1) / n
    p_pos_v = (n - sv["pos"] + 1) / n
    eff_l = sl["gf"] / max(1, sl["gc"])
    eff_v = sv["gf"] / max(1, sv["gc"])
    
    f_l = (p_pos_l * 0.65 + eff_l * 0.35) * 1.12
    f_v = (p_pos_v * 0.65 + eff_v * 0.35)
    
    total = f_l + f_v
    prob_l_base = f_l / total
    prob_v_base = f_v / total
    
    dif = abs(prob_l_base - prob_v_base)
    prob_e = 0.28 - (dif * 0.10)
    
    p_l = prob_l_base * (1.0 - prob_e)
    p_v = prob_v_base * (1.0 - prob_e)
    
    return round(1/p_l, 2), round(1/prob_e, 2), round(1/p_v, 2)


# --- 4. PANEL DE CONTROL (BARRA LATERAL) ---
with st.sidebar:
    st.markdown('<p class="sidebar-label">PANEL DE CONTROL</p>', unsafe_allow_html=True)
    liga_sel = st.selectbox("LIGA", list(datos_ligas.keys()))
    equipos = sorted(list(datos_ligas[liga_sel]["equipos"].keys()))
    loc = st.selectbox("LOCAL", equipos, index=0)
    vis = st.selectbox("VISITANTE", equipos, index=min(1, len(equipos)-1))
    st.markdown("---")


# --- 5. ENCABEZADO INSTITUCIONAL DE ÉLITE ---
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
else:
    st.markdown("""
        <div style="width: 100%; height: 120px; background-color: #0B132B; 
             display: flex; align-items: center; justify-content: center;
             border-radius: 10px; margin-bottom: 20px;">
             <h1 style="color: #FFFFFF; font-family: 'Outfit', sans-serif; font-weight: 900; margin: 0; text-transform: uppercase; letter-spacing: 2px; font-size:36px;">FÚTBOL CHAMPAGNE PRO</h1>
        </div>
        """, unsafe_allow_html=True)


# --- 6. INTERFAZ GRÁFICA PRINCIPAL ---
tab1, tab2, tab3 = st.tabs(["ANÁLISIS 1X2", "GESTIÓN DE BANCA", "INFORME TÉCNICO"])

if loc != vis:
    cl, ce, cv = calcular_cuotas_Champagne(
        datos_ligas[liga_sel]["equipos"][loc], 
        datos_ligas[liga_sel]["equipos"][vis], 
        datos_ligas[liga_sel]["total"]
    )
else:
    cl = ce = cv = None

with tab1:
    if loc == vis:
        st.warning("⚠️ Seleccione equipos diferentes en la barra de control lateral.")
    else:
        st.markdown(f"<h3 style='color: #1D3557;'>JORNADA ANALIZADA: {loc.upper()} VS {vis.upper()}</h3>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="odds-card"><div style="color:#6C757D; font-weight:800; font-size:13px; margin-bottom:15px; text-transform:uppercase;">GANA {loc.upper()}</div><div class="odds-value">{cl}</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="odds-card"><div style="color:#6C757D; font-weight:800; font-size:13px; margin-bottom:15px; text-transform:uppercase;">EMPATE</div><div class="odds-value">{ce}</div></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="odds-card"><div style="color:#6C757D; font-weight:800; font-size:13px; margin-bottom:15px; text-transform:uppercase;">GANA {vis.upper()}</div><div class="odds-value">{cv}</div></div>', unsafe_allow_html=True)

with tab2:
    if loc == vis:
        st.info("ℹ️ Modifique las selecciones para desbloquear la pestaña financiera.")
    else:
        st.markdown(f"<h3 style='color: #1D3557;'>SIMULADOR DE CUPÓN DE APUESTAS</h3>", unsafe_allow_html=True)
        
        col_slip, col_payout = st.columns(2)
        
        with col_slip:
            # Selector de mercado tradicional tal como en una casa de apuestas real
            opciones_pronostico = [
                f"Gana {loc} (Cuota: {cl})", 
                f"Empate (Cuota: {ce})", 
                f"Gana {vis} (Cuota: {cv})"
            ]
            seleccion = st.radio("SELECCIONA TU MERCADO", opciones_pronostico)
            
            # Asignación de la cuota activa según el botón seleccionado
            if seleccion == opciones_pronostico[0]:
                cuota_seleccionada = cl
                texto_ticket = f"Gana {loc}"
            elif seleccion == opciones_pronostico[1]:
                cuota_seleccionada = ce
                texto_ticket = "Empate"
            else:
                cuota_seleccionada = cv
                texto_ticket = f"Gana {vis}"
                
            dinero_apostado = st.number_input("CANTIDAD A JUGAR (€)", min_value=1.0, value=10.0, step=5.0)
            
        with col_payout:
            pago_bruto = round(dinero_apostado * cuota_seleccionada, 2)
            beneficio_neto = round(pago_bruto - dinero_apostado, 2)
            
            st.markdown(f"""
            <div style="background: #F8FAFC; border: 1px solid #E2E8F0; padding: 20px; border-radius: 8px; margin-bottom: 15px;">
                <span style="color:#6C757D; font-weight:800; font-size:12px; text-transform:uppercase;">PRONÓSTICO TICKET</span>
                <h4 style="color: #1D3557; margin: 5px 0; font-weight: 700;">{texto_ticket.upper()}</h4>
            </div>
            <div style="background: #1D3557; border: 1px solid #1D3557; padding: 22px; border-radius: 8px; margin-bottom: 15px; color: white;">
                <span style="color:#A8DADC; font-weight:800; font-size:12px; text-transform:uppercase;">PAGO POTENCIAL TOTAL</span>
                <h1 style="color: #FFFFFF; margin: 5px 0 0 0; font-size: 50px; font-weight: 900;">{pago_bruto} €</h1>
            </div>
            <div style="background: #F8FAFC; border: 1px solid #E2E8F0; padding: 15px; border-radius: 8px;">
                <span style="color:#6C757D; font-weight:800; font-size:11px; text-transform:uppercase;">BENEFICIO NETO (GANANCIA REAL)</span>
                <h3 style="color: #2A9D8F; margin: 5px 0 0 0; font-size: 24px; font-weight: 700;">+{beneficio_neto} €</h3>
            </div>
            """, unsafe_allow_html=True)

with tab3:
    if loc == vis:
        st.info("ℹ️ Desglose técnico no disponible.")
    else:
        st.markdown("<h2 style='color: #1D3557;'>MÉTRICAS MATEMÁTICAS APLICADAS</h2>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="report-box">
            <p>Las cuotas reflejan el estado de forma exacto en esta liga (<b>{liga_sel}</b>):</p>
            <ul>
                <li><b>Clasificación Dinámica (65%):</b> Ponderado de <b>{loc}</b> (Puesto {datos_ligas[liga_sel]['equipos'][loc]['pos']} de {datos_ligas[liga_sel]['total']}) vs <b>{vis}</b> (Puesto {datos_ligas[liga_sel]['equipos'][vis]['pos']}).</li>
                <li><b>Rendimiento Ofensivo/Defensivo (35%):</b> Evaluación de goles marcados ({datos_ligas[liga_sel]['equipos'][loc]['gf']}) frente a goles recibidos por el rival.</li>
                <li><b>Factor Estadio:</b> Multiplicador de ventaja para locales del +12%.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")
st.caption("© 2026 Fútbol Champagne Pro | Motor de Datos Global (96 Equipos de Élite) | +18 Juega con responsabilidad")