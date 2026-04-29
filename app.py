import streamlit as st
from datetime import date

st.set_page_config(page_title="Eksportgodtgørelse Estimator", page_icon="🚗", layout="wide")

st.title("🚗 Eksportgodtgørelse Estimator")
st.write("Forhandler-model til at estimere eksportgodtgørelse ud fra handelspris, nypris, årgang, km, brændstof og stand.")

st.warning(
    "Dette er kun et estimat. Motorstyrelsen fastsætter den endelige handelsværdi og eksportgodtgørelse."
)

# 2026 satser personbil
TRIN1 = 76400
TRIN2 = 237400
SATS1 = 0.25
SATS2 = 0.85
SATS3 = 1.50
EKSPORT_FRADRAG_PROCENT = 0.15
MIN_FRADRAG_PERSONBIL = 8500
MOTORST_GEBYR = 2250


def registreringsafgift_personbil(afgiftsvaerdi):
    afgiftsvaerdi = max(0, afgiftsvaerdi)

    if afgiftsvaerdi <= TRIN1:
        return afgiftsvaerdi * SATS1
    elif afgiftsvaerdi <= TRIN2:
        return TRIN1 * SATS1 + (afgiftsvaerdi - TRIN1) * SATS2
    else:
        return (
            TRIN1 * SATS1
            + (TRIN2 - TRIN1) * SATS2
            + (afgiftsvaerdi - TRIN2) * SATS3
        )


def find_afgiftsvaerdi_fra_handelspris(handelspris):
    """
    Finder afgiftspligtig værdi ved at løse:
    afgiftsværdi + registreringsafgift = handelspris inkl. afgift
    """
    lav = 0
    hoej = handelspris

    for _ in range(120):
        midt = (lav + hoej) / 2
        samlet = midt + registreringsafgift_personbil(midt)

        if samlet < handelspris:
            lav = midt
        else:
            hoej = midt

    return (lav + hoej) / 2


def aldersfaktor(alder):
    if alder <= 1:
        return 0.82
    elif alder <= 2:
        return 0.72
    elif alder <= 3:
        return 0.64
    elif alder <= 4:
        return 0.56
    elif alder <= 5:
        return 0.49
    elif alder <= 6:
        return 0.43
    elif alder <= 8:
        return 0.34
    elif alder <= 10:
        return 0.27
    elif alder <= 12:
        return 0.21
    elif alder <= 15:
        return 0.15
    else:
        return 0.10


def km_justering(km, alder):
    normal_km = max(alder, 1) * 18000
    forskel = km - normal_km

    if forskel <= -50000:
        return 0.08
    elif forskel <= -25000:
        return 0.04
    elif forskel <= 25000:
        return 0.00
    elif forskel <= 50000:
        return -0.04
    elif forskel <= 100000:
        return -0.08
    else:
        return -0.13


def braendstof_justering(braendstof):
    if braendstof == "Diesel":
        return -0.05
    elif braendstof == "Benzin":
        return 0.00
    elif braendstof == "Hybrid":
        return 0.02
    elif braendstof == "El":
        return -0.08
    else:
        return 0.00


def stand_justering(stand):
    mapping = {
        "Meget flot": 0.06,
        "God": 0.02,
        "Normal": 0.00,
        "Slidt": -0.07,
        "Dårlig/skader": -0.15,
    }
    return mapping.get(stand, 0)


st.sidebar.header("Input")

bilnavn = st.sidebar.text_input("Bil", "VW Polo 1.4 TDI")
aar = st.sidebar.number_input("Årgang", min_value=1980, max_value=date.today().year, value=2016)
km = st.sidebar.number_input("Kilometer", min_value=0, value=180000, step=5000)
braendstof = st.sidebar.selectbox("Brændstof", ["Diesel", "Benzin", "Hybrid", "El"])
stand = st.sidebar.selectbox("Stand", ["Meget flot", "God", "Normal", "Slidt", "Dårlig/skader"])

st.sidebar.divider()

nypris = st.sidebar.number_input("Nypris inkl. afgift da bilen var ny", min_value=0, value=260000, step=5000)
handelspris = st.sidebar.number_input("Dansk handelspris inkl. afgift i dag", min_value=0, value=65000, step=1000)

st.sidebar.caption("Tip: Handelspris bør helst være baseret på 3-5 sammenlignelige biler i DK.")

alder = date.today().year - aar

# Model A: direkte ud fra handelspris
afgiftsvaerdi_direkte = find_afgiftsvaerdi_fra_handelspris(handelspris)
regafgift_direkte = registreringsafgift_personbil(afgiftsvaerdi_direkte)

# Model B: sanity check ud fra nypris, alder, km, brændstof og stand
basis_vaerdi_fra_nypris = nypris * aldersfaktor(alder)
samlet_justering = (
    km_justering(km, alder)
    + braendstof_justering(braendstof)
    + stand_justering(stand)
)

