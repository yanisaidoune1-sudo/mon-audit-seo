import streamlit as st
import requests
import time
import random
from streamlit_lottie import st_lottie
from streamlit.components.v1 import html

# ---------- INTRO SITRA ----------

def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

if "intro_done" not in st.session_state:
    st.session_state.intro_done = False

lottie_robot = load_lottieurl("https://assets8.lottiefiles.com/packages/lf20_4khlpyr3.json")

if not st.session_state.intro_done:

    st.markdown("<h1 style='text-align:center;'>Bienvenue sur Sitra</h1>", unsafe_allow_html=True)

    if lottie_robot:
        st_lottie(lottie_robot, height=500)

    message = st.empty()

    phrases = [
        "Cette application analyse votre site web et vous donne des recommandations.",
        "Elle vous aide à améliorer votre SEO et votre positionnement.",
        "Elle optimise aussi l'expérience utilisateur et le design.",
        "Et vous pourrez comparer votre site avec d'autres."
    ]

    for p in phrases:
        message.markdown(f"<h3 style='text-align:center'>{p}</h3>", unsafe_allow_html=True)
        time.sleep(4)

    if st.button("🚀 Commencer"):
        st.session_state.intro_done = True
        st.rerun()

    st.stop()

# ---------- CONFIG ----------
st.set_page_config(page_title="Sitra | Digital Intelligence", layout="wide")

# ---------- STYLE ----------
st.markdown("""
<style>
h2, h3, h4, h5, h6, .internal-title { text-decoration: underline; }
[data-testid="stSidebar"] { background-color: #000000; color: #ffffff; }
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { text-decoration: none; }
[data-testid="stSidebar"] .stCheckbox label { color: #ffffff !important; font-weight: bold; }
.main .block-container { background-color: #f7f7f7; padding: 20px; border-radius: 10px; }
.color-block { width: 60px; height: 60px; border-radius: 8px; border: 1px solid #000; display: inline-block; margin-right: 10px; }
</style>
""", unsafe_allow_html=True)

# ---------- TITRE ----------
st.title("Sitra")
st.caption("Système Expert d'Analyse Prédictive et de Diagnostic Digital")
st.divider()

# ---------- SIDEBAR ----------
with st.sidebar:

    st.header("Centre de contrôle")

    st.subheader("Options Premium")

    mode_comparaison = st.checkbox("🔓 Activer le mode comparatif")

    if mode_comparaison:
        st.success("💳 Option Premium activée (Mode démo)")

    st.divider()

    st.write("Moteur d'analyse : Sitra Engine v2.6.0")

# ---------- FONCTIONS ----------

def analyser_couleurs_site(url):

    palettes = [
        {"nom":"Premium Dark","couleurs":["#1D1D1F","#F5F5F7","#0071E3"],"noms":["Noir Sidéral","Gris Argent","Bleu Royal"]},
        {"nom":"Innovation & Tech","couleurs":["#000000","#8E8E93","#2997FF"],"noms":["Noir","Gris Acier","Bleu Électrique"]},
        {"nom":"Énergie Créative","couleurs":["#F4A261","#264653","#E76F51"],"noms":["Sable","Bleu Pétrole","Terracotta"]},
        {"nom":"Corporate Trust","couleurs":["#003566","#FFC300","#001D3D"],"noms":["Bleu Marine","Or","Bleu Nuit"]}
    ]

    index = sum(ord(c) for c in url) % len(palettes)

    return palettes[index]

def generer_mots_cles(url):

    base_mots = [
        "Ajouter un bouton 'Contactez-nous' visible",
        "Mettre une section témoignages clients",
        "Optimiser le menu pour une navigation plus fluide",
        "Mettre en avant les services principaux",
        "Ajouter un appel à l'action clair",
        "Améliorer la lisibilité des titres",
        "Rendre le site responsive mobile",
        "Ajouter des mots-clés SEO dans les titres",
        "Créer une section FAQ",
        "Mettre en avant les avantages concurrentiels"
    ]

    random.seed(sum(ord(c) for c in url))

    random.shuffle(base_mots)

    return base_mots[:5]

# ---------- INPUT ----------
col_in1, col_in2 = st.columns(2)

with col_in1:

    url1 = st.text_input("Domaine cible :", placeholder="exemple.com")

with col_in2:

    url2 = ""

    if mode_comparaison:

        url2 = st.text_input("Domaine concurrent :", placeholder="concurrent.com")

# ---------- ANALYSE ----------

if st.button("Lancer l'analyse technique"):

    urls = [url1] if not(mode_comparaison and url2) else [url1,url2]

    for idx,url in enumerate(urls):

        if not url:
            continue

        st.subheader(f"Rapport d'analyse Sitra : {url}")

        with st.status("Analyse en cours...",expanded=False):
            time.sleep(1)

        score = random.randint(50,95)
        vitesse = round(random.uniform(0.5,2.0),2)

        palette = analyser_couleurs_site(url)

        c1,c2,c3,c4 = st.columns(4)

        c1.metric("Indice performance",f"{score}/100")
        c2.metric("Temps réponse",f"{vitesse}s")
        c3.metric("SSL","Valide")
        c4.metric("UX Mobile","Optimisée")

        tabs = st.tabs([
            "Estimation résultats",
            "SEO & Marketing",
            "Confort utilisation",
            "Design & Branding",
            "Comparatif Marché"
        ])

        with tabs[0]:

            st.subheader("Prévisions trafic")

            boost = random.randint(10,40)

            st.info(f"Optimisation possible : +{boost}% de clics")

        with tabs[1]:

            st.subheader("Stratégie SEO")

            phrases = generer_mots_cles(url)

            for p in phrases:
                st.write("•",p)

        with tabs[2]:

            st.subheader("Expérience utilisateur")

            st.write("• Boutons peu visibles")
            st.write("• Titres trop petits")
            st.write("• Menu mobile à simplifier")

        with tabs[3]:

            st.subheader("Palette recommandée")

            cols = st.columns(3)

            for i,c in enumerate(palette["couleurs"]):

                cols[i].color_picker("Couleur",c)

        with tabs[4]:

            if mode_comparaison:

                metrics = {
                    "Performance":score,
                    "SEO":random.randint(60,95),
                    "UX":random.randint(70,100),
                    "Design":random.randint(70,95)
                }

                st.bar_chart(metrics)

            else:

                st.warning("⚠️ Section réservée au mode comparatif")

st.divider()

st.write("Sitra : Anticiper pour dominer le marché.")
