"""
Sitra - Moteur d'analyse réel de sites web
Remplace tous les random() par de vraies vérifications
"""

import requests
import time
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import re
import ssl
import socket


HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; SitraBot/1.0; site analysis)"
}

TIMEOUT = 10


def detect_secteur_et_concurrents(url: str, html: str) -> dict:
    """Détecte le secteur du site et trouve des concurrents à comparer"""
    try:
        soup = BeautifulSoup(html, "lxml")
        text = soup.get_text(" ", strip=True).lower()[:2000]

        # Détection du secteur par mots-clés
        secteurs = {
            "Restaurant / Food": ["restaurant", "menu", "plat", "cuisine", "food", "pizza", "burger", "reservation", "table"],
            "E-commerce": ["acheter", "panier", "boutique", "shop", "produit", "prix", "livraison", "commander"],
            "Artisan / Services": ["artisan", "devis", "chantier", "renovation", "plombier", "electricien", "maçon", "peinture"],
            "Santé / Médical": ["médecin", "docteur", "consultation", "santé", "cabinet", "rendez-vous", "clinique"],
            "Immobilier": ["immobilier", "appartement", "maison", "louer", "vente", "agence", "bien", "m2"],
            "Éducation / Formation": ["formation", "cours", "apprendre", "école", "université", "certification", "étudiant"],
            "Beauté / Bien-être": ["coiffeur", "salon", "beauté", "spa", "massage", "soin", "esthétique"],
            "Juridique / Finance": ["avocat", "comptable", "juridique", "finance", "conseil", "expertise"],
            "Tech / Digital": ["développement", "web", "application", "digital", "software", "logiciel", "startup"],
            "Autre": []
        }

        scores_secteur = {}
        for secteur, mots in secteurs.items():
            score = sum(1 for mot in mots if mot in text)
            scores_secteur[secteur] = score

        secteur_detecte = max(scores_secteur, key=scores_secteur.get)
        if scores_secteur[secteur_detecte] == 0:
            secteur_detecte = "Autre"

        # Concurrents types par secteur
        concurrents_types = {
            "Restaurant / Food": ["tripadvisor.fr", "lafourchette.com", "deliveroo.fr"],
            "E-commerce": ["amazon.fr", "cdiscount.com", "fnac.com"],
            "Artisan / Services": ["pages-jaunes.fr", "habitatpresto.com", "houzz.fr"],
            "Santé / Médical": ["doctolib.fr", "ameli.fr", "sante.fr"],
            "Immobilier": ["seloger.com", "leboncoin.fr", "logic-immo.com"],
            "Éducation / Formation": ["openclassrooms.com", "coursera.org", "udemy.com"],
            "Beauté / Bien-être": ["treatwell.fr", "fresha.com", "planity.com"],
            "Juridique / Finance": ["captain-contrat.com", "legalstart.fr", "shine.fr"],
            "Tech / Digital": ["malt.fr", "upwork.com", "clutch.co"],
            "Autre": ["google.fr", "wikipedia.org", "yelp.fr"],
        }

        concurrents = concurrents_types.get(secteur_detecte, [])

        return {
            "secteur": secteur_detecte,
            "concurrents": concurrents,
            "score_detection": scores_secteur[secteur_detecte]
        }
    except Exception:
        return {"secteur": "Autre", "concurrents": [], "score_detection": 0}


    """Détecte automatiquement les pages principales du site en lisant la navigation"""
    url = normalize_url(url)
    pages = []
    try:
        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"

        session = requests.Session()
        session.headers.update(HEADERS)
        r = session.get(url, timeout=TIMEOUT, allow_redirects=True)
        if r.status_code != 200:
            return []

        soup = BeautifulSoup(r.text, "lxml")

        # Cherche les liens dans la navigation
        nav_links = []
        for nav in soup.find_all(["nav", "header"]):
            for a in nav.find_all("a", href=True):
                href = a.get("href", "").strip()
                if not href or href == "/" or href.startswith("#") or href.startswith("javascript"):
                    continue
                # Construit l'URL complète
                if href.startswith("http"):
                    full_url = href
                elif href.startswith("/"):
                    full_url = base_url + href
                else:
                    full_url = base_url + "/" + href

                # Garde seulement les pages du même domaine
                if parsed.netloc in full_url and full_url != url and full_url not in nav_links:
                    # Filtre les URLs de ressources
                    if not any(ext in full_url.lower() for ext in [".css", ".js", ".png", ".jpg", ".pdf", ".ico"]):
                        nav_links.append(full_url)

        # Garde max 4 pages
        return nav_links[:4]

    except Exception:
        return []


