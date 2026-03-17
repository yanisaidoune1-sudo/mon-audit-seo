import streamlit as st
import time
import json
from analyzer import full_analysis, get_score_label, normalize_url

# ── CONFIGURATION ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Sitra | Analyseur de Sites Web",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Fonts & Base ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ── Fond principal ── */
.main .block-container {
    padding-top: 2rem;
    padding-bottom: 4rem;
    max-width: 1200px;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a0a0a 0%, #1a1a2e 100%);
    border-right: 1px solid #2a2a3e;
}
[data-testid="stSidebar"] * {
    color: #e0e0e0 !important;
}
[data-testid="stSidebar"] .stCheckbox label {
    color: #ffffff !important;
    font-weight: 500;
}
[data-testid="stSidebar"] .stDivider { border-color: #2a2a3e !important; }

/* ── Hero Header ── */
.hero-header {
    background: linear-gradient(135deg, #0f0f1a 0%, #1a1a3e 50%, #0f0f1a 100%);
    border: 1px solid #2a2a5e;
    border-radius: 16px;
    padding: 2.5rem 3rem;
    margin-bottom: 2rem;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.hero-header::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(ellipse at center, rgba(100,100,255,0.08) 0%, transparent 60%);
    pointer-events: none;
}
.hero-title {
    font-size: 3.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
    letter-spacing: -1px;
}
.hero-subtitle {
    color: #888;
    font-size: 1rem;
    margin-top: 0.5rem;
    letter-spacing: 2px;
    text-transform: uppercase;
}

/* ── Score Card ── */
.score-ring-container {
    text-align: center;
    padding: 1.5rem;
}
.score-big {
    font-size: 4rem;
    font-weight: 800;
    line-height: 1;
}
.score-label-txt {
    font-size: 1rem;
    font-weight: 600;
    margin-top: 0.3rem;
    letter-spacing: 1px;
    text-transform: uppercase;
}

/* ── Cards métriques ── */
.metric-card {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    border: 1px solid #2a2a4e;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    text-align: center;
    transition: transform 0.2s, border-color 0.2s;
}
.metric-card:hover {
    transform: translateY(-2px);
    border-color: #667eea;
}
.metric-value {
    font-size: 1.8rem;
    font-weight: 700;
    color: #667eea;
}
.metric-label {
    font-size: 0.75rem;
    color: #888;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 0.2rem;
}

/* ── Issue items ── */
.issue-item {
    padding: 0.6rem 1rem;
    border-radius: 8px;
    margin: 0.4rem 0;
    font-size: 0.9rem;
    line-height: 1.5;
    border-left: 3px solid;
}
.issue-critical {
    background: rgba(220,53,69,0.1);
    border-left-color: #dc3545;
}
.issue-warning {
    background: rgba(255,193,7,0.08);
    border-left-color: #ffc107;
}
.issue-ok {
    background: rgba(40,167,69,0.1);
    border-left-color: #28a745;
}

/* ── Section headers ── */
.section-header {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin: 1.5rem 0 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #2a2a4e;
}
.section-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #e0e0e0;
    margin: 0;
}

/* ── Score bar ── */
.score-bar-container {
    margin: 0.5rem 0;
}
.score-bar-label {
    display: flex;
    justify-content: space-between;
    font-size: 0.85rem;
    color: #ccc;
    margin-bottom: 0.3rem;
}
.score-bar-bg {
    background: #2a2a3e;
    border-radius: 999px;
    height: 8px;
    overflow: hidden;
}
.score-bar-fill {
    height: 100%;
    border-radius: 999px;
    transition: width 0.8s ease;
}

/* ── Challenge checkboxes ── */
.challenge-item {
    background: #1a1a2e;
    border: 1px solid #2a2a4e;
    border-radius: 10px;
    padding: 0.8rem 1.2rem;
    margin: 0.5rem 0;
}

/* ── Input field ── */
.stTextInput > div > div > input {
    background: #1a1a2e;
    border: 2px solid #2a2a5e;
    border-radius: 10px;
    color: #fff;
    font-size: 1rem;
    padding: 0.8rem 1rem;
    transition: border-color 0.2s;
}
.stTextInput > div > div > input:focus {
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102,126,234,0.15);
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 10px;
    font-weight: 600;
    font-size: 1rem;
    padding: 0.7rem 2rem;
    transition: all 0.2s;
    width: 100%;
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 8px 20px rgba(102,126,234,0.4);
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #0f0f1a;
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #888;
    border-radius: 8px;
    font-weight: 500;
    font-size: 0.9rem;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #667eea, #764ba2) !important;
    color: white !important;
}

