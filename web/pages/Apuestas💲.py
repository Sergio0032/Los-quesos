import streamlit as st

st.set_page_config(page_title="Control de Apuestas", page_icon="⚽", layout="wide")

st.title("⚽ Seguimiento de Jornada y Cuotas Dinámicas")
st.markdown("Calculadora inteligente y análisis de partidos en tiempo real.")
st.divider()

st.subheader("⭐ Plataformas Recomendadas")
col_1, col_2, col_3 = st.columns(3)

with col_1:
    st.info("**bet365** 🟢\n\nBono 200€ bienvenida")
with col_2:
    st.success("**bwin** 🟡\n\nHasta 200€ de bono")
with col_3:
    st.warning("**Gran Madrid** 🟣\n\n50€ casino online")

st.divider()

def calcular_cuota(posicion, gf, gc, total_equipos=20):
    gc_seguro = gc if gc > 0 else 1
    fuerza = (gf / gc_seguro) + ((total_equipos + 1 - posicion) / 2.0)
    factor_ajuste = 15.0 
    cuota = factor_ajuste / fuerza
    return max(1.05, round(cuota, 2))

def generar_sugerencia_dinamica(eq1, eq2, st1, st2, total_equipos):
    fuerza_eq1 = (st1["gf"] / max(1, st1["gc"])) + (total_equipos - st1["pos"])
    fuerza_eq2 = (st2["gf"] / max(1, st2["gc"])) + (total_equipos - st2["pos"])
    
    recomendaciones = []
    
    if fuerza_eq1 > (fuerza_eq2 * 1.2):
        recomendaciones.append(f"Victoria de {eq1}")
    elif fuerza_eq2 > (fuerza_eq1 * 1.2):
        recomendaciones.append(f"Victoria de {eq2}")
    else:
        recomendaciones.append("Doble Oportunidad (Partido muy reñido)")
        
    total_goles_favor = st1["gf"] + st2["gf"]
    total_goles_contra = st1["gc"] + st2["gc"]
    
    if total_goles_favor > 115:
        recomendaciones.append("Más de 2.5 goles")
    elif total_goles_contra < 55:
        recomendaciones.append("Menos de 2.5 goles")        

    if (st1["gf"] > 45 and st2["gf"] > 45) and (st1["gc"] > 25 and st2["gc"] > 25):
        recomendaciones.append("Ambos Marcan")

    return " + ".join(recomendaciones)

datos_ligas = {
    "LaLiga": {
        "equipos": {
            "FC Barcelona": {"pos": 1, "gf": 80, "gc": 29},
            "Real Madrid": {"pos": 2, "gf": 64, "gc": 28},
            "Villarreal": {"pos": 3, "gf": 54, "gc": 34},
            "At. Madrid": {"pos": 4, "gf": 50, "gc": 30}
        },
        "total_equipos": 20,
        "evento_dia": "Real Madrid vs FC Barcelona",
        "equipos_partido": ["Real Madrid", "FC Barcelona"], 
        "nivel_riesgo": "Medio"
    },
    "Premier League": {
        "equipos": {
            "Arsenal": {"pos": 1, "gf": 61, "gc": 22},
            "Manchester City": {"pos": 2, "gf": 60, "gc": 28},
            "Manchester United": {"pos": 3, "gf": 56, "gc": 43},
            "Aston Villa": {"pos": 4, "gf": 42, "gc": 37},
            "Liverpool": {"pos": 5, "gf": 53, "gc": 38}
        },
        "total_equipos": 20,
        "evento_dia": "Arsenal vs Manchester City",
        "equipos_partido": ["Arsenal", "Manchester City"],
        "nivel_riesgo": "Alto"
    },
    "Bundesliga": {
        "equipos": {
            "Bayern Múnich": {"pos": 1, "gf": 100, "gc": 27},
            "Borussia Dortmund": {"pos": 2, "gf": 60, "gc": 28},
            "RB Leipzig": {"pos": 3, "gf": 55, "gc": 36},
            "VfB Stuttgart": {"pos": 4, "gf": 56, "gc": 38}
        },
        "total_equipos": 18,
        "evento_dia": "Bayern Múnich vs Borussia Dortmund",
        "equipos_partido": ["Bayern Múnich", "Borussia Dortmund"],
        "nivel_riesgo": "Medio"
    },
    "Serie A": {
        "equipos": {
            "Inter": {"pos": 1, "gf": 71, "gc": 26},
            "Milan": {"pos": 2, "gf": 47, "gc": 26},
            "Napoli": {"pos": 3, "gf": 46, "gc": 30},
            "Como": {"pos": 4, "gf": 53, "gc": 22}
        },
        "total_equipos": 20,
        "evento_dia": "Inter vs Milan",
        "equipos_partido": ["Inter", "Milan"],
        "nivel_riesgo": "Bajo"
    },
    "Ligue 1": {
        "equipos": {
            "PSG": {"pos": 1, "gf": 61, "gc": 23},
            "Lens": {"pos": 2, "gf": 54, "gc": 27},
            "Lille": {"pos": 3, "gf": 45, "gc": 34},
            "Marseille": {"pos": 4, "gf": 55, "gc": 37}
        },
        "total_equipos": 18,
        "evento_dia": "PSG vs Marseille",
        "equipos_partido": ["PSG", "Marseille"],
        "nivel_riesgo": "Bajo"
    }
}