def normalize_url(url: str) -> str:
    url = url.strip()
    if not url:
        return ""
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url
    return url


def fetch_site(url: str) -> dict:
    """
    Récupère le contenu d'un site et mesure le temps de réponse.
    Retourne un dict avec html, status_code, response_time, error, final_url
    """
    result = {
        "html": None,
        "status_code": None,
        "response_time": None,
        "error": None,
        "final_url": url,
        "is_https": url.startswith("https://"),
    }

    try:
        start = time.time()
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
        result["response_time"] = round(time.time() - start, 2)
        result["status_code"] = r.status_code
        result["final_url"] = r.url
        result["is_https"] = r.url.startswith("https://")

        if r.status_code == 200:
            result["html"] = r.text
        else:
            result["error"] = f"Le site a répondu avec le code HTTP {r.status_code}"

    except requests.exceptions.SSLError:
        result["error"] = "Erreur SSL : certificat invalide ou expiré"
        result["is_https"] = False
    except requests.exceptions.ConnectionError:
        result["error"] = "Impossible de contacter le site (DNS ou connexion refusée)"
    except requests.exceptions.Timeout:
        result["error"] = f"Le site n'a pas répondu en moins de {TIMEOUT}s"
    except Exception as e:
        result["error"] = str(e)

    return result


def analyze_seo(soup: BeautifulSoup, url: str) -> dict:
    """Analyse SEO réelle : title, meta, H1, H2, images alt, etc."""
    issues = []
    score = 100

    # Title
    title_tag = soup.find("title")
    title_text = title_tag.get_text(strip=True) if title_tag else ""
    if not title_text:
        issues.append("❌ Pas de balise <title> — essentiel pour le référencement Google")
        score -= 20
    elif len(title_text) < 10:
        issues.append(f"⚠️ Titre trop court ({len(title_text)} caractères) — vise 50-60 caractères")
        score -= 10
    elif len(title_text) > 70:
        issues.append(f"⚠️ Titre trop long ({len(title_text)} caractères) — Google le tronque après 60")
        score -= 5

    # Meta description
    meta_desc = soup.find("meta", attrs={"name": "description"})
    meta_content = meta_desc.get("content", "").strip() if meta_desc else ""
    if not meta_content:
        issues.append("❌ Pas de meta description — impacte fortement le taux de clic Google")
        score -= 15
    elif len(meta_content) < 50:
        issues.append(f"⚠️ Meta description trop courte ({len(meta_content)} chars) — vise 120-160 caractères")
        score -= 8
    elif len(meta_content) > 170:
        issues.append(f"⚠️ Meta description trop longue ({len(meta_content)} chars) — Google la tronque")
        score -= 3

    # H1
    h1_tags = soup.find_all("h1")
    if not h1_tags:
        issues.append("❌ Pas de balise H1 — Google utilise le H1 pour comprendre le sujet principal")
        score -= 15
    elif len(h1_tags) > 1:
        issues.append(f"⚠️ {len(h1_tags)} balises H1 détectées — il ne doit y en avoir qu'une seule")
        score -= 5

    # H2 structure
    h2_tags = soup.find_all("h2")
    if not h2_tags:
        issues.append("⚠️ Aucun H2 — structure le contenu avec des sous-titres pour le SEO")
        score -= 5

    # Images sans alt
    images = soup.find_all("img")
    images_no_alt = [img for img in images if not img.get("alt", "").strip()]
    if images_no_alt:
        pct = int(len(images_no_alt) / max(len(images), 1) * 100)
        issues.append(f"⚠️ {len(images_no_alt)}/{len(images)} images sans attribut alt ({pct}%) — Google ne peut pas les indexer")
        score -= min(10, len(images_no_alt) * 2)

    # Canonical
    canonical = soup.find("link", rel="canonical")
    if not canonical:
        issues.append("⚠️ Pas de balise canonical — peut causer du contenu dupliqué")
        score -= 3

    # Viewport meta (mobile)
    viewport = soup.find("meta", attrs={"name": "viewport"})
    if not viewport:
        issues.append("❌ Pas de meta viewport — le site ne sera pas responsive sur mobile")
        score -= 10

    # Lang attribute
    html_tag = soup.find("html")
    lang = html_tag.get("lang", "") if html_tag else ""
    if not lang:
        issues.append("⚠️ Pas d'attribut lang sur <html> — Google ne sait pas quelle langue cibler")
        score -= 3

    score = max(0, min(100, score))

    return {
        "score": score,
        "title": title_text,
        "meta_description": meta_content,
        "h1_count": len(h1_tags),
        "h2_count": len(h2_tags),
        "images_total": len(images),
        "images_no_alt": len(images_no_alt),
        "has_canonical": canonical is not None,
        "has_viewport": viewport is not None,
        "has_lang": bool(lang),
        "issues": issues,
    }


