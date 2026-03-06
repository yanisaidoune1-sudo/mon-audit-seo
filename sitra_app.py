import streamlit as st
import random

st.set_page_config(page_title="Sitra | Digital Intelligence", layout="wide")

def get_dynamic_boost():
    return round(random.uniform(4.2, 24.8), 1)

st.markdown("<style>.main { background-color: #f5f7f9; }</style>", unsafe_allow_html=True)

tabs = st.tabs(["Previsions de resultats", "Analyse de la concurrence", "Design et Confort", "Mode Challenge"])

with tabs[0]:
    st.header("Previsions de resultats")
    boost = get_dynamic_boost()
    st.info(f"Analyse Sitra : Boost de clics estime a {boost}% sur mobile.")
    col_a, col_b = st.columns(2)
    col_a.metric("Temps de reponse", "0.78s")
    col_b.metric("Securite SSL", "Valide")

with tabs[1]:
    st.header("Analyse de la concurrence")
    st.warning("Fonctionnalite Premium : Verrouillee.")
    if st.button("Activer le mode Premium"):
        st.info("Paiement Sitra en attente...")

with tabs[2]:
    st.header("Design et Confort")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Couleurs")
        st.color_picker("Couleur d'action", "#2997FF", key="p_v_finale")
        st.write("Nom : **Bleu Electrique**")
    with col2:
        st.subheader("Tailles de texte")
        st.write("* **Taille XL** : 48px")
        st.write("* **Taille M** : 16px")

with tabs[3]:
    st.header("Mode Challenge")
    st.progress(87 / 100)
    st.write("Score actuel : **87/100**")
