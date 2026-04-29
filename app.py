import streamlit as st

st.set_page_config(page_title="Eksportgodtgørelse Beregner", layout="wide")

st.title("🚗 Eksportgodtgørelse Beregner")
st.write("Beregner om en bil er en god eksportcase for bilforhandler.")

st.warning(
    "Bemærk: Appen er kun en intern beregner. Den faktiske eksportgodtgørelse afhænger af "
    "Motorstyrelsens værdifastsættelse. Gebyret for anmodning om eksportgodtgørelse er 2.250 kr."
)

tab1, tab2 = st.tabs(["Hurtig beregner", "Avanceret beregner"])

with tab1:
    st.header("Hurtig eksportberegner")

    koebspris = st.number_input("Købspris i Danmark", value=30000, step=1000)
    forventet_salg_udland = st.number_input("Forventet salgspris i udlandet", value=15000, step=1000)
    eksportgodtgoerelse = st.number_input("Forventet eksportgodtgørelse", value=40000, step=1000)
    gebyr = st.number_input("Motorstyrelsens gebyr", value=2250, step=100)
    ekstra_omkostninger = st.number_input("Transport / klargøring / diverse", value=3000, step=500)

    samlet_indtaegt = forventet_salg_udland + eksportgodtgoerelse
    samlet_omkostning = koebspris + gebyr + ekstra_omkostninger
    profit = samlet_indtaegt - samlet_omkostning

    st.subheader("Resultat")
    col1, col2, col3 = st.columns(3)

    col1.metric("Samlet indtægt", f"{samlet_indtaegt:,.0f} kr.")
    col2.metric("Samlet omkostning", f"{samlet_omkostning:,.0f} kr.")
    col3.metric("Forventet profit", f"{profit:,.0f} kr.")

    if profit >= 10000:
        st.success("✅ KØB — stærk eksportcase")
    elif profit >= 3000:
        st.warning("⚠️ UNDERSØG MERE — der er profit, men lav sikkerhedsmargin")
    else:
        st.error("❌ DROP — for lav eller negativ profit")

with tab2:
    st.header("Avanceret eksportberegner")

    st.subheader("Biloplysninger")
    bilnavn = st.text_input("Bil", "VW Polo 1.4 TDI")
    aar = st.number_input("Årgang", value=2016)
    km = st.number_input("Kilometerstand", value=180000, step=5000)

    st.subheader("Køb og omkostninger")
    koebspris_adv = st.number_input("Købspris", value=30000, step=1000, key="k1")
    reparation = st.number_input("Reparation / klargøring", value=3000, step=500)
    transport = st.number_input("Transport", value=2000, step=500)
    annonce = st.number_input("Annonce / salgsomkostninger", value=500, step=100)
    gebyr_adv = st.number_input("Motorstyrelsens gebyr", value=2250, step=100, key="g1")
    sikkerhedsmargin = st.number_input("Sikkerhedsmargin / buffer", value=3000, step=500)

    st.subheader("Indtægter")
    salg_udland = st.number_input("Forventet salgspris i udlandet", value=15000, step=1000, key="s1")
    forventet_godtgoerelse = st.number_input("Forventet eksportgodtgørelse", value=40000, step=1000, key="e1")

    samlet_omk = koebspris_adv + reparation + transport + annonce + gebyr_adv + sikkerhedsmargin
    samlet_ind = salg_udland + forventet_godtgoerelse
    profit_adv = samlet_ind - samlet_omk
    profit_uden_buffer = samlet_ind - (samlet_omk - sikkerhedsmargin)

    st.subheader("Eksportanalyse")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Samlede indtægter", f"{samlet_ind:,.0f} kr.")
    col2.metric("Samlede omkostninger", f"{samlet_omk:,.0f} kr.")
    col3.metric("Profit efter buffer", f"{profit_adv:,.0f} kr.")
    col4.metric("Profit før buffer", f"{profit_uden_buffer:,.0f} kr.")

    st.subheader("Vurdering")

    if profit_adv >= 15000:
        st.success("✅ MEGET STÆRK CASE — høj forventet avance")
    elif profit_adv >= 8000:
        st.success("✅ GOD CASE — realistisk eksportmulighed")
    elif profit_adv >= 3000:
        st.warning("⚠️ GRÅZONE — kræver bedre salgspris eller højere godtgørelse")
    else:
        st.error("❌ DÅRLIG CASE — risikoen er for høj")

    st.subheader("Kort rapport")
    st.write(f"""
    **Bil:** {bilnavn}  
    **Årgang:** {aar}  
    **Km:** {km:,.0f} km  

    Den forventede eksportgodtgørelse er **{forventet_godtgoerelse:,.0f} kr.**  
    Den forventede salgspris i udlandet er **{salg_udland:,.0f} kr.**  
    Samlede omkostninger inkl. buffer er **{samlet_omk:,.0f} kr.**  

    **Forventet avance efter sikkerhedsmargin: {profit_adv:,.0f} kr.**
    """)

st.divider()
st.caption("Udviklet som intern beregner til vurdering af eksportbiler.")