def analyze_ux(soup: BeautifulSoup, url: str) -> dict:
    """Analyse UX : navigation, CTA, contact, lisibilité, formulaires"""
    issues = []
    score = 100

    # Menu / navigation
    nav_tags = soup.find_all(["nav", "header"])
    has_nav = len(nav_tags) > 0
    if not has_nav:
        issues.append("⚠️ Pas de balise <nav> ou <header> détectée — structure de navigation manquante")
        score -= 8

    # Liens dans la nav
    nav_links = []
    for nav in nav_tags:
        nav_links.extend(nav.find_all("a"))
    if len(nav_links) == 0:
        issues.append("⚠️ Aucun lien dans la navigation principale")
        score -= 5
    elif len(nav_links) > 10:
        issues.append(f"⚠️ Navigation surchargée ({len(nav_links)} liens) — simplifie à 5-7 éléments max")
        score -= 5

    # Boutons CTA
    buttons = soup.find_all("button") + soup.find_all("a", class_=re.compile(r"btn|button|cta", re.I))
    if not buttons:
        issues.append("❌ Aucun bouton d'action (CTA) détecté — comment les visiteurs passent à l'action ?")
        score -= 15
    
    # Contact
    page_text = soup.get_text().lower()
    has_contact = any(word in page_text for word in ["contact", "email", "e-mail", "@", "téléphone", "telephone", "whatsapp"])
    if not has_contact:
        issues.append("❌ Aucune information de contact visible — les visiteurs ne peuvent pas vous joindre")
        score -= 12

    # Formulaires
    forms = soup.find_all("form")
    forms_no_label = 0
    for form in forms:
        inputs = form.find_all("input", type=lambda t: t not in ["hidden", "submit", "button"])
        labels = form.find_all("label")
        if len(inputs) > len(labels):
            forms_no_label += 1
    if forms_no_label > 0:
        issues.append(f"⚠️ {forms_no_label} formulaire(s) avec des champs sans label — problème d'accessibilité")
        score -= 5

    # Mentions légales / footer
    footer = soup.find("footer")
    has_footer = footer is not None
    if not has_footer:
        issues.append("⚠️ Pas de pied de page — les mentions légales et contacts doivent y figurer")
        score -= 8
    else:
        footer_text = footer.get_text().lower()
        if not any(word in footer_text for word in ["mentions légales", "mention", "cgv", "politique", "privacy", "legal"]):
            issues.append("⚠️ Mentions légales non détectées — obligatoires en France (RGPD)")
            score -= 8

    # Texte lisible (longueur paragraphes)
    paragraphs = soup.find_all("p")
    long_paragraphs = [p for p in paragraphs if len(p.get_text()) > 600]
    if long_paragraphs:
        issues.append(f"⚠️ {len(long_paragraphs)} paragraphe(s) très long(s) — divise-les pour faciliter la lecture")
        score -= 5

    score = max(0, min(100, score))

    return {
        "score": score,
        "has_nav": has_nav,
        "nav_links_count": len(nav_links),
        "buttons_count": len(buttons),
        "has_contact": has_contact,
        "forms_count": len(forms),
        "has_footer": has_footer,
        "long_paragraphs": len(long_paragraphs),
        "issues": issues,
    }


