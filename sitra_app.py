import streamlit as st
import time

# --- CONFIGURATION ---
st.set_page_config(page_title="Sitra Pro", layout="wide")

# --- MEMOIRE (Session State) ---
# Empeche l'application de revenir au debut lors d'un clic
if 'analyse_active' not in st.session_state:
    st.session_state.analyse_active = False
if 'url_cible' not in st.session_state:
    st.session_state.url_cible = ""

# --- STYLE CSS ---
st.markdown("""
    <style>
    .titre-expert { font-size: 2.5rem; font-weight: bold; color: #1D1D1F; }
    .texte-expert { font-size: 1.1rem; color: #3A3A3C; }
    /* Supprime le texte technique a droite qui causait un bug */
    [data-testid="stSidebarNav"] + div { display: none; } 
    </style>
    """, unsafe_allow_html=True)

# --- BARRE LATERALE ---
with st.sidebar:
    st.title("Sitra")
    st.header("Reglages")
    # Cle unique pour eviter l'erreur DuplicateElementId
    premium_mode = st.checkbox("Activer le Comparatif Marche (Premium)", key="chk_p_no_emoji")
    st.divider()
    st.caption("Sitra Engine v2.6.0")

# --- INTERFACE PRINCIPALE ---
st.title("Systeme Expert Sitra")
url_input = st.text_input("Entrez l'adresse du site :", value=st.session_state.url_cible, placeholder="exemple.com")

if st.button("Lancer l'analyse technique") or st.session_state.analyse_active:
    if url_input:
        st.session_state.analyse_active = True
        st.session_state.url_cible = url_input
        
        st.header(f"Rapport d'expertise : {st.session_state.url_cible}")
        
        # Metriques
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Score Global", "82/100")
        m2.metric("Vitesse", "0.78s")
        m3.metric("Securite", "Valide")
        m4.metric("Mobile", "Optimise")

        # ONGLETS
        tabs = st.tabs(["SEO et Mots-cles", "Confort UX", "Design et Look", "Paiement"])

        # 1. SEO (Barre de couleur dynamique)
        with tabs[0]:
            st.subheader("Densite Semantique")
            score_seo = 82 #
            
            # Logique de couleur sans emojis
            if score_seo < 50:
                st.error(f"Niveau Critique : Votre contenu est tres pauvre ({score_seo}%).")
            elif score_seo < 90:
                st.warning(f"Niveau Moyen : Votre contenu couvre {score_seo}% du secteur.")
            else:
                st.success(f"Niveau Parfait : Votre contenu couvre {score_seo}% du secteur.")
            
            st.progress(score_seo / 100)
            
            st.markdown("### Coach SEO : Objectif 100%")
            st.write("Pour ameliorer votre score, ajoutez ces mots-cles manquants :")
            st.info("Innovation technologique, Service apres-vente, Garantie mondiale")

        # 2. UX (Analyse globale)
        with tabs[1]:
            st.subheader("Audit Ergonomique")
            st.write("Analyse detaillee de l'interface :")
            st.write("- Contrastes : Les couleurs respectent les normes d'accessibilite.")
            st.write("- Interactivite : Les boutons de navigation sont bien places.")
            
            st.info("Conseil Sitra : Ecartez davantage vos liens en bas de page pour faciliter le clic sur mobile.")

        # 3. DESIGN (Roles des couleurs)
        with tabs[2]:
            st.subheader("Identite Visuelle")
            st.write("Utilisation recommandee des couleurs :")
            
            d1, d2, d3 = st.columns(3)
            # Roles clairs et sans px
            d1.color_picker("Couleur de FOND", "#003566", disabled=True, key="c_no_1")
            d2.color_picker("Couleur des TITRES", "#FFC300", disabled=True, key="c_no_2")
            d3.color_picker("Couleur des BOUTONS", "#001D3D", key="c_no_3")
            
            st.divider()
            st.write("Apercu des tailles de texte :")
            st.markdown('<p class="titre-expert">Titre : Impact Maximum</p>', unsafe_allow_html=True)
            st.markdown('<p class="texte-expert">Corps de texte : Confort de lecture standard.</p>', unsafe_allow_html=True)

        # 4. PAIEMENT (Liste des modes de paiement)
        with tabs[3]:
            st.subheader("Finaliser votre acces Premium")
            st.write("Selectionnez votre mode de paiement securise :")
            
            pay_col1, pay_col2, pay_col3 = st.columns(3)
            if pay_col1.button("PayPal", use_container_width=True):
                st.success("Connexion a PayPal...")
            if pay_col2.button("Carte Bancaire", use_container_width=True):
                st.success("Ouverture du module Stripe...")
            if pay_col3.button("Apple / Google Pay", use_container_width=True):
                st.success("Verification de l'identite...")

        # EXPORT
        st.divider()
        st.download_button("Telecharger le rapport complet (TXT)", "Rapport Sitra", file_name="audit_sitra.txt", use_container_width=True)
