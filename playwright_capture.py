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
                    "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
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
            except Exception as e:
                import streamlit as st
                st.write(f"DEBUG goto error: {e}")
                browser.close()
                return None, False

            # Capture pleine page visible (pas full_page pour rester dans le viewport)
            screenshot_bytes = page.screenshot(full_page=False)

            # Recuperer la position de l'element
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

        # Dessiner le cadre rouge sur l'image
        img = PIL.Image.open(io.BytesIO(screenshot_bytes))

        if bbox:
            draw = PIL.ImageDraw.Draw(img)
            x = bbox["x"]
            y = bbox["y"]
            w = bbox["width"]
            h = bbox["height"]
            pad = 8
            x1 = max(0, x - pad)
            y1 = max(0, y - pad)
            x2 = min(img.width, x + w + pad)
            y2 = min(img.height, y + h + pad)

            # Cadre rouge epais
            for i in range(4):
                draw.rectangle(
                    [x1 - i, y1 - i, x2 + i, y2 + i],
                    outline=(220, 53, 69),
                    width=2
                )

            # Triangle rouge en haut a gauche pour pointer l'erreur
            draw.polygon(
                [(x1, y1), (x1 + 24, y1), (x1, y1 + 24)],
                fill=(220, 53, 69)
            )
            was_targeted = True
        else:
            was_targeted = False

        # Convertir en base64 data URI
        buf = io.BytesIO()
        img.save(buf, format="PNG", optimize=True)
        data_uri = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()

        return data_uri, was_targeted

    except Exception as e:
        # Log l'erreur pour debug
        try:
            import streamlit as _st
            _st.write(f"DEBUG Playwright error: {type(e).__name__}: {e}")
        except Exception:
            pass
        return None, False