def analyze_content(soup: BeautifulSoup) -> dict:
    """Analyse du contenu : fautes basiques, clarté, lisibilité"""
    issues = []
    score = 100

    text = soup.get_text(" ", strip=True)
    words = text.split()
    word_count = len(words)

    if word_count < 100:
        issues.append(f"⚠️ Contenu très court ({word_count} mots) — Google préfère les pages avec 300+ mots")
        score -= 15
    elif word_count < 300:
        issues.append(f"⚠️ Contenu assez court ({word_count} mots) — vise au moins 400-600 mots sur la page d'accueil")
        score -= 8

    # Détection fautes courantes (français/anglais)
    common_mistakes_fr = [
        (r'\bsa\b(?=\s+(?:va|fait|marche|passe))', "confusion sa/ça"),
        (r'\bdon[ck]\b', "donk → donc"),
        (r'\bpourquoi\s+que\b', "pourquoi que → pourquoi"),
        (r'\bà\s+cause\s+que\b', "à cause que → parce que"),
    ]

    mistakes_found = []
    text_lower = text.lower()
    for pattern, desc in common_mistakes_fr:
        if re.search(pattern, text_lower):
            mistakes_found.append(desc)

    if mistakes_found:
        issues.append(f"⚠️ Erreurs de langue potentielles détectées : {', '.join(mistakes_found)}")
        score -= 8

    # Répétitions excessives
    if word_count > 0:
        from collections import Counter
        word_freq = Counter(w.lower().strip('.,;:!?') for w in words if len(w) > 5)
        most_common = word_freq.most_common(3)
        overused = [(w, c) for w, c in most_common if c / word_count > 0.05]
        if overused:
            issues.append(f"⚠️ Mots très répétés : {', '.join([f'{w} ({c}x)' for w,c in overused])} — varie le vocabulaire")
            score -= 5

    # Majuscules excessives
    caps_words = [w for w in words if w.isupper() and len(w) > 3]
    if len(caps_words) > 5:
        issues.append(f"⚠️ {len(caps_words)} mots en majuscules — évite de crier sur tes visiteurs")
        score -= 5

    score = max(0, min(100, score))

    return {
        "score": score,
        "word_count": word_count,
        "issues": issues,
    }


