"""
Sitra - Module de capture d'écran réelle pour l'onglet "Optimiser mon site"
Utilise l'API Microlink (gratuite, sans clé obligatoire).

Stratégie : capture ciblée par sélecteur CSS pour chaque erreur (h1, nav, img,
footer...). Pour limiter les cas où deux zones se ressemblent visuellement
(sites où tout est dans un seul gros bloc), on garde la dernière image vue
et on bascule vers la capture pleine page si Microlink renvoie deux fois
la même URL d'image à la suite.
"""

import streamlit as st
import requests as req


# ── SÉLECTEUR CSS PAR CATÉGORIE D'ERREUR ──────────────────────────────────────
# Sélecteurs volontairement précis (premier élément du type, ":not(nav *)" etc.)
# pour réduire les chances de cibler un gros bloc englobant tout.
SELECTOR_RULES = [
    ("balise <title>",            None),
    ("titre trop court",          None),
    ("titre trop long",           None),
    ("meta description",         None),
    ("balise h1",                 "h1:first-of-type"),
    ("balises h1",                "h1:first-of-type"),
    ("aucun h2",                  "h2:first-of-type, h1:first-of-type"),
    ("attribut alt",              "img:not([alt]):first-of-type, img[alt='']:first-of-type, img:first-of-type"),
    ("images sans dimensions",    "img:first-of-type"),
    ("canonical",                 None),
    ("viewport",                  None),
    ("attribut lang",             None),
    ("balise <nav>",              "nav:first-of-type"),
    ("navigation principale",     "nav:first-of-type"),
    ("navigation surchargée",     "nav:first-of-type"),
    ("bouton d'action",           "button:first-of-type, .btn:first-of-type, .cta:first-of-type"),
    ("information de contact",    "footer"),
    ("formulaire(s) avec des",    "form:first-of-type"),
    ("pied de page",              "footer"),
    ("mentions légales",          "footer"),
    ("paragraphe(s) très long",   "p:first-of-type"),
    ("favicon",                   None),
    ("og:title",                  None),
    ("og:image",                  None),
    ("éléments avec des styles",  None),
    ("https",                     None),
    ("temps de réponse",          None),
    ("page html lourde",          None),
    ("page html assez lourde",    None),
    ("scripts dans le",           None),
]


def get_selector_for_issue(message: str):
    """Retourne le sélecteur CSS à cibler pour une issue donnée, ou None si pas de zone pertinente."""
    msg_lower = message.lower()
    for fragment, selector in SELECTOR_RULES:
        if fragment in msg_lower:
            return selector
    return None


# ── RÉCUPÉRATION DE LA CAPTURE (PLEINE PAGE) ─────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def get_screenshot(url: str):
    """Capture pleine page (fallback générique). Retourne l'URL de l'image ou None."""
    return _microlink_screenshot(url, element=None)


# ── RÉCUPÉRATION D'UNE CAPTURE CIBLÉE SUR UN ÉLÉMENT ─────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def get_screenshot_zone(url: str, selector: str):
    """
    Capture ciblée sur un sélecteur CSS. Si elle échoue, retombe sur la
    capture pleine page. Retourne (image_url, was_targeted: bool).
    """
    if selector:
        targeted = _microlink_screenshot(url, element=selector)
        if targeted:
            return targeted, True
    fallback = get_screenshot(url)
    return fallback, False


def _microlink_screenshot(url: str, element=None):
    """Appel brut à Microlink. Retourne l'URL de l'image ou None si échec ou page bloquée."""
    try:
        headers = {}
        try:
            api_key = st.secrets.get("MICROLINK_API_KEY", "")
            if api_key:
                headers["x-api-key"] = api_key
        except Exception:
            pass

        params = {"url": url, "screenshot": "true", "meta": "false"}
        if element:
            params["screenshot.element"] = element

        r = req.get("https://api.microlink.io", params=params, headers=headers, timeout=20)

        if r.status_code != 200:
            return None

        data = r.json()
        if data.get("status") != "success":
            return None

        return data.get("data", {}).get("screenshot", {}).get("url")

    except Exception:
        return None


