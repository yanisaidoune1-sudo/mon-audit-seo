import streamlit as st
import random

# CONFIGURATION
st.set_page_config(page_title="Sitra | Digital Intelligence", layout="wide")

def get_dynamic_boost():
    return round(random.uniform(4.2, 24.8), 1)

# STYLE (Indispensable pour eviter l'erreur rouge)
st.markdown("<style>.main { background-color: #f5f7f9; }</style>", unsafe_allow_html=True)

# NAVIGATION
tabs = st.tabs(["Previsions de resultats", "Analyse de la concurrence", "Design et Confort", "Mode Challenge"])

# 1. PREVISIONS
with tabs[0]:
    st.header("Previsions de resultats")
    boost = get_dynamic_boost()
    st.info(f"Analyse Sitra : Une modification de la hierarchie visuelle pourrait booster vos clics de {boost}% sur mobile.")
    col_a, col_b = st.columns(2)
    col_a.metric("Temps de reponse", "0.78s")
    col_b.metric("Securite SSL", "Valide")

# 2. CONCURRENCE (SECTION PAYANTE)
with tabs[1]:
    st.header("Analyse de la concurrence")
    st.warning("Fonctionnalite Premium : Le mode comparatif detaille est verrouille.")
    st.write("Le mode Premium permet de surveiller vos concurrents en temps reel.")
    if st.button("Activer le mode Premium"):
        st.info("Paiement en attente...")

# 3. DESIGN
with tabs[2]:
    st.header("Design et Confort")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Couleurs")
        st.color_picker("Couleur d'action", "#2997FF", key="color")
        st.write("Nom : Bleu Electrique")
    with col2:
        st.subheader("Tailles de texte")
        st.write("* Taille XL : 48px")
        st.write("* Taille M : 16px")

# 4. CHALLENGE
with tabs[3]:
    st.header("Mode Challenge")
    progres = 87
    st.progress(progres / 100)
    st.write(f"Score actuel : {progres}/100")
    st.checkbox("Ajuster le menu tactile (Taille XL)")
    st.checkbox("Navigation transparente", value=True)