def analyze_design(soup: BeautifulSoup, url: str) -> dict:
    """Analyse design : couleurs, polices, images, cohérence visuelle"""
    issues = []
    score = 100

    # Favicon
    favicon = soup.find("link", rel=lambda r: r and "icon" in r)
    if not favicon:
        issues.append("⚠️ Pas de favicon — un détail qui renforce l'identité de la marque")
        score -= 5

    # Inline styles excessifs
    inline_styles = soup.find_all(style=True)
    if len(inline_styles) > 30:
        issues.append(f"⚠️ {len(inline_styles)} éléments avec des styles inline — utilise un fichier CSS dédié")
        score -= 5

    # Images
    images = soup.find_all("img")
    images_no_size = [img for img in images if not (img.get("width") or img.get("height"))]
    if images_no_size and len(images_no_size) > len(images) * 0.5:
        issues.append(f"⚠️ {len(images_no_size)} images sans dimensions — peut causer des sauts de mise en page")
        score -= 5

    # Polices (détection via link Google Fonts ou @font-face)
    google_fonts = soup.find_all("link", href=re.compile(r"fonts\.google|fonts\.gstatic"))
    custom_fonts = bool(google_fonts)

    # Open Graph (partage réseaux sociaux)
    og_title = soup.find("meta", property="og:title")
    og_image = soup.find("meta", property="og:image")
    if not og_title:
        issues.append("⚠️ Pas de balise og:title — le partage sur réseaux sociaux sera peu attrayant")
        score -= 8
    if not og_image:
        issues.append("⚠️ Pas de og:image — aucune image affichée lors du partage sur Facebook/LinkedIn")
        score -= 8

    # Extraction des couleurs dominantes (depuis les styles inline et attributs)
    color_candidates = []
    for tag in soup.find_all(style=True):
        colors = re.findall(r'#([0-9a-fA-F]{3,6})\b|rgba?\([\d,\s.]+\)', tag.get("style", ""))
        color_candidates.extend(colors[:3])

    score = max(0, min(100, score))

    return {
        "score": score,
        "has_favicon": favicon is not None,
        "has_google_fonts": custom_fonts,
        "has_og_tags": og_title is not None,
        "issues": issues,
        "detected_colors": color_candidates[:5],
    }


def analyze_performance(response_time: float, html: str, is_https: bool) -> dict:
    """Analyse performance : vitesse, HTTPS, taille page"""
    issues = []
    score = 100

    # HTTPS
    if not is_https:
        issues.append("❌ Le site n'utilise pas HTTPS — Google pénalise les sites non sécurisés")
        score -= 25

    # Temps de réponse
    if response_time is None:
        score -= 10
    elif response_time > 3:
        issues.append(f"❌ Temps de réponse très lent : {response_time}s — les visiteurs partent après 3s")
        score -= 20
    elif response_time > 1.5:
        issues.append(f"⚠️ Temps de réponse moyen : {response_time}s — vise moins de 1s")
        score -= 10
    elif response_time < 0.5:
        pass  # excellent

    # Taille du HTML
    html_size_kb = len(html.encode("utf-8")) / 1024 if html else 0
    if html_size_kb > 500:
        issues.append(f"⚠️ Page HTML lourde : {html_size_kb:.0f}KB — optimise le code")
        score -= 8
    elif html_size_kb > 200:
        issues.append(f"⚠️ Page HTML assez lourde : {html_size_kb:.0f}KB")
        score -= 4

    # Scripts bloquants
    if html:
        soup_check = BeautifulSoup(html, "lxml")
        blocking_scripts = soup_check.find_all("script", src=True)
        head = soup_check.find("head")
        scripts_in_head = []
        if head:
            scripts_in_head = head.find_all("script", src=True)
        if len(scripts_in_head) > 5:
            issues.append(f"⚠️ {len(scripts_in_head)} scripts dans le <head> — peuvent ralentir le chargement")
            score -= 5

    score = max(0, min(100, score))

    return {
        "score": score,
        "is_https": is_https,
        "response_time": response_time,
        "html_size_kb": round(html_size_kb, 1),
        "issues": issues,
    }


