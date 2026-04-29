import streamlit as st

st.title("🚗 Eksportgodtgørelse Estimator")

nypris = st.number_input("Nypris (inkl. afgift)", value=300000)
alder = st.number_input("Alder (år)", value=8)
km = st.number_input("Kilometer", value=180000)

# Handelsværdi
if alder <= 3:
    faktor = 0.75
elif alder <= 6:
    faktor = 0.55
elif alder <= 10:
    faktor = 0.40
else:
    faktor = 0.20

if km > 200000:
    faktor -= 0.05

handelsvaerdi = nypris * faktor

# Afgiftsandel
afgift = handelsvaerdi * 0.65

# Eksportgodtgørelse
godtgoerelse = afgift * 0.85 - 2250

st.subheader("Resultat")
st.write(f"Handelsværdi DK: {handelsvaerdi:,.0f} kr.")
st.write(f"Afgiftsandel: {afgift:,.0f} kr.")
st.success(f"Forventet eksportgodtgørelse: {godtgoerelse:,.0f} kr.")
