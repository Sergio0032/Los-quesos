import streamlit as st
import pandas as pd                                                
import os
import plotly.graph_objects as go
import numpy as np
import base64

st.set_page_config(
    page_title="Apuestas",
    layout="wide"
)
st.title("Apuestas")
st.divider()

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;600;900&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
        /* Hemos quitado el color blanco forzado para que Streamlit mande */
    }

    .sidebar-label {
        font-size: 15px;
        font-weight: 800;
        color: var(--text-color); /* Se adapta al modo oscuro */
        text-transform: uppercase;
        margin-top: 15px;
        margin-bottom: 5px;
    }

    .stTabs [data-baseweb="tab-list"] { gap: 30px; }
    .stTabs [data-baseweb="tab"] {
        font-size: 17px;
        font-weight: 700;
        color: gray !important;
        text-transform: uppercase;
    }
    .stTabs [aria-selected="true"] {
        color: #E63946 !important;
        border-bottom: 4px solid #E63946 !important;
    }

    .odds-card {
        background: var(--secondary-background-color); /* Gris en claro, gris oscuro en oscuro */
        border: 1px solid var(--secondary-background-color);
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
        background-color: var(--secondary-background-color);
        border-left: 6px solid #E63946; /* Cambiado a rojo para que destaque en ambos modos */
        padding: 25px;
        border-radius: 4px;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def descargar_datos_en_vivo():
    dict_final = {}
    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    ruta_csv = os.path.abspath(os.path.join(directorio_actual, "..", "..", "data_clasificaciones", "clasificacion_2025.csv"))    
    try:
        df = pd.read_csv(ruta_csv)
        for liga in df['Liga'].unique():
            df_liga = df[df['Liga'] == liga]
            total_equipos = len(df_liga)
            equipos_dict = {}
            
            for _, fila in df_liga.iterrows():
                nombre_equipo = str(fila['Equipo']).strip()
                equipos_dict[nombre_equipo] = {
                    "pos": int(fila['Posicion']),
                    "gf": int(fila['Goles_a_favor']),
                    "gc": int(fila['Goles_en_contra'])
                }
                
            dict_final[liga] = {
                "total": total_equipos,
                "equipos": equipos_dict
            }
            
    except FileNotFoundError:
        pass
        
    return dict_final

datos_ligas = descargar_datos_en_vivo()

#COMPROBACIÓN DE SEGURIDAD
if not datos_ligas:
    st.error("⚠️ No se ha encontrado el archivo 'clasificacion_2025.csv' o está vacío. Revisa la carpeta 'data_clasificaciones'.")
else:
    # Cálculo cuotas
    def calcular_cuotas_Champagne(sl, sv, n):
        p_pos_l = (n - sl["pos"] + 1) / n
        p_pos_v = (n - sv["pos"] + 1) / n
        eff_l = sl["gf"] / max(1, sl["gc"])
        eff_v = sv["gf"] / max(1, sv["gc"])
        
        p_pos_l_norm = p_pos_l / (p_pos_l + p_pos_v)
        p_pos_v_norm = p_pos_v / (p_pos_l + p_pos_v)
        
        eff_l_norm = eff_l / (eff_l + eff_v)
        eff_v_norm = eff_v / (eff_l + eff_v)
        
        f_l = (p_pos_l_norm * 0.65 + eff_l_norm * 0.35) * 1.12 
        f_v = (p_pos_v_norm * 0.65 + eff_v_norm * 0.35)
        
        total = f_l + f_v
        prob_l_base = f_l / total
        prob_v_base = f_v / total
        
        dif = abs(prob_l_base - prob_v_base)
        prob_e = 0.28 - (dif * 0.10)
        
        p_l = prob_l_base * (1.0 - prob_e)
        p_v = prob_v_base * (1.0 - prob_e)
        
        return round(1/p_l, 2), round(1/prob_e, 2), round(1/p_v, 2)

    with st.sidebar:
        st.markdown('<p class="sidebar-label">PANEL DE CONTROL</p>', unsafe_allow_html=True)
        
        index_liga_fav = 0
        if "equipo" in st.session_state and st.session_state.equipo:
            for i, (liga, info) in enumerate(datos_ligas.items()):
                if st.session_state.equipo in info["equipos"]:
                    index_liga_fav = i
                    break

        liga_sel = st.selectbox("LIGA", list(datos_ligas.keys()), index=index_liga_fav)
        equipos = sorted(list(datos_ligas[liga_sel]["equipos"].keys()))
        
        index_equipo_fav = 0
        if "equipo" in st.session_state and st.session_state.equipo in equipos:
            index_equipo_fav = equipos.index(st.session_state.equipo)

        loc = st.selectbox("LOCAL", equipos, index=index_equipo_fav)
        vis = st.selectbox("VISITANTE", equipos, index=min(1, len(equipos)-1))
        st.markdown("---")

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
            st.warning("Seleccione equipos diferentes en la barra de control lateral.")
        else:
            st.markdown(f"<h3 style='color: var(--text-color);'>JORNADA ANALIZADA: {loc.upper()} VS {vis.upper()}</h3>", unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            c1.markdown(f'<div class="odds-card"><div style="color:gray; font-weight:800; font-size:13px; margin-bottom:15px; text-transform:uppercase;">GANA {loc.upper()}</div><div class="odds-value">{cl}</div></div>', unsafe_allow_html=True)
            c2.markdown(f'<div class="odds-card"><div style="color:gray; font-weight:800; font-size:13px; margin-bottom:15px; text-transform:uppercase;">EMPATE</div><div class="odds-value">{ce}</div></div>', unsafe_allow_html=True)
            c3.markdown(f'<div class="odds-card"><div style="color:gray; font-weight:800; font-size:13px; margin-bottom:15px; text-transform:uppercase;">GANA {vis.upper()}</div><div class="odds-value">{cv}</div></div>', unsafe_allow_html=True)

    with tab2:
        if loc == vis:
            st.info("Modifique las selecciones para desbloquear la pestaña financiera.")
        else:
            st.markdown(f"<h3 style='color: var(--text-color);'>SIMULADOR DE CUPÓN DE APUESTAS</h3>", unsafe_allow_html=True)
            
            col_slip, col_payout = st.columns(2)
            
            with col_slip:
                opciones_pronostico = [
                    f"Gana {loc} (Cuota: {cl})", 
                    f"Empate (Cuota: {ce})", 
                    f"Gana {vis} (Cuota: {cv})"
                ]
                seleccion = st.radio("SELECCIONA TU MERCADO", opciones_pronostico)
                
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
                <div style="background: var(--secondary-background-color); border: 1px solid var(--secondary-background-color); padding: 20px; border-radius: 8px; margin-bottom: 15px;">
                    <span style="color:gray; font-weight:800; font-size:12px; text-transform:uppercase;">PRONÓSTICO TICKET</span>
                    <h4 style="color: var(--text-color); margin: 5px 0; font-weight: 700;">{texto_ticket.upper()}</h4>
                </div>
                <div style="background: #1D3557; border: 1px solid #1D3557; padding: 22px; border-radius: 8px; margin-bottom: 15px; color: white;">
                    <span style="color:#A8DADC; font-weight:800; font-size:12px; text-transform:uppercase;">PAGO POTENCIAL TOTAL</span>
                    <h1 style="color: #FFFFFF; margin: 5px 0 0 0; font-size: 50px; font-weight: 900;">{pago_bruto} €</h1>
                </div>
                <div style="background: var(--secondary-background-color); border: 1px solid var(--secondary-background-color); padding: 15px; border-radius: 8px;">
                    <span style="color:gray; font-weight:800; font-size:11px; text-transform:uppercase;">BENEFICIO NETO (GANANCIA REAL)</span>
                    <h3 style="color: #2A9D8F; margin: 5px 0 0 0; font-size: 24px; font-weight: 700;">+{beneficio_neto} €</h3>
                </div>
                """, unsafe_allow_html=True)

    with tab3:
        if loc == vis:
            st.info("Desglose técnico no disponible.")
        else:
            st.markdown("<h2 style='color: var(--text-color);'>MÉTRICAS MATEMÁTICAS APLICADAS</h2>", unsafe_allow_html=True)
            st.markdown(f"""
            <div class="report-box">
                <p>Las cuotas reflejan el estado de forma exacto en esta liga (<b>{liga_sel}</b>) mediante un modelo de <b>fuerza normalizada</b>:</p>
                <ul>
                    <li><b>Normalización Relativa:</b> Los datos de ambos equipos se miden estrictamente frente a frente (escala 0 a 1) para garantizar que los porcentajes de peso matemático sean 100% precisos y justos.</li>
                    <li><b>Clasificación Dinámica (65%):</b> Peso principal basado en la posición actual de <b>{loc}</b> (Puesto {datos_ligas[liga_sel]['equipos'][loc]['pos']} de {datos_ligas[liga_sel]['total']}) frente a <b>{vis}</b> (Puesto {datos_ligas[liga_sel]['equipos'][vis]['pos']}).</li>
                    <li><b>Eficacia Goleadora (35%):</b> Ratio de rendimiento puro (Goles a Favor / Goles en Contra) equilibrado contra la eficacia exacta del rival.</li>
                    <li><b>Factor Estadio:</b> Multiplicador de ventaja del +12% aplicado a la cuota base del equipo local.</li>
                    <li><b>Varianza de Empate (Algoritmo No Lineal):</b> Parte de una probabilidad base del 28%, la cual se reduce automáticamente a medida que aumenta la diferencia de nivel (desigualdad) entre ambos clubes.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

st.markdown("---")
st.caption(" +18 Juega con responsabilidad")