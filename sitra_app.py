import streamlit as st
import time
import os
from analyzer import (
    full_analysis,
    get_score_label,
    normalize_url,
    get_pagespeed,
    detect_pages,
    detect_secteur_et_concurrents,
)

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
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    story = []

    # Styles
    title_style = ParagraphStyle('title', fontSize=22, fontName='Helvetica-Bold', textColor=colors.HexColor('#667eea'), spaceAfter=6)
    sub_style = ParagraphStyle('sub', fontSize=10, fontName='Helvetica', textColor=colors.HexColor('#888888'), spaceAfter=20)
    heading_style = ParagraphStyle('heading', fontSize=13, fontName='Helvetica-Bold', textColor=colors.HexColor('#222222'), spaceAfter=8, spaceBefore=16)
    normal_style = ParagraphStyle('normal', fontSize=10, fontName='Helvetica', textColor=colors.HexColor('#333333'), spaceAfter=4)

    story.append(Paragraph("SITRA — Rapport d'analyse", title_style))
    story.append(Paragraph(f"Site : {result['final_url']}", sub_style))
    story.append(Paragraph(f"Date : {time.strftime('%d/%m/%Y')}", sub_style))
    story.append(Spacer(1, 0.5*cm))

    # Scores
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

    # Issues
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

        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
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
        </div>
        """

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
    except Exception:
        return False

# ── ANALYSES ──────────────────────────────────────────────────────────────────
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
        <a href="#pricing" target="_blank" 
           style="background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:1rem 2.5rem;border-radius:12px;text-decoration:none;font-weight:700;font-size:1rem;display:inline-block">
            Voir les offres
        </a>
    </div>
    """, unsafe_allow_html=True)

# ── PAGE ──────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Sitra | Analyseur de Sites Web", page_icon="S", layout="wide", initial_sidebar_state="expanded")

# CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.main .block-container { padding-top: 2rem; padding-bottom: 4rem; max-width: 1200px; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0a0a0a 0%, #1a1a2e 100%); }
[data-testid="stSidebar"] * { color: #e0e0e0 !important; }
</style>
""", unsafe_allow_html=True)
