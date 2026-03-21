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
def generer_pdf(result):
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    import io

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle('title', fontSize=22, fontName='Helvetica-Bold', textColor=colors.HexColor('#667eea'), spaceAfter=6)
    sub_style = ParagraphStyle('sub', fontSize=10, fontName='Helvetica', textColor=colors.HexColor('#888888'), spaceAfter=20)
    heading_style = ParagraphStyle('heading', fontSize=13, fontName='Helvetica-Bold', textColor=colors.HexColor('#222222'), spaceAfter=8, spaceBefore=16)
    normal_style = ParagraphStyle('normal', fontSize=10, fontName='Helvetica', textColor=colors.HexColor('#333333'), spaceAfter=4)

    story.append(Paragraph("SITRA — Rapport d'analyse", title_style))
    story.append(Paragraph(f"Site : {result['final_url']}", sub_style))
    story.append(Paragraph(f"Date : {time.strftime('%d/%m/%Y')}", sub_style))
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph("Scores", heading_style))
    data = [
        ["Categorie", "Score", "Evaluation"],
        ["Score Global", f"{result['global_score']}/100", get_score_label(result['global_score'])[0]],
        ["SEO", f"{result['seo']['score']}/100", get_score_label(result['seo']['score'])[0]],
        ["UX", f"{result['ux']['score']}/100", get_score_label(result['ux']['score'])[0]],
        ["Contenu", f"{result['content']['score']}/100", get_score_label(result['content']['score'])[0]],
        ["Design", f"{result['design']['score']}/100", get_score_label(result['design']['score'])[0]],
        ["Performance", f"{result['performance']['score']}/100", get_score_label(result['performance']['score'])[0]],
    ]
    table = Table(data, colWidths=[6*cm, 4*cm, 5*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#f7f7f7'), colors.white]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dddddd')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph(f"Problemes detectes ({result['total_issues']})", heading_style))
    cats = {}
    for item in result['all_issues']:
        cats.setdefault(item['category'], []).append(item['message'])
    for cat, msgs in cats.items():
        story.append(Paragraph(f"<b>{cat}</b>", normal_style))
        for msg in msgs:
            story.append(Paragraph(f"- {msg}", normal_style))
        story.append(Spacer(1, 0.2*cm))

    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("Rapport genere par Sitra — Analyseur Intelligent de Sites Web",
                           ParagraphStyle('footer', fontSize=8, textColor=colors.HexColor('#aaaaaa'))))
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


# ── CONFIG ────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Sitra | Analyseur de Sites Web", page_icon="S", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.main .block-container { padding-top: 2rem; padding-bottom: 4rem; max-width: 1200px; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0a0a0a 0%, #1a1a2e 100%); }
[data-testid="stSidebar"] * { color: #e0e0e0 !important; }
.hero-header { background: linear-gradient(135deg, #0f0f1a 0%, #1a1a3e 50%, #0f0f1a 100%); border: 1px solid #2a2a5e; border-radius: 16px; padding: 2.5rem 3rem; margin-bottom: 2rem; text-align: center; }
.hero-title { font-size: 3.5rem; font-weight: 800; background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin: 0; letter-spacing: -1px; }
.hero-subtitle { color: #888; font-size: 1rem; margin-top: 0.5rem; letter-spacing: 2px; text-transform: uppercase; }
.metric-card { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); border: 1px solid #2a2a4e; border-radius: 12px; padding: 1.2rem 1.5rem; text-align: center; }
.metric-value { font-size: 1.8rem; font-weight: 700; }
.metric-label { font-size: 0.75rem; color: #888; text-transform: uppercase; letter-spacing: 1px; margin-top: 0.2rem; }
.issue-item { padding: 0.6rem 1rem; border-radius: 8px; margin: 0.4rem 0; font-size: 0.9rem; line-height: 1.5; border-left: 3px solid; }
.issue-critical { background: rgba(220,53,69,0.1); border-left-color: #dc3545; }
.issue-warning { background: rgba(255,193,7,0.08); border-left-color: #ffc107; }
.issue-ok { background: rgba(40,167,69,0.1); border-left-color: #28a745; }
.score-bar-container { margin: 0.5rem 0; }
.score-bar-label { display: flex; justify-content: space-between; font-size: 0.85rem; color: #ccc; margin-bottom: 0.3rem; }
.score-bar-bg { background: #2a2a3e; border-radius: 999px; height: 8px; overflow: hidden; }
.score-bar-fill { height: 100%; border-radius: 999px; }
.stButton > button { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 10px; font-weight: 600; font-size: 1rem; padding: 0.7rem 2rem; width: 100%; }
.stTabs [data-baseweb="tab-list"] { background: #0f0f1a; border-radius: 10px; padding: 4px; gap: 8px; }
.stTabs [data-baseweb="tab"] { background: #1a1a2e; color: #888; border-radius: 8px; font-weight: 500; padding: 0.4rem 1rem; }
.stTabs [aria-selected="true"] { background: linear-gradient(135deg, #667eea, #764ba2) !important; color: white !important; }
input[type="checkbox"] { accent-color: #667eea !important; }
</style>
""", unsafe_allow_html=True)


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
        st.markdown('<div class="issue-item issue-ok">Aucun problème détecté dans cette catégorie.</div>', unsafe_allow_html=True)
    else:
        for issue in issues:
            css_class = "issue-critical" if issue.startswith("[X]") or "pas de" in issue.lower() else "issue-warning"
            st.markdown(f'<div class="issue-item {css_class}">{issue}</div>', unsafe_allow_html=True)


# ── RENDER RESULT ─────────────────────────────────────────────────────────────
def render_result(result, idx=0):
    if result.get("error"):
        st.warning("Impossible d'analyser ce site. Certains grands sites bloquent volontairement les outils d'analyse automatiques. Sitra est conçu pour les sites de PME, artisans, restaurants et portfolios.")
        return

    label_txt, _, label_color = get_score_label(result["global_score"])
    st.divider()
    st.markdown(f"### {result['final_url']}")

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

    st.markdown("")
    with st.expander("Analyse IA — Recommandations personnalisées"):
        with st.spinner("L'IA analyse votre site..."):
            recommandations = generer_recommandations_ia(result)
        if recommandations:
            st.markdown(recommandations)
        else:
            st.warning("Impossible de générer les recommandations IA pour le moment.")

    tabs = st.tabs(["SEO", "UX", "Contenu", "Design", "Performance", "PageSpeed", "Concurrents", "Récapitulatif", "Challenge", "Partager"])

    with tabs[0]:
        seo = result["seo"]
        render_score_bar("SEO et Référencement", seo["score"])
        st.markdown("")
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.markdown("**Données détectées**")
            title_display = seo['title'][:60] + '...' if len(seo['title']) > 60 else seo['title'] or '(manquant)'
            st.markdown(f"- **Titre** : `{title_display}` ({len(seo['title'])} chars)")
            st.markdown(f"- **Meta description** : {len(seo['meta_description'])} chars")
            st.markdown(f"- **H1** : {seo['h1_count']} {'(correct)' if seo['h1_count'] == 1 else '(à corriger)'}")
            st.markdown(f"- **H2** : {seo['h2_count']} {'(correct)' if seo['h2_count'] > 0 else '(manquant)'}")
            st.markdown(f"- **Images sans alt** : {seo['images_no_alt']}/{seo['images_total']}")
        with col_s2:
            st.markdown("**Points à corriger**")
            render_issues(seo["issues"])

    with tabs[1]:
        ux = result["ux"]
        render_score_bar("Expérience Utilisateur", ux["score"])
        st.markdown("")
        col_u1, col_u2 = st.columns(2)
        with col_u1:
            st.markdown("**Données détectées**")
            st.markdown(f"- **Navigation** : {'Présente' if ux['has_nav'] else 'Absente'} ({ux['nav_links_count']} liens)")
            st.markdown(f"- **Boutons CTA** : {ux['buttons_count']} {'(correct)' if ux['buttons_count'] > 0 else '(manquant)'}")
            st.markdown(f"- **Contact** : {'Trouvé' if ux['has_contact'] else 'Absent'}")
            st.markdown(f"- **Footer** : {'Présent' if ux['has_footer'] else 'Absent'}")
        with col_u2:
            st.markdown("**Points à corriger**")
            render_issues(ux["issues"])

    with tabs[2]:
        content = result["content"]
        render_score_bar("Qualité du Contenu", content["score"])
        st.markdown("")
        st.markdown(f"**Mots détectés** : {content['word_count']} {'(correct)' if content['word_count'] >= 300 else '(visez 300+)'}")
        render_issues(content["issues"])

    with tabs[3]:
        design = result["design"]
        render_score_bar("Design et Branding", design["score"])
        st.markdown("")
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.markdown("**Données détectées**")
            st.markdown(f"- **Favicon** : {'Présent' if design['has_favicon'] else 'Absent'}")
            st.markdown(f"- **Google Fonts** : {'Oui' if design['has_google_fonts'] else 'Non détecté'}")
            st.markdown(f"- **Open Graph** : {'Présent' if design['has_og_tags'] else 'Absent'}")
        with col_d2:
            st.markdown("**Points à corriger**")
            render_issues(design["issues"])

    with tabs[4]:
        perf = result["performance"]
        render_score_bar("Performance", perf["score"])
        st.markdown("")
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.markdown("**Données mesurées**")
            rt = perf['response_time']
            rt_label = "Excellent" if rt and rt < 1 else ("Moyen" if rt and rt < 2 else "Lent")
            st.markdown(f"- **HTTPS** : {'Actif' if perf['is_https'] else 'Inactif'}")
            st.markdown(f"- **Temps de réponse** : {rt}s ({rt_label})")
            st.markdown(f"- **Taille HTML** : {perf['html_size_kb']} KB")
        with col_p2:
            st.markdown("**Points à corriger**")
            render_issues(perf["issues"])

    with tabs[5]:
        st.markdown("### Analyse Google PageSpeed")
        st.caption("Métriques officielles Google — même outil que les professionnels du web")
        url_pagespeed = f"https://pagespeed.web.dev/report?url={result['final_url']}"
        st.markdown(f"""
        <div style="background:#1a1a2e;border:1px solid #2a2a4e;border-radius:12px;padding:2rem;text-align:center;margin-top:1rem">
            <p style="color:#ccc;font-size:1rem;margin-bottom:1.5rem">Cliquez sur le bouton ci-dessous pour voir l'analyse Google PageSpeed complète. Les résultats s'ouvriront dans un nouvel onglet.</p>
            <a href="{url_pagespeed}" target="_blank" style="background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:0.8rem 2rem;border-radius:10px;text-decoration:none;font-weight:600;font-size:1rem">
                Voir l'analyse PageSpeed
            </a>
        </div>
        """, unsafe_allow_html=True)

    with tabs[6]:
        st.markdown("### Analyse Concurrentielle")
        st.caption("Sitra détecte automatiquement votre secteur et compare votre site aux références du marché")

        # Détection secteur
        html = result.get("html", "")
        if not html:
            fetch_data = __import__("analyzer").fetch_site(result["final_url"])
            html = fetch_data.get("html", "")

        concurrence = detect_secteur_et_concurrents(result["final_url"], html or "")
        secteur = concurrence["secteur"]
        concurrents = concurrence["concurrents"]

        st.info(f"**Secteur détecté automatiquement : {secteur}**")

        if concurrents:
            st.markdown("**Comparaison avec les références du secteur :**")
            import pandas as pd
            tableau = []
            for concurrent_url in concurrents:
                with st.spinner(f"Analyse de {concurrent_url}..."):
                    c_result = full_analysis(concurrent_url)
                if not c_result.get("error"):
                    label_txt, _, _ = get_score_label(c_result["global_score"])
                    diff = result["global_score"] - c_result["global_score"]
                    diff_txt = f"+{diff}" if diff > 0 else str(diff)
                    tableau.append({
                        "Site": c_result["final_url"],
                        "Score": f"{c_result['global_score']}/100",
                        "SEO": f"{c_result['seo']['score']}/100",
                        "UX": f"{c_result['ux']['score']}/100",
                        "Performance": f"{c_result['performance']['score']}/100",
                        "Vs votre site": diff_txt,
                    })

            # Ajoute votre site en premier
            label_vous, _, _ = get_score_label(result["global_score"])
            tableau.insert(0, {
                "Site": f"⭐ {result['final_url']} (vous)",
                "Score": f"{result['global_score']}/100",
                "SEO": f"{result['seo']['score']}/100",
                "UX": f"{result['ux']['score']}/100",
                "Performance": f"{result['performance']['score']}/100",
                "Vs votre site": "—",
            })

            if tableau:
                df = pd.DataFrame(tableau)
                st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Aucun concurrent de référence trouvé pour ce secteur.")

    with tabs[7]:
        st.markdown(f"### Score global : **{result['global_score']}/100** — {label_txt}")
        render_score_bar("SEO", result["seo"]["score"])
        render_score_bar("UX", result["ux"]["score"])
        render_score_bar("Contenu", result["content"]["score"])
        render_score_bar("Design", result["design"]["score"])
        render_score_bar("Performance", result["performance"]["score"])
        st.divider()
        st.markdown(f"**{result['total_issues']} problèmes détectés :**")
        cats = {}
        for item in result["all_issues"]:
            cats.setdefault(item["category"], []).append(item["message"])
        for cat, msgs in cats.items():
            with st.expander(f"{cat} — {len(msgs)} problème(s)"):
                render_issues(msgs)
        st.divider()
        try:
            pdf_data = generer_pdf(result)
            st.download_button(
                label="Télécharger le rapport PDF",
                data=pdf_data,
                file_name=f"sitra_rapport_{idx}.pdf",
                mime="application/pdf",
                key=f"download_{idx}"
            )
        except Exception:
            st.caption("Export PDF indisponible pour le moment.")

    with tabs[8]:
        st.caption("Cochez les objectifs au fur et à mesure que vous les complétez")
        seo = result["seo"]
        ux = result["ux"]
        challenge_items = []
        if not seo["title"]:
            challenge_items.append("Ajouter une balise title sur toutes les pages")
        elif len(seo["title"]) < 10 or len(seo["title"]) > 70:
            challenge_items.append(f"Optimiser le titre ({len(seo['title'])} chars) — viser 50-60 caractères")
        if not seo["meta_description"]:
            challenge_items.append("Écrire une meta description de 120-160 caractères")
        if seo["h1_count"] != 1:
            challenge_items.append(f"Corriger les balises H1 (vous en avez {seo['h1_count']}, il en faut 1)")
        if seo["images_no_alt"] > 0:
            challenge_items.append(f"Ajouter un attribut alt à {seo['images_no_alt']} image(s)")
        if not ux["has_contact"]:
            challenge_items.append("Ajouter des informations de contact visibles")
        if not result["performance"]["is_https"]:
            challenge_items.append("Activer le HTTPS sur votre hébergeur")
        if not ux["has_footer"]:
            challenge_items.append("Créer un footer avec mentions légales et contact")
        if not result["design"]["has_og_tags"]:
            challenge_items.append("Ajouter les balises Open Graph pour les réseaux sociaux")
        if result["content"]["word_count"] < 300:
            challenge_items.append(f"Enrichir le contenu ({result['content']['word_count']} mots — visez 300+)")
        generals = [
            "Tester le site sur mobile et tablette",
            "Vérifier la vitesse avec Google PageSpeed Insights",
            "Créer une page FAQ",
            "Ajouter des avis clients ou témoignages",
            "Vérifier l'orthographe sur toutes les pages",
        ]
        while len(challenge_items) < 5 and generals:
            challenge_items.append(generals.pop(0))
        total = len(challenge_items)
        completed = 0
        for i, obj in enumerate(challenge_items):
            key = f"ch_{idx}_{i}"
            if key not in st.session_state:
                st.session_state[key] = False
            if st.checkbox(obj, key=key):
                completed += 1
        st.markdown("")
        if total > 0:
            st.progress(completed / total)
            st.caption(f"**{completed}/{total}** objectifs complétés {'— Bravo, site optimisé !' if completed == total else ''}")

    with tabs[9]:
        st.markdown("### Partager mes résultats")
        st.caption("Partagez votre score et faites découvrir Sitra autour de vous")
        score = result["global_score"]
        url_site = result["final_url"]
        texte_partage = f"J'ai analysé {url_site} avec Sitra et obtenu un score de {score}/100 ! Analysez votre site gratuitement sur https://mon-audit-seo.streamlit.app"
        lien_twitter = f"https://twitter.com/intent/tweet?text={texte_partage}"
        lien_linkedin = f"https://www.linkedin.com/sharing/share-offsite/?url=https://mon-audit-seo.streamlit.app"
        lien_facebook = f"https://www.facebook.com/sharer/sharer.php?u=https://mon-audit-seo.streamlit.app&quote={texte_partage}"
        lien_whatsapp = f"https://wa.me/?text={texte_partage}"
        st.markdown("")
        col_sh1, col_sh2, col_sh3, col_sh4 = st.columns(4)
        with col_sh1:
            st.markdown(f'''<a href="{lien_twitter}" target="_blank" style="display:block;text-align:center;background:#1a1a2e;border:1px solid #2a2a4e;border-radius:10px;padding:0.8rem 1rem;color:#1DA1F2;text-decoration:none;font-weight:600;font-size:0.9rem">X (Twitter)</a>''', unsafe_allow_html=True)
        with col_sh2:
            st.markdown(f'''<a href="{lien_linkedin}" target="_blank" style="display:block;text-align:center;background:#1a1a2e;border:1px solid #2a2a4e;border-radius:10px;padding:0.8rem 1rem;color:#0A66C2;text-decoration:none;font-weight:600;font-size:0.9rem">LinkedIn</a>''', unsafe_allow_html=True)
        with col_sh3:
            st.markdown(f'''<a href="{lien_facebook}" target="_blank" style="display:block;text-align:center;background:#1a1a2e;border:1px solid #2a2a4e;border-radius:10px;padding:0.8rem 1rem;color:#1877F2;text-decoration:none;font-weight:600;font-size:0.9rem">Facebook</a>''', unsafe_allow_html=True)
        with col_sh4:
            st.markdown(f'''<a href="{lien_whatsapp}" target="_blank" style="display:block;text-align:center;background:#1a1a2e;border:1px solid #2a2a4e;border-radius:10px;padding:0.8rem 1rem;color:#25D366;text-decoration:none;font-weight:600;font-size:0.9rem">WhatsApp</a>''', unsafe_allow_html=True)
        st.markdown("")
        st.markdown("**Pour Instagram et TikTok** — copiez ce texte et collez-le dans votre post :")
        st.code(texte_partage, language=None)


# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Centre de contrôle")
    st.divider()
    mode_comparaison = st.checkbox("Mode comparatif", key="compare_mode", help="Analysez deux sites en parallèle")
    mode_multipages = st.checkbox("Analyser toutes les pages", key="multipages", help="Détecte et analyse les pages principales automatiquement")
    st.divider()
    st.markdown('<div style="color:#666;font-size:0.75rem;text-align:center">Sitra Engine v1.0<br>Analyse en temps réel</div>', unsafe_allow_html=True)


# ── HERO ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-header">
    <div class="hero-title">SITRA</div>
    <div class="hero-subtitle">Analyseur Intelligent de Sites Web &bull; Données Réelles &bull; Recommandations Précises</div>
</div>
""", unsafe_allow_html=True)


# ── INPUT ─────────────────────────────────────────────────────────────────────
if mode_comparaison:
    col_in1, col_in2 = st.columns(2)
    with col_in1:
        url1 = st.text_input("Votre site :", placeholder="ex : monsite.fr", key="url1")
    with col_in2:
        url2 = st.text_input("Site concurrent :", placeholder="ex : concurrent.fr", key="url2")
else:
    url1 = st.text_input("Votre site :", placeholder="ex : monsite.fr ou https://monsite.fr", key="url1")
    url2 = ""

col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    launch = st.button("Lancer l'analyse", use_container_width=True)


# ── ANALYSE ───────────────────────────────────────────────────────────────────
if launch:
    urls_to_analyze = [u for u in [url1, url2] if u and u.strip()]
    if not urls_to_analyze:
        st.warning("Merci d'entrer une URL valide.")
    else:
        results_list = []
        for url in urls_to_analyze:
            with st.spinner(f"Analyse de {url} en cours..."):
                result = full_analysis(url)
            results_list.append(result)
        st.session_state["results"] = results_list
        st.session_state["mode_comp"] = mode_comparaison

        # Analyse multi-pages automatique
        if mode_multipages and not mode_comparaison and url1.strip():
            with st.spinner("Détection des pages du site en cours..."):
                pages_detectees = detect_pages(normalize_url(url1))
            if pages_detectees:
                st.divider()
                st.markdown("## Pages analysées automatiquement")
                import pandas as pd
                tableau = []
                for page_url in pages_detectees:
                    with st.spinner(f"Analyse de {page_url}..."):
                        page_result = full_analysis(page_url)
                    if not page_result.get("error"):
                        label_txt, _, _ = get_score_label(page_result["global_score"])
                        tableau.append({
                            "Page": page_result["final_url"],
                            "Score Global": f"{page_result['global_score']}/100",
                            "SEO": f"{page_result['seo']['score']}/100",
                            "UX": f"{page_result['ux']['score']}/100",
                            "Design": f"{page_result['design']['score']}/100",
                            "Performance": f"{page_result['performance']['score']}/100",
                            "Niveau": label_txt,
                        })
                if tableau:
                    df = pd.DataFrame(tableau)
                    st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("Aucune page supplémentaire détectée dans la navigation du site.")

if "results" in st.session_state:
    results_list = st.session_state["results"]
    mode_comp = st.session_state.get("mode_comp", False)
    if mode_comp and len(results_list) == 2:
        st.divider()
        st.markdown("## Comparatif")
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            render_result(results_list[0], idx=0)
        with col_r2:
            render_result(results_list[1], idx=1)
    else:
        render_result(results_list[0], idx=0)
else:
    st.markdown("""
    <div style="text-align:center;color:#444;margin-top:3rem;font-size:0.85rem">
        <p><strong>Sitra</strong> analyse réellement votre site — pas de données aléatoires</p>
        <p>SEO — UX — Contenu — Design — Performance — 20 critères vérifiés</p>
    </div>
    """, unsafe_allow_html=True)