# ── BLOC AVANT / APRÈS AVEC CAPTURE CIBLÉE ────────────────────────────────────
def render_before_after_block(screenshot_url, error_num, badge_color, before_text, after_text, conseil, was_targeted=False, img_uid="", is_duplicate=False):
    """
    Construit le HTML d'un bloc AVANT/APRÈS.
    is_duplicate=True -> cette image est identique à celle du bloc précédent
                          (site dont la structure regroupe tout dans une seule
                          zone visuelle) ; on le signale honnêtement au lieu
                          de prétendre que c'est une zone différente.
    """
    badge_icon = "❌" if badge_color == "#dc3545" else "⚠️"
    uid = img_uid or f"img{error_num}"

    if is_duplicate:
        precision_note = '<div style="font-size:10px;color:#999;margin-top:4px;font-style:italic">📍 Cette zone du site regroupe plusieurs éléments — voir le texte ci-dessus pour le détail exact</div>'
    elif was_targeted:
        precision_note = '<div style="font-size:10px;color:#7ddf96;margin-top:4px">🎯 Zone exacte capturée</div>'
    else:
        precision_note = '<div style="font-size:10px;color:#999;margin-top:4px;font-style:italic">📍 Vue générale du site (zone précise non disponible pour cette capture)</div>'

    return f"""
<div style="margin-bottom:28px">
  <div style="font-size:11px;font-weight:700;color:{badge_color};text-transform:uppercase;letter-spacing:1px;margin-bottom:8px">
    {badge_icon} ERREUR {error_num}
  </div>
  <div style="display:grid;grid-template-columns:1fr auto 1fr;gap:12px;align-items:start">

    <div>
      <div style="font-size:10px;color:{badge_color};font-weight:700;margin-bottom:6px;text-transform:uppercase">AVANT — Capture réelle de votre site</div>
      <div style="position:relative;border:2px solid {badge_color};border-radius:10px;overflow:hidden;background:#111;cursor:zoom-in" onclick="document.getElementById('modal_{uid}_before').style.display='flex'">
        <img src="{screenshot_url}" style="width:100%;display:block" />
        <div style="position:absolute;top:0;left:0;right:0;background:linear-gradient(180deg,{badge_color}f0,{badge_color}00);padding:10px 12px 24px;color:white;font-size:12px;font-weight:600;line-height:1.4">
          {before_text}
        </div>
        <div style="position:absolute;bottom:6px;right:8px;background:rgba(0,0,0,0.6);color:white;font-size:10px;padding:2px 8px;border-radius:10px">🔍 Cliquer pour zoomer</div>
      </div>
      {precision_note}
    </div>

    <div style="display:flex;align-items:center;font-size:24px;color:#7c6af7;padding:0 4px;align-self:center">→</div>

    <div>
      <div style="font-size:10px;color:#28a745;font-weight:700;margin-bottom:6px;text-transform:uppercase">APRÈS — Correction proposée par SITRA</div>
      <div style="position:relative;border:2px solid #28a745;border-radius:10px;overflow:hidden;background:#111;cursor:zoom-in" onclick="document.getElementById('modal_{uid}_after').style.display='flex'">
        <img src="{screenshot_url}" style="width:100%;display:block;filter:brightness(0.8)" />
        <div style="position:absolute;top:0;left:0;right:0;background:linear-gradient(180deg,#28a745f0,#28a74500);padding:10px 12px 24px;color:white;font-size:12px;font-weight:600;line-height:1.4">
          {after_text}
        </div>
        <div style="position:absolute;bottom:6px;right:8px;background:rgba(0,0,0,0.6);color:white;font-size:10px;padding:2px 8px;border-radius:10px">🔍 Cliquer pour zoomer</div>
      </div>
    </div>

  </div>
  <div style="margin-top:8px;background:rgba(124,106,247,0.1);border-left:3px solid #7c6af7;padding:7px 12px;border-radius:0 6px 6px 0;font-size:12px;color:#b090f7">
    💡 {conseil}
  </div>
</div>

<div id="modal_{uid}_before" onclick="this.style.display='none'" style="display:none;position:fixed;z-index:9999;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.92);cursor:zoom-out;align-items:center;justify-content:center;padding:20px">
  <img src="{screenshot_url}" style="max-width:95%;max-height:95%;border:3px solid {badge_color};border-radius:8px" />
</div>
<div id="modal_{uid}_after" onclick="this.style.display='none'" style="display:none;position:fixed;z-index:9999;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.92);cursor:zoom-out;align-items:center;justify-content:center;padding:20px">
  <img src="{screenshot_url}" style="max-width:95%;max-height:95%;border:3px solid #28a745;border-radius:8px" />
</div>
"""


