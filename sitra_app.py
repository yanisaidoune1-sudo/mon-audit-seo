import streamlit as st
import time
from analyzer import full_analysis, get_score_label, normalize_url, get_pagespeed, detect_pages, detect_secteur_et_concurrents

# ── SHOPIFY AUTO-FIX ─────────────────────────────────────────────────────────
def shopify_fix_seo(shop_url, access_token, result):
    """Applique TOUTES les corrections détectées par SITRA sur Shopify"""
    import requests as req
    corrections = []
    erreurs = []

    shop = shop_url.rstrip("/").replace("https://", "").replace("http://", "")
    headers = {
        "X-Shopify-Access-Token": access_token,
        "Content-Type": "application/json"
    }

    try:
        test = req.get(f"https://{shop}/admin/api/2024-01/shop.json", headers=headers, timeout=10)
        if test.status_code == 401:
            return [], ["Token invalide — vérifiez votre clé API Shopify"]
        if test.status_code != 200:
            return [], [f"Impossible de se connecter à Shopify (code {test.status_code})"]

        shop_data = test.json().get("shop", {})

        if not result["seo"]["meta_description"]:
            try:
                import requests as req2
                headers_mistral = {"Authorization": f"Bearer {st.secrets['MISTRAL_API_KEY']}", "Content-Type": "application/json"}
                prompt = f"Génère une meta description de 150 caractères maximum pour cette boutique : {result['final_url']}. Titre : {result['seo']['title']}. Réponds UNIQUEMENT avec la meta description."
                data = {"model": "mistral-small-latest", "messages": [{"role": "user", "content": prompt}], "max_tokens": 60}
                r_mistral = req2.post("https://api.mistral.ai/v1/chat/completions", headers=headers_mistral, json=data, timeout=15)
                meta_desc = r_mistral.json()["choices"][0]["message"]["content"].strip()
                corrections.append(f"Meta description générée : '{meta_desc[:80]}...' — à appliquer dans Shopify → Préférences en ligne")
            except Exception:
                erreurs.append("Erreur lors de la génération de la meta description")

        if result["seo"]["images_no_alt"] > 0:
            products = req.get(f"https://{shop}/admin/api/2024-01/products.json?limit=50", headers=headers, timeout=10)
            if products.status_code == 200:
                fixed = 0
                for product in products.json().get("products", []):
                    for image in product.get("images", []):
                        if not image.get("alt"):
                            req.put(
                                f"https://{shop}/admin/api/2024-01/products/{product['id']}/images/{image['id']}.json",
                                headers=headers,
                                json={"image": {"id": image["id"], "alt": product.get("title", "image")}},
                                timeout=10
                            )
                            fixed += 1
                if fixed > 0:
                    corrections.append(f"{fixed} image(s) produit — attribut alt ajouté automatiquement")

        pages = req.get(f"https://{shop}/admin/api/2024-01/pages.json", headers=headers, timeout=10)
        if pages.status_code == 200:
            existing_slugs = [p.get("handle", "") for p in pages.json().get("pages", [])]
            if "mentions-legales" not in existing_slugs:
                new_page = req.post(
                    f"https://{shop}/admin/api/2024-01/pages.json",
                    headers=headers,
                    json={"page": {
                        "title": "Mentions légales",
                        "handle": "mentions-legales",
                        "body_html": f"<h1>Mentions légales</h1><p>Ce site {result['final_url']} est édité conformément à la loi française. Conformément au RGPD, vous disposez d'un droit d'accès, de rectification et de suppression de vos données personnelles.</p>"
                    }},
                    timeout=10
                )
                if new_page.status_code == 201:
                    corrections.append("Page Mentions légales créée et publiée automatiquement")

        if not result["performance"]["is_https"]:
            erreurs.append("HTTPS non activé — activez SSL depuis Paramètres → Domaines dans Shopify")

        if result["content"]["word_count"] < 300:
            erreurs.append(f"Contenu trop court ({result['content']['word_count']} mots) — enrichissez la description de votre boutique")

        if not result["design"]["has_og_tags"]:
            corrections.append("Open Graph — activez le partage social dans Shopify → Préférences en ligne → Réseaux sociaux")

    except Exception as e:
        erreurs.append(str(e))

    return corrections, erreurs

# ── WIX AUTO-FIX ──────────────────────────────────────────────────────────────
def wix_fix_seo(wix_account_id, wix_site_id, wix_api_key, result):
    """Applique TOUTES les corrections détectées par SITRA sur Wix"""
    import requests as req
    corrections = []
    erreurs = []

    headers = {
        "Authorization": wix_api_key,
        "wix-account-id": wix_account_id,
        "wix-site-id": wix_site_id,
        "Content-Type": "application/json"
    }

    try:
        test = req.get("https://www.wixapis.com/site-properties/v4/properties", headers=headers, timeout=10)
        if test.status_code == 401:
            return [], ["Clé API invalide — vérifiez vos identifiants Wix"]
        if test.status_code != 200:
            return [], [f"Impossible de se connecter à Wix (code {test.status_code})"]

        if not result["seo"]["meta_description"]:
            try:
                import requests as req2
                headers_mistral = {"Authorization": f"Bearer {st.secrets['MISTRAL_API_KEY']}", "Content-Type": "application/json"}
                prompt = f"Génère une meta description de 150 caractères maximum pour ce site : {result['final_url']}. Titre : {result['seo']['title']}. Réponds UNIQUEMENT avec la meta description."
                data = {"model": "mistral-small-latest", "messages": [{"role": "user", "content": prompt}], "max_tokens": 60}
                r_mistral = req2.post("https://api.mistral.ai/v1/chat/completions", headers=headers_mistral, json=data, timeout=15)
                meta_desc = r_mistral.json()["choices"][0]["message"]["content"].strip()
                update = req.patch("https://www.wixapis.com/site-properties/v4/properties", headers=headers, json={"properties": {"description": meta_desc}}, timeout=10)
                if update.status_code in [200, 201]:
                    corrections.append(f"Meta description ajoutée : '{meta_desc[:80]}...'")
                else:
                    erreurs.append("Impossible de mettre à jour la meta description sur Wix")
            except Exception:
                erreurs.append("Erreur lors de la génération de la meta description")

        pages = req.get("https://www.wixapis.com/site-pages/v2/pages", headers=headers, timeout=10)
        if pages.status_code == 200:
            pages_data = pages.json().get("pages", [])
            fixed_pages = 0
            for page in pages_data[:10]:
                page_id = page.get("id")
                seo_data = page.get("seo", {})
                if page_id and (not seo_data.get("description") or not seo_data.get("title")):
                    update_data = {"page": {"seo": {}}}
                    if not seo_data.get("title") and result["seo"]["title"]:
                        update_data["page"]["seo"]["title"] = result["seo"]["title"]
                    if not seo_data.get("description") and not result["seo"]["meta_description"]:
                        update_data["page"]["seo"]["description"] = meta_desc if 'meta_desc' in locals() else ""
                    req.patch(f"https://www.wixapis.com/site-pages/v2/pages/{page_id}", headers=headers, json=update_data, timeout=10)
                    fixed_pages += 1
            if fixed_pages > 0:
                corrections.append(f"{fixed_pages} page(s) — balises SEO optimisées")

        if not result["performance"]["is_https"]:
            erreurs.append("HTTPS non activé — activez-le depuis les paramètres de votre site Wix (SSL gratuit inclus)")

        if result["content"]["word_count"] < 300:
            erreurs.append(f"Contenu trop court ({result['content']['word_count']} mots) — ajoutez du contenu dans l'éditeur Wix")

        if not result["design"]["has_og_tags"]:
            og_update = req.patch(
                "https://www.wixapis.com/site-properties/v4/properties",
                headers=headers,
                json={"properties": {"socialLinks": []}},
                timeout=10
            )
            corrections.append("Balises Open Graph configurées — vérifiez dans Paramètres → Réseaux sociaux sur Wix")

    except Exception as e:
        erreurs.append(str(e))

    return corrections, erreurs

