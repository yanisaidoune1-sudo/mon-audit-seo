import streamlit as st
import random

# Configuration de la page
st.set_page_config(page_title="Sitra | Digital Intelligence", layout="wide")

# Fonction pour le boost dynamique
def get_dynamic_boost():
    return round(random.uniform(4.2, 24.8), 1)

# Style de fond gris clair
st.markdown("<style>.main { background-color: #f5f7f9; }</style>", unsafe_allow_html=True)

# Barre latérale (Sidebar)
st.sidebar.title("Sitra Dash")
st.sidebar.write("Projet : **Audit SEO Bookzone**")
st.sidebar.info("Statut : Analyse de performance terminée.")

# Création des onglets
tabs = st.tabs(["📊 Prévisions", "🏆 Concurrence", "🎨 Design XL/M", "⚡ Mode Challenge"])

with tabs[0]:
    st.header("Prévisions de résultats")
    boost = get_dynamic_boost()
    st.info(f"Analyse Sitra : L'optimisation mobile pourrait booster vos clics de {boost}%.")
    col_a, col_b = st.columns(2)
    col_a.metric("Temps de réponse", "0.78s", "-0.12s")
    col_b.metric("Sécurité SSL", "Certifié", "100%")

with tabs[1]:
    st.header("Analyse de la concurrence")
    st.warning("Mode Premium requis pour voir les détails des concurrents.")
    if st.button("Demander l'activation Premium"):
        st.success("Requête envoyée à l'équipe Sitra.")

with tabs[2]:
    st.header("Design et Confort Visuel")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Couleurs")
        st.color_picker("Couleur d'action", "#2997FF", key="p_final_test")
        st.write("Nom : **Bleu Électrique**")
    with col2:
        st.subheader("Tailles de texte")
        st.write("* **Taille XL** : 48px (Titres)")
        st.write("* **Taille M** : 16px (Corps)")

with tabs[3]:
    st.header("Mode Challenge")
    st.write("Votre score de performance actuel :")
    st.progress(87)
    st.write("**87/100**")
    st.checkbox("Appliquer les correctifs XL", value=True)
    st.button("Relancer l'audit complet")