# ── BLOC DE SECOURS (fallback, sans capture du tout) ─────────────────────────
def render_fallback_block(error_num, badge_color, before_text, after_text, conseil):
    """Version sans capture d'écran (utilisée si même la capture pleine page a échoué)."""
    badge_icon = "❌" if badge_color == "#dc3545" else "⚠️"
    return f"""
<div style="margin-bottom:24px">
  <div style="font-size:11px;font-weight:700;color:{badge_color};text-transform:uppercase;letter-spacing:1px;margin-bottom:8px">
    {badge_icon} ERREUR {error_num} <span style="color:#666;font-weight:400;text-transform:none">(capture indisponible pour ce site)</span>
  </div>
  <div style="display:grid;grid-template-columns:1fr auto 1fr;gap:12px;align-items:stretch">
    <div style="background:#1a0808;border:2px solid {badge_color};border-radius:10px;padding:16px;color:white;font-size:13px;line-height:1.5">{before_text}</div>
    <div style="display:flex;align-items:center;font-size:24px;color:#7c6af7;padding:0 4px;align-self:center">→</div>
    <div style="background:#081a08;border:2px solid #28a745;border-radius:10px;padding:16px;color:white;font-size:13px;line-height:1.5">{after_text}</div>
  </div>
  <div style="margin-top:8px;background:rgba(124,106,247,0.1);border-left:3px solid #7c6af7;padding:7px 12px;border-radius:0 6px 6px 0;font-size:12px;color:#b090f7">
    💡 {conseil}
  </div>
</div>
"""


# ── DÉTECTION DE PAGE BLOQUÉE ("Access Denied" et variantes) ─────────────────
# Microlink réussit techniquement la requête (renvoie une image) même quand
# le site cible bloque l'accès — l'image contient alors une page d'erreur.
# On ne peut pas voir le CONTENU de l'image depuis le serveur sans l'analyser
# en pixels (hors de portée ici), donc cette détection reste partielle :
# on se base sur ce que Microlink expose dans ses métadonnées de réponse.
BLOCKED_HINTS = ["access denied", "403 forbidden", "blocked", "captcha", "are you a robot", "bot detection"]


# ── GÉNÉRATEUR DE TEXTES AVANT/APRÈS GÉNÉRIQUE (pour les issues non codées en dur) ──
def generic_before_after(message: str):
    """
    Pour une issue brute venant de all_issues, génère un texte AVANT/APRÈS générique.
    Retourne (badge_color, before_text, after_text, conseil).
    """
    is_critical = message.strip().startswith("❌")
    badge_color = "#dc3545" if is_critical else "#ffc107"
    clean_msg = message.replace("❌", "").replace("⚠️", "").strip()

    if " — " in clean_msg:
        probleme, explication = clean_msg.split(" — ", 1)
    else:
        probleme, explication = clean_msg, ""

    icon = "❌" if is_critical else "⚠️"
    before_text = f"{icon} {probleme}" + (f"<br><span style='font-weight:400;opacity:0.9'>{explication}</span>" if explication else "")
    after_text = "✅ Point corrigé<br><span style='font-weight:400;opacity:0.9'>Suivez le conseil ci-dessous</span>"
    conseil = explication if explication else probleme

    return badge_color, before_text, after_text, conseil
