"""
Sitra - Module de capture d'écran réelle pour l'onglet "Optimiser mon site"
Utilise l'API Microlink (gratuite, sans clé obligatoire) pour récupérer
une vraie capture du site analysé, puis superpose des bandeaux
AVANT (problème) / APRÈS (correction proposée) par-dessus.
"""

import streamlit as st
import requests as req


# ── RÉCUPÉRATION DE LA CAPTURE ────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def get_screenshot(url: str):
    """
    Récupère une vraie capture d'écran du site via Microlink.
    Retourne l'URL de l'image hébergée par Microlink, ou None si échec
    (site qui bloque, quota dépassé, timeout...).
    Mise en cache 1h : un même site n'est pas re-screenshoté à chaque clic.
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


# ── BLOC AVANT / APRÈS AVEC VRAIE CAPTURE ────────────────────────────────────
def render_before_after_block(screenshot_url, error_num, badge_color, before_text, after_text, conseil):
    """
    Construit le HTML d'un bloc AVANT/APRÈS basé sur une vraie capture,
    avec un bandeau superposé en haut de chaque image.
    """
    badge_icon = "❌" if badge_color == "#dc3545" else "⚠️"

    return f"""
<div style="margin-bottom:24px">
  <div style="font-size:11px;font-weight:700;color:{badge_color};text-transform:uppercase;letter-spacing:1px;margin-bottom:8px">
    {badge_icon} ERREUR {error_num}
  </div>
  <div style="display:grid;grid-template-columns:1fr auto 1fr;gap:12px;align-items:start">

    <div>
      <div style="font-size:10px;color:{badge_color};font-weight:700;margin-bottom:6px;text-transform:uppercase">AVANT — Capture réelle de votre site</div>
      <div style="position:relative;border:2px solid {badge_color};border-radius:10px;overflow:hidden;background:#111">
        <img src="{screenshot_url}" style="width:100%;display:block" />
        <div style="position:absolute;top:0;left:0;right:0;background:linear-gradient(180deg,{badge_color}f0,{badge_color}00);padding:10px 12px 24px;color:white;font-size:12px;font-weight:600;line-height:1.4">
          {before_text}
        </div>
      </div>
    </div>

    <div style="display:flex;align-items:center;font-size:24px;color:#7c6af7;padding:0 4px;align-self:center">→</div>

    <div>
      <div style="font-size:10px;color:#28a745;font-weight:700;margin-bottom:6px;text-transform:uppercase">APRÈS — Correction proposée par SITRA</div>
      <div style="position:relative;border:2px solid #28a745;border-radius:10px;overflow:hidden;background:#111">
        <img src="{screenshot_url}" style="width:100%;display:block;filter:brightness(0.8)" />
        <div style="position:absolute;top:0;left:0;right:0;background:linear-gradient(180deg,#28a745f0,#28a74500);padding:10px 12px 24px;color:white;font-size:12px;font-weight:600;line-height:1.4">
          {after_text}
        </div>
      </div>
    </div>

  </div>
  <div style="margin-top:8px;background:rgba(124,106,247,0.1);border-left:3px solid #7c6af7;padding:7px 12px;border-radius:0 6px 6px 0;font-size:12px;color:#b090f7">
    💡 {conseil}
  </div>
</div>
"""


# ── BLOC DE SECOURS (fallback, sans capture) ─────────────────────────────────
def render_fallback_block(error_num, badge_color, before_text, after_text, conseil):
    """
    Version sans capture d'écran (utilisée si get_screenshot a renvoyé None).
    """
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