modelpris = basis_vaerdi_fra_nypris * (1 + samlet_justering)

# Kombineret handelsværdi
# Handelspris vægtes højest, fordi den er tættest på Motorstyrelsens metode.
vaegtet_handelspris = handelspris * 0.75 + modelpris * 0.25

afgiftsvaerdi_vaegtet = find_afgiftsvaerdi_fra_handelspris(vaegtet_handelspris)
regafgift_vaegtet = registreringsafgift_personbil(afgiftsvaerdi_vaegtet)

fradrag = max(regafgift_vaegtet * EKSPORT_FRADRAG_PROCENT, MIN_FRADRAG_PERSONBIL)
eksportgodtgoerelse = max(0, regafgift_vaegtet - fradrag)
netto_efter_gebyr = max(0, eksportgodtgoerelse - MOTORST_GEBYR)

lavt_skoen = max(0, eksportgodtgoerelse * 0.90)
hoejt_skoen = eksportgodtgoerelse * 1.10

st.header("Resultat")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Bil", bilnavn)
col2.metric("Alder", f"{alder} år")
col3.metric("Model-handelspris", f"{modelpris:,.0f} kr.")
col4.metric("Vægtet handelspris", f"{vaegtet_handelspris:,.0f} kr.")

st.divider()

c1, c2, c3 = st.columns(3)
c1.metric("Est. afgiftspligtig værdi", f"{afgiftsvaerdi_vaegtet:,.0f} kr.")
c2.metric("Est. registreringsafgift", f"{regafgift_vaegtet:,.0f} kr.")
c3.metric("Est. eksportgodtgørelse", f"{eksportgodtgoerelse:,.0f} kr.")

st.success(f"Netto efter Motorstyrelsens gebyr: {netto_efter_gebyr:,.0f} kr.")

st.info(
    f"Realistisk spænd: ca. {lavt_skoen:,.0f} kr. - {hoejt_skoen:,.0f} kr. "
    "Spændet tager højde for usikkerhed i Motorstyrelsens værdifastsættelse."
)

st.subheader("Kontrol af input")

forskel = handelspris - modelpris
forskel_pct = forskel / handelspris * 100 if handelspris else 0

if abs(forskel_pct) <= 10:
    st.success("✅ Handelsprisen virker realistisk ift. nypris, alder, km, brændstof og stand.")
elif forskel_pct > 10:
    st.warning("⚠️ Din handelspris ligger højere end modelprisen. Tjek om bilen har særligt udstyr eller lav km.")
else:
    st.warning("⚠️ Din handelspris ligger lavere end modelprisen. Tjek om bilen har høj km, skader eller svag efterspørgsel.")

st.write(f"""
### Beregningsgrundlag

**Bil:** {bilnavn}  
**Årgang:** {aar}  
**Km:** {km:,.0f} km  
**Brændstof:** {braendstof}  
**Stand:** {stand}  

**Nypris:** {nypris:,.0f} kr.  
**Indtastet handelspris:** {handelspris:,.0f} kr.  
**Modelberegnet handelspris:** {modelpris:,.0f} kr.  
**Vægtet handelspris:** {vaegtet_handelspris:,.0f} kr.  

**Estimeret registreringsafgift:** {regafgift_vaegtet:,.0f} kr.  
**Fradrag ved eksport:** {fradrag:,.0f} kr.  
**Estimeret eksportgodtgørelse:** {eksportgodtgoerelse:,.0f} kr.  
**Netto efter gebyr:** {netto_efter_gebyr:,.0f} kr.
""")

st.divider()

st.header("Eksportcase")

koebspris = st.number_input("Din købspris i DK", value=35000, step=1000)
salgspris_udland = st.number_input("Forventet salgspris i udlandet", value=18000, step=1000)
omkostninger = st.number_input("Transport, klargøring, annoncer mv.", value=5000, step=500)
buffer = st.number_input("Sikkerhedsbuffer", value=3000, step=500)

samlede_indtaegter = salgspris_udland + eksportgodtgoerelse
samlede_omkostninger = koebspris + omkostninger + buffer + MOTORST_GEBYR
profit = samlede_indtaegter - samlede_omkostninger

p1, p2, p3 = st.columns(3)
p1.metric("Samlede indtægter", f"{samlede_indtaegter:,.0f} kr.")
p2.metric("Samlede omkostninger", f"{samlede_omkostninger:,.0f} kr.")
p3.metric("Forventet profit", f"{profit:,.0f} kr.")

if profit >= 15000:
    st.success("✅ STÆRK EKSPORTCASE")
elif profit >= 7000:
    st.success("✅ GOD CASE")
elif profit >= 2500:
    st.warning("⚠️ GRÅZONE")
else:
    st.error("❌ DROP")
