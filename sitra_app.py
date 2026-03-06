import streamlit as st
import time
import random

# Configuration
st.set_page_config(page_title="Sitra | Digital Intelligence", layout="wide")

# Style CSS
st.markdown("""
<style>
/* Titre et texte */
.h1-sample { font-size: 48px; font-weight: bold; margin-bottom: 0px; text-decoration: underline; }
.p-sample { font-size: 16px; margin-top: 0px; }

/* Sidebar noire */
[data-testid="stSidebar"] {
    background-color: #000000;
    color: #ffffff;
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
    background-color: #f7f7f7; /* un gris très clair */
    padding: 20px;
    border-radius: 10px;
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

    mode_comparaison = st.checkbox("🔓 Activer le Comparatif Marché", key="premium_check")

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

            st.write("**Prévisions de trafic :**")

            st.info(f"Analyse Sitra : Pour **{url}**, améliorer l'organisation visuelle pourrait augmenter les clics d'environ **{boost_reel}%**.")

            st.write("**Recommandation de couleurs :**")

            st.write(f"• **Couleur principale du site :** {palette['noms'][0]}")
            st.write("→ Utiliser pour le fond ou les sections principales.")

            st.write(f"• **Couleur secondaire :** {palette['noms'][1]}")
            st.write("→ Pour structurer les différentes parties du site.")

            st.write(f"• **Couleur des boutons :** {palette['noms'][2]}")
            st.write("→ Pour les boutons importants : Acheter / S'inscrire / Découvrir.")

        # SEO
        with tabs[1]:

            st.write("**Stratégie SEO (Analyse Profonde) :**")

            score_seo = score-3

            st.write(f"Score d'optimisation : {score_seo}%")

            col_seo1,col_seo2 = st.columns(2)

            with col_seo1:

                st.write("**Mots-clés détectés :**")

                st.code(f"1. Expertise {url}\n2. Solution Digitale\n3. Performance")

            with col_seo2:

                densite = 0.82

                st.write("**Couverture du champ lexical :**")

                st.progress(densite)

                st.caption("82% du champ lexical est couvert.")

                st.write("**Pour atteindre 100%, vous pourriez ajouter :**")

                suggestions = [
                    "innovation digitale",
                    "optimisation web",
                    "expérience utilisateur",
                    "stratégie marketing",
                    "analyse de performance"
                ]

                for mot in suggestions:
                    st.write(f"• {mot}")

        # UX
        with tabs[2]:

            st.write("**Analyse de l'expérience utilisateur (UX) :**")

            st.write("Points détectés par Sitra :")

            st.write("• Certains boutons importants ne sont pas assez visibles.")
            st.write("• Les titres pourraient être plus grands pour améliorer la lecture.")
            st.write("• Le menu mobile pourrait être simplifié.")
            st.write("• Certaines sections pourraient être mieux espacées.")

            st.info("💡 Un site facile à lire et à utiliser augmente fortement le taux de conversion.")

            st.write(f"Fluidité générale : Temps de chargement de **{vitesse}s**.")

        # DESIGN
        with tabs[3]:

            st.write("**Design & Branding :**")

            st.write("Ces couleurs sont recommandées pour renforcer l'identité visuelle du site.")

            st.write("• Couleur principale : fond du site ou sections principales.")
            st.write("• Couleur secondaire : organisation des blocs.")
            st.write("• Couleur d'action : boutons importants.")

            c_p1,c_p2,c_p3 = st.columns(3)

            c_p1.color_picker(f"Couleur principale : {palette['noms'][0]}",palette['couleurs'][0],key=f"c1_{idx}",disabled=True)
            c_p2.color_picker(f"Couleur secondaire : {palette['noms'][1]}",palette['couleurs'][1],key=f"c2_{idx}",disabled=True)
            c_p3.color_picker(f"Bouton d'action : {palette['noms'][2]}",palette['couleurs'][2],key=f"c3_{idx}",disabled=True)

            st.write("---")

            st.write("**Tailles de texte recommandées :**")

            st.write("Titre principal (H1) : environ 40 à 50px")
            st.write("Sous-titres (H2) : environ 24 à 32px")
            st.write("Texte normal : environ 14 à 18px")

            st.markdown('<p class="h1-sample">Exemple de Titre</p>',unsafe_allow_html=True)
            st.markdown('<p class="p-sample">Exemple de texte normal.</p>',unsafe_allow_html=True)

        # COMPARATIF
        with tabs[4]:

            if mode_comparaison:

                st.write("**Comparatif Marché :**")

                st.write(f"Analyse comparative entre {url1} et {url2}.")

                st.line_chart([random.randint(50,100) for _ in range(10)])

            else:

                st.warning("⚠️ Cette section est réservée aux membres Premium.")

                if st.button("Découvrir l'offre Premium",key=f"pay_{idx}"):

                    st.write("### Choisir un moyen de paiement")

                    st.write("• Carte bancaire (Visa / Mastercard)")
                    st.write("• PayPal")
                    st.write("• Apple Pay")
                    st.write("• Google Pay")
                    st.write("• Stripe")

                    st.info("Paiement sécurisé en ligne.")

        # CHALLENGE
        with tabs[5]:

            st.write("**Mode Challenge**")

            progression = random.randint(30,100)

            if progression < 50:

                st.error(f"Progression : {progression}% - Niveau faible")

            elif progression < 80:

                st.warning(f"Progression : {progression}% - Niveau moyen")

            else:

                st.success(f"Progression : {progression}% - Niveau excellent")

            st.progress(progression/100)

            st.checkbox("Appliquer la palette",value=True,key=f"ch1_{idx}")
            st.checkbox("Ajuster les menus",key=f"ch2_{idx}")

        st.write("---")

        st.download_button(
            "📥 Exporter le rapport complet (TXT)",
            f"Audit Sitra pour {url}",
            file_name=f"audit_{url}.txt",
            key=f"exp_{idx}"
        )

st.divider()

st.write("Sitra : Anticiper pour dominer le marché.")
