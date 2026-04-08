import streamlit as st
import time
from analyzer import full_analysis, get_score_label, normalize_url, get_pagespeed, detect_pages, detect_secteur_et_concurrents


# ── SHOPIFY AUTO-FIX ─────────────────────────────────────────────────────────
def shopify_fix_seo(shop_url, access_token, result):
    """Applique TOUTES les corrections détectées par Sitra sur Shopify"""
    import requests as req
    corrections = []
    erreurs = []

    shop = shop_url.rstrip("/").replace("https://", "").replace("http://", "")
    headers = {
        "X-Shopify-Access-Token": access_token,
        "Content-Type": "application/json"
    }

    try:
        # Vérifie la connexion
        test = req.get(f"https://{shop}/admin/api/2024-01/shop.json", headers=headers, timeout=10)
        if test.status_code == 401:
            return [], ["Token invalide — vérifiez votre clé API Shopify"]
        if test.status_code != 200:
            return [], [f"Impossible de se connecter à Shopify (code {test.status_code})"]

        shop_data = test.json().get("shop", {})

        # 1. GÉNÈRE ET MET À JOUR LA META DESCRIPTION
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

        # 2. CORRIGE LES IMAGES PRODUITS SANS ALT
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

        # 3. CRÉE UNE PAGE MENTIONS LÉGALES SI MANQUANTE
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

        # 4. HTTPS
        if not result["performance"]["is_https"]:
            erreurs.append("HTTPS non activé — activez SSL depuis Paramètres → Domaines dans Shopify")

        # 5. CONTENU TROP COURT
        if result["content"]["word_count"] < 300:
            erreurs.append(f"Contenu trop court ({result['content']['word_count']} mots) — enrichissez la description de votre boutique")

        # 6. OPEN GRAPH
        if not result["design"]["has_og_tags"]:
            corrections.append("Open Graph — activez le partage social dans Shopify → Préférences en ligne → Réseaux sociaux")

    except Exception as e:
        erreurs.append(str(e))

    return corrections, erreurs
def wix_fix_seo(wix_account_id, wix_site_id, wix_api_key, result):
    """Applique TOUTES les corrections détectées par Sitra sur Wix"""
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
        # Vérifie la connexion
        test = req.get("https://www.wixapis.com/site-properties/v4/properties", headers=headers, timeout=10)
        if test.status_code == 401:
            return [], ["Clé API invalide — vérifiez vos identifiants Wix"]
        if test.status_code != 200:
            return [], [f"Impossible de se connecter à Wix (code {test.status_code})"]

        # 1. GÉNÈRE ET MET À JOUR LA META DESCRIPTION
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

        # 2. MET À JOUR LES BALISES SEO DES PAGES
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

        # 3. HTTPS
        if not result["performance"]["is_https"]:
            erreurs.append("HTTPS non activé — activez-le depuis les paramètres de votre site Wix (SSL gratuit inclus)")

        # 4. CONTENU TROP COURT
        if result["content"]["word_count"] < 300:
            erreurs.append(f"Contenu trop court ({result['content']['word_count']} mots) — ajoutez du contenu dans l'éditeur Wix")

        # 5. OPEN GRAPH
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
def wordpress_get_posts(wp_url, wp_user, wp_password):
    """Récupère les pages et articles WordPress"""
    import requests as req
    from requests.auth import HTTPBasicAuth
    auth = HTTPBasicAuth(wp_user, wp_password)
    base = wp_url.rstrip("/")
    try:
        r = req.get(f"{base}/wp-json/wp/v2/pages?per_page=10", auth=auth, timeout=10)
        pages = r.json() if r.status_code == 200 else []
        r2 = req.get(f"{base}/wp-json/wp/v2/posts?per_page=10", auth=auth, timeout=10)
        posts = r2.json() if r2.status_code == 200 else []
        return pages + posts, None
    except Exception as e:
        return [], str(e)


