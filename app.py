import streamlit as st
import random

# CONFIGURATION DE L'INTERFACE
st.set_page_config(page_title="Sitra | Digital Intelligence", layout="wide")

# SIMULATION DES DONNEES DYNAMIQUES
def get_dynamic_boost():
    # Genere un chiffre precis pour la credibilite (ex: 14.3%)
    return round(random.uniform(4.2, 24.8), 1)

# STYLE PERSONNALISE (Couleur bleue et fond gris clair)
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stProgress > div > div > div > div { background-color: #2997FF; }
    </style>
    """, unsafe_content_set=True)

# BARRE DE NAVIGATION (Noms professionnels)
tabs = st.tabs(["Previsions de resultats", "Analyse de la concurrence", "Design et Confort", "Mode Challenge"])

# 1. PREVISIONS DE RESULTATS
with tabs[0]:
    st.header("Previsions de resultats")
    boost = get_dynamic_boost()
    st.info(f"Analyse Sitra : Une modification de la hierarchie visuelle pourrait booster vos clics de {boost}% sur mobile.")
    
    st.subheader("Indicateurs de performance actuelle")
    col_a, col_b = st.columns(2)
    col_a.metric("Temps de reponse", "0.78s", "Excellent")
    col_b.metric("Securite SSL", "Valide", "Protege")

# 2. ANALYSE DE LA CONCURRENCE (VERSION PREMIUM PAYANTE)
with tabs[1]:
    st.header("Analyse de la concurrence")
    
    st.warning("Fonctionnalite Premium : Le mode comparatif detaille est verrouille.")
    
    st.write("Le mode Premium vous permet de :")
    st.write("* Surveiller les prix des concurrents en temps reel.")
    st.write("* Recevoir des alertes lors de changements de design chez vos voisins.")
    st.write("* Acceder au rapport d'expertise comparatif complet.")
    
    if st.button("Activer le mode Premium pour Bookzone"):
        st.info("Redirection vers la page de paiement en cours...")

# 3. DESIGN ET CONFORT
with tabs[2]:
    st.header("Design et Confort d'utilisation")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Couleurs recommandees")
        # Palette visuelle avec nom de couleur
        st.color_picker("Choisissez une couleur d'action", "#2997FF", key="color")
        st.write("Nom : Bleu Electrique (Ideal pour les boutons d'appel a l'action)")
        
    with col2:
        st.subheader("Tailles de texte (Points de repere)")
        st.write("* Taille XL (Titres principaux) : 48px - Pour une visibilite maximale sur ordinateur.")
        st.write("* Taille M (Corps de texte) : 16px - Pour un confort de lecture optimal.")

# 4. MODE CHALLENGE
with tabs[3]:
    st.header("Mode Challenge")
    st.write("Progres de l'optimisation de Bookzone :")
    
    # Barre de progression visuelle pour le score de 87/100
    progres = 87
    st.progress(progres / 100)
    st.write(f"Score actuel : {progres}/100")
    
    st.divider()
    st.subheader("Actions a realiser")
    st.checkbox("Ajuster la taille du menu tactile pour les mobiles")
    st.checkbox("Rendre la barre de navigation transparente", value=True)
    st.checkbox("Optimiser le contraste des boutons secondaires")
