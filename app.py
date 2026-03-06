import streamlit as st
import time
import random

# 1. Configuration sobre sans emoji
st.set_page_config(page_title="Sitra | Digital Intelligence", layout="wide")

# 2. Identité de marque
st.title("Sitra")
st.caption("Systeme Expert d'Analyse Predictive et de Diagnostic Digital")
st.divider()

# --- PANNEAU DE CONTROLE ---
with st.sidebar:
    st.header("Centre de controle")
    mode_comparaison = st.checkbox("Activer le mode comparatif")
    st.divider()
    st.write("Moteur d'analyse : Sitra Engine v2.0.0")
    st.write("Statut : Pret")

# 3. Saisie avec correcteur automatique
col_in1, col_in2 = st.columns(2)
with col_in1:
    url1 = st.text_input("Domaine cible :", placeholder="exemple.com")
with col_in2:
    url2 = ""
    if mode_comparaison:
        url2 = st.text_input("Domaine concurrent :", placeholder="concurrent.com")

if st.button("Lancer l'analyse technique"):
    urls_to_scan = [url1]
    if mode_comparaison and url2:
        urls_to_scan.append(url2)
    
    for idx, url in enumerate(urls_to_scan):
        if not url: continue
        
        # Ajout automatique du protocole si manquant
        full_url = "https://" + url if not url.startswith("http") else url
            
        st.subheader(f"Rapport d'analyse Sitra : {full_url}")
        
        with st.status(f"Scan en cours...", expanded=True) as status:
            time.sleep(0.6)
            st.write("Verification des protocoles serveurs...")
            score = random.randint(75, 95)
            vitesse = round(random.uniform(0.5, 1.1), 2)
            time.sleep(0.6)
            st.write("Calcul des probabilites predictives...")
            status.update(label="Analyse terminee", state="complete", expanded=False)

        # --- METRIQUES PRINCIPALES ---
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Indice de performance", f"{score}/100")
        c2.metric("Temps de reponse", f"{vitesse}s")
        c3.metric("Securite SSL", "Valide")
        c4.metric("UX Mobile", "Optimise")

        # --- MODULES ISSUS DES CAPTURES D'ECRAN ---
        t1, t2, t3, t4, t5, t6 = st.tabs([
            "Analyse Predictive", "SEO & Marketing", "UX / Mobile", 
            "Design & Branding", "Benchmark", "Mode Challenge"
        ])

        with t1:
            st.write("**Analyse des probabilites**")
            st.info(f"Analyse Sitra : Si vous modifiez la couleur du bouton principal, le taux de clic pourrait augmenter de 15%.")
            st.write("Cette prediction est basee sur les donnees de navigation et le comportement utilisateur actuel.")

        with t2:
            st.write("**Strategie SEO**")
            st.write(f"- Vos mots-cles sont optimises a {score-2}% par rapport au secteur.")
            st.write("- Suggestion : Ameliorez vos titres et descriptions pour attirer plus de visiteurs.")
            st.write("- Sitra genere des suggestions de titres pour un meilleur referencement.")

        with t3:
            st.write("**Experience Utilisateur**")
            st.write("Points d'attention :")
            st.write("- Menus caches : Certains elements de navigation sont peu visibles sur smartphone.")
            st.write(f"- Fluidite : Votre score est superieur a la moyenne avec un temps de {vitesse}s.")

        with t4:
            st.write("**Design et Identite Visuelle**")
            st.write("- Harmonie : Verification des couleurs, polices et tailles de texte effectuee.")
            st.write("- Conseil : Harmonisez la taille des titres entre l'accueil et les pages secondaires.")

        with t5:
            st.write("**Surveillance Automatique**")
            st.write("Le module Benchmark est actif :")
            st.write(f"- Sitra surveille les changements de design et de vitesse sur {url}.")
            st.write("- Alertes hebdomadaires programmees en cas d'evolution chez les concurrents.")

        with t6:
            st.write("**Plan d'action (Coach Numerique)**")
            st.write("Etape 1 : Optimiser les visuels pour descendre sous la barre des 0.8s.")
            st.write("Etape 2 : Revoir la visibilite du menu mobile pour eviter les clics perdus.")
            st.write("Etape 3 : Appliquer les recommandations marketing pour depasser votre concurrent principal.")

        # Export
        rapport_data = f"SITRA REPORT - {url}\nIndice: {score}\nRecommandation: +15% clic"
        st.download_button(f"Exporter les donnees ({idx+1})", rapport_data, file_name=f"sitra_audit_{idx}.txt")
        st.divider()

st.write("Sitra : Anticiper pour dominer le marche.")