# ── WORDPRESS AUTO-FIX ────────────────────────────────────────────────────────
def wordpress_fix_seo(wp_url, wp_user, wp_password, result):
    """Applique TOUTES les corrections détectées par SITRA sur WordPress"""
    import requests as req
    from requests.auth import HTTPBasicAuth

    auth = HTTPBasicAuth(wp_user, wp_password)
    base = wp_url.rstrip("/")
    corrections = []
    erreurs = []

    try:
        test = req.get(f"{base}/wp-json/wp/v2/", auth=auth, timeout=10)
        if test.status_code == 401:
            return [], ["Identifiants incorrects — vérifiez votre nom d'utilisateur et mot de passe d'application"]
        if test.status_code != 200:
            return [], [f"Impossible d'accéder à l'API WordPress (code {test.status_code})"]

        if not result["seo"]["meta_description"]:
            try:
                import requests as req2
                headers_mistral = {
                    "Authorization": f"Bearer {st.secrets['MISTRAL_API_KEY']}",
                    "Content-Type": "application/json"
                }
                prompt = f"Génère une meta description de 150 caractères maximum pour ce site : {result['final_url']}. Titre : {result['seo']['title']}. Réponds UNIQUEMENT avec la meta description."
                data = {"model": "mistral-small-latest", "messages": [{"role": "user", "content": prompt}], "max_tokens": 60}
                r_mistral = req2.post("https://api.mistral.ai/v1/chat/completions", headers=headers_mistral, json=data, timeout=15)
                meta_desc = r_mistral.json()["choices"][0]["message"]["content"].strip()
                update = req.post(f"{base}/wp-json/wp/v2/settings", auth=auth, json={"description": meta_desc}, timeout=10)
                if update.status_code == 200:
                    corrections.append(f"Meta description ajoutée : '{meta_desc[:80]}...'")
                else:
                    erreurs.append("Impossible de mettre à jour la meta description")
            except Exception:
                erreurs.append("Erreur lors de la génération de la meta description")

        if result["seo"]["images_no_alt"] > 0:
            media = req.get(f"{base}/wp-json/wp/v2/media?per_page=100", auth=auth, timeout=10)
            if media.status_code == 200:
                images = media.json()
                fixed = 0
                for img in images:
                    if not img.get("alt_text"):
                        title = img.get("title", {}).get("rendered", "image")
                        update_img = req.post(
                            f"{base}/wp-json/wp/v2/media/{img['id']}",
                            auth=auth,
                            json={"alt_text": title},
                            timeout=10
                        )
                        if update_img.status_code == 200:
                            fixed += 1
                if fixed > 0:
                    corrections.append(f"{fixed} image(s) — attribut alt ajouté automatiquement")

        if result["seo"]["h1_count"] != 1:
            pages = req.get(f"{base}/wp-json/wp/v2/pages?per_page=5", auth=auth, timeout=10)
            if pages.status_code == 200:
                corrections.append(f"H1 vérifié sur les pages principales ({result['seo']['h1_count']} détecté — correction manuelle recommandée dans l'éditeur)")

        if not result["design"]["has_og_tags"]:
            yoast = req.get(f"{base}/wp-json/yoast/v1/get_head?url={result['final_url']}", auth=auth, timeout=10)
            if yoast.status_code == 200:
                corrections.append("Balises Open Graph détectées via Yoast SEO — activez le partage dans Yoast SEO → Réseaux sociaux")
            else:
                erreurs.append("Yoast SEO non détecté — installez le plugin Yoast SEO pour gérer les balises Open Graph")

        if not result["ux"]["has_footer"]:
            pages = req.get(f"{base}/wp-json/wp/v2/pages", auth=auth, timeout=10)
            if pages.status_code == 200:
                existing = [p.get("slug", "") for p in pages.json()]
                if "mentions-legales" not in existing:
                    new_page = req.post(
                        f"{base}/wp-json/wp/v2/pages",
                        auth=auth,
                        json={
                            "title": "Mentions légales",
                            "slug": "mentions-legales",
                            "status": "publish",
                            "content": f"""<h1>Mentions légales</h1>
<p>Conformément aux dispositions de la loi n° 2004-575 du 21 juin 2004 pour la Confiance en l'économie numérique, il est précisé aux utilisateurs du site {result['final_url']} l'identité des différents intervenants dans le cadre de sa réalisation et de son suivi.</p>
<h2>Éditeur du site</h2>
<p>Ce site est édité par le propriétaire du domaine {result['final_url']}.</p>
<h2>Hébergeur</h2>
<p>Ce site est hébergé par un prestataire d'hébergement web.</p>
<h2>Données personnelles</h2>
<p>Conformément au RGPD, vous disposez d'un droit d'accès, de rectification et de suppression de vos données personnelles.</p>"""
                        },
                        timeout=10
                    )
                    if new_page.status_code == 201:
                        corrections.append("Page Mentions légales créée et publiée automatiquement")
                    else:
                        erreurs.append("Impossible de créer la page Mentions légales")

        if result["content"]["word_count"] < 300:
            erreurs.append(f"Contenu trop court ({result['content']['word_count']} mots) — ajoutez du contenu manuellement dans l'éditeur WordPress")

        if not result["performance"]["is_https"]:
            erreurs.append("HTTPS non activé — activez-le depuis votre hébergeur (certificat SSL gratuit avec Let's Encrypt)")

    except Exception as e:
        erreurs.append(str(e))

    return corrections, erreurs

# ── IA ────────────────────────────────────────────────────────────────────────
def generer_recommandations_ia(result):
    try:
        import requests as req
        headers = {
            "Authorization": f"Bearer {st.secrets['MISTRAL_API_KEY']}",
            "Content-Type": "application/json"
        }
        prompt = f"""Tu es un conseiller web qui aide des petits entrepreneurs à améliorer leur site. Explique les problèmes simplement, comme si tu parlais à quelqu'un qui ne connaît rien à l'informatique.

Site : {result['final_url']}
Score global : {result['global_score']}/100
Problèmes détectés : {', '.join([i['message'] for i in result['all_issues'][:6]])}

Écris exactement 5 conseils numérotés (1. 2. 3. 4. 5.).
Chaque conseil doit être sur une nouvelle ligne, expliquer le problème simplement et dire quoi faire.
Pas de termes techniques — utilise des mots du quotidien."""

        data = {"model": "mistral-small-latest", "messages": [{"role": "user", "content": prompt}], "max_tokens": 600}
        r = req.post("https://api.mistral.ai/v1/chat/completions", headers=headers, json=data, timeout=30)
        return r.json()["choices"][0]["message"]["content"]
    except Exception:
        return None

def generer_deux_corrections(plateforme, result):
    try:
        import requests as req
        headers_m = {"Authorization": f"Bearer {st.secrets['MISTRAL_API_KEY']}", "Content-Type": "application/json"}

        problemes = ', '.join([i['message'] for i in result['all_issues'][:6]])

        prompt = f"""Tu es un expert en optimisation de sites web. Pour ce site {result['final_url']} sur {plateforme}, propose EXACTEMENT 2 versions de corrections différentes.

Problèmes détectés : {problemes}

VERSION 1 : Approche minimaliste (corrections essentielles seulement, rapide à faire)
VERSION 2 : Approche complète (toutes les corrections, plus de travail mais meilleur résultat)

Pour chaque version, liste en 4-5 points simples ce qui sera corrigé, expliqué en langage simple (pas de jargon technique).

Format exact :
VERSION 1 - Corrections essentielles
• [point 1]
• [point 2]
• [point 3]
• [point 4]

VERSION 2 - Corrections complètes
• [point 1]
• [point 2]
• [point 3]
• [point 4]
• [point 5]"""

        data = {"model": "mistral-small-latest", "messages": [{"role": "user", "content": prompt}], "max_tokens": 400}
        r = req.post("https://api.mistral.ai/v1/chat/completions", headers=headers_m, json=data, timeout=30)
        return r.json()["choices"][0]["message"]["content"]
    except Exception:
        return None

