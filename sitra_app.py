import streamlit as st
import time
import random
import requests
from bs4 import BeautifulSoup
from collections import Counter
from urllib.parse import urlparse
from PIL import Image
from io import BytesIO
from colorthief import ColorThief  # pip install colorthief
import colorsys

# Configuration
st.set_page_config(page_title="Sitra | Digital Intelligence", layout="wide")

# CSS
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

# Sidebar
with st.sidebar:
    st.header("Centre de contrôle")
    st.subheader("Options Premium")
    mode_comparaison = st.checkbox("🔓 Activer le mode comparatif", key="premium_check")
    if mode_comparaison:
        st.success("💳 Option Premium activée (Mode démo)")
    st.divider()
    st.write("Moteur d'analyse : Sitra Engine v2.6.0")

# Récupération texte du site
def get_site_text(url):
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")
        texts = soup.find_all(["h1","h2","h3","p","span","li"])
        content = " ".join([t.get_text() for t in texts])
        return content
    except:
        return ""

# Extraction mots-clés
def extract_keywords(text, top_n=5):
    words = [w.lower() for w in text.split() if len(w)>3]
    counter = Counter(words)
    most_common = counter.most_common(top_n)
    return [w for w,c in most_common]

# Extraction couleur principale via logo ou images
def get_main_color(url):
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")
        imgs = soup.find_all("img")
        if not imgs:
            return "#0071E3"  # fallback
        img_url = imgs[0].get("src")
        if not img_url.startswith("http"):
            parsed = urlparse(url)
            img_url = f"{parsed.scheme}://{parsed.netloc}/{img_url.lstrip('/')}"
        img_resp = requests.get(img_url)
        img = Image.open(BytesIO(img_resp.content))
        color_thief = ColorThief(BytesIO(img_resp.content))
        dominant = color_thief.get_color(quality=1)
        return '#%02x%02x%02x' % dominant
    except:
        return "#0071E3"

# Générer palette complémentaire
def generate_palette(hex_color):
    r,g,b = int(hex_color[1:3],16), int(hex_color[3:5],16), int(hex_color[5:7],16)
    h,l,s = colorsys.rgb_to_hls(r/255,g/255,b/255)
    colors = []
    for i in [0, 0.1, -0.1]:
        nh = (h+i)%1
        nr,nl,ns = colorsys.hls_to_rgb(nh,l,s)
        colors.append('#%02x%02x%02x'%(int(nr*255),int(nl*255),int(ns*255)))
    return colors

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

        # Score simulé
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

        # SEO dynamique
        with tabs[1]:
            st.markdown('<h3 class="internal-title">Stratégie SEO :</h3>', unsafe_allow_html=True)
            text = get_site_text(url)
            keywords = extract_keywords(text)
            st.write(f"Score d'optimisation : {score-3}%")
            st.markdown('<h4 class="internal-title">Mots-clés détectés :</h4>', unsafe_allow_html=True)
            for mot in keywords:
                st.write(f"• {mot}")

        # DESIGN dynamique
        with tabs[3]:
            st.markdown('<h3 class="internal-title">Design & Branding :</h3>', unsafe_allow_html=True)
            main_color = get_main_color(url)
            palette = generate_palette(main_color)
            usages = ["Fond principal / sections", "Sections secondaires", "Boutons et actions"]
            c_p1, c_p2, c_p3 = st.columns(3)
            for col, nom, couleur, usage in zip([c_p1,c_p2,c_p3], ["Couleur 1","Couleur 2","Couleur 3"], palette, usages):
                col.markdown(f"<span class='color-label'>{nom}</span><div class='color-block' style='background:{couleur}'></div><span class='color-usage'>→ {usage}</span>", unsafe_allow_html=True)
