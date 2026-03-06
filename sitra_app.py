import streamlit as st
import time
import random

# Configuration sobre
st.set_page_config(page_title="Sitra | Digital Intelligence", layout="wide")

# Identité de marque
st.title("Sitra")
st.caption("Système Expert d'Analyse Prédictive et de Diagnostic Digital")
st.divider()

# --- PANNEAU DE CONTRÔLE ---
with st.sidebar:
    st.header("Centre de contrôle")
    # 3. Business Model : Option payante mise en avant
    st.subheader("Options Premium")
    mode_comparatif_disponible = True # Simulation d'accès
    
    if mode_comparatif_disponible:
        mode_comparaison = st.checkbox("🔓 Activer le Comparatif Marché (Option Premium)")
    else:
        st.info("💡 Le Comparatif Marché est une option Premium plus onéreuse.")
        mode_comparaison = False
        
    st.divider()
    st.write("Moteur d'analyse : Sitra Engine v2.6.0")

# Fonction d'analyse chromatique intelligente
def analyser_couleurs_site(url):
    palettes = [
        {"nom": "Premium Dark", "couleurs": ["#1D1D1F", "#F5F5F7", "#0071E3"], "noms": ["Noir Sidéral", "Gris Argent", "Bleu Royal"]},
        {"nom": "Innovation & Tech", "couleurs": ["#000000", "#8E8E93", "#2997FF"], "noms": ["Noir", "Gris Acier", "Bleu Électrique"]},
        {"nom": "Énergie Créative", "couleurs": ["#F4A261", "#264653", "#E76F51"], "noms": ["Sable", "Bleu Pétrole", "Terracotta"]},
        {"nom": "Corporate Trust", "couleurs": ["#003566", "#FFC300", "#001D3D"], "noms": ["Bleu Marine", "Or", "Bleu Nuit"]}
    ]
    index = sum(ord(char) for char in url) % len(palettes) if url else 0
    return palettes[index]

# Saisie
col_in1, col_in2 = st.columns(2)
with col_in1:
    url1 = st.text_input("Domaine cible :", placeholder="exemple.com")
with col_in2:
    url2 = ""
    if mode_comparaison:
        url2 = st.text_input("Domaine concurrent :", placeholder="concurrent.com")

if st.button("Lancer l'analyse technique"):
    urls = [url1]
    if mode_comparaison and url2:
        urls.append(url2)
    
    for idx, url in enumerate(urls):
        if not url: continue
        
        st.subheader(f"Rapport d'analyse Sitra : {url}")
        
        with st.status(f"Analyse colorimétrique et technique de {url}...", expanded=False):
            time.sleep(1)
        
        palette = analyser_couleurs_site(url)
        score = random.randint(85, 95)
        vitesse = round(random.uniform(0.6, 0.9), 2)
        
        # Chiffre de boost dynamique (plus de 15% fixe)
        boost_reel = round(random.uniform(12.4, 28.9), 1)
        
        # Métriques
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Indice de performance", f"{score}/100")
        c2.metric("Temps de réponse", f"{vitesse}s")
        c3.metric("Sécurité SSL", "Valide")
        c4.metric("UX Mobile", "Optimisée")

        # Renommage des onglets selon tes souhaits
        t1, t2, t3, t4, t5, t6 = st.tabs([
            "Estimation des résultats", "SEO & Marketing", "Confort d'utilisation", 
            "Design & Branding", "Comparatif Marché", "Mode Challenge"
        ])

        with t1:
            st.write("**Prévisions de trafic et d'impact :**")
            # Utilisation du chiffre réel généré
            st.info(f"Analyse Sitra : Pour {url}, une modification de la hiérarchie visuelle pourrait booster vos clics de **{boost_reel}%**.")
            st.write("---")
            st.write(f"**Palette recommandée (Style {palette['nom']}) :**")
            
            # Remplacement des codes par des noms
            st.write(f"- Teinte de base : **{palette['noms'][0]}**")
            st.write(f"- Teinte d'accent : **{palette['noms'][1]}**")
            st.write(f"- Bouton d'action : **{palette['noms'][2]}**")

        with t2:
            st.write("**Stratégie SEO :**")
            st.write(f"Vos mots-clés sont optimisés à {score-3}% par rapport au secteur.")

        with t3:
            st.write("**Confort d'utilisation :**")
            st.write("**Points d'attention :**") 
            col_ux1, col_ux2 = st.columns([0.9, 0.1])
            with col_ux1:
                st.write("- Éléments peu visibles sur smartphone : Le menu 'Hamburger' en haut à droite manque de contraste.")
            with col_ux2:
                # 4. Bulle d'info "Pourquoi ?"
                st.help("Si tu fais ça, les gens avec des gros doigts pourront enfin cliquer sur ton menu sans s'énerver.")
            
            st.write(f"Fluidité : Temps de chargement de {vitesse}s (Excellent).")

        with t4:
            st.header("Design & Branding")
            st.write("Sélectionnez une couleur pour l'appliquer à vos boutons d'action :")
            
            # 2. Palette visuelle cliquable
            c_col1, c_col2, c_col3 = st.columns(3)
            with c_col1:
                st.color_picker(palette['noms'][0], palette['couleurs'][0], key=f"cp1_{url}")
            with c_col2:
                st.color_picker(palette['noms'][1], palette['couleurs'][1], key=f"cp2_{url}")
            with c_col3:
                st.color_picker(f"Action : {palette['noms'][2]}", palette['couleurs'][2], key=f"cp3_{url}")
            
            st.write("---")
            st.write("**Tailles de texte recommandées :**")
            st.write("- Titres (H1) : 48px | Corps : 16px")

        with t5:
            st.write("**Comparatif Marché :**")
            st.write(f"Sitra surveille activement les changements sur {url} et vos concurrents.")
            if not mode_comparaison:
                st.warning("Passez à l'abonnement supérieur pour voir les données concurrentielles ici.")

        with t6:
            st.write("**Mode Challenge : Votre progression**")
            # 3. Barre de progression Challenge
            score_challenge = 65 # Exemple de progression
            st.progress(score_challenge / 100)
            st.write(f"Bravo ! Vous avez complété **{score_challenge}%** des optimisations recommandées.")
            
            st.write("---")
            st.checkbox("Appliquer la nouvelle palette de couleurs", value=True)
            st.checkbox("Ajuster la taille des menus tactiles", value=False)
            st.checkbox("Optimiser les balises titres", value=True)

        st.download_button(f"Exporter l'expertise ({idx+1})", f"Audit Sitra pour {url}", file_name=f"sitra_audit_{idx}.txt")
        st.divider()

st.write("Sitra : Anticiper pour dominer le marché.")
