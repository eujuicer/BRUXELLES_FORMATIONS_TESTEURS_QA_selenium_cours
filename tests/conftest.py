import os
from dotenv import load_dotenv
from selenium import webdriver
import pytest

load_dotenv()

@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()

    if os.getenv("HEADLESS", "true").lower() == "true":
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1366,900")

    drv = webdriver.Chrome(options=options)

    yield drv

    drv.quit()


import base64
import io
import re

from PIL import Image, ImageDraw, ImageFont


def _capture_pleine_page(driver) -> Image.Image:
    """Capture la page entière (au-delà du viewport) via le protocole Chrome DevTools."""
    resultat = driver.execute_cdp_cmd(
        "Page.captureScreenshot",
        {"format": "png", "captureBeyondViewport": True, "fromSurface": True},
    )
    return Image.open(io.BytesIO(base64.b64decode(resultat["data"]))).convert("RGB")


def _ajouter_bandeau_url(image: Image.Image, url: str, titre: str) -> Image.Image:
    """Ajoute en haut de l'image un faux bandeau de navigateur avec l'URL (absente d'une capture Selenium)."""
    hauteur = 56
    try:
        police = ImageFont.truetype("arial.ttf", 18)
    except OSError:
        police = ImageFont.load_default()

    bandeau = Image.new("RGB", (image.width, hauteur), "#dee1e6")
    dessin = ImageDraw.Draw(bandeau)
    dessin.rounded_rectangle(
        (12, 10, image.width - 12, hauteur - 10), radius=14, fill="white"
    )
    dessin.text((28, 16), url, fill="#202124", font=police)
    if titre:
        largeur = dessin.textlength(titre, font=police)
        dessin.text(
            (max(image.width - largeur - 28, 28 + dessin.textlength(url, font=police) + 30), 16),
            titre,
            fill="#5f6368",
            font=police,
        )

    final = Image.new("RGB", (image.width, image.height + hauteur))
    final.paste(bandeau, (0, 0))
    final.paste(image, (0, hauteur))
    return final


def _enregistrer_capture(driver, fichier) -> None:
    try:
        image = _capture_pleine_page(driver)
    except Exception:
        # Navigateur non-Chromium ou session CDP indisponible : capture viewport classique.
        image = Image.open(io.BytesIO(driver.get_screenshot_as_png())).convert("RGB")
    image = _ajouter_bandeau_url(image, driver.current_url, driver.title)
    image.save(fichier)


@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(item, call):
    """Enregistre une capture d'écran (pleine page + URL) quand un test échoue."""
    rapport = yield
    if rapport.when == "call" and rapport.failed:
        driver = item.funcargs.get("driver")
        if driver is not None:
            dossier = item.config.rootpath / "captures"
            dossier.mkdir(exist_ok=True)
            fichier = dossier / (re.sub(r"[^\w.-]", "_", item.name) + ".png")
            _enregistrer_capture(driver, str(fichier))
            rapport.sections.append(("Capture d'écran", str(fichier)))
    return rapport