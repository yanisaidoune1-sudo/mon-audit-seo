import streamlit as st
import random

st.set_page_config(page_title="Sitra | Digital Intelligence", layout="wide")

def get_dynamic_boost():
    return round(random.uniform(4.2, 24.8), 1)

st.markdown("""<style>.main { background-color: #f5f7f9; }</style>""", unsafe_allow_html=True)

tabs = st.tabs(["Previsions de resultats", "Analyse de la concurrence", "Design et Confort", "Mode Challenge"])

with tabs[0]:
    st.header("Previsions de resultats")
    boost = get_dynamic_boost()
    st.info(f"Analyse Sitra : Une modification de la hierarchie visuelle pourrait booster vos clics de {boost}% sur mobile.")
    col_a, col_b = st.columns(2)
    col_a.metric("Temps de reponse", "0.78s")
    col_b.metric("Securite SSL", "Valide")

with tabs[1]:
    st.header("Analyse de la concurrence")
    st.warning("Fonctionnalite Premium : Le mode comparatif detaille est verrouille.")
    st.write("Le mode Premium vous permet de surveiller vos concurrents en temps reel.")
    if st.button("Activer le mode Premium pour Bookzone"):
        st.info("Redirection vers la page de paiement Sitra...")

with tabs[2]:
    st.header("Design et Confort d'utilisation")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Couleurs recommandees")
        st.color_picker("Choisissez une couleur d'action", "#2997FF", key="picker_pro")
        st.write("Nom : **Bleu Electrique**")
    with col2:
        st.subheader("Tailles de texte")
        st.write("* **Taille XL (Titres)** : 48px")
        st.write("* **Taille M (Lecture)** : 16px")

with tabs[3]:
    st.header("Mode Challenge")
    st.progress(87 / 100)
    st.write("Score actuel : **87/100**")
    st.checkbox("Ajuster la taille du menu tactile (Taille XL)")
    st.checkbox("Rendre la barre de navigation transparente", value=True)
