"""
Sitra - Affichage du site reel dans un iframe avec cadre de reperage
Au lieu d'une capture statique, on affiche le vrai site dans un iframe
et on superpose un cadre rouge CSS positionne sur la zone de l'erreur.
"""

# Position verticale du cadre selon le type d'erreur
ZONE_POSITION = {
    "h1":       {"top": "8%",  "height": "20%", "label": "Le titre principal est dans cette zone"},
    "nav":      {"top": "0%",  "height": "12%", "label": "Le menu de navigation est dans cette zone"},
    "img":      {"top": "20%", "height": "35%", "label": "Les images sont dans cette zone"},
    "footer":   {"top": "75%", "height": "25%", "label": "Le pied de page est dans cette zone"},
    "form":     {"top": "30%", "height": "40%", "label": "Le formulaire est dans cette zone"},
    "p":        {"top": "25%", "height": "50%", "label": "Le contenu texte est dans cette zone"},
    "button":   {"top": "20%", "height": "40%", "label": "Les boutons d'action sont dans cette zone"},
    None:       {"top": "0%",  "height": "100%", "label": ""},
}


def get_zone_from_selector(selector):
    """Determine la zone d'affichage a partir du selecteur CSS."""
    if not selector:
        return None
    s = selector.lower()
    if "h1" in s or "h2" in s:
        return "h1"
    if "nav" in s or "header" in s:
        return "nav"
    if "img" in s:
        return "img"
    if "footer" in s:
        return "footer"
    if "form" in s:
        return "form"
    if "p" in s or "paragraphe" in s:
        return "p"
    if "button" in s or "btn" in s or "cta" in s:
        return "button"
    return None


def render_iframe_before_after(url_site, error_num, badge_color, before_text, after_text, conseil, selector=None, img_uid=""):
    """
    Affiche le vrai site dans un iframe (AVANT) avec un cadre rouge
    superpose sur la zone de l'erreur, et un iframe assombri (APRES)
    avec le texte de correction.
    """
    badge_icon = "X" if badge_color == "#dc3545" else "!"
    uid = img_uid or f"err{error_num}"
    zone_key = get_zone_from_selector(selector)
    zone = ZONE_POSITION.get(zone_key, ZONE_POSITION[None])
    
    has_zone = zone_key is not None
    zone_label = zone["label"] if has_zone else ""

    # Couleur du cadre : rouge pour erreur critique, orange pour avertissement
    frame_color = "#dc3545" if badge_color == "#dc3545" else "#ffc107"

    iframe_before = f"""
<div style="position:relative;border:3px solid {frame_color};border-radius:10px;overflow:hidden;height:300px">
  <iframe src="{url_site}" style="width:100%;height:300px;border:none;pointer-events:none" scrolling="no" loading="lazy"></iframe>
  <div style="position:absolute;top:0;left:0;right:0;background:linear-gradient(180deg,{frame_color}ee,{frame_color}00);padding:10px 12px 28px;color:white;font-size:12px;font-weight:600;line-height:1.5;z-index:10">
    {before_text}
  </div>
  {"" if not has_zone else f'''
  <div style="position:absolute;left:4px;right:4px;top:{zone["top"]};height:{zone["height"]};border:3px dashed {frame_color};border-radius:6px;z-index:9;pointer-events:none">
    <div style="position:absolute;top:-22px;left:0;background:{frame_color};color:white;font-size:10px;font-weight:700;padding:2px 8px;border-radius:4px">
      Erreur ici
    </div>
  </div>'''}
  <div style="position:absolute;bottom:8px;right:10px;background:rgba(0,0,0,0.65);color:white;font-size:10px;padding:2px 8px;border-radius:10px;z-index:10">
    Vue reelle du site
  </div>
</div>
{"" if not zone_label else f'<div style="font-size:10px;color:#7ddf96;margin-top:4px">Fleche rouge : {zone_label}</div>'}
"""

    iframe_after = f"""
<div style="position:relative;border:3px solid #28a745;border-radius:10px;overflow:hidden;height:300px">
  <iframe src="{url_site}" style="width:100%;height:300px;border:none;pointer-events:none;filter:brightness(0.75) saturate(0.5)" scrolling="no" loading="lazy"></iframe>
  <div style="position:absolute;top:0;left:0;right:0;background:linear-gradient(180deg,#28a745ee,#28a74500);padding:10px 12px 28px;color:white;font-size:12px;font-weight:600;line-height:1.5;z-index:10">
    {after_text}
  </div>
</div>
"""

    return f"""
<div style="margin-bottom:32px">
  <div style="font-size:11px;font-weight:700;color:{frame_color};text-transform:uppercase;letter-spacing:1px;margin-bottom:8px">
    ERREUR {error_num}
  </div>
  <div style="display:grid;grid-template-columns:1fr auto 1fr;gap:12px;align-items:start">
    <div>
      <div style="font-size:10px;color:{frame_color};font-weight:700;margin-bottom:6px;text-transform:uppercase">AVANT — Votre site tel qu'il est</div>
      {iframe_before}
    </div>
    <div style="display:flex;align-items:center;font-size:24px;color:#7c6af7;padding:0 4px;align-self:center">→</div>
    <div>
      <div style="font-size:10px;color:#28a745;font-weight:700;margin-bottom:6px;text-transform:uppercase">APRES — Ce qu'il faut corriger</div>
      {iframe_after}
    </div>
  </div>
  <div style="margin-top:8px;background:rgba(124,106,247,0.1);border-left:3px solid #7c6af7;padding:7px 12px;border-radius:0 6px 6px 0;font-size:12px;color:#b090f7">
    {conseil}
  </div>
</div>
"""


def render_iframe_fallback(error_num, badge_color, before_text, after_text, conseil):
    """Version texte seul si l'iframe ne peut pas etre utilise."""
    badge_icon = "X" if badge_color == "#dc3545" else "!"
    return f"""
<div style="margin-bottom:24px">
  <div style="font-size:11px;font-weight:700;color:{badge_color};text-transform:uppercase;letter-spacing:1px;margin-bottom:8px">
    ERREUR {error_num}
  </div>
  <div style="display:grid;grid-template-columns:1fr auto 1fr;gap:12px;align-items:stretch">
    <div style="background:#1a0808;border:2px solid {badge_color};border-radius:10px;padding:16px;color:white;font-size:13px;line-height:1.6">{before_text}</div>
    <div style="display:flex;align-items:center;font-size:24px;color:#7c6af7;padding:0 4px;align-self:center">→</div>
    <div style="background:#081a08;border:2px solid #28a745;border-radius:10px;padding:16px;color:white;font-size:13px;line-height:1.6">{after_text}</div>
  </div>
  <div style="margin-top:8px;background:rgba(124,106,247,0.1);border-left:3px solid #7c6af7;padding:7px 12px;border-radius:0 6px 6px 0;font-size:12px;color:#b090f7">
    {conseil}
  </div>
</div>
"""