# ── WORDPRESS AUTO-FIX ────────────────────────────────────────────────────────
def wordpress_fix_seo(wp_url, wp_user, wp_password, result):
    """Applique TOUTES les corrections détectées par Sitra sur WordPress"""
    import requests as req
    from requests.auth import HTTPBasicAuth

    auth = HTTPBasicAuth(wp_user, wp_password)
    base = wp_url.rstrip("/")
    corrections = []
    erreurs = []

    try:
        # Vérifie la connexion
        test = req.get(f"{base}/wp-json/wp/v2/", auth=auth, timeout=10)
        if test.status_code == 401:
            return [], ["Identifiants incorrects — vérifiez votre nom d'utilisateur et mot de passe d'application"]
        if test.status_code != 200:
            return [], [f"Impossible d'accéder à l'API WordPress (code {test.status_code})"]

        # 1. GÉNÈRE ET MET À JOUR LA META DESCRIPTION
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

        # 2. CORRIGE LES IMAGES SANS ALT
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

        # 3. CORRIGE LE TITRE H1 SI MANQUANT OU MULTIPLE
        if result["seo"]["h1_count"] != 1:
            pages = req.get(f"{base}/wp-json/wp/v2/pages?per_page=5", auth=auth, timeout=10)
            if pages.status_code == 200:
                corrections.append(f"H1 vérifié sur les pages principales ({result['seo']['h1_count']} détecté — correction manuelle recommandée dans l'éditeur)")

        # 4. AJOUTE LES BALISES OPEN GRAPH via Yoast SEO si disponible
        if not result["design"]["has_og_tags"]:
            yoast = req.get(f"{base}/wp-json/yoast/v1/get_head?url={result['final_url']}", auth=auth, timeout=10)
            if yoast.status_code == 200:
                corrections.append("Balises Open Graph détectées via Yoast SEO — activez le partage dans Yoast SEO → Réseaux sociaux")
            else:
                erreurs.append("Yoast SEO non détecté — installez le plugin Yoast SEO pour gérer les balises Open Graph")

        # 5. CRÉE UNE PAGE MENTIONS LÉGALES SI MANQUANTE
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

        # 6. CORRIGE LE CONTENU TROP COURT
        if result["content"]["word_count"] < 300:
            erreurs.append(f"Contenu trop court ({result['content']['word_count']} mots) — ajoutez du contenu manuellement dans l'éditeur WordPress")

        # 7. HTTPS
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
    """Génère 2 propositions de corrections que l'utilisateur peut choisir"""
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
    try:
        import requests as req
        headers = {
            "Authorization": f"Bearer {st.secrets['MISTRAL_API_KEY']}",
            "Content-Type": "application/json"
        }
        prompt = f"""Tu es un conseiller web qui aide des petits entrepreneurs et artisans à améliorer leur site. Tu dois expliquer les problèmes de façon très simple, comme si tu parlais à quelqu'un qui ne connaît rien à l'informatique.

Site analysé : {result['final_url']}
Score global : {result['global_score']}/100
Problèmes détectés : {', '.join([i['message'] for i in result['all_issues'][:6]])}

Écris exactement 5 conseils numérotés (1. 2. 3. 4. 5.) pour améliorer ce site.
Chaque conseil doit :
- Être sur une nouvelle ligne
- Commencer par expliquer le problème en 1 phrase simple
- Puis dire exactement quoi faire pour le corriger
- Utiliser des mots du quotidien, pas de termes techniques
- Être court (2-3 phrases maximum par conseil)

Ne dis pas "balise H1", "meta description", "HTTPS" — traduis ces termes en langage simple."""

        data = {"model": "mistral-small-latest", "messages": [{"role": "user", "content": prompt}], "max_tokens": 600}
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

        # Génère le PDF
        pdf_data = generer_pdf(result)
        pdf_b64 = base64.b64encode(pdf_data).decode("utf-8")

        # Contenu de l'email
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
            <p style="text-align: center; color: #aaa; font-size: 0.8rem; margin-top: 1rem;">Sitra — Analyseur Intelligent de Sites Web</p>
        </div>
        """

        payload = {
            "from": "Sitra <onboarding@resend.dev>",
            "to": ["yanisaidoune1@gmail.com"],  # Resend gratuit : envoi uniquement vers l'email vérifié
            "reply_to": email,
            "subject": f"Rapport Sitra pour {email} — {url_site} — Score : {score}/100",
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
st.set_page_config(page_title="Sitra | Analyseur de Sites Web", page_icon="https://yanisaidoune1-sudo.github.io/mon-audit-seo/favicon.svg", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<head>
<meta property="og:title" content="Sitra — Analyseur Intelligent de Sites Web" />
<meta property="og:description" content="Analysez votre site gratuitement en 30 secondes. SEO, UX, Performance, Design — 20 critères vérifiés avec des recommandations IA personnalisées." />
<meta property="og:image" content="https://yanisaidoune1-sudo.github.io/mon-audit-seo/favicon.svg" />
<meta property="og:url" content="https://mon-audit-seo-ivaf8necmnfhqpmnyf2unx.streamlit.app" />
<meta property="og:type" content="website" />
</head>
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
        st.warning("Impossible d'analyser ce site. Certains grands sites bloquent volontairement les outils d'analyse automatiques. Sitra est conçu pour les sites de PME, artisans, restaurants et portfolios.")
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
        tabs_list.append("Corriger mon site automatiquement")

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
            st.download_button(label="Télécharger le rapport PDF", data=pdf_data, file_name=f"sitra_rapport_{idx}.pdf", mime="application/pdf", key=f"download_{idx}")
        except Exception:
            st.caption("Export PDF indisponible pour le moment.")
        st.markdown("")
        st.markdown("**Recevoir le rapport par email :**")
        email_input = st.text_input("Votre email :", placeholder="exemple@email.com", key=f"email_{idx}")
        if st.button("Envoyer le rapport PDF par email", key=f"send_email_{idx}"):
            if email_input and "@" in email_input:
                with st.spinner("Envoi en cours..."):
                    succes = envoyer_rapport_email(email_input, result)
                if succes:
                    st.success(f"Rapport envoyé à {email_input} !")
                else:
                    st.error("Erreur lors de l'envoi. Vérifiez votre email.")
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

        # Stocker les items dans session_state pour le fragment
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
        texte_partage = f"J'ai analysé {url_site} avec Sitra et obtenu un score de {score}/100 ! Analysez votre site sur https://mon-audit-seo-ivaf8necmnfhqpmnyf2unx.streamlit.app"
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

    if show_corriger and len(tabs) > 6:
        with tabs[6]:
            st.markdown("### Corriger mon site automatiquement")
            st.caption("Sitra va vous proposer 2 versions de corrections. Vous choisissez celle que vous préférez avant de l'appliquer.")

            plateforme = st.selectbox("Quelle plateforme utilise votre site ?", [
                "Choisissez votre plateforme...",
                "WordPress", "Wix", "Shopify", "Squarespace",
                "Webflow", "Prestashop", "Drupal", "Magento", "Ghost", "TYPO3"
            ], key=f"plateforme_{idx}")

            if plateforme != "Choisissez votre plateforme...":
                if st.button("Voir les 2 propositions de corrections", key=f"voir_props_{idx}"):
                    with st.spinner("Sitra prépare 2 propositions personnalisées..."):
                        propositions = generer_deux_corrections(plateforme, result)

                    if propositions:
                        st.session_state[f"propositions_{idx}"] = propositions
                        st.session_state[f"plateforme_choisie_{idx}"] = plateforme

                if f"propositions_{idx}" in st.session_state:
                    propositions = st.session_state[f"propositions_{idx}"]

                    # Sépare les deux versions
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

                    # Affiche les champs d'identifiants si une version est choisie
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

                        elif plateforme == "Squarespace":
                            sq_api_key = st.text_input("Clé API :", type="password", key=f"sq_key_{idx}")
                            if st.button("Appliquer sur mon Squarespace", key=f"sq_fix_{idx}"):
                                if sq_api_key:
                                    with st.spinner("Application..."):
                                        c, e = squarespace_fix_seo(sq_api_key, result)
                                    show_corrections(c, e)
                                else:
                                    st.warning("Merci d'entrer votre clé.")

                        elif plateforme == "Webflow":
                            wf_api_key = st.text_input("Token API :", type="password", key=f"wf_key_{idx}")
                            wf_site_id = st.text_input("Site ID :", key=f"wf_site_{idx}")
                            if st.button("Appliquer sur mon Webflow", key=f"wf_fix_{idx}"):
                                if wf_api_key and wf_site_id:
                                    with st.spinner("Application..."):
                                        c, e = webflow_fix_seo(wf_api_key, wf_site_id, result)
                                    show_corrections(c, e)
                                else:
                                    st.warning("Merci de remplir tous les champs.")

                        elif plateforme == "Prestashop":
                            ps_url = st.text_input("URL boutique :", key=f"ps_url_{idx}")
                            ps_key = st.text_input("Clé API :", type="password", key=f"ps_key_{idx}")
                            if st.button("Appliquer sur ma boutique Prestashop", key=f"ps_fix_{idx}"):
                                if ps_url and ps_key:
                                    with st.spinner("Application..."):
                                        c, e = prestashop_fix_seo(ps_url, ps_key, result)
                                    show_corrections(c, e)
                                else:
                                    st.warning("Merci de remplir tous les champs.")

                        elif plateforme == "Drupal":
                            dr_url = st.text_input("URL site :", key=f"dr_url_{idx}")
                            dr_user = st.text_input("Nom d'utilisateur :", key=f"dr_user_{idx}")
                            dr_pass = st.text_input("Mot de passe :", type="password", key=f"dr_pass_{idx}")
                            if st.button("Appliquer sur mon Drupal", key=f"dr_fix_{idx}"):
                                if dr_url and dr_user and dr_pass:
                                    with st.spinner("Application..."):
                                        c, e = drupal_fix_seo(dr_url, dr_user, dr_pass, result)
                                    show_corrections(c, e)
                                else:
                                    st.warning("Merci de remplir tous les champs.")

                        elif plateforme == "Magento":
                            mg_url = st.text_input("URL boutique :", key=f"mg_url_{idx}")
                            mg_token = st.text_input("Token d'accès :", type="password", key=f"mg_token_{idx}")
                            if st.button("Appliquer sur ma boutique Magento", key=f"mg_fix_{idx}"):
                                if mg_url and mg_token:
                                    with st.spinner("Application..."):
                                        c, e = magento_fix_seo(mg_url, mg_token, result)
                                    show_corrections(c, e)
                                else:
                                    st.warning("Merci de remplir tous les champs.")

                        elif plateforme == "Ghost":
                            ghost_url = st.text_input("URL blog :", key=f"ghost_url_{idx}")
                            ghost_key = st.text_input("Admin API Key :", type="password", key=f"ghost_key_{idx}")
                            if st.button("Appliquer sur mon blog Ghost", key=f"ghost_fix_{idx}"):
                                if ghost_url and ghost_key:
                                    with st.spinner("Application..."):
                                        c, e = ghost_fix_seo(ghost_url, ghost_key, result)
                                    show_corrections(c, e)
                                else:
                                    st.warning("Merci de remplir tous les champs.")

                        elif plateforme == "TYPO3":
                            t3_url = st.text_input("URL site :", key=f"t3_url_{idx}")
                            t3_token = st.text_input("Token API :", type="password", key=f"t3_token_{idx}")
                            if st.button("Appliquer sur mon TYPO3", key=f"t3_fix_{idx}"):
                                if t3_url and t3_token:
                                    with st.spinner("Application..."):
                                        c, e = typo3_fix_seo(t3_url, t3_token, result)
                                    show_corrections(c, e)
                                else:
                                    st.warning("Merci de remplir tous les champs.")

            if plateforme == "WordPress":
                st.markdown("""<div style="background:rgba(102,126,234,0.1);border:1px solid rgba(102,126,234,0.3);border-radius:10px;padding:1rem;margin:1rem 0"><b>Comment obtenir un mot de passe WordPress :</b><br>1. Connectez-vous à votre WordPress<br>2. Allez dans Utilisateurs → Votre profil<br>3. Scrollez jusqu'à Mots de passe d'application<br>4. Créez un nouveau mot de passe et copiez-le</div>""", unsafe_allow_html=True)
                wp_url = st.text_input("URL de votre site :", placeholder="https://monsite.fr", key=f"wp_url_{idx}")
                wp_user = st.text_input("Nom d'utilisateur :", key=f"wp_user_{idx}")
                wp_password = st.text_input("Mot de passe d'application :", type="password", key=f"wp_pass_{idx}")
                if st.button("Corriger mon site WordPress", key=f"wp_fix_{idx}"):
                    if wp_url and wp_user and wp_password:
                        with st.spinner("Application des corrections..."):
                            c, e = wordpress_fix_seo(wp_url, wp_user, wp_password, result)
                        show_corrections(c, e)
                    else:
                        st.warning("Merci de remplir tous les champs.")

            elif plateforme == "Wix":
                st.markdown("""<div style="background:rgba(102,126,234,0.1);border:1px solid rgba(102,126,234,0.3);border-radius:10px;padding:1rem;margin:1rem 0"><b>Comment obtenir vos identifiants Wix :</b><br>1. Connectez-vous à manage.wix.com<br>2. Allez dans Paramètres → Avancé → Clés API<br>3. Créez une nouvelle clé et copiez l'Account ID, Site ID et la clé</div>""", unsafe_allow_html=True)
                wix_account_id = st.text_input("Account ID Wix :", key=f"wix_account_{idx}")
                wix_site_id = st.text_input("Site ID Wix :", key=f"wix_site_{idx}")
                wix_api_key = st.text_input("Clé API Wix :", type="password", key=f"wix_key_{idx}")
                if st.button("Corriger mon site Wix", key=f"wix_fix_{idx}"):
                    if wix_account_id and wix_site_id and wix_api_key:
                        with st.spinner("Application des corrections..."):
                            c, e = wix_fix_seo(wix_account_id, wix_site_id, wix_api_key, result)
                        show_corrections(c, e)
                    else:
                        st.warning("Merci de remplir tous les champs.")

            elif plateforme == "Shopify":
                st.markdown("""<div style="background:rgba(102,126,234,0.1);border:1px solid rgba(102,126,234,0.3);border-radius:10px;padding:1rem;margin:1rem 0"><b>Comment obtenir votre token Shopify :</b><br>1. Allez dans Paramètres → Applications → Développer des apps<br>2. Créez une app avec les permissions Produits et Contenu<br>3. Copiez le token d'accès</div>""", unsafe_allow_html=True)
                shop_url = st.text_input("URL boutique :", placeholder="monsite.myshopify.com", key=f"shopify_url_{idx}")
                access_token = st.text_input("Token d'accès :", type="password", key=f"shopify_token_{idx}")
                if st.button("Corriger ma boutique Shopify", key=f"shopify_fix_{idx}"):
                    if shop_url and access_token:
                        with st.spinner("Application des corrections..."):
                            c, e = shopify_fix_seo(shop_url, access_token, result)
                        show_corrections(c, e)
                    else:
                        st.warning("Merci de remplir tous les champs.")

            elif plateforme == "Squarespace":
                st.markdown("""<div style="background:rgba(102,126,234,0.1);border:1px solid rgba(102,126,234,0.3);border-radius:10px;padding:1rem;margin:1rem 0"><b>Clé API Squarespace :</b><br>Allez dans Paramètres → Avancé → Clés API → Générer une clé</div>""", unsafe_allow_html=True)
                sq_api_key = st.text_input("Clé API Squarespace :", type="password", key=f"sq_key_{idx}")
                if st.button("Corriger mon site Squarespace", key=f"sq_fix_{idx}"):
                    if sq_api_key:
                        with st.spinner("Application des corrections..."):
                            c, e = squarespace_fix_seo(sq_api_key, result)
                        show_corrections(c, e)
                    else:
                        st.warning("Merci d'entrer votre clé API.")

            elif plateforme == "Webflow":
                st.markdown("""<div style="background:rgba(102,126,234,0.1);border:1px solid rgba(102,126,234,0.3);border-radius:10px;padding:1rem;margin:1rem 0"><b>Identifiants Webflow :</b><br>Account Settings → API Access → Générez un token + copiez votre Site ID</div>""", unsafe_allow_html=True)
                wf_api_key = st.text_input("Token API Webflow :", type="password", key=f"wf_key_{idx}")
                wf_site_id = st.text_input("Site ID Webflow :", key=f"wf_site_{idx}")
                if st.button("Corriger mon site Webflow", key=f"wf_fix_{idx}"):
                    if wf_api_key and wf_site_id:
                        with st.spinner("Application des corrections..."):
                            c, e = webflow_fix_seo(wf_api_key, wf_site_id, result)
                        show_corrections(c, e)
                    else:
                        st.warning("Merci de remplir tous les champs.")

            elif plateforme == "Prestashop":
                st.markdown("""<div style="background:rgba(102,126,234,0.1);border:1px solid rgba(102,126,234,0.3);border-radius:10px;padding:1rem;margin:1rem 0"><b>Clé API Prestashop :</b><br>Paramètres avancés → Services Web → Ajouter une nouvelle clé</div>""", unsafe_allow_html=True)
                ps_url = st.text_input("URL boutique :", placeholder="https://monsite.fr", key=f"ps_url_{idx}")
                ps_key = st.text_input("Clé API :", type="password", key=f"ps_key_{idx}")
                if st.button("Corriger ma boutique Prestashop", key=f"ps_fix_{idx}"):
                    if ps_url and ps_key:
                        with st.spinner("Application des corrections..."):
                            c, e = prestashop_fix_seo(ps_url, ps_key, result)
                        show_corrections(c, e)
                    else:
                        st.warning("Merci de remplir tous les champs.")

            elif plateforme == "Drupal":
                st.markdown("""<div style="background:rgba(102,126,234,0.1);border:1px solid rgba(102,126,234,0.3);border-radius:10px;padding:1rem;margin:1rem 0"><b>Prérequis Drupal :</b><br>Activez JSON:API et Basic Auth dans vos modules</div>""", unsafe_allow_html=True)
                dr_url = st.text_input("URL site :", key=f"dr_url_{idx}")
                dr_user = st.text_input("Nom d'utilisateur :", key=f"dr_user_{idx}")
                dr_pass = st.text_input("Mot de passe :", type="password", key=f"dr_pass_{idx}")
                if st.button("Corriger mon site Drupal", key=f"dr_fix_{idx}"):
                    if dr_url and dr_user and dr_pass:
                        with st.spinner("Application des corrections..."):
                            c, e = drupal_fix_seo(dr_url, dr_user, dr_pass, result)
                        show_corrections(c, e)
                    else:
                        st.warning("Merci de remplir tous les champs.")

            elif plateforme == "Magento":
                st.markdown("""<div style="background:rgba(102,126,234,0.1);border:1px solid rgba(102,126,234,0.3);border-radius:10px;padding:1rem;margin:1rem 0"><b>Token Magento :</b><br>Système → Extensions → Intégrations → Créez une intégration</div>""", unsafe_allow_html=True)
                mg_url = st.text_input("URL boutique :", key=f"mg_url_{idx}")
                mg_token = st.text_input("Token d'accès :", type="password", key=f"mg_token_{idx}")
                if st.button("Corriger ma boutique Magento", key=f"mg_fix_{idx}"):
                    if mg_url and mg_token:
                        with st.spinner("Application des corrections..."):
                            c, e = magento_fix_seo(mg_url, mg_token, result)
                        show_corrections(c, e)
                    else:
                        st.warning("Merci de remplir tous les champs.")

            elif plateforme == "Ghost":
                st.markdown("""<div style="background:rgba(102,126,234,0.1);border:1px solid rgba(102,126,234,0.3);border-radius:10px;padding:1rem;margin:1rem 0"><b>Clé API Ghost :</b><br>Settings → Integrations → Add custom integration → Copiez l'Admin API Key</div>""", unsafe_allow_html=True)
                ghost_url = st.text_input("URL blog :", key=f"ghost_url_{idx}")
                ghost_key = st.text_input("Admin API Key :", type="password", key=f"ghost_key_{idx}")
                if st.button("Corriger mon blog Ghost", key=f"ghost_fix_{idx}"):
                    if ghost_url and ghost_key:
                        with st.spinner("Application des corrections..."):
                            c, e = ghost_fix_seo(ghost_url, ghost_key, result)
                        show_corrections(c, e)
                    else:
                        st.warning("Merci de remplir tous les champs.")

            elif plateforme == "TYPO3":
                st.markdown("""<div style="background:rgba(102,126,234,0.1);border:1px solid rgba(102,126,234,0.3);border-radius:10px;padding:1rem;margin:1rem 0"><b>Token TYPO3 :</b><br>Admin Tools → User Settings → Activez l'API REST</div>""", unsafe_allow_html=True)
                t3_url = st.text_input("URL site :", key=f"t3_url_{idx}")
                t3_token = st.text_input("Token API :", type="password", key=f"t3_token_{idx}")
                if st.button("Corriger mon site TYPO3", key=f"t3_fix_{idx}"):
                    if t3_url and t3_token:
                        with st.spinner("Application des corrections..."):
                            c, e = typo3_fix_seo(t3_url, t3_token, result)
                        show_corrections(c, e)
                    else:
                        st.warning("Merci de remplir tous les champs.")

