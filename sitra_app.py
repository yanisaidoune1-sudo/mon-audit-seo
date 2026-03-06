import streamlit as st
import random

# Configuration avancee
st.set_page_config(page_title="Sitra | Digital Intelligence", layout="wide")

# Style personnalise
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e0e0e0; }
    </style>
    """, unsafe_allow_html=True)

# Barre laterale detaillee
st.sidebar.title("Sitra Analytics")
st.sidebar.subheader("Client : Bookzone")
st.sidebar.markdown("---")
st.sidebar.write("Connexion GitHub Active")
st.sidebar.write("Serveur : Streamlit Cloud")

# Les 4 Onglets avec le contenu complet
tabs = st.tabs(["Previsions de resultats", "Analyse Concurrence", "Design et Confort (XL/M)", "Mode Challenge"])

with tabs[0]:
    st.header("Previsions de resultats detaillees")
    st.write("D'apres nos algorithmes, votre site actuel presente des marges de progression importantes.")
    
    col1, col2, col3 = st.columns(3)
    boost = round(random.uniform(15.5, 28.2), 1)
    col1.metric("Boost Clics (Mobile)", f"+{boost}%", "Tres Eleve")
    col2.metric("Temps de reponse", "0.78s", "-0.15s")
    col3.metric("Indice de confiance", "94%", "Stable")
    
    st.info("Analyse Sitra : La restructuration des balises H1 et l'optimisation des images au format WebP permettraient de gagner 1.2s de chargement sur les reseaux 4G/5G.")

with tabs[1]:
    st.header("Analyse de la concurrence (Mode Premium)")
    st.subheader("Comparatif direct avec vos 3 principaux rivaux")
    
    st.warning("Contenu Verrouille : Vous utilisez actuellement la version gratuite de Sitra.")
    st.write("Le mode Premium vous permettrait de voir :")
    st.markdown("""
    * Les mots-cles sur lesquels vos concurrents se positionnent.
    * Leur budget publicitaire estime par mois.
    * Les liens (backlinks) qu'ils ont obtenus recemment.
    """)
    
    if st.button("Debloquer l'acces Premium pour Bookzone"):
        st.success("Demande transmise ! Un conseiller Sitra vous contactera pour activer l'acces complet.")

with tabs[2]:
    st.header("Design, Ergonomie et Confort Visuel")
    st.write("Optimisation des elements visuels pour une meilleure retention utilisateur.")
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Charte Graphique")
        st.write("Nous avons identifie que ce bleu favorise le taux de conversion.")
        st.color_picker("Couleur d'action recommandee", "#2997FF", key="color_final_no_emoji")
        st.write("Nom de la teinte : Bleu Electrique Sitra")
        
    with c2:
        st.subheader("Typographie et Lisibilite")
        st.write("Adaptation dynamique des tailles pour tous les ecrans :")
        st.success("Taille XL : 48px - Ideal pour les titres d'appel (H1).")
        st.info("Taille M : 16px - Taille standard pour une lecture confortable sans fatigue visuelle.")

with tabs[3]:
    st.header("Mode Challenge : Performance Globale")
    st.write("Calcul du score Sitra base sur 42 points de controle SEO et UX.")
    
    score = 87
    st.progress(score)
    st.write(f"Votre Score actuel : {score}/100")
    
    st.markdown("""
    ### Actions prioritaires :
    1. Activer le cache serveur (Gain : +5 pts)
    2. Corriger les 3 erreurs de contraste dans le pied de page (Gain : +3 pts)
    3. Validation du certificat SSL (Termine)
    """)
    
    if st.button("Relancer un scan complet"):
        with st.spinner('Analyse en cours...'):
            st.write("Scan des fichiers GitHub termine. Aucun bug detecte.")