with st.sidebar:
    st.header("⚙️ Configuración")
    liga_activa = st.selectbox("🏆 Seleccionar competición:", list(datos_ligas.keys()))
    st.markdown("---")
    st.markdown("💡 *Las cuotas y predicciones se calculan mediante un algoritmo basado en los goles y la posición en la tabla.*")

st.markdown(f"### 🏟️ Análisis de jornada: **{liga_activa}**")

with st.expander("🔍 Ver detalle del partido destacado", expanded=True):
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**⚔️ Evento principal:**")
        st.info(f"**{datos_ligas[liga_activa]['evento_dia']}**")
    with col_b:
        st.markdown("**🎯 Sugerencia de apuesta algorítmica:**")
        
        eq_local, eq_visitante = datos_ligas[liga_activa]["equipos_partido"]
        stats_local = datos_ligas[liga_activa]["equipos"][eq_local]
        stats_visitante = datos_ligas[liga_activa]["equipos"][eq_visitante]
        total_eq = datos_ligas[liga_activa]["total_equipos"]
        
        apuesta_recomendada = generar_sugerencia_dinamica(eq_local, eq_visitante, stats_local, stats_visitante, total_eq)
        
        st.error(f"🔥 {apuesta_recomendada}")

st.divider()

col_1, col_2 = st.columns([1, 1.5]) 

equipos_stats = datos_ligas[liga_activa]["equipos"]
total_eq = datos_ligas[liga_activa]["total_equipos"]

cuotas_dinamicas = {}
for equipo, stats in equipos_stats.items():
    cuotas_dinamicas[equipo] = calcular_cuota(stats["pos"], stats["gf"], stats["gc"], total_eq)

with col_1:
    with st.container(border=True):
        st.markdown("#### 🎟️ Ajustes de apuesta")
        seleccion = st.selectbox("Elige tu equipo:", list(cuotas_dinamicas.keys()))
        
        valor_cuota = cuotas_dinamicas[seleccion]
        st.markdown(f"**Cuota actual:** `{valor_cuota}`")
        
        importe = st.number_input("Euros (€):", min_value=5.0, value=10.0, step=5.0)

with col_2:
    tab_calc, tab_tabla = st.tabs(["💰 Previsión de Cobro", "📊 Listado Completo de Cuotas"])
    
    with tab_calc:
        total_bruto = importe * valor_cuota
        neto = total_bruto - importe
        
        st.metric(
            label="Cobro total estimado", 
            value=f"{total_bruto:.2f} €", 
            delta=f"+ {neto:.2f} € de beneficio neto"
        )
        
        riesgo = datos_ligas[liga_activa]['nivel_riesgo']
        st.caption(f"Nivel de riesgo de la liga: **{riesgo}**")
        
    with tab_tabla:
        df_cuotas = [{"Equipo": k, "Cuota Calculada": v} for k, v in cuotas_dinamicas.items()]
        st.dataframe(df_cuotas, use_container_width=True, hide_index=True)