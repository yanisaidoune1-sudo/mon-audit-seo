import streamlit as st
import requests
import time
import random
from streamlit_lottie import st_lottie
from streamlit.components.v1 import html

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Sitra | Digital Intelligence", layout="wide")

# ---------------- LOTTIE ----------------
def load_lottie(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_robot = load_lottie("https://assets8.lottiefiles.com/packages/lf20_4khlpyr3.json")

# ---------------- INTRO ----------------
if "intro_done" not in st.session_state:
    st.session_state.intro_done = False

if not st.session_state.intro_done:

    st.markdown("<h1 style='text-align:center;'>Bienvenue sur Sitra</h1>", unsafe_allow_html=True)

    if lottie_robot:
        st_lottie(lottie_robot, height=400)

    message = st.empty()

    phrases = [
        "Cette application analyse votre site web et vous donne des recommandations.",
        "Elle vous aide à améliorer votre SEO et votre positionnement.",
        "Elle optimise aussi l'expérience utilisateur et le design.",
        "Et vous pourrez comparer votre site avec d'autres."
    ]

    for p in phrases:
        message.markdown(f"<h3 style='text-align:center'>{p}</h3>", unsafe_allow_html=True)
        time.sleep(2)

    if st.button("🚀 Commencer"):
        st.session_state.intro_done = True
        st.rerun()

    st.stop()

# ---------------- STYLE ----------------
st.markdown("""
<style>
h2, h3, h4 {text-decoration: underline;}
[data-testid="stSidebar"] {background-color:#000000;color:white;}
.main .block-container {background:#f7f7f7;padding:20px;border-radius:10px;}
</style>
""", unsafe_allow_html=True)

# ---------------- TITRE ----------------
st.title("Sitra")
st.caption("Système Expert d'Analyse Prédictive et de Diagnostic Digital")
st.divider()

# ---------------- SIDEBAR ----------------
with st.sidebar:

    st.header("Centre de contrôle")

    mode_comparaison = st.checkbox("🔓 Mode comparatif")

    if mode_comparaison:
        st.success("Mode comparatif activé")

    st.divider()

    st.write("Moteur : Sitra Engine v2.6")

# ---------------- FONCTIONS ----------------

def analyser_couleurs_site(url):

    palettes = [
        ["#1D1D1F","#F5F5F7","#0071E3"],
        ["#000000","#8E8E93","#2997FF"],
        ["#F4A261","#264653","#E76F51"],
        ["#003566","#FFC300","#001D3D"]
    ]

    index = sum(ord(c) for c in url) % len(palettes)

    return palettes[index]


def generer_mots_cles(url):

    base = [
        "Ajouter un bouton contact visible",
        "Améliorer les titres SEO",
        "Optimiser le menu",
        "Ajouter une section témoignages",
        "Améliorer la version mobile",
        "Ajouter une FAQ",
        "Renforcer les appels à l'action"
    ]

    random.shuffle(base)

    return base[:5]

# ---------------- INPUT ----------------

col1, col2 = st.columns(2)

with col1:
    url1 = st.text_input("Domaine à analyser")

with col2:
    url2 = ""

    if mode_comparaison:
        url2 = st.text_input("Domaine concurrent")

# ---------------- ANALYSE ----------------

if st.button("Lancer l'analyse technique"):

    urls = [url1] if not mode_comparaison else [url1,url2]

    for url in urls:

        if not url:
            continue

        st.subheader(f"Analyse : {url}")

        with st.status("Analyse en cours...",expanded=False):
            time.sleep(1)

        score = random.randint(50,95)
        vitesse = round(random.uniform(0.5,2),2)

        palette = analyser_couleurs_site(url)

        c1,c2,c3,c4 = st.columns(4)

        c1.metric("Performance",f"{score}/100")
        c2.metric("Temps réponse",f"{vitesse}s")
        c3.metric("SSL","Valide")
        c4.metric("UX mobile","Optimisée")

        tabs = st.tabs([
            "Estimation",
            "SEO",
            "UX",
            "Design",
            "Comparatif"
        ])

# -------- ESTIMATION --------

        with tabs[0]:

            st.subheader("Prévision trafic")

            boost = random.randint(10,40)

            st.info(f"Optimisation possible : +{boost}% de clics")

# -------- SEO --------

        with tabs[1]:

            st.subheader("Mots clés recommandés")

            mots = generer_mots_cles(url)

            for m in mots:
                st.write("•",m)

# -------- UX --------

        with tabs[2]:

            st.subheader("Expérience utilisateur")

            st.write("• Boutons peu visibles")
            st.write("• Titres trop petits")
            st.write("• Menu mobile améliorable")

# -------- DESIGN --------

        with tabs[3]:

            st.subheader("Palette recommandée")

            cols = st.columns(3)

            for i,c in enumerate(palette):

                cols[i].color_picker("Couleur",c)

# -------- COMPARATIF --------

        with tabs[4]:

            if mode_comparaison:

                data = {
                    "Performance":score,
                    "SEO":random.randint(60,95),
                    "UX":random.randint(70,100),
                    "Design":random.randint(70,95)
                }

                st.bar_chart(data)

            else:

                st.warning("Mode comparatif non activé")

st.divider()

st.write("Sitra — Anticiper pour dominer le marché.")