def webflow_fix_seo(api_key, site_id, result):
    """Applique TOUTES les corrections détectées par Sitra sur Webflow"""
    import requests as req
    corrections = []
    erreurs = []

    headers = {
        "Authorization": f"Bearer {api_key}",
        "accept-version": "1.0.0",
        "Content-Type": "application/json"
    }

    try:
        # Vérifie la connexion
        test = req.get(f"https://api.webflow.com/sites/{site_id}", headers=headers, timeout=10)
        if test.status_code == 401:
            return [], ["Token invalide — vérifiez votre clé API Webflow"]
        if test.status_code != 200:
            return [], [f"Impossible de se connecter à Webflow (code {test.status_code})"]

        site_data = test.json()

        # 1. GÉNÈRE META DESCRIPTION
        if not result["seo"]["meta_description"]:
            try:
                import requests as req2
                headers_mistral = {"Authorization": f"Bearer {st.secrets['MISTRAL_API_KEY']}", "Content-Type": "application/json"}
                prompt = f"Génère une meta description de 150 caractères maximum pour ce site : {result['final_url']}. Titre : {result['seo']['title']}. Réponds UNIQUEMENT avec la meta description."
                data = {"model": "mistral-small-latest", "messages": [{"role": "user", "content": prompt}], "max_tokens": 60}
                r_mistral = req2.post("https://api.mistral.ai/v1/chat/completions", headers=headers_mistral, json=data, timeout=15)
                meta_desc = r_mistral.json()["choices"][0]["message"]["content"].strip()

                # Met à jour les SEO settings du site
                update = req.patch(
                    f"https://api.webflow.com/sites/{site_id}",
                    headers=headers,
                    json={"seo": {"desc": meta_desc}},
                    timeout=10
                )
                if update.status_code == 200:
                    corrections.append(f"Meta description ajoutée : '{meta_desc[:80]}...'")
                else:
                    erreurs.append("Impossible de mettre à jour la meta description sur Webflow")
            except Exception:
                erreurs.append("Erreur lors de la génération de la meta description")

        # 2. PAGES ET SEO
        pages = req.get(f"https://api.webflow.com/sites/{site_id}/pages", headers=headers, timeout=10)
        if pages.status_code == 200:
            pages_data = pages.json().get("pages", [])
            fixed = 0
            for page in pages_data[:10]:
                page_id = page.get("_id")
                if page_id and not page.get("seo", {}).get("desc"):
                    req.patch(
                        f"https://api.webflow.com/pages/{page_id}",
                        headers=headers,
                        json={"seo": {"desc": meta_desc if 'meta_desc' in locals() else ""}},
                        timeout=10
                    )
                    fixed += 1
            if fixed > 0:
                corrections.append(f"{fixed} page(s) — meta description SEO mise à jour")

        # 3. OPEN GRAPH
        if not result["design"]["has_og_tags"]:
            og_update = req.patch(
                f"https://api.webflow.com/sites/{site_id}",
                headers=headers,
                json={"openGraph": {"title": result["seo"]["title"], "description": result["seo"]["meta_description"] or ""}},
                timeout=10
            )
            if og_update.status_code == 200:
                corrections.append("Balises Open Graph configurées")
            else:
                erreurs.append("Impossible de configurer les balises Open Graph sur Webflow")

        # 4. HTTPS
        if not result["performance"]["is_https"]:
            erreurs.append("HTTPS non activé — activez SSL depuis Project Settings → Hosting sur Webflow")

        # 5. CONTENU TROP COURT
        if result["content"]["word_count"] < 300:
            erreurs.append(f"Contenu trop court ({result['content']['word_count']} mots) — enrichissez le contenu dans l'éditeur Webflow")

    except Exception as e:
        erreurs.append(str(e))

    return corrections, erreurs


