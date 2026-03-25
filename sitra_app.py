import streamlit as st
import time
from analyzer import full_analysis, get_score_label, normalize_url, get_pagespeed, detect_pages, detect_secteur_et_concurrents

# ── IA ────────────────────────────────────────────────────────────────────────
def generer_recommandations_ia(result):
    try:
        import requests as req
        headers = {
            "Authorization": f"Bearer {st.secrets['MISTRAL_API_KEY']}",
            "Content-Type": "application/json"
        }
        prompt = f"""Tu es un expert en optimisation de sites web. Analyse ces données et génère un rapport de recommandations personnalisé en 5-7 phrases naturelles. Détecte la langue du site et réponds dans cette langue.

Site : {result['final_url']}
Score global : {result['global_score']}/100
SEO : {result['seo']['score']}/100
UX : {result['ux']['score']}/100
Contenu : {result['content']['score']}/100
Design : {result['design']['score']}/100
Performance : {result['performance']['score']}/100
HTTPS : {'Oui' if result['is_https'] else 'Non'}
Temps de réponse : {result['response_time']}s
Problèmes : {', '.join([i['message'] for i in result['all_issues'][:5]])}"""
        data = {"model": "mistral-large-latest", "messages": [{"role": "user", "content": prompt}]}
        r = req.post("https://api.mistral.ai/v1/chat/completions", headers=headers, json=data, timeout=30)
        return r.json()["choices"][0]["message"]["content"]
    except Exception:
        return None

# ── PDF ───────────────────────────────────────────────────────────────────────
def envoyer_rapport_email(email: str, result: dict) -> bool:
    """Envoie le rapport PDF par email via Resend"""
    try:
        import requests as req
        import base64

        pdf_data = generer_pdf(result)
        pdf_b64 = base64.b64encode(pdf_data).decode("utf-8")

        score = result["global_score"]
        label_txt, _, _ = get_score_label(score)
        url_site = result["final_url"]

        html_content = f"""<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #667eea, #764ba2); padding: 2rem; text-align: center; border-radius: 12px 12px 0 0;">
                <h1 style="color: white; margin: 0; font-size: 2rem;">SITRA</h1>
                <p style="color: rgba(255,255,255,0.8); margin: 0.5rem 0 0;">Rapport d'analyse de site web</p>
            </div>
            <div style="background: #f7f7f7; padding: 2rem; border-radius: 0 0 12px 12px;">
                <h2 style="color: #333;">Votre rapport est prêt !</h2>
                <p style="color: #666;">Voici les résultats de l'analyse de <strong>{url_site}</strong> :</p>
                <div style="background: white; border-radius: 8px; padding: 1.5rem; margin: 1rem 0;">
                    <div style="font-size: 2.5rem; font-weight: bold; color: #667eea; text-align: center;">{score}/100</div>
                    <div style="text-align: center; color: #888; font-size: 0.9rem;">{label_txt}</div>
                </div>
            </div>
        </div>"""

        payload = {
            "from": "Sitra <onboarding@resend.dev>",
            "to": [email],
            "subject": f"Votre rapport Sitra — {url_site} — Score : {score}/100",
            "html": html_content,
            "attachments": [{
                "filename": f"sitra_rapport.pdf",
                "content": pdf_b64
            }]
        }

        headers = {
            "Authorization": f"Bearer {st.secrets['RESEND_API_KEY']}",
            "Content-Type": "application/json"
        }

        r = req.post("https://api.resend.com/emails", headers=headers, json=payload, timeout=30)
        return r.status_code == 200

    except Exception as e:
        return False

# ── LIMITE ANALYSES ───────────────────────────────────────────────────────────
def get_analyses_count():
    if "analyses_count" not in st.session_state:
        st.session_state["analyses_count"] = 0
    return st.session_state["analyses_count"]

def increment_analyses_count():
    if "analyses_count" not in st.session_state:
        st.session_state["analyses_count"] = 0
    st.session_state["analyses_count"] += 1