/* ── Responsive ── */
@media (max-width: 768px) {
    .hero-title { font-size: 2rem; }
    .metric-value { font-size: 1.4rem; }
}
</style>
""", unsafe_allow_html=True)


# ── HELPERS ──────────────────────────────────────────────────────────────────

def render_score_bar(label: str, score: int, emoji: str = ""):
    label_txt, _, color = get_score_label(score)
    st.markdown(f"""
    <div class="score-bar-container">
        <div class="score-bar-label">
            <span>{emoji} {label}</span>
            <span style="color:{color};font-weight:700">{score}/100 — {label_txt}</span>
        </div>
        <div class="score-bar-bg">
            <div class="score-bar-fill" style="width:{score}%;background:{color}"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_issues(issues: list):
    if not issues:
        st.markdown('<div class="issue-item issue-ok">✅ Aucun problème détecté dans cette catégorie !</div>', unsafe_allow_html=True)
        return
    for issue in issues:
        css_class = "issue-critical" if "❌" in issue else "issue-warning"
        st.markdown(f'<div class="issue-item {css_class}">{issue}</div>', unsafe_allow_html=True)


def build_export_report(result: dict) -> str:
    lines = []
    lines.append("=" * 60)
    lines.append(f"RAPPORT D'ANALYSE SITRA")
    lines.append(f"Site analysé : {result['url']}")
    lines.append(f"Date : {time.strftime('%d/%m/%Y à %H:%M')}")
    lines.append("=" * 60)
    lines.append(f"\n📊 SCORE GLOBAL : {result['global_score']}/100")
    lines.append(f"🔒 HTTPS : {'✅ Oui' if result['is_https'] else '❌ Non'}")
    lines.append(f"⚡ Temps de réponse : {result['response_time']}s")
    lines.append(f"\n📈 SCORES PAR CATÉGORIE :")
    lines.append(f"  • SEO & Référencement : {result['seo']['score']}/100")
    lines.append(f"  • Expérience Utilisateur : {result['ux']['score']}/100")
    lines.append(f"  • Qualité du Contenu : {result['content']['score']}/100")
    lines.append(f"  • Design & Branding : {result['design']['score']}/100")
    lines.append(f"  • Performance : {result['performance']['score']}/100")
    lines.append(f"\n⚠️ PROBLÈMES DÉTECTÉS ({result['total_issues']}) :")
    for item in result['all_issues']:
        lines.append(f"  [{item['category']}] {item['message']}")
    lines.append("\n" + "=" * 60)
    lines.append("Rapport généré par Sitra — sitra.app")
    return "\n".join(lines)


# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🎛️ Centre de contrôle")
    st.divider()

    st.markdown("**Options d'analyse**")
    mode_comparaison = st.checkbox("⚡ Mode comparatif", key="compare_mode",
                                   help="Analyse deux sites en parallèle")
    if mode_comparaison:
        st.info("💳 Comparez votre site avec un concurrent")

    st.divider()
    st.markdown("**Catégories à analyser**")
    check_seo = st.checkbox("🔍 SEO & Référencement", value=True)
    check_ux = st.checkbox("🖱️ Expérience Utilisateur", value=True)
    check_content = st.checkbox("📝 Qualité du Contenu", value=True)
    check_design = st.checkbox("🎨 Design & Branding", value=True)
    check_perf = st.checkbox("⚡ Performance", value=True)

    st.divider()
    st.markdown("""
    <div style="color:#666;font-size:0.75rem;text-align:center">
    Sitra Engine v1.0<br>
    Analyse en temps réel • Données réelles
    </div>
    """, unsafe_allow_html=True)


# ── HERO ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-header">
    <div class="hero-title">SITRA</div>
    <div class="hero-subtitle">Analyseur Intelligent de Sites Web • Données Réelles • Recommandations Précises</div>
