"""
Sitra - Module de capture précise via Playwright
Prend une capture complète de la page, localise l'élément concerné
et dessine un cadre de repérage directement sur l'image.
"""

import os
import io
import base64
import streamlit as st

# Installation automatique des navigateurs Playwright au premier appel
def _ensure_playwright_installed():
    try:
        os.system("playwright install chromium --with-deps 2>/dev/null")
    except Exception:
        pass

@st.cache_data(ttl=3600, show_spinner=False)
def get_screenshot_with_highlight(url: str, selector: str = None):
    """
    Prend une capture complète de la page via Playwright.
    Si selector est fourni, dessine un cadre rouge/orange autour de l'élément.
    Retourne l'image en base64 (data URI) ou None si échec.
    """
    try:
        _ensure_playwright_installed()
        from playwright.sync_api import sync_playwright
        import PIL.Image
        import PIL.ImageDraw

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
            )
            page = browser.new_page(viewport={"width": 1280, "height": 800})

            try:
                page.goto(url, timeout=15000, wait_until="domcontentloaded")
                page.wait_for_timeout(2000)
            except Exception:
                browser.close()
                return None, None

            # Capture pleine page
            screenshot_bytes = page.screenshot(full_page=False)

            # Si on a un sélecteur, on récupère la position de l'élément
            bbox = None
            if selector:
                try:
                    # On essaie chaque sélecteur séparé par une virgule
                    selectors = [s.strip() for s in selector.split(",")]
                    for sel in selectors:
                        try:
                            element = page.query_selector(sel)
                            if element:
                                box = element.bounding_box()
                                if box and box["width"] > 0 and box["height"] > 0:
                                    bbox = box
                                    break
                        except Exception:
                            continue
                except Exception:
                    bbox = None

            browser.close()

        # Dessiner le cadre sur l'image si on a une bbox
        img = PIL.Image.open(io.BytesIO(screenshot_bytes))
        
        if bbox:
            draw = PIL.ImageDraw.Draw(img)
            x, y, w, h = bbox["x"], bbox["y"], bbox["width"], bbox["height"]
            # Cadre rouge épais autour de l'élément
            padding = 6
            x1, y1 = max(0, x - padding), max(0, y - padding)
            x2, y2 = min(img.width, x + w + padding), min(img.height, y + h + padding)
            # Dessine 3 rectangles pour un cadre épais et visible
            for offset in range(3):
                draw.rectangle(
                    [x1 - offset, y1 - offset, x2 + offset, y2 + offset],
                    outline=(220, 53, 69),  # Rouge SITRA
                    width=2
                )
            # Petite flèche indicatrice en haut à gauche du cadre
            draw.polygon(
                [(x1, y1), (x1 + 20, y1), (x1, y1 + 20)],
                fill=(220, 53, 69)
            )
            was_targeted = True
        else:
            was_targeted = False

        # Convertir en base64
        buffer = io.BytesIO()
        img.save(buffer, format="PNG", optimize=True)
        img_b64 = base64.b64encode(buffer.getvalue()).decode()
        data_uri = f"data:image/png;base64,{img_b64}"

        return data_uri, was_targeted

    except Exception:
        return None, None
