import streamlit as st
import time
import random

# Configuration
st.set_page_config(page_title="Sitra | Digital Intelligence", layout="wide")

# CSS
st.markdown("""
<style>
/* Surligner uniquement les titres internes et sections */
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

/* Checkbox sidebar : texte blanc et alignée */
[data-testid="stSidebar"] .stCheckbox label {
    color: #ffffff !important;  /* texte blanc */
    font-weight: bold;
    background-color: #000000 !important;
    padding: 4px 6px;
    border-radius: 4px;
    vertical-align: middle;
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
    background-color: #f7f7f7;
    padding: 20px;
    border-radius: 10px;
}

/* Blocs couleur */
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
    margin-right: 10px;
    font-weight: bold;
}
.color-usage {
    display: inline-block;
    vertical-align: middle;
    font-style: italic;
    color: #555;
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

# INPUT
col_in1, col_in2 = st.columns(2)
with col_in1:
    url1 = st.text_input("Domaine cible :", placeholder="exemple URL ou .com")
    if mode_comparaison:
        st.info("💡 Ce mode permet d'analyser votre site et de voir comment l'améliorer pour dépasser un concurrent.")
with col_in2:
    url2 = ""
    if mode_comparaison:
        url2 = st.text_input("Domaine concurrent :", placeholder="exemple URL ou .com")

# ANALYSE
if st.button("Lancer l'analyse technique") and url1:
    urls = [url1] if not (mode_comparaison and url2) else [url1, url2]
    for idx, url in enumerate(urls):
        if not url:
            continue
        st.subheader(f"Rapport d'analyse Sitra : {url}")
        with st.status(f"Analyse de {url}...", expanded=False):
            time.sleep(1)

        # Simulations
        score = random.randint(85,95)
        vitesse = round(random.uniform(0.6,0.9),2)
        boost_reel = round(random.uniform(12.4,28.9),1)

        # Metrics
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

        # Estimation
        with tabs[0]:
            st.markdown('<h3 class="internal-title">Prévisions de trafic :</h3>', unsafe_allow_html=True)
            st.info(f"Pour **{url}**, améliorer l'organisation visuelle pourrait augmenter les clics d\'environ **{boost_reel}%**.")

        # SEO
        with tabs[1]:
            st.markdown('<h3 class="internal-title">Stratégie SEO :</h3>', unsafe_allow_html=True)
            mots = ["innovation", "performance", "UX", "marketing", "digital"]
            st.markdown('<h4 class="internal-title">Mots-clés détectés :</h4>', unsafe_allow_html=True)
            for m in mots:
                st.write(f"• {m}")

        # Confort d'utilisation
        with tabs[2]:
            st.markdown('<h3 class="internal-title">Expérience Utilisateur :</h3>', unsafe_allow_html=True)
            st.write("Points détectés :")
            st.write("• Boutons importants à rendre plus visibles")
            st.write("• Titres à augmenter pour lisibilité")
            st.write(f"• Temps de chargement : {vitesse}s")

        # Design & Branding
        with tabs[3]:
            st.markdown('<h3 class="internal-title">Design & Branding :</h3>', unsafe_allow_html=True)
            palette = ["#0071E3","#F5F5F7","#1D1D1F"]
            usages = ["Fond principal / sections","Sections secondaires","Boutons / Actions"]
            c_p1, c_p2, c_p3 = st.columns(3)
            for col, couleur, usage in zip([c_p1,c_p2,c_p3], palette, usages):
                col.markdown(f"<div class='color-block' style='background:{couleur}'></div><span class='color-usage'>→ {usage}</span>", unsafe_allow_html=True)

        # Comparatif Marché
        with tabs[4]:
            if mode_comparaison and url2:
                st.markdown('<h3 class="internal-title">Comparatif Marché :</h3>', unsafe_allow_html=True)
                metrics = {
                    "Performance": score,
                    "UX": random.randint(70,100),
                    "Vitesse": round((1-vitesse)*100,0),
                    "SEO": score-3,
                    "Design": random.randint(75,95)
                }
                st.bar_chart(metrics)
                st.info("💡 Légende des scores : 0-39 Très mauvais, 40-69 Moyen, 70-89 Bon, 90-100 Excellent")
                st.info("💡 Pour améliorer votre site et dépasser le concurrent, travaillez sur ces indicateurs.")
            else:
                st.warning("⚠️ Cette section est réservée aux membres Premium.")

        # Mode Challenge
        with tabs[5]:
            st.markdown('<h3 class="internal-title">Mode Challenge</h3>', unsafe_allow_html=True)
            objectifs = [
                "Changer couleur du bouton principal",
                "Augmenter H2 à 28px",
                "Réduire temps de chargement <0.8s",
                "Ajouter 3 mots-clés SEO pertinents",
                "Simplifier menu mobile"
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
