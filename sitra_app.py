import streamlit as st
import requests
import time
import random
from streamlit_lottie import st_lottie
from streamlit.components.v1 import html

# ---------- INTRO SITRA ----------
def load_lottieurl(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

if "intro_done" not in st.session_state:
    st.session_state.intro_done = False

# --- Animation futuriste / tech / IA ---
lottie_robot = load_lottieurl("https://assets8.lottiefiles.com/packages/lf20_4khlpyr3.json")

if not st.session_state.intro_done:
    st.markdown("<h1 style='text-align:center;'>Bienvenue sur Sitra</h1>", unsafe_allow_html=True)
    if lottie_robot:
        st_lottie(lottie_robot, height=500)
    else:
        st.warning("⚠️ L'animation Lottie n'a pas pu être chargée. Vérifie l'URL.")
    
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
    st.markdown("")
    if st.button("🚀 Commencer"):
        st.session_state.intro_done = True
        st.rerun()
    st.stop()

# ---------- FIN INTRO ----------

# --- Configuration ---
st.set_page_config(page_title="Sitra | Digital Intelligence", layout="wide")

# --- Style CSS ---
st.markdown("""
<style>
h2, h3, h4, h5, h6, .internal-title { text-decoration: underline; }
[data-testid="stSidebar"] { background-color: #000000; color: #ffffff; }
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { text-decoration: none; }
[data-testid="stSidebar"] .stCheckbox label { color: #ffffff !important; font-weight: bold; }
input[type="text"] { border: 2px solid #ccc; border-radius: 5px; padding: 6px; }
input[type="text"]:focus { border: 2px solid #28a745; outline: none; }
.main .block-container { background-color: #f7f7f7; padding: 20px; border-radius: 10px; }
.color-block { width: 60px; height: 60px; border-radius: 8px; border: 1px solid #000; display: inline-block; margin-right: 10px; vertical-align: middle; }
.color-label { display: inline-block; vertical-align: middle; margin-right: 15px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- Identité ---
st.title("Sitra")
st.caption("Système Expert d'Analyse Prédictive et de Diagnostic Digital")
st.divider()

# --- SIDEBAR ---
with st.sidebar:
    st.header("Centre de contrôle")
    st.subheader("Options Premium")
    mode_comparaison = st.checkbox("🔓 Activer le mode comparatif", key="premium_check")
    if mode_comparaison:
        st.success("💳 Option Premium activée (Mode démo)")
    st.divider()
    st.write("Moteur d'analyse : Sitra Engine v2.6.0")

# --- Fonction palette ---
def analyser_couleurs_site(url):
    palettes = [
        {"nom": "Premium Dark", "couleurs": ["#1D1D1F", "#F5F5F7", "#0071E3"], "noms": ["Noir Sidéral", "Gris Argent", "Bleu Royal"]},
        {"nom": "Innovation & Tech", "couleurs": ["#000000", "#8E8E93", "#2997FF"], "noms": ["Noir", "Gris Acier", "Bleu Électrique"]},
        {"nom": "Énergie Créative", "couleurs": ["#F4A261", "#264653", "#E76F51"], "noms": ["Sable", "Bleu Pétrole", "Terracotta"]},
        {"nom": "Corporate Trust", "couleurs": ["#003566", "#FFC300", "#001D3D"], "noms": ["Bleu Marine", "Or", "Bleu Nuit"]}
    ]
    index = sum(ord(char) for char in url) % len(palettes) if url else 0
    return palettes[index]

# --- Fonction mots-clés dynamiques ---
def generer_mots_cles(url):
    base_mots = [
        "Ajouter un bouton 'Contactez-nous' visible sur la page d'accueil",
        "Mettre une section témoignages clients pour renforcer la confiance",
        "Optimiser le menu pour une navigation plus fluide",
        "Mettre en avant les produits/services principaux dès l'arrivée sur le site",
        "Ajouter un appel à l'action clair sur chaque page",
        "Améliorer la lisibilité des titres et sous-titres",
        "Rendre le site responsive sur mobile et tablette",
        "Ajouter des mots-clés relatifs à votre secteur dans les titres et textes",
        "Créer une section FAQ pour répondre aux questions fréquentes",
        "Mettre en avant les avantages concurrentiels de votre service"
    ]
    random.seed(sum(ord(c) for c in url))
    random.shuffle(base_mots)
    return base_mots[:5]

# --- Barre de positionnement SEO colorée ---
def barre_positionnement(score):
    if score < 50:
        couleur = "#f44336"  # rouge
        texte = "Positionnement faible"
        emoji = "🔴"
    elif score < 80:
        couleur = "#ff9800"  # orange
        texte = "Positionnement moyen"
        emoji = "🟠"
    else:
        couleur = "#28a745"  # vert
        texte = "Bon positionnement"
        emoji = "🟢"
    
    html(f"""
    <div style="margin-bottom:10px;">
        <strong>{emoji} {score}</strong><br>
        Positionnement sur les moteurs de recherche : <strong>{score}/100</strong><br>
        <span style="color:{couleur}; font-weight:bold;">{emoji} {texte}</span>
        <div style="background:#e0e0e0; border-radius:5px; width:100%; height:25px; margin-top:5px;">
            <div style="width:{score}%; background:{couleur}; height:25px; border-radius:5px;"></div>
        </div>
    </div>
    """, height=80)

# --- INPUT ---
col_in1, col_in2 = st.columns(2)
with col_in1:
    url1 = st.text_input("Domaine cible :", placeholder="exemple URL ou .com")
    if mode_comparaison:
        st.info("💡 Ce mode permet d'analyser votre site et de voir comment l'améliorer pour dépasser un concurrent.")
with col_in2:
    url2 = ""
    if mode_comparaison:
        url2 = st.text_input("Domaine concurrent :", placeholder="exemple URL ou .com")

# --- ANALYSE ---
if st.button("Lancer l'analyse technique"):
    urls = [url1] if not (mode_comparaison and url2) else [url1, url2]
    for idx, url in enumerate(urls):
        if not url:
            continue

        st.subheader(f"Rapport d'analyse Sitra : {url}")
        with st.status(f"Analyse de {url}...", expanded=False):
            time.sleep(1)

        # Valeurs temporaires pour fonctionnement
        score = random.randint(50, 95)
        vitesse = round(random.uniform(0.5, 2.0), 2)
        palette = analyser_couleurs_site(url)
        boost_reel = random.randint(10, 40)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Indice de performance", f"{score}/100")
        c2.metric("Temps de réponse", f"{vitesse}s")
        c3.metric("Sécurité SSL", "Valide")
        c4.metric("UX Mobile", "Optimisée")

        tabs = st.tabs([
            "Estimation des résultats",
            "SEO & Marketing",
            "Confort d'utilisation",
            "Design & Branding",
            "Comparatif Marché",
            "Mode Challenge"
        ])

        # --- ESTIMATION ---
        with tabs[0]:
            st.markdown('<h3 class="internal-title">Prévisions de trafic :</h3>', unsafe_allow_html=True)
            st.info(f"Pour **{url}**, améliorer l'organisation visuelle pourrait augmenter les clics d'environ **{boost_reel}%**.")
            st.markdown('<h3 class="internal-title">Recommandation de couleurs :</h3>', unsafe_allow_html=True)
            st.write(f"• **Couleur principale :** {palette['noms'][0]}")
            st.write(f"• **Couleur secondaire :** {palette['noms'][1]}")
            st.write(f"• **Couleur d'action :** {palette['noms'][2]}")

        # --- SEO & Marketing ---
        with tabs[1]:
            st.markdown('<h3 class="internal-title">Stratégie SEO :</h3>', unsafe_allow_html=True)
            score_seo = score - 3
            st.write(f"Score d'optimisation : {score_seo}%")
            col_seo1, col_seo2 = st.columns(2)
            with col_seo1:
                st.markdown('<h4 class="internal-title">Mots-clés recommandés et leur usage :</h4>', unsafe_allow_html=True)
                phrases = generer_mots_cles(url)
                for i, phrase in enumerate(phrases, 1):
                    st.write(f"{i}. {phrase}")
                st.caption("💡 Ces actions sont recommandées pour améliorer la structure et le contenu de votre site.")
            with col_seo2:
                st.markdown('<h4 class="internal-title">Positionnement sur les moteurs de recherche :</h4>', unsafe_allow_html=True)
                barre_positionnement(score)
                st.caption("💡 Cette métrique montre comment votre site est référencé sur Google et autres moteurs.")

        # --- UX ---
        with tabs[2]:
            st.markdown('<h3 class="internal-title">Expérience Utilisateur :</h3>', unsafe_allow_html=True)
            st.write("Points détectés :")
            st.write("• Certains boutons importants ne sont pas assez visibles.")
            st.write("• Les titres pourraient être plus grands pour améliorer la lecture.")
            st.write("• Le menu mobile pourrait être simplifié.")
            st.info(f"💡 Temps de chargement : {vitesse}s")

        # --- DESIGN ---
        with tabs[3]:
            st.markdown('<h3 class="internal-title">Design & Branding :</h3>', unsafe_allow_html=True)
            c_p1, c_p2, c_p3 = st.columns(3)
            emplacements = ["Header / navigation", "Section principale", "Boutons / actions"]
            for i, (nom, couleur) in enumerate(zip(palette['noms'], palette['couleurs'])):
                col = [c_p1, c_p2, c_p3][i]
                col.markdown(f"<span class='color-label'>{nom} ({emplacements[i]})</span><div class='color-block' style='background:{couleur}'></div>", unsafe_allow_html=True)

        # --- COMPARATIF ---
        with tabs[4]:
            if mode_comparaison:
                st.markdown('<h3 class="internal-title">Comparatif Marché :</h3>', unsafe_allow_html=True)
                st.info("""
**💡 Légende des scores (0-100) :**  
- 0-39 : Très mauvais  
- 40-69 : Moyen  
- 70-89 : Bon  
- 90-100 : Excellent  

Chaque barre représente un indice pour votre site : **Performance**, **UX**, **Vitesse**, **SEO**, **Design**
                """)
                metrics = {
                    "Performance": score,
                    "UX": random.randint(70, 100),
                    "Vitesse": round((1 - vitesse) * 100, 0),
                    "SEO": score_seo,
                    "Design": random.randint(75, 95)
                }
                st.bar_chart(metrics)
                st.info("💡 Pour améliorer votre site et dépasser le concurrent, travaillez sur ces indicateurs.")
            else:
                st.warning("⚠️ Cette section est réservée aux membres Premium.")

        # --- MODE CHALLENGE ---
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
            st.progress(score_challenge / 100)

        st.download_button(
            "📥 Exporter le rapport complet (TXT)",
            f"Audit Sitra pour {url}",
            file_name=f"audit_{url}.txt",
            key=f"exp_{idx}"
        )

st.divider()
st.write("Sitra : Anticiper pour dominer le marché.")
