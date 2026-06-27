"""
Sitra - Module de capture precise via Playwright
Prend une capture de la page et dessine un cadre rouge autour de l'element concerne.
"""

import os
import io
import base64
import streamlit as st


@st.cache_data(ttl=3600, show_spinner=False)
def get_screenshot_with_highlight(url: str, selector: str = None):
    """
    Prend une capture de la page via Playwright.
    Si selector est fourni, dessine un cadre rouge autour de l'element.
    Retourne (data_uri, was_targeted) ou (None, False) si echec.
    """
    try:
        from playwright.sync_api import sync_playwright
        import PIL.Image
        import PIL.ImageDraw

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-blink-features=AutomationControlled",
                ]
            )
            context = browser.new_context(
                viewport={"width": 1280, "height": 800},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()

            try:
                page.goto(url, timeout=20000, wait_until="domcontentloaded")
                page.wait_for_timeout(2000)
            except Exception:
                browser.close()
                return None, False

            screenshot_bytes = page.screenshot(full_page=False)

            bbox = None
            if selector:
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

            browser.close()

        img = PIL.Image.open(io.BytesIO(screenshot_bytes))
        img_w, img_h = img.width, img.height

        if bbox:
            draw = PIL.ImageDraw.Draw(img)
            pad = 8

            # Calcul des coordonnees avec clamp strict dans les limites de l'image
            x1 = max(0, int(bbox["x"]) - pad)
            y1 = max(0, int(bbox["y"]) - pad)
            x2 = min(img_w - 1, int(bbox["x"] + bbox["width"]) + pad)
            y2 = min(img_h - 1, int(bbox["y"] + bbox["height"]) + pad)

            # Securite : s'assurer que x2 > x1 et y2 > y1
            if x2 <= x1:
                x2 = min(img_w - 1, x1 + 10)
            if y2 <= y1:
                y2 = min(img_h - 1, y1 + 10)

            # Cadre rouge epais
            for i in range(4):
                x1i = max(0, x1 - i)
                y1i = max(0, y1 - i)
                x2i = min(img_w - 1, x2 + i)
                y2i = min(img_h - 1, y2 + i)
                if x2i > x1i and y2i > y1i:
                    draw.rectangle([x1i, y1i, x2i, y2i], outline=(220, 53, 69), width=2)

            # Triangle rouge indicateur en haut a gauche
            tri_size = 20
            tx1 = x1
            ty1 = y1
            tx2 = min(img_w - 1, x1 + tri_size)
            ty2 = min(img_h - 1, y1 + tri_size)
            if tx2 > tx1 and ty2 > ty1:
                draw.polygon([(tx1, ty1), (tx2, ty1), (tx1, ty2)], fill=(220, 53, 69))

            was_targeted = True
        else:
            was_targeted = False

        buf = io.BytesIO()
        img.save(buf, format="PNG", optimize=True)
        data_uri = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()

        return data_uri, was_targeted

    except Exception as e:
        return None, False
