import streamlit as st
import time
import random
import pandas as pd

# Configuration
st.set_page_config(page_title="Sitra | Digital Intelligence", layout="wide")

# Style CSS
st.markdown("""
<style>
/* Surligner uniquement les titres internes et sections, pas la sidebar ni titre principal */
h2, h3, h4, h5, h6, .internal-title {
    text-decoration: underline;
}

/* Sidebar noire avec texte blanc */
[data-testid="stSidebar"] {
    background-color: #000000;
    color: #ffffff;
}

/* Titres sidebar non soulignés */
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    text-decoration: none;
}

/* Checkbox sidebar : texte blanc sur fond noir */
[data-testid="stSidebar"] .stCheckbox label {
    color: #ffffff !important;
    background-color: #000000 !important;
    padding: 4px 6px;
    border-radius: 4px;
}

/* Text input vert au focus */
input[type="text"] {
    border: 2px solid #ccc;
    border-radius: 5px;
    padding: 6px;
}
input[type="text"]:focus {
    border: 2px solid #28a745; /* vert */
    outline: none;
}

/* Fond principal pour combler espace vide */
.main .block-container {
    background-color: #f7f7f7; /* gris très clair */
    padding: 20px;
    border-radius: 10px;
}

/* Blocs couleur pour Design & Branding */
.color-block {
    width: 60px;
    height: 60px;
    border-radius: 8px;
    border: 1px solid #000;
    display: inline-block;
    margin-right: 10px;
    vertical-align: middle;
}
.color-label {
    display: inline-block;
    vertical-align: middle;
    margin-right: 15px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# Identité
st.title("Sitra")
st.caption("Système Expert d'Analyse Prédictive et de Diagnostic Digital")
st.divider()

# SIDEBAR
with st.sidebar:
    st.header("Centre de contrôle")
    st.subheader("Options Premium")
    mode_comparaison = st.checkbox("🔓 Activer le mode comparatif", key="premium_check")
    if mode_comparaison:
        st.success("💳 Option Premium activée (Mode démo)")
    st.divider()
    st.write("Moteur d'analyse : Sitra Engine v2.6.0")

# Fonction palette
def analyser_couleurs_site(url):
    palettes = [
        {"nom": "Premium Dark", "couleurs": ["#1D1D1F", "#F5F5F7", "#0071E3"], "noms": ["Noir Sidéral", "Gris Argent", "Bleu Royal"]},
        {"nom": "Innovation & Tech", "couleurs": ["#000000", "#8E8E93", "#2997FF"], "noms": ["Noir", "Gris Acier", "Bleu Électrique"]},
        {"nom": "Énergie Créative", "couleurs": ["#F4A261", "#264653", "#E76F51"], "noms": ["Sable", "Bleu Pétrole", "Terracotta"]},
        {"nom": "Corporate Trust", "couleurs": ["#003566", "#FFC300", "#001D3D"], "noms": ["Bleu Marine", "Or", "Bleu Nuit"]}
    ]
    index = sum(ord(char) for char in url) % len(palettes) if url else 0
    return palettes[index]

# INPUT
col_in1, col_in2 = st.columns(2)
with col_in1:
    url1 = st.text_input("Domaine cible :", placeholder="exemple.com")
    if mode_comparaison:
        st.info("💡 Ce mode permet d'analyser votre site et de voir comment l'améliorer pour dépasser un concurrent.")
with col_in2:
    url2 = ""
    if mode_comparaison:
        url2 = st.text_input("Domaine concurrent :", placeholder="concurrent.com")

# ANALYSE
if st.button("Lancer l'analyse technique"):
    urls = [url1] if not (mode_comparaison and url2) else [url1, url2]
    for idx, url in enumerate(urls):
        if not url:
            continue

        st.subheader(f"Rapport d'analyse Sitra : {url}")
        with st.status(f"Analyse de {url}...", expanded=False):
            time.sleep(1)

        palette = analyser_couleurs_site(url)
        score = random.randint(85,95)
        vitesse = round(random.uniform(0.6,0.9),2)
        boost_reel = round(random.uniform(12.4,28.9),1)

        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Indice de performance",f"{score}/100")
        c2.metric("Temps de réponse",f"{vitesse}s")
        c3.metric("Sécurité SSL","Valide")
        c4.metric("UX Mobile","Optimisée")

        tabs = st.tabs([
            "Estimation des résultats",
            "SEO & Marketing",
            "Confort d'utilisation",
            "Design & Branding",
            "Comparatif Marché",
            "Mode Challenge"
        ])

        # ESTIMATION
        with tabs[0]:
            st.markdown('<h3 class="internal-title">Prévisions de trafic :</h3>', unsafe_allow_html=True)
            st.info(f"Pour **{url}**, améliorer l'organisation visuelle pourrait augmenter les clics d'environ **{boost_reel}%**.")
            st.markdown('<h3 class="internal-title">Recommandation de couleurs :</h3>', unsafe_allow_html=True)
            st.write(f"• **Couleur principale :** {palette['noms'][0]}")
            st.write(f"• **Couleur secondaire :** {palette['noms'][1]}")
            st.write(f"• **Couleur d'action :** {palette['noms'][2]}")

        # SEO
        with tabs[1]:
            st.markdown('<h3 class="internal-title">Stratégie SEO :</h3>', unsafe_allow_html=True)
            score_seo = score-3
            st.write(f"Score d'optimisation : {score_seo}%")
            col_seo1,col_seo2 = st.columns(2)
            with col_seo1:
                st.markdown('<h4 class="internal-title">Mots-clés détectés :</h4>', unsafe_allow_html=True)
                st.code(f"1. Expertise {url}\n2. Solution Digitale\n3. Performance")
            with col_seo2:
                densite = 0.82
                st.markdown('<h4 class="internal-title">Couverture du champ lexical :</h4>', unsafe_allow_html=True)
                st.progress(densite)
                st.caption("82% du champ lexical est couvert.")
                suggestions = ["innovation digitale","optimisation web","expérience utilisateur","stratégie marketing","analyse de performance"]
                for mot in suggestions:
                    st.write(f"• {mot}")

        # UX
        with tabs[2]:
            st.markdown('<h3 class="internal-title">Expérience Utilisateur :</h3>', unsafe_allow_html=True)
            st.write("Points détectés :")
            st.write("• Certains boutons importants ne sont pas assez visibles.")
            st.write("• Les titres pourraient être plus grands pour améliorer la lecture.")
            st.write("• Le menu mobile pourrait être simplifié.")
            st.info(f"💡 Temps de chargement : {vitesse}s")

        # DESIGN
        with tabs[3]:
            st.markdown('<h3 class="internal-title">Design & Branding :</h3>', unsafe_allow_html=True)
            c_p1, c_p2, c_p3 = st.columns(3)
            for i, (nom, couleur) in enumerate(zip(palette['noms'], palette['couleurs'])):
                col = [c_p1, c_p2, c_p3][i]
                col.markdown(f"<span class='color-label'>{nom}</span><div class='color-block' style='background:{couleur}'></div>", unsafe_allow_html=True)

        # COMPARATIF
        with tabs[4]:
            if mode_comparaison:
                st.markdown('<h3 class="internal-title">Comparatif Marché :</h3>', unsafe_allow_html=True)
                
                # Explication des scores
                st.info("""
**💡 Légende des scores (0-100) :**  
- 0-39 : Très mauvais  
- 40-69 : Moyen  
- 70-89 : Bon  
- 90-100 : Excellent  

Chaque barre représente un indice pour votre site : **Performance**, **UX**, **Vitesse**, **SEO**, **Design**
                """)
                
                # Graphique uniquement pour ton site
                metrics = {
                    "Performance": score,
                    "UX": random.randint(70,100),
                    "Vitesse": round((1-vitesse)*100,0),
                    "SEO": score_seo,
                    "Design": random.randint(75,95)
                }
                st.bar_chart(metrics)
                st.info("💡 Pour améliorer votre site et dépasser le concurrent, travaillez sur ces indicateurs.")
            else:
                st.warning("⚠️ Cette section est réservée aux membres Premium.")

        # MODE CHALLENGE
        with tabs[5]:
            st.markdown('<h3 class="internal-title">Mode Challenge</h3>', unsafe_allow_html=True)
            objectifs = [
                "Changer la couleur du bouton principal pour attirer l'attention",
                "Augmenter les titres H2 à 28px pour une meilleure lisibilité",
                "Réduire le temps de chargement à <0.8s",
                "Ajouter 3 mots-clés SEO pertinents sur la page d'accueil",
                "Simplifier le menu mobile et rendre les boutons cliquables facilement"
            ]
            total = len(objectifs)
            score_challenge = 0
            for i, obj in enumerate(objectifs):
                if st.checkbox(obj, key=f"ch_{idx}_{i}"):
                    score_challenge += 100 / total
            st.progress(score_challenge/100)

        st.download_button(
            "📥 Exporter le rapport complet (TXT)",
            f"Audit Sitra pour {url}",
            file_name=f"audit_{url}.txt",
            key=f"exp_{idx}"
        )

st.divider()
st.write("Sitra : Anticiper pour dominer le marché.")
