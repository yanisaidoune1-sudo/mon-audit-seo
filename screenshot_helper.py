"""
Sitra - Module de capture d'écran réelle pour l'onglet "Optimiser mon site"
Utilise l'API Microlink (gratuite, sans clé obligatoire) pour récupérer
une vraie capture du site analysé, puis superpose un cadre de repérage
(zone approximative : haut / milieu / bas de page) + bandeaux
AVANT (problème) / APRÈS (correction proposée).
Les images sont cliquables pour zoomer en plein écran.
"""

import streamlit as st
import requests as req


# ── RÉCUPÉRATION DE LA CAPTURE ────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def get_screenshot(url: str):
    """
    Récupère une vraie capture d'écran du site via Microlink.
    Retourne l'URL de l'image hébergée par Microlink, ou None si échec.
    Mise en cache 1h.
    """
    try:
        headers = {}
        try:
            api_key = st.secrets.get("MICROLINK_API_KEY", "")
            if api_key:
                headers["x-api-key"] = api_key
        except Exception:
            pass

        r = req.get(
            "https://api.microlink.io",
            params={"url": url, "screenshot": "true", "meta": "false"},
            headers=headers,
            timeout=20,
        )

        if r.status_code != 200:
            return None

        data = r.json()
        if data.get("status") != "success":
            return None

        return data.get("data", {}).get("screenshot", {}).get("url")

    except Exception:
        return None


# ── ZONE DE REPÉRAGE PAR CATÉGORIE D'ERREUR ───────────────────────────────────
ZONE_RULES = [
    ("balise <title>",            "top"),
    ("titre trop court",          "top"),
    ("titre trop long",           "top"),
    ("meta description",          "top"),
    ("balise h1",                 "top"),
    ("balises h1",                "top"),
    ("aucun h2",                  "middle"),
    ("attribut alt",              "middle"),
    ("canonical",                 "none"),
    ("viewport",                  "none"),
    ("attribut lang",             "none"),
    ("balise <nav>",              "top"),
    ("navigation principale",     "top"),
    ("navigation surchargée",     "top"),
    ("bouton d'action",           "middle"),
    ("information de contact",    "middle"),
    ("formulaire(s) avec des",    "middle"),
    ("pied de page",              "bottom"),
    ("mentions légales",          "bottom"),
    ("paragraphe(s) très long",   "middle"),
    ("contenu très court",        "middle"),
    ("contenu assez court",       "middle"),
    ("erreurs de langue",         "middle"),
    ("mots très répétés",         "middle"),
    ("mots en majuscules",        "middle"),
    ("favicon",                   "top"),
    ("og:title",                  "none"),
    ("og:image",                  "none"),
    ("éléments avec des styles",  "none"),
    ("images sans dimensions",    "middle"),
    ("https",                     "top"),
    ("temps de réponse",          "none"),
    ("page html lourde",          "none"),
    ("page html assez lourde",    "none"),
    ("scripts dans le",           "none"),
]


def get_zone_for_issue(message: str) -> str:
    """Détermine la zone (top/middle/bottom/none) à repérer sur l'image pour un message d'erreur donné."""
    msg_lower = message.lower()
    for fragment, zone in ZONE_RULES:
        if fragment in msg_lower:
            return zone
    return "none"


ZONE_STYLES = {
    "top": {"top": "0%", "height": "22%", "label": "Zone concernée : haut de page"},
    "middle": {"top": "30%", "height": "30%", "label": "Zone concernée : corps de la page"},
    "bottom": {"top": "70%", "height": "30%", "label": "Zone concernée : bas de page"},
}


# ── BLOC AVANT / APRÈS AVEC VRAIE CAPTURE + CADRE DE REPÉRAGE ────────────────
def render_before_after_block(screenshot_url, error_num, badge_color, before_text, after_text, conseil, zone="none", img_uid=""):
    """
    Construit le HTML d'un bloc AVANT/APRÈS basé sur une vraie capture, avec :
      - un bandeau de texte (problème / correction)
      - un cadre de repérage pointillé sur la zone concernée (si zone != "none")
      - les images cliquables pour zoom plein écran (modale JS légère)
    """
    badge_icon = "❌" if badge_color == "#dc3545" else "⚠️"

    zone_overlay = ""
    zone_caption = ""
    if zone in ZONE_STYLES:
        zs = ZONE_STYLES[zone]
        zone_overlay = f"""<div style="position:absolute;left:0;right:0;top:{zs['top']};height:{zs['height']};border:3px dashed {badge_color};background:{badge_color}1a;pointer-events:none"></div>"""
        zone_caption = f"""<div style="font-size:10px;color:#999;margin-top:4px;font-style:italic">📍 {zs['label']} (zone approximative)</div>"""

    uid = img_uid or f"img{error_num}"

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
        {zone_overlay}
        <div style="position:absolute;top:0;left:0;right:0;background:linear-gradient(180deg,{badge_color}f0,{badge_color}00);padding:10px 12px 24px;color:white;font-size:12px;font-weight:600;line-height:1.4">
          {before_text}
        </div>
        <div style="position:absolute;bottom:6px;right:8px;background:rgba(0,0,0,0.6);color:white;font-size:10px;padding:2px 8px;border-radius:10px">🔍 Cliquer pour zoomer</div>
      </div>
      {zone_caption}
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


# ── BLOC DE SECOURS (fallback, sans capture) ─────────────────────────────────
def render_fallback_block(error_num, badge_color, before_text, after_text, conseil):
    """Version sans capture d'écran (utilisée si get_screenshot a renvoyé None)."""
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
    Pour une issue brute venant de all_issues (ex: "⚠️ Pas de balise canonical — ..."),
    génère un texte AVANT (le problème tel quel) et un texte APRÈS générique.
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