def full_analysis(url: str) -> dict:
    """
    Lance l'analyse complète d'un site.
    Retourne un dict structuré avec tous les résultats.
    """
    url = normalize_url(url)
    if not url:
        return {"error": "URL invalide"}

    # Fetch
    fetch = fetch_site(url)

    if fetch["error"] and not fetch["html"]:
        return {
            "url": url,
            "error": fetch["error"],
            "is_https": fetch["is_https"],
            "response_time": fetch["response_time"],
            "status_code": fetch["status_code"],
        }

    html = fetch["html"] or ""
    soup = BeautifulSoup(html, "lxml")

    # Analyses
    seo = analyze_seo(soup, url)
    ux = analyze_ux(soup, url)
    content = analyze_content(soup)
    design = analyze_design(soup, url)
    performance = analyze_performance(fetch["response_time"], html, fetch["is_https"])

    # Score global pondéré
    global_score = round(
        seo["score"] * 0.30 +
        ux["score"] * 0.25 +
        content["score"] * 0.15 +
        design["score"] * 0.15 +
        performance["score"] * 0.15
    )

    # Toutes les issues triées par catégorie
    all_issues = []
    for cat, data in [("SEO", seo), ("UX", ux), ("Contenu", content), ("Design", design), ("Performance", performance)]:
        for issue in data.get("issues", []):
            all_issues.append({"category": cat, "message": issue})

    return {
        "url": url,
        "final_url": fetch["final_url"],
        "status_code": fetch["status_code"],
        "response_time": fetch["response_time"],
        "is_https": fetch["is_https"],
        "global_score": global_score,
        "seo": seo,
        "ux": ux,
        "content": content,
        "design": design,
        "performance": performance,
        "all_issues": all_issues,
        "total_issues": len(all_issues),
        "error": None,
    }


def get_score_label(score: int) -> tuple:
    if score >= 90:
        return "Excellent", "vert", "#28a745"
    elif score >= 75:
        return "Bon", "jaune", "#ffc107"
    elif score >= 55:
        return "A ameliorer", "orange", "#fd7e14"
    else:
        return "Critique", "rouge", "#dc3545"


def detect_pages(url: str) -> list:
    """Détecte automatiquement les pages principales du site"""
    url = normalize_url(url)
    pages = []
    try:
        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        session = requests.Session()
        session.headers.update(HEADERS)
        r = session.get(url, timeout=TIMEOUT, allow_redirects=True)
        if r.status_code != 200:
            return []
        soup = BeautifulSoup(r.text, "lxml")
        nav_links = []
        for nav in soup.find_all(["nav", "header"]):
            for a in nav.find_all("a", href=True):
                href = a.get("href", "").strip()
                if not href or href == "/" or href.startswith("#") or href.startswith("javascript"):
                    continue
                if href.startswith("http"):
                    full_url = href
                elif href.startswith("/"):
                    full_url = base_url + href
                else:
                    full_url = base_url + "/" + href
                if parsed.netloc in full_url and full_url != url and full_url not in nav_links:
                    if not any(ext in full_url.lower() for ext in [".css", ".js", ".png", ".jpg", ".pdf", ".ico"]):
                        nav_links.append(full_url)
        return nav_links[:4]
    except Exception:
        return []


def get_pagespeed(url: str) -> dict:
    """Recupere les vraies metriques Google PageSpeed sans cle API"""
    result = {
        "performance": None,
        "accessibility": None,
        "seo": None,
        "best_practices": None,
        "fcp": None,
        "lcp": None,
        "cls": None,
        "error": None,
    }
    try:
        api_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&strategy=mobile"
        r = requests.get(api_url, timeout=30)
        if r.status_code != 200:
            result["error"] = f"PageSpeed indisponible (code {r.status_code})"
            return result
        data = r.json()
        cats = data.get("lighthouseResult", {}).get("categories", {})
        audits = data.get("lighthouseResult", {}).get("audits", {})

        result["performance"] = round((cats.get("performance", {}).get("score", 0) or 0) * 100)
        result["accessibility"] = round((cats.get("accessibility", {}).get("score", 0) or 0) * 100)
        result["seo"] = round((cats.get("seo", {}).get("score", 0) or 0) * 100)
        result["best_practices"] = round((cats.get("best-practices", {}).get("score", 0) or 0) * 100)

        fcp = audits.get("first-contentful-paint", {}).get("displayValue", "")
        lcp = audits.get("largest-contentful-paint", {}).get("displayValue", "")
        cls = audits.get("cumulative-layout-shift", {}).get("displayValue", "")

        result["fcp"] = fcp
        result["lcp"] = lcp
        result["cls"] = cls

    except Exception as e:
        result["error"] = str(e)

    return result
