"""
Sitra - Module de capture precise via Playwright
Scrolle jusqu'a l'element concerne, le centre dans la capture,
et dessine un cadre rouge autour pour montrer exactement ou est l'erreur.
"""

import io
import base64
import streamlit as st


@st.cache_data(ttl=3600, show_spinner=False)
def get_screenshot_with_highlight(url: str, selector: str = None):
    """
    1. Charge la page
    2. Ferme les popups/cookies
    3. Scrolle jusqu'a l'element concerne
    4. Prend une capture centree sur cet element
    5. Dessine un cadre rouge autour
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

            # Ferme les popups et widgets tiers
            try:
                for sel in [
                    "button[id*='accept']", "button[id*='cookie']",
                    "button[class*='close']", "button[aria-label*='close']",
                    "button[aria-label*='fermer']", "button[aria-label*='Close']",
                    "[class*='zenchef'] button", "[id*='zenchef'] button",
                    "[class*='widget'] .close", "[class*='popup'] .close",
                    "[class*='modal'] .close", "[class*='overlay'] .close"
                ]:
                    try:
                        btn = page.query_selector(sel)
                        if btn and btn.is_visible():
                            btn.click()
                            page.wait_for_timeout(300)
                    except Exception:
                        continue
            except Exception:
                pass

            # Attend que les widgets tiers disparaissent
            page.wait_for_timeout(500)

            bbox = None
            was_targeted = False

            if selector:
                # Pour les images : on exclut les logos (petites images en haut)
                # en cherchant la plus grande image visible sur la page
                if "img" in selector.lower():
                    try:
                        images = page.query_selector_all("img")
                        best = None
                        best_area = 0
                        for img_el in images:
                            try:
                                box = img_el.bounding_box()
                                if box and box["width"] > 100 and box["height"] > 80:
                                    area = box["width"] * box["height"]
                                    if area > best_area:
                                        # Verifie que l'image n'a pas d'attribut alt
                                        alt = img_el.get_attribute("alt") or ""
                                        if not alt.strip():
                                            best_area = area
                                            best = (img_el, box)
                            except Exception:
                                continue
                        # Si aucune sans alt, prend la plus grande quand meme
                        if not best:
                            for img_el in images:
                                try:
                                    box = img_el.bounding_box()
                                    if box and box["width"] > 100 and box["height"] > 80:
                                        area = box["width"] * box["height"]
                                        if area > best_area:
                                            best_area = area
                                            best = (img_el, box)
                                except Exception:
                                    continue
                        if best:
                            best[0].scroll_into_view_if_needed()
                            page.wait_for_timeout(500)
                            bbox = best[0].bounding_box()
                            was_targeted = True
                    except Exception:
                        pass
                else:
                    # Pour les autres elements
                    selectors = [s.strip() for s in selector.split(",")]
                    for sel in selectors:
                        try:
                            element = page.query_selector(sel)
                            if element and element.is_visible():
                                element.scroll_into_view_if_needed()
                                page.wait_for_timeout(500)
                                box = element.bounding_box()
                                if box and box["width"] > 0 and box["height"] > 0:
                                    bbox = box
                                    was_targeted = True
                                    break
                        except Exception:
                            continue

            # Capture du viewport apres scroll
            screenshot_bytes = page.screenshot(full_page=False)
            browser.close()

        img = PIL.Image.open(io.BytesIO(screenshot_bytes))
        img_w, img_h = img.width, img.height

        if bbox:
            draw = PIL.ImageDraw.Draw(img)
            pad = 10

            x1 = max(0, int(bbox["x"]) - pad)
            y1 = max(0, int(bbox["y"]) - pad)
            x2 = min(img_w - 1, int(bbox["x"] + bbox["width"]) + pad)
            y2 = min(img_h - 1, int(bbox["y"] + bbox["height"]) + pad)

            if x2 <= x1:
                x2 = min(img_w - 1, x1 + 50)
            if y2 <= y1:
                y2 = min(img_h - 1, y1 + 50)

            # Cadre rouge epais
            for i in range(4):
                rx1 = max(0, x1 - i)
                ry1 = max(0, y1 - i)
                rx2 = min(img_w - 1, x2 + i)
                ry2 = min(img_h - 1, y2 + i)
                if rx2 > rx1 and ry2 > ry1:
                    draw.rectangle([rx1, ry1, rx2, ry2], outline=(220, 53, 69), width=2)

            # Triangle rouge indicateur
            tri = 22
            tx2 = min(img_w - 1, x1 + tri)
            ty2 = min(img_h - 1, y1 + tri)
            if tx2 > x1 and ty2 > y1:
                draw.polygon([(x1, y1), (tx2, y1), (x1, ty2)], fill=(220, 53, 69))

        buf = io.BytesIO()
        img.save(buf, format="PNG", optimize=True)
        data_uri = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()

        return data_uri, was_targeted

    except Exception:
        return None, False
