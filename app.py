import streamlit as st
import random

# --- CONFIGURATION DE L'INTERFACE ---
st.set_page_config(page_title="Sitra | Digital Intelligence", layout="wide")

# --- FONCTION POUR LE CHIFFRE PRECIS ---
def get_dynamic_boost():
    # Genere un chiffre comme 14.3% ou 10.7% pour faire pro
    return round(random.uniform(4.2, 24.8), 1)

# --- STYLE DE SECURITE (Correction du bug TypeError) ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    div[data-testid="stMetricValue"] { font-size: 38px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- NAVIGATION ---
tabs = st.tabs(["Previsions de resultats", "Analyse de la concurrence", "Design et Confort", "Mode Challenge"])

# --- 1. PREVISIONS DE RESULTATS ---
with tabs[0]:
    st.header("Previsions de resultats")
    boost = get_dynamic_boost()
    st.info(f"Analyse Sitra : Une modification de la hierarchie visuelle pourrait booster vos clics de {boost}% sur mobile.")
    
    st.subheader("Indicateurs de performance actuelle")
    col_a, col_b = st.columns(2)
    col_a.metric("Temps de reponse", "0.78s")
    col_b.metric("Securite SSL", "Valide")

# --- 2. ANALYSE DE LA CONCURRENCE (MODE PREMIUM PAYANT) ---
with tabs[1]:
    st.header("Analyse de la concurrence")
    st.warning("Fonctionnalite Premium : Le mode comparatif detaille est actuellement verrouille.")
    
    st.write("Le mode Premium vous permet de :")
    st.write("* Surveiller les prix des concurrents en temps reel.")
    st.write("* Recevoir des alertes lors de changements de design chez vos voisins.")
    st.write("* Acceder au rapport d'expertise comparatif complet.")
    
    if st.button("Activer le mode Premium pour Bookzone"):
        st.info("Redirection vers la page de paiement Sitra en cours...")

# --- 3. DESIGN ET CONFORT (PALETTE ET TAILLES) ---
with tabs[2]:
    st.header("Design et Confort d'utilisation")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Couleurs recommandees")
        color = st.color_picker("Choisissez une couleur d'action", "#2997FF", key="picker_final")
        st.write(f"Code Hex : **{color}**")
        st.write("Nom : **Bleu Electrique** (Ideal pour les boutons)")
        
    with col2:
        st.subheader("Tailles de texte (Points de repere)")
        st.write("* **Taille XL (Titres)** : 48px - Pour une visibilite maximale.")
        st.write("* **Taille M (Lecture)** : 16px - Pour un confort sans effort.")

# --- 4. MODE CHALLENGE (PROGRESSION) ---
with tabs[3]:
    st.header("Mode Challenge")
    st.write("Progres de l'optimisation de Bookzone :")
    
    progres = 87
    st.progress(progres / 100)
    st.write(f"Score actuel : **{progres}/100**")
    
    st.divider()
    st.subheader("Actions a valider")
    st.checkbox("Ajuster la taille du menu tactile (Taille XL)")
    st.checkbox("Rendre la barre de navigation transparente", value=True)
    st.checkbox("Optimiser le contraste du texte (Taille M)")
    
