import streamlit as st
import time
from analyzer import full_analysis, get_score_label, normalize_url

st.set_page_config(
    page_title="Sitra | Analyseur de Sites Web",
    page_icon="S",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.main .block-container { padding-top: 2rem; padding-bottom: 4rem; max-width: 1200px; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0a0a0a 0%, #1a1a2e 100%); }
[data-testid="stSidebar"] * { color: #e0e0e0 !important; }
.hero-header {
    background: linear-gradient(135deg, #0f0f1a 0%, #1a1a3e 50%, #0f0f1a 100%);
    border: 1px solid #2a2a5e; border-radius: 16px;
    padding: 2.5rem 3rem; margin-bottom: 2rem; text-align: center;
}
.hero-title {
    font-size: 3.5rem; font-weight: 800;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; margin: 0; letter-spacing: -1px;
}
.hero-subtitle { color: #888; font-size: 1rem; margin-top: 0.5rem; letter-spacing: 2px; text-transform: uppercase; }
.metric-card {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    border: 1px solid #2a2a4e; border-radius: 12px;
    padding: 1.2rem 1.5rem; text-align: center;
}
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
.stButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white; border: none; border-radius: 10px;
    font-weight: 600; font-size: 1rem; padding: 0.7rem 2rem; width: 100%;
}
.stTabs [data-baseweb="tab-list"] { background: #0f0f1a; border-radius: 10px; padding: 4px; gap: 4px; }
.stTabs [data-baseweb="tab"] { background: transparent; color: #888; border-radius: 8px; font-weight: 500; }
.stTabs [aria-selected="true"] { background: linear-gradient(135deg, #667eea, #764ba2) !important; color: white !important; }
</style>
""", unsafe_allow_html=True)


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
        st.markdown('<div class="issue-item issue-ok">Aucun probleme detecte dans cette categorie.</div>', unsafe_allow_html=True)
    else:
        for issue in issues:
            css_class = "issue-critical" if issue.startswith("[X]") or "pas de" in issue.lower() else "issue-warning"
            st.markdown(f'<div class="issue-item {css_class}">{issue}</div>', unsafe_allow_html=True)


def build_export_report(result):
    lines = [
        "=" * 60,
        "RAPPORT D'ANALYSE SITRA",
        f"Site analyse : {result['url']}",
        f"Date : {time.strftime('%d/%m/%Y a %H:%M')}",
        "=" * 60,
        f"\nSCORE GLOBAL : {result['global_score']}/100",
        f"HTTPS : {'Oui' if result['is_https'] else 'Non'}",
        f"Temps de reponse : {result['response_time']}s",
        "\nSCORES PAR CATEGORIE :",
        f"  SEO : {result['seo']['score']}/100",
        f"  UX : {result['ux']['score']}/100",
        f"  Contenu : {result['content']['score']}/100",
        f"  Design : {result['design']['score']}/100",
        f"  Performance : {result['performance']['score']}/100",
        f"\nPROBLEMES DETECTES ({result['total_issues']}) :",
    ]
    for item in result['all_issues']:
        lines.append(f"  [{item['category']}] {item['message']}")
    lines.append("\n" + "=" * 60)
    lines.append("Rapport genere par Sitra")
    return "\n".join(lines)


def render_result(result, idx=0):
    if result.get("error") and not result.get("global_score"):
        st.error(f"Erreur — {result['url']} : {result['error']}")
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
    tabs = st.tabs(["SEO", "UX", "Contenu", "Design", "Performance", "Recapitulatif", "Challenge"])

    with tabs[0]:
        seo = result["seo"]
        render_score_bar("SEO et Referencement", seo["score"])
        st.markdown("")
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.markdown("**Donnees detectees**")
            title_display = seo['title'][:60] + '...' if len(seo['title']) > 60 else seo['title'] or '(manquant)'
            st.markdown(f"- **Titre** : `{title_display}` ({len(seo['title'])} chars)")
            st.markdown(f"- **Meta description** : {len(seo['meta_description'])} chars")
            st.markdown(f"- **H1** : {seo['h1_count']} {'(correct)' if seo['h1_count'] == 1 else '(a corriger)'}")
            st.markdown(f"- **H2** : {seo['h2_count']} {'(correct)' if seo['h2_count'] > 0 else '(manquant)'}")
            st.markdown(f"- **Images sans alt** : {seo['images_no_alt']}/{seo['images_total']}")
        with col_s2:
            st.markdown("**Points a corriger**")
            render_issues(seo["issues"])

    with tabs[1]:
        ux = result["ux"]
        render_score_bar("Experience Utilisateur", ux["score"])
        st.markdown("")
        col_u1, col_u2 = st.columns(2)
        with col_u1:
            st.markdown("**Donnees detectees**")
            st.markdown(f"- **Navigation** : {'Presente' if ux['has_nav'] else 'Absente'} ({ux['nav_links_count']} liens)")
            st.markdown(f"- **Boutons CTA** : {ux['buttons_count']} {'(correct)' if ux['buttons_count'] > 0 else '(manquant)'}")
            st.markdown(f"- **Contact** : {'Trouve' if ux['has_contact'] else 'Absent'}")
            st.markdown(f"- **Footer** : {'Present' if ux['has_footer'] else 'Absent'}")
        with col_u2:
            st.markdown("**Points a corriger**")
            render_issues(ux["issues"])

    with tabs[2]:
        content = result["content"]
        render_score_bar("Qualite du Contenu", content["score"])
        st.markdown("")
        st.markdown(f"**Mots detectes** : {content['word_count']} {'(correct)' if content['word_count'] >= 300 else '(vise 300+)'}")
        render_issues(content["issues"])

    with tabs[3]:
        design = result["design"]
        render_score_bar("Design et Branding", design["score"])
        st.markdown("")
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.markdown("**Donnees detectees**")
            st.markdown(f"- **Favicon** : {'Present' if design['has_favicon'] else 'Absent'}")
            st.markdown(f"- **Google Fonts** : {'Oui' if design['has_google_fonts'] else 'Non detecte'}")
            st.markdown(f"- **Open Graph** : {'Present' if design['has_og_tags'] else 'Absent'}")
        with col_d2:
            st.markdown("**Points a corriger**")
            render_issues(design["issues"])

    with tabs[4]:
        perf = result["performance"]
        render_score_bar("Performance", perf["score"])
        st.markdown("")
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.markdown("**Donnees mesurees**")
            rt = perf['response_time']
            rt_label = "Excellent" if rt and rt < 1 else ("Moyen" if rt and rt < 2 else "Lent")
            st.markdown(f"- **HTTPS** : {'Actif' if perf['is_https'] else 'Inactif'}")
            st.markdown(f"- **Temps de reponse** : {rt}s ({rt_label})")
            st.markdown(f"- **Taille HTML** : {perf['html_size_kb']} KB")
        with col_p2:
            st.markdown("**Points a corriger**")
            render_issues(perf["issues"])

    with tabs[5]:
        st.markdown(f"### Score global : **{result['global_score']}/100** — {label_txt}")
        render_score_bar("SEO", result["seo"]["score"])
        render_score_bar("UX", result["ux"]["score"])
        render_score_bar("Contenu", result["content"]["score"])
        render_score_bar("Design", result["design"]["score"])
        render_score_bar("Performance", result["performance"]["score"])
        st.divider()
        st.markdown(f"**{result['total_issues']} problemes detectes :**")
        cats = {}
        for item in result["all_issues"]:
            cats.setdefault(item["category"], []).append(item["message"])
        for cat, msgs in cats.items():
            with st.expander(f"{cat} — {len(msgs)} probleme(s)"):
                render_issues(msgs)
        st.divider()
        report_txt = build_export_report(result)
        st.download_button(
            label="Telecharger le rapport (.txt)",
            data=report_txt,
            file_name=f"sitra_rapport_{idx}.txt",
            mime="text/plain",
            key=f"download_{idx}"
        )

    with tabs[6]:
        st.markdown("### Mode Challenge")
        st.caption("Coche les objectifs au fur et a mesure que tu les completes")

        seo = result["seo"]
        ux = result["ux"]
        challenge_items = []

        if not seo["title"]:
            challenge_items.append("Ajouter une balise title sur toutes les pages")
        elif len(seo["title"]) < 10 or len(seo["title"]) > 70:
            challenge_items.append(f"Optimiser le titre ({len(seo['title'])} chars) — viser 50-60 caracteres")
        if not seo["meta_description"]:
            challenge_items.append("Ecrire une meta description de 120-160 caracteres")
        if seo["h1_count"] != 1:
            challenge_items.append(f"Corriger les balises H1 (tu en as {seo['h1_count']}, il en faut 1)")
        if seo["images_no_alt"] > 0:
            challenge_items.append(f"Ajouter un attribut alt a {seo['images_no_alt']} image(s)")
        if not ux["has_contact"]:
            challenge_items.append("Ajouter des informations de contact visibles")
        if not result["performance"]["is_https"]:
            challenge_items.append("Activer le HTTPS sur ton hebergeur")
        if not ux["has_footer"]:
            challenge_items.append("Creer un footer avec mentions legales et contact")
        if not result["design"]["has_og_tags"]:
            challenge_items.append("Ajouter les balises Open Graph pour les reseaux sociaux")
        if result["content"]["word_count"] < 300:
            challenge_items.append(f"Enrichir le contenu ({result['content']['word_count']} mots — vise 300+)")

        generals = [
            "Tester le site sur mobile et tablette",
            "Verifier la vitesse avec Google PageSpeed Insights",
            "Creer une page FAQ",
            "Ajouter des avis clients ou temoignages",
            "Verifier l'orthographe sur toutes les pages",
        ]
        while len(challenge_items) < 5 and generals:
            challenge_items.append(generals.pop(0))

        total = len(challenge_items)
        completed = sum(1 for i, obj in enumerate(challenge_items) if st.checkbox(obj, key=f"ch_{idx}_{i}"))

        st.markdown("")
        if total > 0:
            st.progress(completed / total)
            st.caption(f"**{completed}/{total}** objectifs completes {'— Bravo, site optimise !' if completed == total else ''}")


# Sidebar
with st.sidebar:
    st.markdown("### Centre de controle")
    st.divider()
    mode_comparaison = st.checkbox("Mode comparatif", key="compare_mode",
                                   help="Analyse deux sites en parallele")
    st.divider()
    st.markdown('<div style="color:#666;font-size:0.75rem;text-align:center">Sitra Engine v1.0<br>Analyse en temps reel</div>', unsafe_allow_html=True)


# Hero
st.markdown("""
<div class="hero-header">
    <div class="hero-title">SITRA</div>
    <div class="hero-subtitle">Analyseur Intelligent de Sites Web &bull; Donnees Reelles &bull; Recommandations Precises</div>
</div>
""", unsafe_allow_html=True)


# Input
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


# Analyse
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

        if mode_comparaison and len(results_list) == 2:
            st.divider()
            st.markdown("## Comparatif")
            col_r1, col_r2 = st.columns(2)
            with col_r1:
                render_result(results_list[0], idx=0)
            with col_r2:
                render_result(results_list[1], idx=1)
        else:
            render_result(results_list[0], idx=0)

if not launch:
    st.markdown("""
    <div style="text-align:center;color:#444;margin-top:3rem;font-size:0.85rem">
        <p><strong>Sitra</strong> analyse reellement votre site — pas de donnees aleatoires</p>
        <p>SEO — UX — Contenu — Design — Performance — 20 criteres verifies</p>
    </div>
    """, unsafe_allow_html=True)