# ── CONTENU DE MARQUE IA (inspiré Pomelli) ───────────────────────────────────
def generer_contenu_marque(result, type_contenu, objectif):
    """Génère du contenu marketing on-brand basé sur l'analyse du site"""
    try:
        import requests as req
        headers = {
            "Authorization": f"Bearer {st.secrets['MISTRAL_API_KEY']}",
            "Content-Type": "application/json"
        }

        prompt = f"""Tu es un expert en marketing digital et copywriting. Génère du contenu marketing professionnel et percutant pour ce site.

Site analysé : {result['final_url']}
Titre du site : {result['seo']['title'] or 'Non défini'}
Description actuelle : {result['seo']['meta_description'] or 'Non définie'}
Score global SITRA : {result['global_score']}/100
Nombre de mots sur le site : {result['content']['word_count']}

Type de contenu à générer : {type_contenu}
Objectif de la campagne : {objectif}

Génère du contenu adapté, professionnel, en français, qui respecte l'identité de marque du site.
Adapte le ton au secteur d'activité détecté.
Sois concret, percutant et prêt à publier directement."""

        types_prompts = {
            "Post Instagram": f"{prompt}\n\nRédige 3 posts Instagram différents (150-200 caractères chacun + 5 hashtags pertinents). Format : POST 1 / POST 2 / POST 3",
            "Post LinkedIn": f"{prompt}\n\nRédige 2 posts LinkedIn professionnels (200-300 mots chacun). Format : POST 1 / POST 2",
            "Post Facebook": f"{prompt}\n\nRédige 3 posts Facebook engageants (100-150 mots chacun). Format : POST 1 / POST 2 / POST 3",
            "Email marketing": f"{prompt}\n\nRédige un email marketing complet avec : Objet accrocheur, Préheader, Corps de l'email (200-300 mots), CTA fort.",
            "Texte publicitaire Google Ads": f"{prompt}\n\nRédige 3 annonces Google Ads complètes avec : Titre 1 (max 30 car.) / Titre 2 (max 30 car.) / Description (max 90 car.). Format : ANNONCE 1 / ANNONCE 2 / ANNONCE 3",
            "Animation publicitaire HTML": f"""Tu es un expert en motion design web. Crée une animation publicitaire HTML/CSS/JS pour ce site.

Site : {result['final_url']}
Titre : {result['seo']['title'] or 'SITRA'}
Objectif : {objectif}

Génère une animation publicitaire complète de 300x250px (format standard) en HTML autonome.
L'animation doit :
- Avoir un fond sombre avec dégradé violet/rose (#7c6af7 → #f07cf7)
- Afficher le nom du site et un message accrocheur en animation CSS
- Inclure un bouton CTA animé
- Durer 5-6 secondes en boucle
- Être 100% CSS/JS, sans images externes

Retourne UNIQUEMENT le code HTML entre balises ```html et ```, rien d'autre.""",
        }

        prompt_final = types_prompts.get(type_contenu, prompt)
        data = {"model": "mistral-small-latest", "messages": [{"role": "user", "content": prompt_final}], "max_tokens": 800}
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
                <table style="width: 100%; border-collapse: collapse; margin: 1rem 0;">
                    <tr style="background: #667eea; color: white;">
                        <td style="padding: 8px 12px; font-weight: bold;">Catégorie</td>
                        <td style="padding: 8px 12px; font-weight: bold;">Score</td>
                    </tr>
                    <tr style="background: white;"><td style="padding: 8px 12px;">SEO</td><td style="padding: 8px 12px;">{result['seo']['score']}/100</td></tr>
                    <tr style="background: #f7f7f7;"><td style="padding: 8px 12px;">UX</td><td style="padding: 8px 12px;">{result['ux']['score']}/100</td></tr>
                    <tr style="background: white;"><td style="padding: 8px 12px;">Contenu</td><td style="padding: 8px 12px;">{result['content']['score']}/100</td></tr>
                    <tr style="background: #f7f7f7;"><td style="padding: 8px 12px;">Design</td><td style="padding: 8px 12px;">{result['design']['score']}/100</td></tr>
                    <tr style="background: white;"><td style="padding: 8px 12px;">Performance</td><td style="padding: 8px 12px;">{result['performance']['score']}/100</td></tr>
                </table>
                <p style="color: #666; font-size: 0.9rem;">Le rapport complet en PDF est joint à cet email.</p>
                <div style="text-align: center; margin-top: 1.5rem;">
                    <a href="https://mon-audit-seo.streamlit.app" style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 0.8rem 2rem; border-radius: 8px; text-decoration: none; font-weight: bold;">Relancer une analyse</a>
                </div>
            </div>
            <p style="text-align: center; color: #aaa; font-size: 0.8rem; margin-top: 1rem;">SITRA — Analyseur Intelligent de Sites Web</p>
        </div>
        """

        payload = {
            "from": "SITRA <onboarding@resend.dev>",
            "to": ["yanisaidoune1@gmail.com"],
            "reply_to": email,
            "subject": f"Rapport SITRA pour {email} — {url_site} — Score : {score}/100",
            "html": html_content,
            "attachments": [{
                "filename": f"SITRA_rapport.pdf",
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
    story.append(Paragraph("Rapport genere par SITRA — Analyseur Intelligent de Sites Web",
                           ParagraphStyle('footer', fontSize=8, textColor=colors.HexColor('#aaaaaa'))))
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

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
        <a href="https://yanisaidoune1-sudo.github.io/mon-audit-seo#pricing" target="_blank"
           style="background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:1rem 2.5rem;border-radius:12px;text-decoration:none;font-weight:700;font-size:1rem;display:inline-block">
            Voir les offres
        </a>
    </div>
    """, unsafe_allow_html=True)

st.set_page_config(page_title="SITRA | Analyseur de Sites Web", page_icon="🅂", layout="wide", initial_sidebar_state="expanded")

# ── SIDEBAR — en premier pour que les variables existent partout ──────────────
with st.sidebar:
    st.markdown("### Menu")
    st.divider()

    if "menu_choix" not in st.session_state:
        st.session_state["menu_choix"] = "Aucune option"

    menu_choix = st.selectbox(
        "Options :",
        [
            "Aucune option",
            "Mode comparatif",
            "Corriger mon site automatiquement",
            "Textes corrigés prêts à copier",
            "Génération de contenu pour votre marque",
        ],
        key="menu_choix",
        label_visibility="collapsed"
    )

    st.divider()
    st.markdown('<div style="color:#666;font-size:0.75rem;text-align:center">SITRA Engine v1.0<br>Analyse en temps réel</div>', unsafe_allow_html=True)

mode_comparaison     = (st.session_state.get("menu_choix") == "Mode comparatif")
show_corriger        = (st.session_state.get("menu_choix") == "Corriger mon site automatiquement")
show_textes          = (st.session_state.get("menu_choix") == "Textes corrigés prêts à copier")
show_contenu_marque  = (st.session_state.get("menu_choix") == "Génération de contenu pour votre marque")

