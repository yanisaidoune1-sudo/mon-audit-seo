import streamlit as st
import time
import random
import pandas as pd

st.set_page_config(page_title="Sitra | Digital Intelligence", layout="wide")

st.markdown("""
<style>

h2, h3, h4, h5, h6, .internal-title {
    text-decoration: underline;
}

[data-testid="stSidebar"] {
    background-color: #000000;
    color: #ffffff;
}

[data-testid="stSidebar"] label {
    color: #ffffff !important;
}

[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    text-decoration: none;
}

input[type="text"] {
    border: 2px solid #ccc;
    border-radius: 5px;
    padding: 6px;
}

input[type="text"]:focus {
    border: 2px solid #28a745;
    outline: none;
}

.main .block-container {
    background-color: #f7f7f7;
    padding: 20px;
    border-radius: 10px;
}

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

st.title("Sitra")
st.caption("Système Expert d'Analyse Prédictive et de Diagnostic Digital")
st.divider()

with st.sidebar:

    st.header("Centre de contrôle")

    st.subheader("Options Premium")

    mode_comparaison = st.checkbox("🔓 Activer le mode comparatif", key="premium_check")

    if mode_comparaison:
        st.success("💳 Option Premium activée (Mode démo)")

    st.divider()

    st.write("Moteur d'analyse : Sitra Engine v2.6.0")


def analyser_couleurs_site(url):

    palettes = [
        {"nom": "Premium Dark","couleurs": ["#1D1D1F","#F5F5F7","#0071E3"],"noms": ["Noir Sidéral","Gris Argent","Bleu Royal"]},
        {"nom": "Innovation & Tech","couleurs": ["#000000","#8E8E93","#2997FF"],"noms": ["Noir","Gris Acier","Bleu Électrique"]},
        {"nom": "Énergie Créative","couleurs": ["#F4A261","#264653","#E76F51"],"noms": ["Sable","Bleu Pétrole","Terracotta"]},
        {"nom": "Corporate Trust","couleurs": ["#003566","#FFC300","#001D3D"],"noms": ["Bleu Marine","Or","Bleu Nuit"]}
    ]

    index = sum(ord(char) for char in url) % len(palettes) if url else 0
    return palettes[index]


def generer_mots_cles(url):

    base_keywords = [
        "innovation","digital","performance","solution",
        "expérience","technologie","marketing","web","design"
    ]

    random.shuffle(base_keywords)

    mots_cles = base_keywords[:5]

    usage = [
        "à mettre dans le titre H1 de la page d'accueil",
        "à inclure dans un titre H2",
        "à intégrer dans la meta description",
        "à répéter dans le contenu principal",
        "à utiliser dans les boutons ou appels à l'action"
    ]

    return [(mot, usage[i]) for i, mot in enumerate(mots_cles)]


def generer_defis(score_seo, score_design, score_ux):

    defis = []

    if score_seo < 60:
        defis += [
            "Ajouter des mots-clés dans les titres H1 et H2",
            "Optimiser les balises meta description",
            "Ajouter du contenu texte optimisé SEO"
        ]
    else:
        defis += [
            "Créer un article de blog optimisé SEO",
            "Améliorer le maillage interne",
            "Ajouter des liens internes entre les pages"
        ]

    if score_design < 60:
        defis += [
            "Améliorer les couleurs pour plus de lisibilité",
            "Uniformiser le style visuel du site",
            "Ajouter des images plus professionnelles"
        ]
    else:
        defis += [
            "Ajouter des micro-animations",
            "Optimiser les visuels pour un rendu moderne"
        ]

    if score_ux < 60:
        defis += [
            "Simplifier le menu de navigation",
            "Ajouter un bouton d'appel à l'action visible",
            "Améliorer le parcours utilisateur"
        ]
    else:
        defis += [
            "Ajouter une section témoignages clients",
            "Optimiser le tunnel de conversion"
        ]

    return random.sample(defis, min(5, len(defis)))


col_in1, col_in2 = st.columns(2)

with col_in1:

    url1 = st.text_input("Domaine cible :",placeholder="exemple URL ou .com")

    if mode_comparaison:
        st.info("💡 Ce mode permet d'analyser votre site et de voir comment l'améliorer pour dépasser un concurrent.")

with col_in2:

    url2 = ""

    if mode_comparaison:
        url2 = st.text_input("Domaine concurrent :",placeholder="exemple URL ou .com")


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
        score_seo = score - 3
        score_design = random.randint(60,90)
        score_ux = random.randint(60,90)

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

        with tabs[0]:

            st.markdown('<h3 class="internal-title">Prévisions de trafic :</h3>',unsafe_allow_html=True)

            st.info(f"Pour **{url}**, améliorer l'organisation visuelle pourrait augmenter les clics d'environ **{boost_reel}%**.")

            st.markdown('<h3 class="internal-title">Recommandation de couleurs :</h3>',unsafe_allow_html=True)

            st.write(f"• **Couleur principale :** {palette['noms'][0]}")
            st.write(f"• **Couleur secondaire :** {palette['noms'][1]}")
            st.write(f"• **Couleur d'action :** {palette['noms'][2]}")

        with tabs[1]:

            st.markdown('<h3 class="internal-title">Stratégie SEO :</h3>',unsafe_allow_html=True)

            st.write(f"Score d'optimisation : {score_seo}%")

            col_seo1,col_seo2 = st.columns(2)

            with col_seo1:

                st.markdown('<h4 class="internal-title">Mots-clés recommandés et leur usage :</h4>',unsafe_allow_html=True)

                mots_cles = generer_mots_cles(url)

                for mot, usage in mots_cles:
                    st.write(f"• **{mot}** → {usage}")

            with col_seo2:

                st.markdown('<h4 class="internal-title">Positionnement sur les moteurs :</h4>',unsafe_allow_html=True)

                densite = 0.82

                st.progress(densite)

                st.caption("💡 Indique la pertinence du site et comment il se positionne sur les moteurs de recherche")

        with tabs[2]:

            st.markdown('<h3 class="internal-title">Expérience Utilisateur :</h3>',unsafe_allow_html=True)

            st.write("• Certains boutons importants ne sont pas assez visibles.")
            st.write("• Les titres pourraient être plus grands pour améliorer la lecture.")
            st.write("• Le menu mobile pourrait être simplifié.")

            st.info(f"💡 Temps de chargement : {vitesse}s")

        with tabs[3]:

            st.markdown('<h3 class="internal-title">Design & Branding :</h3>',unsafe_allow_html=True)

            c_p1,c_p2,c_p3 = st.columns(3)

            positions = [
                "fond principal / sections",
                "sections secondaires / blocs",
                "boutons importants / CTA"
            ]

            for i,(nom,couleur) in enumerate(zip(palette['noms'],palette['couleurs'])):

                col = [c_p1,c_p2,c_p3][i]

                col.markdown(
                    f"<span class='color-label'>{nom}</span>"
                    f"<div class='color-block' style='background:{couleur}'></div>"
                    f" → {positions[i]}",
                    unsafe_allow_html=True
                )

        with tabs[5]:

            st.markdown('<h3 class="internal-title">Mode Challenge</h3>',unsafe_allow_html=True)

            defis = generer_defis(score_seo, score_design, score_ux)

            total = len(defis)
            score_challenge = 0

            for i, defi in enumerate(defis):

                if st.checkbox(defi, key=f"challenge_{idx}_{i}"):

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
