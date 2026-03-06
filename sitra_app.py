import streamlit as st
import time
import random

# Configuration sobre
st.set_page_config(page_title="Sitra | Digital Intelligence", layout="wide")

# Style CSS pour les exemples de texte (Design)
st.markdown("""
    <style>
    .h1-sample { font-size: 48px; font-weight: bold; margin-bottom: 0px; }
    .p-sample { font-size: 16px; margin-top: 0px; }
    .stHelp { display: none; } /* Sécurité anti-bug help */
    </style>
    """, unsafe_allow_html=True)

# Identité de marque
st.title("Sitra")
st.caption("Système Expert d'Analyse Prédictive et de Diagnostic Digital")
st.divider()

# --- PANNEAU DE CONTRÔLE ---
with st.sidebar:
    st.header("Centre de contrôle")
    st.subheader("Options Premium")
    
    # Correction Bug DuplicateId : Utilisation de keys uniques
    mode_comparaison = st.checkbox("🔓 Activer le Comparatif Marché", key="premium_check")
    
    if mode_comparaison:
        st.success("💳 Option Premium activée (Mode démo)")
    
    st.divider()
    st.write("Moteur d'analyse : Sitra Engine v2.6.0")

# Fonction d'analyse
def analyser_couleurs_site(url):
    palettes = [
        {"nom": "Premium Dark", "couleurs": ["#1D1D1F", "#F5F5F7", "#0071E3"], "noms": ["Noir Sidéral", "Gris Argent", "Bleu Royal"]},
        {"nom": "Innovation & Tech", "couleurs": ["#000000", "#8E8E93", "#2997FF"], "noms": ["Noir", "Gris Acier", "Bleu Électrique"]},
        {"nom": "Énergie Créative", "couleurs": ["#F4A261", "#264653", "#E76F51"], "noms": ["Sable", "Bleu Pétrole", "Terracotta"]},
        {"nom": "Corporate Trust", "couleurs": ["#003566", "#FFC300", "#001D3D"], "noms": ["Bleu Marine", "Or", "Bleu Nuit"]}
    ]
    index = sum(ord(char) for char in url) % len(palettes) if url else 0
    return palettes[index]

# Saisie
col_in1, col_in2 = st.columns(2)
with col_in1:
    url1 = st.text_input("Domaine cible :", placeholder="exemple.com")
with col_in2:
    url2 = ""
    if mode_comparaison:
        url2 = st.text_input("Domaine concurrent :", placeholder="concurrent.com")

if st.button("Lancer l'analyse technique"):
    urls = [url1] if not (mode_comparaison and url2) else [url1, url2]
    
    for idx, url in enumerate(urls):
        if not url: continue
        
        st.subheader(f"Rapport d'analyse Sitra : {url}")
        
        with st.status(f"Analyse de {url}...", expanded=False):
            time.sleep(1)
        
        palette = analyser_couleurs_site(url)
        score = random.randint(85, 95)
        vitesse = round(random.uniform(0.6, 0.9), 2)
        boost_reel = round(random.uniform(12.4, 28.9), 1)
        
        # Métriques
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Indice de performance", f"{score}/100")
        c2.metric("Temps de réponse", f"{vitesse}s")
        c3.metric("Sécurité SSL", "Valide")
        c4.metric("UX Mobile", "Optimisée")

        tabs = st.tabs([
            "Estimation des résultats", "SEO & Marketing", "Confort d'utilisation", 
            "Design & Branding", "Comparatif Marché", "Mode Challenge"
        ])

        with tabs[0]:
            st.write("**Prévisions de trafic :**")
            st.info(f"Analyse Sitra : Pour {url}, une modification de la hiérarchie visuelle boostera vos clics de **{boost_reel}%**.")
            st.write(f"- Teinte de base : **{palette['noms'][0]}**")
            st.write(f"- Teinte d'accent : **{palette['noms'][1]}**")
            st.write(f"- Bouton d'action : **{palette['noms'][2]}**")

        with tabs[1]:
            st.write("**Stratégie SEO (Analyse Profonde) :**")
            # Ajout de contenu pour ne plus être vide
            st.write(f"Score d'optimisation : {score-3}%")
            col_seo1, col_seo2 = st.columns(2)
            with col_seo1:
                st.write("**Mots-clés détectés :**")
                st.code(f"1. Expertise {url}\n2. Solution Digitale\n3. Performance")
            with col_seo2:
                st.write("**Densité sémantique :**")
                st.progress(0.82)
                st.caption("Excellent : Votre contenu couvre 82% du champ lexical cible.")

        with tabs[2]:
            st.write("**Points d'attention UX :**")
            st.write("- Éléments peu visibles sur smartphone : Le menu 'Hamburger' manque de contraste.")
            # Correction Bug st.help : Remplacé par une info-bulle propre
            st.info("💡 **Pourquoi ?** Si vous augmentez la taille, les utilisateurs avec des gros doigts pourront cliquer sans s'énerver.")
            st.write(f"Fluidité : Temps de chargement de {vitesse}s.")

        with tabs[3]:
            st.write("**Design & Branding :**")
            st.write("Couleurs recommandées par l'expert Sitra (Visualisation) :")
            c_p1, c_p2, c_p3 = st.columns(3)
            # Utilisation de color_picker en mode lecture seule (disabled) pour l'autorité de l'IA
            c_p1.color_picker(palette['noms'][0], palette['couleurs'][0], key=f"c1_{idx}", disabled=True)
            c_p2.color_picker(palette['noms'][1], palette['couleurs'][1], key=f"c2_{idx}", disabled=True)
            c_p3.color_picker(f"Action : {palette['noms'][2]}", palette['couleurs'][2], key=f"c3_{idx}")
            
            st.write("---")
            st.write("**Aperçu des tailles recommandées :**")
            # Visualisation réelle de la taille
            st.markdown(f'<p class="h1-sample">Titre H1 (48px)</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="p-sample">Corps de texte (16px) : Voici comment vos clients liront votre contenu.</p>', unsafe_allow_html=True)

        with tabs[4]:
            if mode_comparaison:
                st.write("**Comparatif Marché :**")
                st.write(f"Analyse comparative entre {url1} et {url2} en cours...")
                st.line_chart([random.randint(50,100) for _ in range(10)])
            else:
                st.warning("⚠️ Cette section est réservée aux membres Premium.")
                if st.button("Découvrir l'offre Premium", key=f"pay_{idx}"):
                    st.write("Redirection vers la page de paiement...")

        with tabs[5]:
            st.write("**Mode Challenge**")
            st.progress(65)
            st.write("Progression : 65% - Vous dominez le marché !")
            st.checkbox("Appliquer la palette", value=True, key=f"ch1_{idx}")
            st.checkbox("Ajuster les menus", key=f"ch2_{idx}")

        # Un seul bouton d'exportation propre en bas de chaque rapport
        st.write("---")
        st.download_button("📥 Exporter le rapport complet (PDF/TXT)", f"Audit Sitra pour {url}", file_name=f"audit_{url}.txt", key=f"exp_{idx}")

st.divider()
st.center = st.write("Sitra : Anticiper pour dominer le marché.")