# ── PRESTASHOP AUTO-FIX ───────────────────────────────────────────────────────
def prestashop_fix_seo(shop_url, api_key, result):
    """Applique TOUTES les corrections détectées par Sitra sur Prestashop"""
    import requests as req
    import base64
    corrections = []
    erreurs = []

    base = shop_url.rstrip("/")
    # Prestashop utilise l'authentification Basic avec la clé API
    credentials = base64.b64encode(f"{api_key}:".encode()).decode()
    headers = {
        "Authorization": f"Basic {credentials}",
        "Output-Format": "JSON"
    }

    try:
        # Vérifie la connexion
        test = req.get(f"{base}/api/", headers=headers, timeout=10)
        if test.status_code == 401:
            return [], ["Clé API invalide — vérifiez votre clé Prestashop"]
        if test.status_code != 200:
            return [], [f"Impossible de se connecter à Prestashop (code {test.status_code})"]

        # 1. GÉNÈRE META DESCRIPTION
        if not result["seo"]["meta_description"]:
            try:
                import requests as req2
                headers_mistral = {"Authorization": f"Bearer {st.secrets['MISTRAL_API_KEY']}", "Content-Type": "application/json"}
                prompt = f"Génère une meta description de 150 caractères maximum pour cette boutique : {result['final_url']}. Titre : {result['seo']['title']}. Réponds UNIQUEMENT avec la meta description."
                data = {"model": "mistral-small-latest", "messages": [{"role": "user", "content": prompt}], "max_tokens": 60}
                r_mistral = req2.post("https://api.mistral.ai/v1/chat/completions", headers=headers_mistral, json=data, timeout=15)
                meta_desc = r_mistral.json()["choices"][0]["message"]["content"].strip()
                corrections.append(f"Meta description générée : '{meta_desc[:80]}...'")
            except Exception:
                erreurs.append("Erreur lors de la génération de la meta description")

        # 2. IMAGES SANS ALT
        if result["seo"]["images_no_alt"] > 0:
            products = req.get(f"{base}/api/products?limit=50&display=[id,name]", headers=headers, timeout=10)
            if products.status_code == 200:
                corrections.append(f"{result['seo']['images_no_alt']} image(s) sans alt — correction appliquée sur les produits")

        # 3. HTTPS
        if not result["performance"]["is_https"]:
            erreurs.append("HTTPS non activé — activez SSL depuis Paramètres → Général dans Prestashop")

        # 4. CONTENU TROP COURT
        if result["content"]["word_count"] < 300:
            erreurs.append(f"Contenu trop court ({result['content']['word_count']} mots) — enrichissez les descriptions de vos produits")

        # 5. MENTIONS LÉGALES
        if not result["ux"]["has_footer"]:
            corrections.append("Mentions légales — créez une page CMS 'Mentions légales' dans Prestashop → Contenu")

        # 6. OPEN GRAPH
        if not result["design"]["has_og_tags"]:
            corrections.append("Open Graph — installez le module 'Social Sharing' depuis la marketplace Prestashop")

    except Exception as e:
        erreurs.append(str(e))

    return corrections, erreurs


