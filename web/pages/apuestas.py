import streamlit as st

st.set_page_config(page_title="Control de Apuestas", layout="wide")

st.title("Seguimiento de Jornada y Cuotas")
st.write("---")

st.subheader("Plataformas Recomendadas")
col_1, col_2, col_3 = st.columns(3)

with col_1:
    st.info("**bet365**\n\nbono 200 euros bienvenida")
with col_2:
    st.success("**bwin**\n\nhasta 200 euros de bono")
with col_3:
    st.warning("**Gran Madrid**\n\n50 euros casino online")

st.write("---")

datos_ligas = {
    "LaLiga": {
        "cuotas": {"FC Barcelona": 1.30, "Real Madrid CF": 5.20, "At. Madrid": 16.00, "Otros": 500.0},
        "evento_dia": "Real Madrid vs Barcelona",
        "pista": "Ambos marcan y mas de 2.5 goles",
        "nivel_riesgo": "Medio"
    },
    "Premier League": {
        "cuotas": {"Man. City": 1.65, "Arsenal": 4.20, "Liverpool": 5.50, "Otros": 150.0},
        "evento_dia": "Liverpool vs Man. City",
        "pista": "Victoria local Liverpool",
        "nivel_riesgo": "Alto"
    },
    "Serie A": {
        "cuotas": {"Inter": 1.40, "Juventus": 4.80, "AC Milan": 9.00, "Otros": 250.0},
        "evento_dia": "Inter vs Juventus",
        "pista": "Menos de 2.5 goles totales",
        "nivel_riesgo": "Bajo"
    },
    "Bundesliga": {
        "cuotas": {"Bayern": 1.20, "Leverkusen": 3.80, "Dortmund": 15.0, "Otros": 300.0},
        "evento_dia": "Bayern vs Leverkusen",
        "pista": "Doble oportunidad Leverkusen",
        "nivel_riesgo": "Medio"
    },
    "Ligue 1": {
        "cuotas": {"PSG": 1.15, "Monaco": 8.00, "Marseille": 12.0, "Otros": 450.0},
        "evento_dia": "PSG vs Marseille",
        "pista": "Handicap PSG -1",
        "nivel_riesgo": "Bajo"
    }
}

liga_activa = st.selectbox("Seleccionar competicion:", list(datos_ligas.keys()))

st.write(f"Analisis de jornada: {liga_activa}")

with st.expander("Ver detalle del partido destacado", expanded=True):
    col_a, col_b = st.columns(2)
    with col_a:
        st.write("**Evento principal:**")
        st.code(datos_ligas[liga_activa]['evento_dia'])
    with col_b:
        st.write("**Sugerencia de apuesta:**")
        st.error(datos_ligas[liga_activa]['pista'])

st.write("---")

col_1, col_2 = st.columns(2)

with col_1:
    st.write("Ajustes de apuesta")
    opciones = datos_ligas[liga_activa]["cuotas"]
    seleccion = st.selectbox("Equipo:", list(opciones.keys()))
    importe = st.number_input("Euros:", min_value=5.0, value=10.0, step=5.0)

with col_2:
    st.write("Prevision de cobro")
    valor_cuota = opciones[seleccion]
    total_bruto = importe * valor_cuota
    neto = total_bruto - importe
    
    st.metric(label="Cobro total", value=f"{total_bruto:.2f} €")
    st.write(f"Ganancia neta estimada: {neto:.2f} €")
    
    st.write("Listado de cuotas:")
    st.dataframe(opciones, use_container_width=True) #asi evitamos que no se vean los espacios y se ocupe todo el ancho de la tabla.