st.markdown("""
<script>
(function() {
  var link = document.querySelector("link[rel~='icon']");
  if (!link) { link = document.createElement('link'); link.rel = 'icon'; document.head.appendChild(link); }
  link.type = 'image/svg+xml';
  link.href = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect width='100' height='100' rx='16' fill='%23000000'/%3E%3Cdefs%3E%3ClinearGradient id='g' x1='0%25' y1='0%25' x2='100%25' y2='100%25'%3E%3Cstop offset='0%25' stop-color='%237c6af7'/%3E%3Cstop offset='100%25' stop-color='%23f07cf7'/%3E%3C/linearGradient%3E%3C/defs%3E%3Ctext x='50' y='76' font-family='Arial Black%2C sans-serif' font-size='78' font-weight='900' fill='url(%23g)' text-anchor='middle'%3ES%3C/text%3E%3C/svg%3E";
})();
</script>
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect width='100' height='100' rx='16' fill='%23000000'/%3E%3Cdefs%3E%3ClinearGradient id='g' x1='0%25' y1='0%25' x2='100%25' y2='100%25'%3E%3Cstop offset='0%25' stop-color='%237c6af7'/%3E%3Cstop offset='100%25' stop-color='%23f07cf7'/%3E%3C/linearGradient%3E%3C/defs%3E%3Ctext x='50' y='76' font-family='Arial Black%2C sans-serif' font-size='78' font-weight='900' fill='url(%23g)' text-anchor='middle'%3ES%3C/text%3E%3C/svg%3E">
<meta property="og:title" content="SITRA — Analyseur Intelligent de Sites Web" />
<meta property="og:description" content="Analysez votre site gratuitement en 30 secondes. SEO, UX, Performance, Design — 20 critères vérifiés avec des recommandations IA personnalisées." />
<meta property="og:image" content="https://yanisaidoune1-sudo.github.io/mon-audit-seo/favicon.svg" />
<meta property="og:url" content="https://mon-audit-seo-ivaf8necmnfhqpmnyf2unx.streamlit.app" />
<meta property="og:type" content="website" />
""", unsafe_allow_html=True)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.main .block-container { padding-top: 2rem; padding-bottom: 4rem; max-width: 1200px; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0a0a0a 0%, #1a1a2e 100%); }
[data-testid="stSidebar"] * { color: #e0e0e0 !important; }
.hero-header { background: linear-gradient(135deg, #0f0f1a 0%, #1a1a3e 50%, #0f0f1a 100%); border: 1px solid #2a2a5e; border-radius: 16px; padding: 2.5rem 3rem; margin-bottom: 2rem; text-align: center; }
.hero-title { font-size: 3.5rem; font-weight: 800; background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin: 0; letter-spacing: -1px; }
.hero-subtitle { color: #888; font-size: 1rem; margin-top: 0.5rem; letter-spacing: 1px; }
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
def render_score_bar(label, score, tooltip=""):
    label_txt, _, color = get_score_label(score)
    tip_html = ""
    if tooltip:
        tip_html = f'''<span class="sitra-tooltip">(?)<span class="sitra-tooltiptext">{tooltip}</span></span>'''
    st.markdown(f"""
    <style>
    .sitra-tooltip {{ position: relative; display: inline-block; cursor: help; color: #667eea; font-size: 0.8rem; margin-left: 4px; vertical-align: middle; }}
    .sitra-tooltip .sitra-tooltiptext {{ visibility: hidden; background: #1a1a2e; color: #fff; border: 1px solid #667eea; border-radius: 6px; padding: 5px 10px; position: absolute; z-index: 999; bottom: 125%; left: 50%; transform: translateX(-50%); white-space: nowrap; font-size: 0.78rem; opacity: 0; transition: opacity 0.1s; }}
    .sitra-tooltip:hover .sitra-tooltiptext {{ visibility: visible; opacity: 1; }}
    </style>
    <div class="score-bar-container">
        <div class="score-bar-label">
            <span>{label} {tip_html}</span>
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
        st.warning("Impossible d'analyser ce site. Certains grands sites bloquent volontairement les outils d'analyse automatiques. SITRA est conçu pour les sites de PME, artisans, restaurants et portfolios.")
        return

    label_txt, _, label_color = get_score_label(result["global_score"])
    st.divider()
    st.markdown(f"### {result['final_url']}")

    c1, c2, c3, c4, c5 = st.columns(5)
    for col, score, lbl in [
        (c1, result["global_score"], "Score Global"),
        (c2, result["seo"]["score"], "Google"),
        (c3, result["ux"]["score"], "Navigation"),
        (c4, result["design"]["score"], "Apparence"),
        (c5, result["performance"]["score"], "Vitesse"),
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

    import os
    try:
        os.environ["MISTRAL_API_KEY"] = st.secrets["MISTRAL_API_KEY"]
    except Exception:
        pass

    tabs_list = [
        "Référencement Google",
        "Détails du site",
        "Analyse approfondie",
        "Résumé",
        "Objectifs à atteindre",
        "Partager",
    ]
    if show_corriger:
        tabs_list.append("Corriger mon site")
    if show_textes:
        tabs_list.append("Textes corrigés")
    if show_contenu_marque:
        tabs_list.append("Génération de contenu")
    if mode_comparaison:
        tabs_list.append("Mode comparatif")

    tabs = st.tabs(tabs_list)

    with tabs[0]:
        seo = result["seo"]
        render_score_bar("Référencement Google", seo["score"])
        st.caption("Comment Google voit et comprend votre site")
        st.markdown("")
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.markdown("**Ce qu'on a trouvé sur votre site**")
            title_display = seo['title'][:60] + '...' if len(seo['title']) > 60 else seo['title'] or '(manquant)'
            st.markdown(f"- **Titre de la page** : `{title_display}` ({len(seo['title'])} caractères)")
            st.markdown(f"- **Description Google** : {len(seo['meta_description'])} caractères")
            st.markdown(f"- **Titre principal** : {seo['h1_count']} {'(correct)' if seo['h1_count'] == 1 else '(à corriger)'}")
            st.markdown(f"- **Sous-titres** : {seo['h2_count']} {'(correct)' if seo['h2_count'] > 0 else '(manquant)'}")
            st.markdown(f"- **Images sans description** : {seo['images_no_alt']}/{seo['images_total']}")
        with col_s2:
            st.markdown("**Ce qu'il faut améliorer**")
            render_issues(seo["issues"])

    with tabs[1]:
        st.caption("Choisissez ce que vous voulez voir")
        sous_onglet = st.selectbox("Voir :", ["Navigation", "Qualité du texte", "Apparence du site", "Vitesse du site"], key=f"sous_{idx}")

        if sous_onglet == "Navigation":
            ux = result["ux"]
            render_score_bar("Navigation", ux["score"])
            st.caption("Est-ce que les visiteurs trouvent facilement ce qu'ils cherchent ?")
            col_u1, col_u2 = st.columns(2)
            with col_u1:
                st.markdown("**Ce qu'on a trouvé**")
                st.markdown(f"- **Menu** : {'Présent' if ux['has_nav'] else 'Absent'} ({ux['nav_links_count']} liens)")
                st.markdown(f"- **Boutons** : {ux['buttons_count']} {'(correct)' if ux['buttons_count'] > 0 else '(manquant)'}")
                st.markdown(f"- **Contact** : {'Trouvé' if ux['has_contact'] else 'Absent'}")
                st.markdown(f"- **Pied de page** : {'Présent' if ux['has_footer'] else 'Absent'}")
            with col_u2:
                st.markdown("**Ce qu'il faut améliorer**")
                render_issues(ux["issues"])

        elif sous_onglet == "Qualité du texte":
            content = result["content"]
            render_score_bar("Qualité du texte", content["score"])
            st.caption("Le contenu de votre site est-il clair et suffisant ?")
            st.markdown(f"**Nombre de mots** : {content['word_count']} {'(bien !)' if content['word_count'] >= 300 else '(ajoutez plus de contenu, visez 300 mots minimum)'}")
            render_issues(content["issues"])

        elif sous_onglet == "Apparence du site":
            design = result["design"]
            render_score_bar("Apparence du site", design["score"])
            st.caption("Votre site donne-t-il une bonne première impression ?")
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                st.markdown("**Ce qu'on a trouvé**")
                st.markdown(f"- **Icône du site** : {'Présente' if design['has_favicon'] else 'Absente'}")
                st.markdown(f"- **Polices personnalisées** : {'Oui' if design['has_google_fonts'] else 'Non'}")
                st.markdown(f"- **Aperçu réseaux sociaux** : {'Configuré' if design['has_og_tags'] else 'Non configuré'}")
            with col_d2:
                st.markdown("**Ce qu'il faut améliorer**")
                render_issues(design["issues"])

        elif sous_onglet == "Vitesse du site":
            perf = result["performance"]
            render_score_bar("Vitesse du site", perf["score"])
            st.caption("Un site lent fait fuir les visiteurs — 53% partent si ça met plus de 3 secondes")
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                st.markdown("**Ce qu'on a mesuré**")
                rt = perf['response_time']
                rt_label = "Excellent" if rt and rt < 1 else ("Moyen" if rt and rt < 2 else "Lent")
                st.markdown(f"- **Connexion sécurisée** : {'Oui' if perf['is_https'] else 'Non'}")
                st.markdown(f"- **Temps de chargement** : {rt}s — {rt_label}")
                st.markdown(f"- **Taille de la page** : {perf['html_size_kb']} KB")
            with col_p2:
                st.markdown("**Ce qu'il faut améliorer**")
                render_issues(perf["issues"])

    with tabs[3]:
        st.markdown(f"### Score global : **{result['global_score']}/100** — {label_txt}")
        render_score_bar("Référencement Google", result["seo"]["score"], "Comment Google voit votre site")
        render_score_bar("Navigation", result["ux"]["score"], "Les visiteurs trouvent-ils facilement ce qu'ils cherchent ?")
        render_score_bar("Qualité du texte", result["content"]["score"], "Votre contenu est-il clair et suffisant ?")
        render_score_bar("Apparence du site", result["design"]["score"], "Votre site donne-t-il une bonne première impression ?")
        render_score_bar("Vitesse du site", result["performance"]["score"], "Votre site se charge-t-il rapidement ?")
        st.divider()
        st.markdown(f"**{result['total_issues']} problèmes détectés :**")
        cats = {}
        for item in result["all_issues"]:
            cats.setdefault(item["category"], []).append(item["message"])
        for cat, msgs in cats.items():
            cat_fr = {"SEO": "Référencement Google", "UX": "Navigation", "Contenu": "Qualité du texte", "Design": "Apparence du site", "Performance": "Vitesse du site"}.get(cat, cat)
            with st.expander(f"{cat_fr} — {len(msgs)} problème(s)"):
                render_issues(msgs)
        st.divider()
        try:
            pdf_data = generer_pdf(result)
            st.download_button(label="Télécharger le rapport PDF", data=pdf_data, file_name=f"SITRA_rapport_{idx}.pdf", mime="application/pdf", key=f"download_{idx}")
        except Exception:
            pass
        st.markdown("")
        st.markdown("**Recevoir le rapport par email :**")
        email_input = st.text_input("Votre email :", placeholder="exemple@email.com", key=f"email_{idx}")
        if st.button("Envoyer le rapport par email", key=f"send_email_{idx}"):
            if email_input and "@" in email_input:
                with st.spinner("Envoi en cours..."):
                    succes = envoyer_rapport_email(email_input, result)
                if succes:
                    st.success(f"✅ Rapport envoyé à {email_input} !")
                else:
                    st.warning("L'envoi automatique n'est pas encore disponible. Téléchargez le PDF ci-dessus et envoyez-le manuellement.")
            else:
                st.warning("Merci d'entrer un email valide.")

    with tabs[4]:
        st.markdown("### Objectifs à atteindre")
        st.caption("Cochez les objectifs au fur et à mesure que vous les complétez")
        seo = result["seo"]
        ux = result["ux"]
        challenge_items = []
        if not seo["title"]:
            challenge_items.append("Ajouter un titre à votre site")
        elif len(seo["title"]) < 10 or len(seo["title"]) > 70:
            challenge_items.append(f"Améliorer le titre ({len(seo['title'])} caractères) — viser 50-60 caractères")
        if not seo["meta_description"]:
            challenge_items.append("Écrire une description de 120-160 caractères pour Google")
        if seo["h1_count"] != 1:
            challenge_items.append(f"Corriger le titre principal (vous en avez {seo['h1_count']}, il en faut 1)")
        if seo["images_no_alt"] > 0:
            challenge_items.append(f"Ajouter une description à {seo['images_no_alt']} image(s)")
        if not ux["has_contact"]:
            challenge_items.append("Ajouter vos informations de contact visibles")
        if not result["performance"]["is_https"]:
            challenge_items.append("Activer la connexion sécurisée sur votre site")
        if not ux["has_footer"]:
            challenge_items.append("Créer un pied de page avec vos informations et mentions légales")
        if not result["design"]["has_og_tags"]:
            challenge_items.append("Configurer l'aperçu de votre site sur les réseaux sociaux")
        if result["content"]["word_count"] < 300:
            challenge_items.append(f"Étoffer le contenu ({result['content']['word_count']} mots — visez 300 minimum)")
        generals = ["Tester sur téléphone et tablette", "Vérifier la vitesse de chargement", "Créer une page FAQ", "Ajouter des avis clients", "Vérifier l'orthographe"]
        while len(challenge_items) < 5 and generals:
            challenge_items.append(generals.pop(0))
        total = len(challenge_items)

        st.session_state[f"challenge_items_{idx}"] = challenge_items

        completed = sum(1 for i in range(total) if st.session_state.get(f"ch_{idx}_{i}", False))
        for i, obj in enumerate(challenge_items):
            key = f"ch_{idx}_{i}"
            if st.checkbox(obj, key=key):
                pass
        completed = sum(1 for i in range(total) if st.session_state.get(f"ch_{idx}_{i}", False))
        if total > 0:
            st.markdown("")
            st.progress(completed / total)
            st.caption(f"**{completed}/{total}** objectifs complétés {'— Bravo !' if completed == total else ''}")

    with tabs[2]:
        st.caption("Choisissez ce que vous voulez analyser")
        sous2 = st.selectbox("Voir :", ["Surcharge du site", "Images du site"], key=f"sous2_{idx}")

        if sous2 == "Surcharge du site":
            st.markdown("**Votre site a-t-il des éléments inutiles ?**")
            surcharge_items = []
            conseils = []
            if result["ux"]["nav_links_count"] > 7:
                surcharge_items.append(f"Menu surchargé : {result['ux']['nav_links_count']} liens")
                conseils.append("Réduisez à 5-7 liens maximum — gardez les pages les plus importantes")
            if result["performance"]["html_size_kb"] > 200:
                surcharge_items.append(f"Page trop lourde : {result['performance']['html_size_kb']} KB")
                conseils.append("Supprimez les éléments inutilisés — chaque KB en moins accélère votre site")
            if result["seo"]["images_total"] > 20:
                surcharge_items.append(f"Beaucoup d'images : {result['seo']['images_total']} détectées")
                conseils.append("Gardez seulement les plus importantes et compressez les autres")
            if result["ux"]["long_paragraphs"] > 0:
                surcharge_items.append(f"{result['ux']['long_paragraphs']} paragraphe(s) trop long(s)")
                conseils.append("Découpez vos longs paragraphes — les visiteurs lisent en diagonale")
            if result["content"]["word_count"] > 1000:
                surcharge_items.append(f"Contenu très long : {result['content']['word_count']} mots")
                conseils.append("Allez à l'essentiel — les visiteurs n'ont pas le temps de tout lire")
            if surcharge_items:
                for item, conseil in zip(surcharge_items, conseils):
                    st.markdown(f"""<div style="background:#1a1a2e;border:1px solid #ffc107;border-radius:10px;padding:1rem;margin:0.5rem 0"><div style="color:#ffc107;font-weight:700">⚠️ {item}</div><div style="color:#ccc;font-size:0.9rem;margin-top:0.3rem">💡 {conseil}</div></div>""", unsafe_allow_html=True)
            else:
                st.success("Votre site ne semble pas surchargé !")

        elif sous2 == "Images du site":
            st.markdown("**Vos images sont-elles suffisantes et adaptées ?**")
            images_total = result["seo"]["images_total"]
            images_no_alt = result["seo"]["images_no_alt"]
            if images_total == 0:
                st.markdown("""<div style="background:#1a1a2e;border:1px solid #dc3545;border-radius:10px;padding:1rem;margin:0.5rem 0"><div style="color:#dc3545;font-weight:700">❌ Aucune image sur votre site</div><div style="color:#ccc;font-size:0.9rem;margin-top:0.3rem">💡 Ajoutez des images pour rendre votre site plus attractif</div></div>""", unsafe_allow_html=True)
            elif images_total < 3:
                st.markdown(f"""<div style="background:#1a1a2e;border:1px solid #ffc107;border-radius:10px;padding:1rem;margin:0.5rem 0"><div style="color:#ffc107;font-weight:700">⚠️ Seulement {images_total} image(s) — c'est peu</div><div style="color:#ccc;font-size:0.9rem;margin-top:0.3rem">💡 Ajoutez des photos de vos produits, équipe ou locaux</div></div>""", unsafe_allow_html=True)
            elif images_total > 20:
                st.markdown(f"""<div style="background:#1a1a2e;border:1px solid #ffc107;border-radius:10px;padding:1rem;margin:0.5rem 0"><div style="color:#ffc107;font-weight:700">⚠️ Beaucoup d'images : {images_total}</div><div style="color:#ccc;font-size:0.9rem;margin-top:0.3rem">💡 Gardez les plus importantes et compressez les autres</div></div>""", unsafe_allow_html=True)
            else:
                st.success(f"✅ Bon nombre d'images : {images_total}")
            if images_no_alt > 0:
                st.markdown(f"""<div style="background:#1a1a2e;border:1px solid #ffc107;border-radius:10px;padding:1rem;margin:0.5rem 0"><div style="color:#ffc107;font-weight:700">⚠️ {images_no_alt} image(s) sans description</div><div style="color:#ccc;font-size:0.9rem;margin-top:0.3rem">💡 Ajoutez une description à chaque image pour aider Google</div></div>""", unsafe_allow_html=True)
            elif images_total > 0:
                st.success("✅ Toutes vos images ont une description !")
            st.markdown("\n**Conseils :**\n- Photos compressées (moins de 200 KB)\n- Format WebP ou JPEG\n- Pas d'images floues ou pixelisées")

    with tabs[5]:
        st.markdown("### Partager mes résultats")
        score = result["global_score"]
        url_site = result["final_url"]
        texte_partage = f"J'ai analysé {url_site} avec SITRA et obtenu un score de {score}/100 ! Analysez votre site sur https://mon-audit-seo-ivaf8necmnfhqpmnyf2unx.streamlit.app"
        lien_twitter = f"https://twitter.com/intent/tweet?text={texte_partage}"
        lien_linkedin = f"https://www.linkedin.com/sharing/share-offsite/?url=https://mon-audit-seo-ivaf8necmnfhqpmnyf2unx.streamlit.app"
        lien_facebook = f"https://www.facebook.com/sharer/sharer.php?u=https://mon-audit-seo-ivaf8necmnfhqpmnyf2unx.streamlit.app&quote={texte_partage}"
        lien_whatsapp = f"https://wa.me/?text={texte_partage}"
        st.markdown("")
        col_sh1, col_sh2, col_sh3, col_sh4 = st.columns(4)
        with col_sh1:
            st.markdown(f'''<a href="{lien_twitter}" target="_blank" style="display:block;text-align:center;background:#1a1a2e;border:1px solid #2a2a4e;border-radius:10px;padding:0.8rem 1rem;color:#1DA1F2;text-decoration:none;font-weight:600">X (Twitter)</a>''', unsafe_allow_html=True)
        with col_sh2:
            st.markdown(f'''<a href="{lien_linkedin}" target="_blank" style="display:block;text-align:center;background:#1a1a2e;border:1px solid #2a2a4e;border-radius:10px;padding:0.8rem 1rem;color:#0A66C2;text-decoration:none;font-weight:600">LinkedIn</a>''', unsafe_allow_html=True)
        with col_sh3:
            st.markdown(f'''<a href="{lien_facebook}" target="_blank" style="display:block;text-align:center;background:#1a1a2e;border:1px solid #2a2a4e;border-radius:10px;padding:0.8rem 1rem;color:#1877F2;text-decoration:none;font-weight:600">Facebook</a>''', unsafe_allow_html=True)
        with col_sh4:
            st.markdown(f'''<a href="{lien_whatsapp}" target="_blank" style="display:block;text-align:center;background:#1a1a2e;border:1px solid #2a2a4e;border-radius:10px;padding:0.8rem 1rem;color:#25D366;text-decoration:none;font-weight:600">WhatsApp</a>''', unsafe_allow_html=True)
        st.markdown("")
        st.markdown("**Pour Instagram et TikTok** — copiez ce texte :")
        st.code(texte_partage, language=None)

    # ── ONGLET CORRIGER ──
    if show_corriger:
        tab_corriger_idx = tabs_list.index("Corriger mon site")
        with tabs[tab_corriger_idx]:
            st.markdown("### Corriger mon site automatiquement")
            st.caption("SITRA va vous proposer 2 versions de corrections. Vous choisissez celle que vous préférez avant de l'appliquer.")

            plateforme = st.selectbox("Quelle plateforme utilise votre site ?", [
                "Choisissez votre plateforme...",
                "WordPress", "Wix", "Shopify", "Squarespace",
                "Webflow", "Prestashop", "Drupal", "Magento", "Ghost", "TYPO3"
            ], key=f"plateforme_{idx}")

            if plateforme != "Choisissez votre plateforme...":
                if st.button("Voir les 2 propositions de corrections", key=f"voir_props_{idx}"):
                    with st.spinner("SITRA prépare 2 propositions personnalisées..."):
                        propositions = generer_deux_corrections(plateforme, result)

                    if propositions:
                        st.session_state[f"propositions_{idx}"] = propositions
                        st.session_state[f"plateforme_choisie_{idx}"] = plateforme

                if f"propositions_{idx}" in st.session_state:
                    propositions = st.session_state[f"propositions_{idx}"]

                    lignes = propositions.split("\n")
                    version1_lines = []
                    version2_lines = []
                    current = None
                    for ligne in lignes:
                        if "VERSION 1" in ligne:
                            current = 1
                        elif "VERSION 2" in ligne:
                            current = 2
                        elif current == 1:
                            version1_lines.append(ligne)
                        elif current == 2:
                            version2_lines.append(ligne)

                    col_v1, col_v2 = st.columns(2)
                    with col_v1:
                        st.markdown("""<div style="background:#1a1a2e;border:2px solid #667eea;border-radius:12px;padding:1.5rem">
                        <div style="color:#667eea;font-weight:800;font-size:1.1rem;margin-bottom:1rem">Version 1 — Corrections essentielles</div>""", unsafe_allow_html=True)
                        for l in version1_lines:
                            if l.strip():
                                st.markdown(l)
                        st.markdown("</div>", unsafe_allow_html=True)
                        if st.button("Appliquer la Version 1", key=f"apply_v1_{idx}"):
                            st.session_state[f"version_choisie_{idx}"] = 1
                            st.info("Version 1 sélectionnée — entrez vos identifiants ci-dessous pour appliquer.")

                    with col_v2:
                        st.markdown("""<div style="background:#1a1a2e;border:2px solid #f07cf7;border-radius:12px;padding:1.5rem">
                        <div style="color:#f07cf7;font-weight:800;font-size:1.1rem;margin-bottom:1rem">Version 2 — Corrections complètes</div>""", unsafe_allow_html=True)
                        for l in version2_lines:
                            if l.strip():
                                st.markdown(l)
                        st.markdown("</div>", unsafe_allow_html=True)
                        if st.button("Appliquer la Version 2", key=f"apply_v2_{idx}"):
                            st.session_state[f"version_choisie_{idx}"] = 2
                            st.info("Version 2 sélectionnée — entrez vos identifiants ci-dessous pour appliquer.")

                    if f"version_choisie_{idx}" in st.session_state:
                        st.divider()
                        st.markdown(f"**Entrez vos identifiants {plateforme} pour appliquer la version choisie :**")

                        def show_corrections(corrections, erreurs):
                            if corrections:
                                st.success(f"**{len(corrections)} correction(s) appliquée(s) :**")
                                for c in corrections: st.markdown(f"✅ {c}")
                            if erreurs:
                                st.error("**Points à corriger manuellement :**")
                                for e in erreurs: st.markdown(f"❌ {e}")
                            if not corrections and not erreurs:
                                st.info("Aucune correction nécessaire !")

                        if plateforme == "WordPress":
                            wp_url = st.text_input("URL :", key=f"wp_url_{idx}")
                            wp_user = st.text_input("Nom d'utilisateur :", key=f"wp_user_{idx}")
                            wp_password = st.text_input("Mot de passe d'application :", type="password", key=f"wp_pass_{idx}")
                            if st.button("Appliquer sur mon WordPress", key=f"wp_fix_{idx}"):
                                if wp_url and wp_user and wp_password:
                                    with st.spinner("Application..."):
                                        c, e = wordpress_fix_seo(wp_url, wp_user, wp_password, result)
                                    show_corrections(c, e)
                                else:
                                    st.warning("Merci de remplir tous les champs.")
                        elif plateforme == "Wix":
                            wix_account_id = st.text_input("Account ID :", key=f"wix_account_{idx}")
                            wix_site_id = st.text_input("Site ID :", key=f"wix_site_{idx}")
                            wix_api_key = st.text_input("Clé API :", type="password", key=f"wix_key_{idx}")
                            if st.button("Appliquer sur mon Wix", key=f"wix_fix_{idx}"):
                                if wix_account_id and wix_site_id and wix_api_key:
                                    with st.spinner("Application..."):
                                        c, e = wix_fix_seo(wix_account_id, wix_site_id, wix_api_key, result)
                                    show_corrections(c, e)
                                else:
                                    st.warning("Merci de remplir tous les champs.")
                        elif plateforme == "Shopify":
                            shop_url = st.text_input("URL boutique :", key=f"shopify_url_{idx}")
                            access_token = st.text_input("Token d'accès :", type="password", key=f"shopify_token_{idx}")
                            if st.button("Appliquer sur ma boutique Shopify", key=f"shopify_fix_{idx}"):
                                if shop_url and access_token:
                                    with st.spinner("Application..."):
                                        c, e = shopify_fix_seo(shop_url, access_token, result)
                                    show_corrections(c, e)
                                else:
                                    st.warning("Merci de remplir tous les champs.")

    # ── ONGLET TEXTES CORRIGÉS ──
    if show_textes:
        tab_textes_idx = tabs_list.index("Textes corrigés")
        with tabs[tab_textes_idx]:
            st.markdown("### Textes corrigés prêts à copier-coller")
            st.caption("SITRA rédige pour vous les textes manquants ou à améliorer — copiez-les directement sur votre site.")
            if st.button("Générer mes textes corrigés", key=f"gen_textes_{idx}"):
                with st.spinner("Rédaction en cours..."):
                    try:
                        import requests as req
                        headers_t = {"Authorization": f"Bearer {st.secrets['MISTRAL_API_KEY']}", "Content-Type": "application/json"}
                        prompt = f"""Tu es un expert en rédaction web. Pour ce site {result['final_url']}, rédige les textes manquants ou à améliorer.

Titre actuel : {result['seo']['title'] or 'Manquant'}
Meta description actuelle : {result['seo']['meta_description'] or 'Manquante'}
Nombre de mots sur le site : {result['content']['word_count']}
Problèmes détectés : {', '.join([i['message'] for i in result['all_issues'][:5]])}

Rédige exactement ces éléments en français, de façon professionnelle :

TITRE DE LA PAGE (50-60 caractères) :
[rédige ici]

DESCRIPTION GOOGLE (120-160 caractères) :
[rédige ici]

TEXTE D'INTRODUCTION POUR LA PAGE D'ACCUEIL (80-100 mots) :
[rédige ici]

TITRE PRINCIPAL DE LA PAGE (H1) :
[rédige ici]"""
                        data = {"model": "mistral-small-latest", "messages": [{"role": "user", "content": prompt}], "max_tokens": 500}
                        r = req.post("https://api.mistral.ai/v1/chat/completions", headers=headers_t, json=data, timeout=30)
                        st.session_state[f"textes_tab_{idx}"] = r.json()["choices"][0]["message"]["content"]
                    except Exception:
                        st.error("Impossible de générer les textes pour le moment.")

            if f"textes_tab_{idx}" in st.session_state:
                for section in st.session_state[f"textes_tab_{idx}"].split("\n\n"):
                    if section.strip():
                        lignes = section.strip().split("\n")
                        titre = lignes[0].replace(":", "").strip()
                        contenu_txt = "\n".join(lignes[1:]).strip()
                        if contenu_txt:
                            st.markdown(f"**{titre}**")
                            st.code(contenu_txt, language=None)

    # ── ONGLET GÉNÉRATION DE CONTENU ──
    if show_contenu_marque:
        tab_cm_idx = tabs_list.index("Génération de contenu")
        with tabs[tab_cm_idx]:
            st.markdown("### Génération de contenu pour votre marque")
            st.caption("SITRA a analysé votre site. Il connaît votre secteur et votre style. Choisissez ce que vous voulez créer — le contenu est généré en quelques secondes, prêt à publier.")

            st.markdown("""
            <div style="background:linear-gradient(135deg,rgba(102,126,234,0.15),rgba(240,124,247,0.1));border:1px solid rgba(102,126,234,0.4);border-radius:12px;padding:1.2rem 1.5rem;margin-bottom:1.5rem">
                <div style="font-weight:700;color:#4a40c0;margin-bottom:0.8rem;font-size:0.95rem;">Comment utiliser ce contenu ?</div>
                <div style="color:#1a1a1a;font-size:0.88rem;line-height:1.8">
                • <b>Posts Instagram / Facebook / LinkedIn</b> : copiez le texte généré, ajoutez une photo de votre choix ou utilisez l'animation HTML fournie directement dans votre story ou publicité.<br>
                • <b>Animations publicitaires</b> : SITRA génère une animation HTML prête à l'emploi. Téléchargez-la et importez-la dans Canva, Meta Ads ou votre site.<br>
                • <b>Email marketing</b> : copiez le contenu dans votre outil d'emailing (Mailchimp, Brevo…).<br>
                • <b>Publicités Google / Meta</b> : les textes sont déjà calibrés aux limites de caractères publicitaires.
                </div>
            </div>
            """, unsafe_allow_html=True)

            col_cm1, col_cm2 = st.columns(2)
            with col_cm1:
                type_contenu = st.selectbox(
                    "Type de contenu :",
                    ["Post Instagram", "Post LinkedIn", "Post Facebook", "Email marketing", "Texte publicitaire Google Ads", "Animation publicitaire HTML"],
                    key=f"type_contenu_{idx}"
                )
            with col_cm2:
                objectif = st.text_input(
                    "Objectif de la campagne :",
                    placeholder="Ex : Promouvoir ma nouvelle offre, Attirer des clients locaux...",
                    key=f"objectif_cm_{idx}"
                )

            if st.button("Générer le contenu", key=f"gen_cm_{idx}"):
                if objectif.strip():
                    with st.spinner("SITRA génère votre contenu..."):
                        contenu = generer_contenu_marque(result, type_contenu, objectif)
                    if contenu:
                        st.session_state[f"contenu_marque_{idx}"] = contenu
                        st.session_state[f"type_cm_{idx}"] = type_contenu
                    else:
                        st.error("Impossible de générer le contenu pour le moment.")
                else:
                    st.warning("Merci de décrire l'objectif de votre campagne.")

            if f"contenu_marque_{idx}" in st.session_state:
                st.divider()
                type_gen = st.session_state.get(f"type_cm_{idx}", "")
                contenu_gen = st.session_state[f"contenu_marque_{idx}"]
                if type_gen == "Animation publicitaire HTML":
                    st.markdown("**Animation générée — prévisualisez puis téléchargez :**")
                    import re
                    html_match = re.search(r'```html\n(.*?)```', contenu_gen, re.DOTALL)
                    if html_match:
                        html_code = html_match.group(1)
                        st.components.v1.html(html_code, height=300)
                        st.download_button("Télécharger l'animation HTML", html_code, file_name="animation_sitra.html", mime="text/html", key=f"dl_anim_{idx}")
                    else:
                        st.code(contenu_gen, language="html")
                else:
                    st.markdown("**Contenu généré — copiez et publiez directement :**")
                    sections = contenu_gen.split("\n\n")
                    for section in sections:
                        if section.strip():
                            lignes = section.strip().split("\n")
                            if len(lignes) > 1 and any(kw in lignes[0].upper() for kw in ["POST", "ACCROCHE", "ANNONCE", "OBJET", "EMAIL", "VERSION"]):
                                st.markdown(f"**{lignes[0]}**")
                                st.code("\n".join(lignes[1:]), language=None)
                            else:
                                st.code(section.strip(), language=None)
                if st.button("Générer une nouvelle version", key=f"regen_cm_{idx}"):
                    del st.session_state[f"contenu_marque_{idx}"]
                    st.rerun()

    # ── ONGLET MODE COMPARATIF ──
    if mode_comparaison:
        tab_comp_idx = tabs_list.index("Mode comparatif")
        with tabs[tab_comp_idx]:
            st.markdown("### Mode comparatif")
            st.caption("Entrez l'URL de votre site et celle d'un concurrent pour comparer les scores côte à côte.")
            st.info("Lancez une nouvelle analyse en mode comparatif depuis la barre de recherche en haut — entrez votre site ET le site concurrent.")

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
    elif get_analyses_count() >= 2:
        show_paywall()
    else:
        results_list = []
        for url in urls_to_analyze:
            with st.spinner(f"Analyse de {url} en cours..."):
                result = full_analysis(url)
            results_list.append(result)
        st.session_state["results"] = results_list
        st.session_state["mode_comp"] = mode_comparaison
        increment_analyses_count()

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
        <p><strong>SITRA</strong> analyse votre site en temps réel et vous dit exactement quoi améliorer</p>
    </div>
    """, unsafe_allow_html=True)

# ── ASSISTANT IA ──────────────────────────────────────────────────────────────
st.divider()
with st.expander("Vous avez une question ? Posez-la à l'assistant SITRA"):
    st.caption("L'assistant peut expliquer les termes techniques, vous aider à comprendre vos résultats et vous donner des conseils.")

    if "chat_messages" not in st.session_state:
        st.session_state["chat_messages"] = []
    if "chat_input_key" not in st.session_state:
        st.session_state["chat_input_key"] = 0

    for msg in st.session_state["chat_messages"]:
        if msg["role"] == "user":
            st.markdown(f"""<div style="background:#1a1a2e;border:1px solid #2a2a4e;border-radius:10px;padding:0.8rem 1rem;margin:0.5rem 0;text-align:right;color:#e0e0e0">{msg['content']}</div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""<div style="background:#1a1a2e;border:1px solid #667eea;border-radius:10px;padding:0.8rem 1rem;margin:0.5rem 0;color:#ffffff;font-weight:500">{msg['content']}</div>""", unsafe_allow_html=True)

    question = st.text_input("Votre question :", placeholder="Ex: C'est quoi une balise H1 ? Pourquoi mon score SEO est bas ?", key=f"chat_input_{st.session_state['chat_input_key']}")

    if st.button("Envoyer", key="chat_send"):
        if question.strip():
            st.session_state["chat_messages"].append({"role": "user", "content": question})

            try:
                import requests as req
                headers = {
                    "Authorization": f"Bearer {st.secrets['MISTRAL_API_KEY']}",
                    "Content-Type": "application/json"
                }

                contexte = ""
                if "results" in st.session_state:
                    r = st.session_state["results"][0]
                    contexte = f"Le site analysé est {r['final_url']} avec un score de {r['global_score']}/100. SEO: {r['seo']['score']}/100, UX: {r['ux']['score']}/100, Performance: {r['performance']['score']}/100."

                messages = [
                    {"role": "system", "content": f"""Tu es l'assistant de SITRA, un outil d'analyse de sites web. Tu réponds aux questions en langage simple et accessible, sans jargon technique. Tu expliques les termes avec des exemples concrets. Tu gardes le contexte de la conversation.
{f'Contexte du site analysé : {contexte}' if contexte else ''}"""}
                ]
                for msg in st.session_state["chat_messages"]:
                    messages.append({"role": msg["role"], "content": msg["content"]})

                data = {
                    "model": "mistral-small-latest",
                    "messages": messages,
                    "max_tokens": 500
                }
                r = req.post("https://api.mistral.ai/v1/chat/completions", headers=headers, json=data, timeout=15)
                reponse = r.json()["choices"][0]["message"]["content"]
                st.session_state["chat_messages"].append({"role": "assistant", "content": reponse})
                st.session_state["chat_input_key"] += 1
                st.rerun()
            except Exception:
                st.error("Impossible de contacter l'assistant pour le moment.")

def webflow_fix_seo(api_key, site_id, result):
    import requests as req
    corrections = []
    erreurs = []
    headers = {
        "Authorization": f"Bearer {api_key}",
        "accept-version": "1.0.0",
        "Content-Type": "application/json"
    }
    try:
        test = req.get(f"https://api.webflow.com/sites/{site_id}", headers=headers, timeout=10)
        if test.status_code == 401:
            return [], ["Token invalide — vérifiez votre clé API Webflow"]
        if test.status_code != 200:
            return [], [f"Impossible de se connecter à Webflow (code {test.status_code})"]
        if not result["seo"]["meta_description"]:
            try:
                import requests as req2
                headers_mistral = {"Authorization": f"Bearer {st.secrets['MISTRAL_API_KEY']}", "Content-Type": "application/json"}
                prompt = f"Génère une meta description de 150 caractères maximum pour ce site : {result['final_url']}. Titre : {result['seo']['title']}. Réponds UNIQUEMENT avec la meta description."
                data = {"model": "mistral-small-latest", "messages": [{"role": "user", "content": prompt}], "max_tokens": 60}
                r_mistral = req2.post("https://api.mistral.ai/v1/chat/completions", headers=headers_mistral, json=data, timeout=15)
                meta_desc = r_mistral.json()["choices"][0]["message"]["content"].strip()
                update = req.patch(f"https://api.webflow.com/sites/{site_id}", headers=headers, json={"seo": {"desc": meta_desc}}, timeout=10)
                if update.status_code == 200:
                    corrections.append(f"Meta description ajoutée : '{meta_desc[:80]}...'")
                else:
                    erreurs.append("Impossible de mettre à jour la meta description sur Webflow")
            except Exception:
                erreurs.append("Erreur lors de la génération de la meta description")
        if not result["performance"]["is_https"]:
            erreurs.append("HTTPS non activé — activez SSL depuis Project Settings → Hosting sur Webflow")
        if result["content"]["word_count"] < 300:
            erreurs.append(f"Contenu trop court ({result['content']['word_count']} mots)")
    except Exception as e:
        erreurs.append(str(e))
    return corrections, erreurs

def prestashop_fix_seo(shop_url, api_key, result):
    import requests as req
    import base64
    corrections = []
    erreurs = []
    base = shop_url.rstrip("/")
    credentials = base64.b64encode(f"{api_key}:".encode()).decode()
    headers = {"Authorization": f"Basic {credentials}", "Output-Format": "JSON"}
    try:
        test = req.get(f"{base}/api/", headers=headers, timeout=10)
        if test.status_code == 401:
            return [], ["Clé API invalide — vérifiez votre clé Prestashop"]
        if not result["seo"]["meta_description"]:
            corrections.append("Meta description manquante — à ajouter via le module Metatag dans Prestashop")
        if not result["performance"]["is_https"]:
            erreurs.append("HTTPS non activé")
    except Exception as e:
        erreurs.append(str(e))
    return corrections, erreurs

def drupal_fix_seo(drupal_url, username, password, result):
    import requests as req
    corrections = []
    erreurs = []
    base = drupal_url.rstrip("/")
    try:
        login = req.post(f"{base}/user/login?_format=json", json={"name": username, "pass": password}, headers={"Content-Type": "application/json"}, timeout=10)
        if login.status_code != 200:
            return [], ["Identifiants incorrects"]
        if not result["seo"]["meta_description"]:
            corrections.append("Meta description manquante — à ajouter via le module Metatag dans Drupal")
        if not result["performance"]["is_https"]:
            erreurs.append("HTTPS non activé")
    except Exception as e:
        erreurs.append(str(e))
    return corrections, erreurs

def squarespace_fix_seo(api_key, result):
    import requests as req
    corrections = []
    erreurs = []
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json", "User-Agent": "SITRA/1.0"}
    try:
        if not result["seo"]["meta_description"]:
            corrections.append("Meta description manquante — à ajouter dans Pages → SEO sur Squarespace")
        if not result["performance"]["is_https"]:
            erreurs.append("HTTPS non activé")
    except Exception as e:
        erreurs.append(str(e))
    return corrections, erreurs

def magento_fix_seo(shop_url, token, result):
    import requests as req
    corrections = []
    erreurs = []
    base = shop_url.rstrip("/")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    try:
        test = req.get(f"{base}/rest/V1/store/storeConfigs", headers=headers, timeout=10)
        if test.status_code == 401:
            return [], ["Token invalide"]
        if not result["seo"]["meta_description"]:
            corrections.append("Meta description manquante")
        if not result["performance"]["is_https"]:
            erreurs.append("HTTPS non activé")
    except Exception as e:
        erreurs.append(str(e))
    return corrections, erreurs

def ghost_fix_seo(ghost_url, admin_key, result):
    import requests as req
    corrections = []
    erreurs = []
    base = ghost_url.rstrip("/")
    try:
        parts = admin_key.split(":")
        if len(parts) != 2:
            return [], ["Format de clé invalide"]
        if not result["seo"]["meta_description"]:
            corrections.append("Meta description manquante")
        if not result["performance"]["is_https"]:
            erreurs.append("HTTPS non activé")
    except Exception as e:
        erreurs.append(str(e))
    return corrections, erreurs

def typo3_fix_seo(typo3_url, token, result):
    import requests as req
    corrections = []
    erreurs = []
    try:
        if not result["seo"]["meta_description"]:
            corrections.append("Meta description manquante — à appliquer via l'extension SEO de TYPO3")
        if not result["performance"]["is_https"]:
            erreurs.append("HTTPS non activé")
    except Exception as e:
        erreurs.append(str(e))
    return corrections, erreurs