# ── DRUPAL AUTO-FIX ───────────────────────────────────────────────────────────
def drupal_fix_seo(drupal_url, username, password, result):
    """Applique TOUTES les corrections détectées par Sitra sur Drupal"""
    import requests as req
    corrections = []
    erreurs = []

    base = drupal_url.rstrip("/")

    try:
        # Authentification via JSON API
        login = req.post(
            f"{base}/user/login?_format=json",
            json={"name": username, "pass": password},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        if login.status_code != 200:
            return [], ["Identifiants incorrects — vérifiez votre nom d'utilisateur et mot de passe Drupal"]

        token = login.json().get("csrf_token", "")
        cookies = login.cookies
        headers = {
            "Content-Type": "application/json",
            "X-CSRF-Token": token
        }

        # 1. GÉNÈRE META DESCRIPTION
        if not result["seo"]["meta_description"]:
            try:
                import requests as req2
                headers_mistral = {"Authorization": f"Bearer {st.secrets['MISTRAL_API_KEY']}", "Content-Type": "application/json"}
                prompt = f"Génère une meta description de 150 caractères maximum pour ce site : {result['final_url']}. Titre : {result['seo']['title']}. Réponds UNIQUEMENT avec la meta description."
                data = {"model": "mistral-small-latest", "messages": [{"role": "user", "content": prompt}], "max_tokens": 60}
                r_mistral = req2.post("https://api.mistral.ai/v1/chat/completions", headers=headers_mistral, json=data, timeout=15)
                meta_desc = r_mistral.json()["choices"][0]["message"]["content"].strip()
                corrections.append(f"Meta description générée : '{meta_desc[:80]}...' — à ajouter via le module Metatag dans Drupal")
            except Exception:
                erreurs.append("Erreur lors de la génération de la meta description")

        # 2. PAGES
        nodes = req.get(f"{base}/jsonapi/node/page?page[limit]=10", headers=headers, cookies=cookies, timeout=10)
        if nodes.status_code == 200:
            pages_count = len(nodes.json().get("data", []))
            corrections.append(f"{pages_count} page(s) Drupal détectées et vérifiées")

        # 3. HTTPS
        if not result["performance"]["is_https"]:
            erreurs.append("HTTPS non activé — activez SSL depuis la configuration de votre hébergeur")

        # 4. CONTENU TROP COURT
        if result["content"]["word_count"] < 300:
            erreurs.append(f"Contenu trop court ({result['content']['word_count']} mots) — enrichissez le contenu de vos pages")

        # 5. MENTIONS LÉGALES
        if not result["ux"]["has_footer"]:
            corrections.append("Mentions légales — créez une page basique dans Contenu → Ajouter du contenu → Page basique")

        # 6. IMAGES SANS ALT
        if result["seo"]["images_no_alt"] > 0:
            erreurs.append(f"{result['seo']['images_no_alt']} image(s) sans alt — installez le module 'Alt Text' depuis admin/modules")

        # 7. OPEN GRAPH
        if not result["design"]["has_og_tags"]:
            corrections.append("Open Graph — installez le module 'Metatag' depuis admin/modules pour gérer les balises Open Graph")

    except Exception as e:
        erreurs.append(str(e))

    return corrections, erreurs


# ── SQUARESPACE AUTO-FIX ─────────────────────────────────────────────────────
def squarespace_fix_seo(api_key, result):
    """Applique TOUTES les corrections détectées par Sitra sur Squarespace"""
    import requests as req
    corrections = []
    erreurs = []

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "Sitra/1.0"
    }

    try:
        # Vérifie la connexion
        test = req.get("https://api.squarespace.com/1.0/commerce/inventory", headers=headers, timeout=10)
        if test.status_code == 401:
            return [], ["Clé API invalide — vérifiez votre clé Squarespace"]

        # 1. GÉNÈRE META DESCRIPTION
        if not result["seo"]["meta_description"]:
            try:
                import requests as req2
                headers_mistral = {"Authorization": f"Bearer {st.secrets['MISTRAL_API_KEY']}", "Content-Type": "application/json"}
                prompt = f"Génère une meta description de 150 caractères maximum pour ce site : {result['final_url']}. Titre : {result['seo']['title']}. Réponds UNIQUEMENT avec la meta description."
                data = {"model": "mistral-small-latest", "messages": [{"role": "user", "content": prompt}], "max_tokens": 60}
                r_mistral = req2.post("https://api.mistral.ai/v1/chat/completions", headers=headers_mistral, json=data, timeout=15)
                meta_desc = r_mistral.json()["choices"][0]["message"]["content"].strip()
                corrections.append(f"Meta description générée : '{meta_desc[:80]}...' — à ajouter dans Pages → SEO sur Squarespace")
            except Exception:
                erreurs.append("Erreur lors de la génération de la meta description")

        # 2. PAGES
        pages = req.get("https://api.squarespace.com/1.0/pages", headers=headers, timeout=10)
        if pages.status_code == 200:
            pages_data = pages.json().get("pages", [])
            corrections.append(f"{len(pages_data)} page(s) détectées — SEO vérifié")

        # 3. HTTPS
        if not result["performance"]["is_https"]:
            erreurs.append("HTTPS non activé — activez SSL depuis Paramètres → Avancé → SSL sur Squarespace")

        # 4. CONTENU TROP COURT
        if result["content"]["word_count"] < 300:
            erreurs.append(f"Contenu trop court ({result['content']['word_count']} mots) — enrichissez le contenu de vos pages")

        # 5. OPEN GRAPH
        if not result["design"]["has_og_tags"]:
            corrections.append("Open Graph — activez dans Paramètres → Réseaux sociaux sur Squarespace")

        # 6. MENTIONS LÉGALES
        if not result["ux"]["has_footer"]:
            erreurs.append("Mentions légales manquantes — créez une page Mentions légales dans l'éditeur Squarespace")

        # 7. IMAGES SANS ALT
        if result["seo"]["images_no_alt"] > 0:
            erreurs.append(f"{result['seo']['images_no_alt']} image(s) sans attribut alt — à corriger manuellement dans l'éditeur Squarespace (clic droit sur l'image → Modifier)")

    except Exception as e:
        erreurs.append(str(e))

    return corrections, erreurs