</div>
""", unsafe_allow_html=True)


# ── INPUT ─────────────────────────────────────────────────────────────────────
if mode_comparaison:
    col_in1, col_in2 = st.columns(2)
else:
    col_in1 = st.container()
    col_in2 = st.container()

with col_in1:
    url1 = st.text_input(
        "🌐 Votre site :",
        placeholder="ex : monsite.fr ou https://monsite.fr",
        key="url1"
    )

url2 = ""
if mode_comparaison:
    with col_in2:
        url2 = st.text_input(
            "🆚 Site concurrent :",
            placeholder="ex : concurrent.fr",
            key="url2"
        )

col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    launch = st.button("🚀 Lancer l'analyse", use_container_width=True)


# ── ANALYSE ───────────────────────────────────────────────────────────────────
if launch:
    urls_to_analyze = [url1]
    if mode_comparaison and url2:
        urls_to_analyze.append(url2)

    results_list = []

    for url in urls_to_analyze:
        if not url.strip():
            st.warning("⚠️ Merci d'entrer une URL valide.")
            continue

        with st.spinner(f"🔍 Analyse de **{url}** en cours — vérification de {20 if not mode_comparaison else 15} critères réels..."):
            result = full_analysis(url)

        results_list.append(result)

    # ── AFFICHAGE RÉSULTATS ────────────────────────────────────────────────────
    if mode_comparaison and len(results_list) == 2:
        st.divider()
        st.markdown("## 📊 Comparatif")
        comp_cols = st.columns(2)

    for idx, result in enumerate(results_list):
        # Colonne ou plein écran
        if mode_comparaison and len(results_list) == 2:
            ctx = comp_cols[idx]
        else:
            ctx = st

        with ctx:
            if result.get("error") and not result.get("global_score"):
                st.error(f"❌ **{result['url']}** — {result['error']}")
                continue

            label_txt, label_emoji, label_color = get_score_label(result["global_score"])

            st.divider()

            # ── Score global ──
            st.markdown(f"### 🌐 {result['final_url']}")

            c1, c2, c3, c4, c5 = st.columns(5)
            metrics = [
                (c1, result["global_score"], "Score Global", "🏆"),
                (c2, result["seo"]["score"], "SEO", "🔍"),
                (c3, result["ux"]["score"], "UX", "🖱️"),
                (c4, result["design"]["score"], "Design", "🎨"),
                (c5, result["performance"]["score"], "Perf.", "⚡"),
            ]
            for col, score, lbl, em in metrics:
                lbl_t, _, clr = get_score_label(score)
                with col:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value" style="color:{clr}">{score}</div>
                        <div class="metric-label">{em} {lbl}</div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("")

            # ── Tabs ──
            tab_names = []
            if check_seo: tab_names.append("🔍 SEO")
            if check_ux: tab_names.append("🖱️ UX")
            if check_content: tab_names.append("📝 Contenu")
            if check_design: tab_names.append("🎨 Design")
            if check_perf: tab_names.append("⚡ Performance")
            tab_names.append("📋 Récapitulatif")
            tab_names.append("🏆 Challenge")

            tabs = st.tabs(tab_names)
            tab_idx = 0

            # ── SEO ──
            if check_seo:
                with tabs[tab_idx]:
                    seo = result["seo"]
                    render_score_bar("SEO & Référencement", seo["score"], "🔍")
                    st.markdown("")

                    col_s1, col_s2 = st.columns(2)
                    with col_s1:
                        st.markdown("**📌 Données détectées**")
                        st.markdown(f"- **Titre** : `{seo['title'][:60] + '...' if len(seo['title']) > 60 else seo['title'] or '(manquant)'}` ({len(seo['title'])} chars)")
                        st.markdown(f"- **Meta description** : {len(seo['meta_description'])} chars {('✅' if 50 <= len(seo['meta_description']) <= 170 else '⚠️')}")
                        st.markdown(f"- **H1** : {seo['h1_count']} {'✅' if seo['h1_count'] == 1 else '⚠️'}")
                        st.markdown(f"- **H2** : {seo['h2_count']} {'✅' if seo['h2_count'] > 0 else '⚠️'}")
                        st.markdown(f"- **Images sans alt** : {seo['images_no_alt']}/{seo['images_total']} {'✅' if seo['images_no_alt'] == 0 else '❌'}")
                    with col_s2:
                        st.markdown("**🔧 Points à corriger**")
                        render_issues(seo["issues"])

                tab_idx += 1

            # ── UX ──
            if check_ux:
                with tabs[tab_idx]:
                    ux = result["ux"]
                    render_score_bar("Expérience Utilisateur", ux["score"], "🖱️")
                    st.markdown("")

                    col_u1, col_u2 = st.columns(2)
                    with col_u1:
                        st.markdown("**📌 Données détectées**")
                        st.markdown(f"- **Navigation** : {'✅ Présente' if ux['has_nav'] else '❌ Absente'} ({ux['nav_links_count']} liens)")
                        st.markdown(f"- **Boutons CTA** : {ux['buttons_count']} {'✅' if ux['buttons_count'] > 0 else '❌'}")
                        st.markdown(f"- **Infos contact** : {'✅ Trouvées' if ux['has_contact'] else '❌ Absentes'}")
                        st.markdown(f"- **Formulaires** : {ux['forms_count']}")
                        st.markdown(f"- **Footer** : {'✅ Présent' if ux['has_footer'] else '⚠️ Absent'}")
                        st.markdown(f"- **Paragraphes longs** : {ux['long_paragraphs']}")
                    with col_u2:
                        st.markdown("**🔧 Points à corriger**")
                        render_issues(ux["issues"])

                tab_idx += 1

            # ── CONTENU ──
            if check_content:
                with tabs[tab_idx]:
                    content = result["content"]
                    render_score_bar("Qualité du Contenu", content["score"], "📝")
                    st.markdown("")

                    st.markdown(f"**Nombre de mots détectés** : {content['word_count']} {'✅' if content['word_count'] >= 300 else '⚠️ (vise 300+)'}")
                    st.markdown("**🔧 Points à corriger**")
                    render_issues(content["issues"])

                tab_idx += 1

            # ── DESIGN ──
            if check_design:
                with tabs[tab_idx]:
                    design = result["design"]
                    render_score_bar("Design & Branding", design["score"], "🎨")
                    st.markdown("")

                    col_d1, col_d2 = st.columns(2)
                    with col_d1:
                        st.markdown("**📌 Données détectées**")
                        st.markdown(f"- **Favicon** : {'✅ Présent' if design['has_favicon'] else '⚠️ Absent'}")
                        st.markdown(f"- **Google Fonts** : {'✅ Oui' if design['has_google_fonts'] else 'Non détecté'}")
                        st.markdown(f"- **Balises Open Graph** : {'✅ Oui' if design['has_og_tags'] else '⚠️ Manquantes'}")
                        if design['detected_colors']:
                            st.markdown("- **Couleurs détectées** :")
                            cols_color = st.columns(len(design['detected_colors'][:5]))
                            for ci, color in enumerate(design['detected_colors'][:5]):
                                clr_val = f"#{color}" if not color.startswith('#') and not color.startswith('rgb') else color
                                cols_color[ci].markdown(f'<div style="width:40px;height:40px;background:{clr_val};border-radius:6px;border:1px solid #444"></div>', unsafe_allow_html=True)
                    with col_d2:
                        st.markdown("**🔧 Points à corriger**")
                        render_issues(design["issues"])

                tab_idx += 1

            # ── PERFORMANCE ──
            if check_perf:
                with tabs[tab_idx]:
                    perf = result["performance"]
                    render_score_bar("Performance", perf["score"], "⚡")
                    st.markdown("")

                    col_p1, col_p2 = st.columns(2)
                    with col_p1:
                        st.markdown("**📌 Données mesurées**")
                        rt = perf['response_time']
                        rt_emoji = "✅" if rt and rt < 1 else ("⚠️" if rt and rt < 2 else "❌")
                        st.markdown(f"- **HTTPS** : {'✅ Activé' if perf['is_https'] else '❌ Non sécurisé'}")
                        st.markdown(f"- **Temps de réponse** : {rt}s {rt_emoji}")
                        st.markdown(f"- **Taille HTML** : {perf['html_size_kb']} KB")
                    with col_p2:
                        st.markdown("**🔧 Points à corriger**")
                        render_issues(perf["issues"])

                tab_idx += 1

            # ── RÉCAPITULATIF ──
            with tabs[tab_idx]:
                st.markdown(f"### Score global : **{result['global_score']}/100** {label_emoji}")

                if check_seo: render_score_bar("SEO", result["seo"]["score"], "🔍")
                if check_ux: render_score_bar("UX", result["ux"]["score"], "🖱️")
                if check_content: render_score_bar("Contenu", result["content"]["score"], "📝")
                if check_design: render_score_bar("Design", result["design"]["score"], "🎨")
                if check_perf: render_score_bar("Performance", result["performance"]["score"], "⚡")

                st.divider()
                st.markdown(f"**{result['total_issues']} problèmes détectés** sur l'ensemble du site :")

                cats = {}
                for item in result["all_issues"]:
                    cats.setdefault(item["category"], []).append(item["message"])

                for cat, msgs in cats.items():
                    with st.expander(f"{cat} — {len(msgs)} problème(s)"):
                        render_issues(msgs)

                st.divider()
                report_txt = build_export_report(result)
                st.download_button(
                    label="📥 Télécharger le rapport complet (.txt)",
                    data=report_txt,
                    file_name=f"sitra_rapport_{normalize_url(url1).replace('https://','').replace('/','_')}.txt",
                    mime="text/plain",
                    key=f"download_{idx}"
                )

            tab_idx += 1

            # ── CHALLENGE ──
            with tabs[tab_idx]:
                st.markdown("### 🏆 Mode Challenge — Améliore ton site")
                st.caption("Coche les objectifs au fur et à mesure que tu les complètes")

                # Challenges basés sur les VRAIS problèmes détectés
                challenge_items = []

                seo = result["seo"]
                ux = result["ux"]

                if not seo["title"]:
                    challenge_items.append("Ajouter une balise <title> descriptive sur toutes les pages")
                elif len(seo["title"]) < 10 or len(seo["title"]) > 70:
                    challenge_items.append(f"Optimiser le titre (actuellement {len(seo['title'])} chars) → viser 50-60 caractères")
                if not seo["meta_description"]:
                    challenge_items.append("Écrire une meta description de 120-160 caractères pour chaque page")
                if seo["h1_count"] != 1:
                    challenge_items.append(f"Corriger les balises H1 (tu en as {seo['h1_count']}, il en faut exactement 1)")
                if seo["images_no_alt"] > 0:
                    challenge_items.append(f"Ajouter un attribut alt à {seo['images_no_alt']} image(s)")
                if not ux["has_contact"]:
                    challenge_items.append("Ajouter des informations de contact visibles (email, téléphone, formulaire)")
                if not result["performance"]["is_https"]:
                    challenge_items.append("Activer le HTTPS sur ton hébergeur (certificat SSL gratuit avec Let's Encrypt)")
                if not ux["has_footer"]:
                    challenge_items.append("Créer un footer avec mentions légales, contact et liens utiles")
                if not result["design"]["has_og_tags"]:
                    challenge_items.append("Ajouter les balises Open Graph pour améliorer le partage sur réseaux sociaux")
                if result["content"]["word_count"] < 300:
                    challenge_items.append(f"Enrichir le contenu ({result['content']['word_count']} mots actuellement → vise 300+)")

                # Complète avec des objectifs généraux si pas assez
                general_challenges = [
                    "Tester le site sur mobile et tablette (responsive design)",
                    "Vérifier la vitesse avec Google PageSpeed Insights",
                    "Créer une page FAQ pour répondre aux questions fréquentes",
                    "Ajouter des avis clients ou témoignages pour la confiance",
                    "Vérifier l'orthographe et la grammaire sur toutes les pages",
                ]
                while len(challenge_items) < 5:
                    if general_challenges:
                        challenge_items.append(general_challenges.pop(0))
                    else:
                        break

                total = len(challenge_items)
                completed = 0

                for i, obj in enumerate(challenge_items):
                    checked = st.checkbox(obj, key=f"ch_{idx}_{i}")
                    if checked:
                        completed += 1

                st.markdown("")
                if total > 0:
                    progress_pct = completed / total
                    st.progress(progress_pct)
                    st.caption(f"**{completed}/{total}** objectifs complétés — {'🎉 Bravo, site optimisé !' if completed == total else 'Continue, tu y es presque !'}")


# ── FOOTER ────────────────────────────────────────────────────────────────────
if not launch:
    st.markdown("""
    <div style="text-align:center;color:#444;margin-top:3rem;font-size:0.85rem">
        <p>🔍 <strong>Sitra</strong> analyse réellement votre site — pas de données aléatoires</p>
        <p style="margin-top:0.3rem">SEO • UX • Contenu • Design • Performance • 20+ critères vérifiés</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center;color:#333;padding:2rem 0 1rem;font-size:0.8rem;border-top:1px solid #1a1a2e;margin-top:3rem">
    Sitra — Anticiper pour dominer le marché
</div>
""", unsafe_allow_html=True)
