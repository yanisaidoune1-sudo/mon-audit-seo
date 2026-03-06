import streamlit as st
import random

# CONFIGURATION DE L'INTERFACE
st.set_page_config(page_title="Sitra | Digital Intelligence", layout="wide")

# SIMULATION DES DONNEES DYNAMIQUES
def get_dynamic_boost():
    return round(random.uniform(4.2, 24.8), 1)

# STYLE CORRIGE (Plus simple pour eviter les erreurs)
st.markdown("<style>.main { background-color: #f5f7f9; }</style>", unsafe_allow_html=True)

# BARRE DE NAVIGATION
tabs = st.tabs(["Previsions de resultats", "Analyse de la concurrence", "Design et Confort", "Mode Challenge"])

# 1. PREVISIONS DE RESULTATS
with tabs[0]:
    st.header("Previsions de resultats")
    boost = get_dynamic_boost()
    st.info(f"Analyse Sitra : Une modification de la hierarchie visuelle pourrait booster vos clics de {boost}% sur mobile.")
    
    st.subheader("Indicateurs de performance actuelle")
    col_a, col_b = st.columns(2)
    col_a.metric("Temps de reponse", "0.78s")
    col_b.metric("Securite SSL", "Valide")

# 2. ANALYSE DE LA CONCURRENCE (VERSION PREMIUM)
with tabs[1]:
    st.header("Analyse de la concurrence")
    st.warning("Fonctionnalite Premium : Le mode comparatif detaille est verrouille.")
    st.write("Le mode Premium vous permet de surveiller les prix et le design de vos concurrents en temps reel.")
    if st.button("Activer le mode Premium"):
        st.info("Lien de paiement en cours de preparation...")

# 3. DESIGN ET CONFORT
with tabs[2]:
    st.header("Design et Confort d'utilisation")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Couleurs recommandees")
        st.color_picker("Couleur d'action", "#2997FF", key="color")
        st.write("Nom : Bleu Electrique")
    with col2:
        st.subheader("Tailles de texte")
        st.write("* Taille XL (Titres) : 48px")
        st.write("* Taille M (Lecture) : 16px")

# 4. MODE CHALLENGE
with tabs[3]:
    st.header("Mode Challenge")
    progres = 87
    st.progress(progres / 100)
    st.write(f"Score actuel : {progres}/100")
    st.checkbox("Ajuster la taille du menu tactile")
    st.checkbox("Barre de navigation transparente", value=True)
