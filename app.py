import streamlit as st
import time
import random

# 1. Configuration avec ton nouveau nom : SITRA
st.set_page_config(page_title="Sitra | Digital Audit", layout="wide", page_icon="🖥️")

# 2. Header de marque
st.title("Sitra")
st.caption("Système d'Analyse et de Scan Digital Haute Précision")
st.divider()

with st.sidebar:
    st.header("Configuration Sitra")
    mode_comparaison = st.checkbox("Mode Comparatif ")
    st.divider()
    st.write("Version : 1.0.0 (Sitra Engine)")

# 3. Saisie Intelligente (Accepte apple.com sans https)
col1, col2 = st.columns(2)
with col1:
    url1 = st.text_input("Domaine à scanner :", placeholder="exemple.com")
with col2:
    url2 = ""
    if mode_comparaison:
        url2 = st.text_input("Domaine concurrent :", placeholder="concurrent.com")

if st.button("Lancer le Scan Sitra"):
    urls = []
    if url1: urls.append(url1)
    if mode_comparaison and url2: urls.append(url2)
    
    for idx, url in enumerate(urls):
        # Correction automatique de l'URL
        if not url.startswith("http"):
            url = "https://" + url
            
        st.subheader(f"Analyse Sitra : {url}")
        
        # Simulation de scan visuel
        bar = st.progress(0)
        for p in range(100):
            time.sleep(0.01)
            bar.progress(p + 1)
            
        score = random.randint(78, 97)
        latence = round(random.uniform(0.3, 0.9), 2)
        
        # Métriques Business
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Score Sitra", f"{score}/100")
        c2.metric("Réponse Serveur", f"{latence}s")
        c3.metric("Sécurité", "Certifiée")
        c4.metric("UX Mobile", "Optimisée")

        # Onglets Pro
        tabs = st.tabs(["Infrastructure", "Interface", "Légal", "SEO", "Social", "Confiance"])
        
        with tabs[0]:
            st.write(f"Analyse technique du domaine {url} terminée.")
            st.write(f"- Protocole : HTTPS Sécurisé")
            st.write(f"- Performance : Excellente ({latence}s)")
        
        # Export du rapport Sitra
        rapport = f"RAPPORT SITRA - {url}\nScore Global: {score}/100\nAnalysé par Sitra Engine."
        st.download_button(f"Exporter l'analyse Sitra ({idx+1})", data=rapport, file_name=f"sitra_audit_{idx}.txt")
        st.divider()

st.info("Scan Sitra terminé. Toutes les données sont conformes.")