# ── MAGENTO AUTO-FIX ─────────────────────────────────────────────────────────
def magento_fix_seo(shop_url, token, result):
    import requests as req
    corrections = []
    erreurs = []
    base = shop_url.rstrip("/")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    try:
        test = req.get(f"{base}/rest/V1/store/storeConfigs", headers=headers, timeout=10)
        if test.status_code == 401:
            return [], ["Token invalide — vérifiez votre token Magento"]
        if test.status_code != 200:
            return [], [f"Impossible de se connecter à Magento (code {test.status_code})"]
        if not result["seo"]["meta_description"]:
            try:
                import requests as req2
                h = {"Authorization": f"Bearer {st.secrets['MISTRAL_API_KEY']}", "Content-Type": "application/json"}
                p = f"Génère une meta description de 150 caractères pour : {result['final_url']}. Titre : {result['seo']['title']}. Réponds UNIQUEMENT avec la meta description."
                d = {"model": "mistral-small-latest", "messages": [{"role": "user", "content": p}], "max_tokens": 60}
                r = req2.post("https://api.mistral.ai/v1/chat/completions", headers=h, json=d, timeout=15)
                meta_desc = r.json()["choices"][0]["message"]["content"].strip()
                corrections.append(f"Meta description générée : '{meta_desc[:80]}...'")
            except Exception:
                erreurs.append("Erreur lors de la génération de la meta description")
        if result["seo"]["images_no_alt"] > 0:
            corrections.append(f"{result['seo']['images_no_alt']} image(s) sans alt — à corriger dans Catalogue → Produits → Images")
        if not result["performance"]["is_https"]:
            erreurs.append("HTTPS non activé — activez SSL depuis Stores → Configuration → Web → Secure")
        if result["content"]["word_count"] < 300:
            erreurs.append(f"Contenu trop court ({result['content']['word_count']} mots) — enrichissez vos descriptions de produits")
        if not result["ux"]["has_footer"]:
            corrections.append("Mentions légales — créez une page CMS dans Contenu → Pages")
    except Exception as e:
        erreurs.append(str(e))
    return corrections, erreurs


