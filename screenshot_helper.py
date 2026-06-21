"""
Sitra - Module de capture d'écran réelle pour l'onglet "Optimiser mon site"
Utilise l'API Microlink (gratuite, sans clé obligatoire).

Stratégie : au lieu d'une seule capture pleine page réutilisée pour toutes
les erreurs (peu lisible), on cible une capture PAR ZONE concernée
(ex: la balise <h1>, le <nav>, une <img>, le <footer>) via le paramètre
screenshot.element de Microlink (sélecteur CSS).
Si le sélecteur échoue (élément absent, timeout...), on retombe sur une
capture pleine page, puis sur le mode texte si tout échoue.
"""

import streamlit as st
import requests as req


# ── SÉLECTEUR CSS PAR CATÉGORIE D'ERREUR ──────────────────────────────────────
# Associe un fragment du message d'erreur (en minuscules) à un sélecteur CSS
# ciblant l'élément concerné. L'ordre compte : règles spécifiques en premier.
SELECTOR_RULES = [
    ("balise <title>",            None),       # le <title> n'est pas visible à l'écran, pas de capture ciblée utile
    ("titre trop court",          None),
    ("titre trop long",           None),
    ("meta description",         None),
    ("balise h1",                 "h1"),
    ("balises h1",                "h1"),
    ("aucun h2",                  "h1, h2"),
    ("attribut alt",              "img"),
    ("images sans dimensions",    "img"),
    ("canonical",                 None),
    ("viewport",                  None),
    ("attribut lang",             None),
    ("balise <nav>",              "nav, header"),
    ("navigation principale",     "nav, header"),
    ("navigation surchargée",     "nav, header"),
    ("bouton d'action",           "button, .btn, .button, .cta"),
    ("information de contact",    "footer"),
    ("formulaire(s) avec des",    "form"),
    ("pied de page",              "footer"),
    ("mentions légales",          "footer"),
    ("paragraphe(s) très long",   "p"),
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
    Capture ciblée sur un sélecteur CSS (ex: 'nav', 'footer', 'img').
    Si la capture ciblée échoue (élément absent, timeout), retombe sur
    la capture pleine page. Retourne (image_url, was_targeted: bool) ou (None, False).
    """
    if selector:
        targeted = _microlink_screenshot(url, element=selector)
        if targeted:
            return targeted, True
    fallback = get_screenshot(url)
    return fallback, False


def _microlink_screenshot(url: str, element=None):
    """Appel brut à Microlink. Retourne l'URL de l'image ou None si échec."""
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
def render_before_after_block(screenshot_url, error_num, badge_color, before_text, after_text, conseil, was_targeted=False, img_uid=""):
    """
    Construit le HTML d'un bloc AVANT/APRÈS.
    was_targeted=True  -> la capture montre précisément la zone concernée (pas besoin de cadre)
    was_targeted=False -> capture pleine page générique (fallback), on l'indique au survol
    """
    badge_icon = "❌" if badge_color == "#dc3545" else "⚠️"
    uid = img_uid or f"img{error_num}"

    precision_note = (
        '<div style="font-size:10px;color:#7ddf96;margin-top:4px">🎯 Zone exacte capturée</div>'
        if was_targeted else
        '<div style="font-size:10px;color:#999;margin-top:4px;font-style:italic">📍 Vue générale du site (zone précise non disponible pour cette capture)</div>'
    )

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