def show_paywall():
    st.markdown("""
    <div style="background:linear-gradient(135deg,#1a1a2e,#16213e);border:1px solid #667eea;border-radius:16px;padding:3rem;text-align:center;margin:2rem 0">
        <div style="font-size:2rem;font-weight:800;background:linear-gradient(135deg,#667eea,#f07cf7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:1rem">
            Vous avez utilisé vos 2 analyses gratuites
        </div>
        <p style="color:#aaa;font-size:1rem;margin-bottom:2rem;max-width:500px;margin-left:auto;margin-right:auto">
            Pour continuer à analyser vos sites et accéder aux recommandations IA, à l'export PDF et à l'analyse concurrentielle, passez au plan Pro.
        </p>
        <a href="#pricing" style="background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:1rem 2.5rem;border-radius:12px;text-decoration:none;font-weight:700;font-size:1rem;display:inline-block">
            Voir les offres
        </a>
    </div>
    """, unsafe_allow_html=True)

# ── CONFIG ───────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Sitra | Analyseur de Sites Web", page_icon="S", layout="wide", initial_sidebar_state="expanded")

# ── HELPERS ───────────────────────────────────────────────────────────────────
def render_score_bar(label, score):
    label_txt, _, color = get_score_label(score)
    st.markdown(f"""
    <div class="score-bar-container">
        <div class="score-bar-label">
            <span>{label}</span>
            <span style="color:{color};font-weight:700">{score}/100 — {label_txt}</span>
        </div>
        <div class="score-bar-bg">
            <div class="score-bar-fill" style="width:{score}%;background:{color}"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_issues(issues):
    if not issues:
        st.info("🛈 Rien à afficher pour le moment.")
    else:
        for issue in issues:
            css_class = "issue-critical" if issue.startswith("[X]") or "pas de" in issue.lower() else "issue-warning"
            st.markdown(f'<div class="issue-item {css_class}">{issue}</div>', unsafe_allow_html=True)

# ── RENDER RESULT ─────────────────────────────────────────────────────────────
def render_result(result, idx=0):
    if result.get("error"):
        st.warning("Impossible d'analyser ce site. Certains grands sites bloquent volontairement les outils d'analyse automatiques.")
        return

    label_txt, _, label_color = get_score_label(result["global_score"])
    st.divider()
    st.markdown(f"### {result['final_url']}")

    # Scores en cartes
    c1, c2, c3, c4, c5 = st.columns(5)
    for col, score, lbl in [
        (c1, result["global_score"], "Score Global"),
        (c2, result["seo"]["score"], "SEO"),
        (c3, result["ux"]["score"], "UX"),
        (c4, result["design"]["score"], "Design"),
        (c5, result["performance"]["score"], "Performance"),
    ]:
        lbl_t, _, clr = get_score_label(score)
        col.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color:{clr}">{score}</div>
            <div class="metric-label">{lbl}</div>
        </div>
        """, unsafe_allow_html=True)

    # Recommandations IA
    with st.expander("Analyse IA — Recommandations personnalisées"):
        with st.spinner("L'IA analyse votre site..."):
            recommandations = generer_recommandations_ia(result)
        if recommandations:
            st.markdown(recommandations)
        else:
            st.info("🛈 Rien à afficher pour le moment.")

    # Onglets
    tabs = st.tabs(["SEO", "UX", "Contenu", "Design", "Performance", "PageSpeed", "Concurrents", "Récapitulatif", "Challenge", "Partager"])
    
    # Exemple pour SEO
    with tabs[0]:
        seo = result["seo"]
        render_score_bar("SEO et Référencement", seo["score"])
        st.markdown("")
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.markdown("**Données détectées**")
            if seo["title"] or seo["meta_description"]:
                title_display = seo['title'][:60] + '...' if len(seo['title']) > 60 else seo['title'] or '(manquant)'
                st.markdown(f"- **Titre** : `{title_display}` ({len(seo['title'])} chars)")
                st.markdown(f"- **Meta description** : {len(seo['meta_description'])} chars")
                st.markdown(f"- **H1** : {seo['h1_count']} {'(correct)' if seo['h1_count'] == 1 else '(à corriger)'}")
                st.markdown(f"- **H2** : {seo['h2_count']} {'(correct)' if seo['h2_count'] > 0 else '(manquant)'}")
                st.markdown(f"- **Images sans alt** : {seo['images_no_alt']}/{seo['images_total']}")
            else:
                st.info("🛈 Rien à afficher pour le moment.")
        with col_s2:
            st.markdown("**Points à corriger**")
            render_issues(seo["issues"])

    # ⚡ Tu peux répéter le même principe pour les autres onglets (UX, Contenu, Design...)  