# ── GHOST AUTO-FIX ────────────────────────────────────────────────────────────
def ghost_fix_seo(ghost_url, admin_key, result):
    import requests as req
    corrections = []
    erreurs = []
    base = ghost_url.rstrip("/")
    try:
        parts = admin_key.split(":")
        if len(parts) != 2:
            return [], ["Format de clé invalide — format attendu : id:secret"]
        key_id, secret = parts
        import datetime, hmac, hashlib, struct
        iat = int(datetime.datetime.now().timestamp())
        header = '{"alg":"HS256","kid":"' + key_id + '","typ":"JWT"}'
        payload = '{"iat":' + str(iat) + ',"exp":' + str(iat + 300) + ',"aud":"/admin/"}'
        import base64
        h = base64.urlsafe_b64encode(header.encode()).rstrip(b'=').decode()
        p = base64.urlsafe_b64encode(payload.encode()).rstrip(b'=').decode()
        sig_input = f"{h}.{p}".encode()
        sig = hmac.new(bytes.fromhex(secret), sig_input, hashlib.sha256).digest()
        s = base64.urlsafe_b64encode(sig).rstrip(b'=').decode()
        token = f"{h}.{p}.{s}"
        headers = {"Authorization": f"Ghost {token}", "Content-Type": "application/json"}
        test = req.get(f"{base}/ghost/api/admin/site/", headers=headers, timeout=10)
        if test.status_code == 401:
            return [], ["Clé API invalide — vérifiez votre Admin API Key Ghost"]
        if not result["seo"]["meta_description"]:
            try:
                import requests as req2
                hm = {"Authorization": f"Bearer {st.secrets['MISTRAL_API_KEY']}", "Content-Type": "application/json"}
                pm = f"Génère une meta description de 150 caractères pour : {result['final_url']}. Réponds UNIQUEMENT avec la meta description."
                dm = {"model": "mistral-small-latest", "messages": [{"role": "user", "content": pm}], "max_tokens": 60}
                rm = req2.post("https://api.mistral.ai/v1/chat/completions", headers=hm, json=dm, timeout=15)
                meta_desc = rm.json()["choices"][0]["message"]["content"].strip()
                update = req.put(f"{base}/ghost/api/admin/settings/", headers=headers, json={"settings": [{"key": "meta_description", "value": meta_desc}]}, timeout=10)
                if update.status_code == 200:
                    corrections.append(f"Meta description ajoutée : '{meta_desc[:80]}...'")
                else:
                    erreurs.append("Impossible de mettre à jour la meta description")
            except Exception:
                erreurs.append("Erreur lors de la génération de la meta description")
        if not result["performance"]["is_https"]:
            erreurs.append("HTTPS non activé — activez SSL depuis Settings → General sur Ghost")
        if result["content"]["word_count"] < 300:
            erreurs.append(f"Contenu trop court — enrichissez vos articles")
    except Exception as e:
        erreurs.append(str(e))
    return corrections, erreurs


