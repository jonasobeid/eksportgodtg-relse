import streamlit as st

st.set_page_config(page_title="Eksportgodtgørelse Estimator", page_icon="🚗", layout="wide")

st.title("🚗 Eksportgodtgørelse Estimator")
st.write("Estimerer eksportgodtgørelse ud fra dansk handelsværdi og 2026-afgiftssatser.")

st.warning(
    "Dette er et estimat. Motorstyrelsens faktiske værdifastsættelse er afgørende. "
    "Brug altid sammenlignelige biler fra markedet som grundlag."
)

# 2026 satser for personbiler
TRIN_1 = 76400
TRIN_2 = 237400
SATS_1 = 0.25
SATS_2 = 0.85
SATS_3 = 1.50

MIN_FRADRAG_PERSONBIL = 8500
EKSPORT_FRADRAG_PROCENT = 0.15
GEBYR = 2250


def beregn_regafgift(afgiftspligtig_vaerdi):
    """Beregner estimeret registreringsafgift før eksportfradrag."""
    v = max(0, afgiftspligtig_vaerdi)

    if v <= TRIN_1:
        afgift = v * SATS_1
    elif v <= TRIN_2:
        afgift = TRIN_1 * SATS_1 + (v - TRIN_1) * SATS_2
    else:
        afgift = (
            TRIN_1 * SATS_1
            + (TRIN_2 - TRIN_1) * SATS_2
            + (v - TRIN_2) * SATS_3
        )

    return max(0, afgift)


def find_afgiftspligtig_vaerdi_fra_handelspris(handelspris):
    """
    Finder den afgiftspligtige værdi bag en dansk handelspris inkl. reg.afgift.
    Løser: afgiftspligtig værdi + registreringsafgift = handelspris.
    """
    lav = 0
    hoej = handelspris

    for _ in range(100):
        midt = (lav + hoej) / 2
        samlet = midt + beregn_regafgift(midt)

        if samlet < handelspris:
            lav = midt
        else:
            hoej = midt

    return (lav + hoej) / 2


tab1, tab2 = st.tabs(["🚀 Hurtig estimator", "📊 Eksportcase / profit"])

with tab1:
    st.header("Beregn estimeret eksportgodtgørelse")

    col1, col2 = st.columns(2)

    with col1:
        handelspris = st.number_input(
            "Dansk handelsværdi inkl. registreringsafgift",
            min_value=0,
            value=75000,
            step=1000,
            help="Brug realistisk markedsværdi i DK, fx fra Bilbasen eller tilsvarende biler."
        )

        markedsjustering = st.slider(
            "Markedsjustering",
            min_value=-20,
            max_value=20,
            value=0,
            step=1,
            help="Brug fx -10% hvis bilen har høj km, skader, dårlig stand eller svag efterspørgsel."
        )

    with col2:
        biltype = st.selectbox(
            "Køretøjstype",
            ["Personbil", "Varebil / MC"]
        )

        medregn_gebyr = st.checkbox("Træk Motorstyrelsens gebyr fra i nettoresultat", value=True)

    justeret_handelspris = handelspris * (1 + markedsjustering / 100)

    afgiftspligtig_vaerdi = find_afgiftspligtig_vaerdi_fra_handelspris(justeret_handelspris)
    beregnet_regafgift = beregn_regafgift(afgiftspligtig_vaerdi)

    if biltype == "Personbil":
        fradrag = max(beregnet_regafgift * EKSPORT_FRADRAG_PROCENT, 8500)
    else:
        fradrag = max(beregnet_regafgift * EKSPORT_FRADRAG_PROCENT, 4500)

    brutto_godtgoerelse = max(0, beregnet_regafgift - fradrag)
    netto_efter_gebyr = brutto_godtgoerelse - GEBYR if medregn_gebyr else brutto_godtgoerelse

    st.subheader("Resultat")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Justeret handelsværdi", f"{justeret_handelspris:,.0f} kr.")
    c2.metric("Est. afgiftspligtig værdi", f"{afgiftspligtig_vaerdi:,.0f} kr.")
    c3.metric("Est. reg.afgift", f"{beregnet_regafgift:,.0f} kr.")
    c4.metric("Est. eksportgodtgørelse", f"{brutto_godtgoerelse:,.0f} kr.")

    st.success(f"Netto efter gebyr: {netto_efter_gebyr:,.0f} kr.")

    st.info(
        "Jo mere præcis dansk handelsværdi du indtaster, jo bedre bliver estimatet. "
        "Brug 3-5 sammenlignelige biler og vælg en realistisk gennemsnitspris."
    )

with tab2:
    st.header("Eksportcase og forventet profit")

    col1, col2 = st.columns(2)

    with col1:
        koebspris = st.number_input("Købspris i DK", value=35000, step=1000)
        salgspris_udland = st.number_input("Forventet salgspris i udlandet", value=18000, step=1000)
        transport = st.number_input("Transport", value=2000, step=500)
        klargoering = st.number_input("Klargøring / reparation", value=3000, step=500)

    with col2:
        andre_omk = st.number_input("Andre omkostninger", value=1000, step=500)
        buffer = st.number_input("Sikkerhedsbuffer", value=3000, step=500)
        brug_estimat = st.checkbox("Brug beregnet eksportgodtgørelse fra fanen ovenfor", value=True)

        manuel_godtgoerelse = st.number_input(
            "Manuel eksportgodtgørelse",
            value=int(brutto_godtgoerelse),
            step=1000,
            disabled=brug_estimat
        )

    anvendt_godtgoerelse = brutto_godtgoerelse if brug_estimat else manuel_godtgoerelse

    samlede_indtaegter = salgspris_udland + anvendt_godtgoerelse
    samlede_omkostninger = koebspris + transport + klargoering + andre_omk + buffer + GEBYR
    profit = samlede_indtaegter - samlede_omkostninger

    st.subheader("Eksportanalyse")

    c1, c2, c3 = st.columns(3)
    c1.metric("Samlede indtægter", f"{samlede_indtaegter:,.0f} kr.")
    c2.metric("Samlede omkostninger", f"{samlede_omkostninger:,.0f} kr.")
    c3.metric("Forventet profit", f"{profit:,.0f} kr.")

    if profit >= 15000:
        st.success("✅ STÆRK EKSPORTCASE")
    elif profit >= 7000:
        st.success("✅ GOD CASE, men tjek markedsværdi grundigt")
    elif profit >= 2500:
        st.warning("⚠️ GRÅZONE — kræver bedre købspris eller mere sikker godtgørelse")
    else:
        st.error("❌ DROP — for lav margin eller for høj risiko")

    st.divider()

    st.write("### Rapport")
    st.write(f"""
    **Estimeret eksportgodtgørelse:** {anvendt_godtgoerelse:,.0f} kr.  
    **Forventet salgspris i udlandet:** {salgspris_udland:,.0f} kr.  
    **Købspris:** {koebspris:,.0f} kr.  
    **Samlede omkostninger inkl. buffer og gebyr:** {samlede_omkostninger:,.0f} kr.  

    **Forventet profit:** {profit:,.0f} kr.
    """)

st.caption("Bygget til intern vurdering af eksportbiler. Ikke en officiel Motorstyrelsen-beregner.")