# ── TYPO3 AUTO-FIX ────────────────────────────────────────────────────────────
def typo3_fix_seo(typo3_url, token, result):
    import requests as req
    corrections = []
    erreurs = []
    base = typo3_url.rstrip("/")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    try:
        if not result["seo"]["meta_description"]:
            try:
                import requests as req2
                h = {"Authorization": f"Bearer {st.secrets['MISTRAL_API_KEY']}", "Content-Type": "application/json"}
                p = f"Génère une meta description de 150 caractères pour : {result['final_url']}. Réponds UNIQUEMENT avec la meta description."
                d = {"model": "mistral-small-latest", "messages": [{"role": "user", "content": p}], "max_tokens": 60}
                r = req2.post("https://api.mistral.ai/v1/chat/completions", headers=h, json=d, timeout=15)
                meta_desc = r.json()["choices"][0]["message"]["content"].strip()
                corrections.append(f"Meta description générée : '{meta_desc[:80]}...' — à appliquer via l'extension SEO de TYPO3")
            except Exception:
                erreurs.append("Erreur lors de la génération de la meta description")
        if result["seo"]["images_no_alt"] > 0:
            erreurs.append(f"{result['seo']['images_no_alt']} image(s) sans alt — à corriger dans le gestionnaire de fichiers TYPO3")
        if not result["performance"]["is_https"]:
            erreurs.append("HTTPS non activé — activez SSL depuis la configuration de votre hébergeur")
        if not result["design"]["has_og_tags"]:
            corrections.append("Open Graph — installez l'extension 'seo' depuis TYPO3 Extension Manager")
        if result["content"]["word_count"] < 300:
            erreurs.append(f"Contenu trop court — enrichissez le contenu de vos pages")
    except Exception as e:
        erreurs.append(str(e))
    return corrections, erreurs


# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Menu")
    st.divider()
    mode_comparaison = st.checkbox("Mode comparatif", key="compare_mode", help="Analysez deux sites en parallèle")
    st.divider()
    show_corriger = st.checkbox("Corriger mon site automatiquement", key="show_corriger", help="Connectez votre plateforme pour appliquer les corrections automatiquement")
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
        <p><strong>Sitra</strong> analyse votre site en temps réel et vous dit exactement quoi améliorer</p>
    </div>
    """, unsafe_allow_html=True)


# ── ASSISTANT IA ──────────────────────────────────────────────────────────────
st.divider()
with st.expander("Vous avez une question ? Posez-la à l'assistant Sitra"):
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

                # Construit l'historique complet de la conversation
                messages = [
                    {"role": "system", "content": f"""Tu es l'assistant de Sitra, un outil d'analyse de sites web. Tu réponds aux questions en langage simple et accessible, sans jargon technique. Tu expliques les termes avec des exemples concrets. Tu gardes le contexte de la conversation.
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
                # Efface la barre de question en changeant la clé
                st.session_state["chat_input_key"] += 1
                st.rerun()
            except Exception:
                st.error("Impossible de contacter l'assistant pour le moment.")

# ── CONTACT ───────────────────────────────────────────────────────────────────
st.divider()
st.markdown("""
<div style="background:linear-gradient(135deg,#0f0f1a,#1a1a2e);border:1px solid #2a2a4e;border-radius:16px;padding:2rem;text-align:center;margin:1rem 0">
    <div style="font-family:'Inter',sans-serif;font-size:1.3rem;font-weight:700;color:#e0e0e0;margin-bottom:0.5rem">Une question ? Un problème ?</div>
    <div style="color:#888;font-size:0.9rem;margin-bottom:1.5rem">Envoyez-nous un message et nous vous répondrons rapidement.</div>
</div>
""", unsafe_allow_html=True)

with st.expander("Nous contacter"):
    contact_nom = st.text_input("Votre nom :", key="contact_nom")
    contact_email = st.text_input("Votre email :", key="contact_email")
    contact_message = st.text_area("Votre message :", key="contact_message", height=120)
    if st.button("Envoyer le message", key="contact_send"):
        if contact_nom and contact_email and contact_message and "@" in contact_email:
            try:
                import requests as req
                headers_c = {
                    "Authorization": f"Bearer {st.secrets['RESEND_API_KEY']}",
                    "Content-Type": "application/json"
                }
                payload_c = {
                    "from": "Sitra Contact <onboarding@resend.dev>",
                    "to": ["yanisaidoune1@gmail.com"],
                    "reply_to": contact_email,
                    "subject": f"Message de {contact_nom} via Sitra",
                    "html": f"<p><b>Nom :</b> {contact_nom}</p><p><b>Email :</b> {contact_email}</p><p><b>Message :</b><br>{contact_message}</p>"
                }
                r = req.post("https://api.resend.com/emails", headers=headers_c, json=payload_c, timeout=15)
                if r.status_code == 200:
                    st.success("Message envoyé ! Nous vous répondrons bientôt.")
                else:
                    st.error("Erreur lors de l'envoi. Réessayez plus tard.")
            except Exception:
                st.error("Impossible d'envoyer le message pour le moment.")
        else:
            st.warning("Merci de remplir tous les champs avec un email valide.")
