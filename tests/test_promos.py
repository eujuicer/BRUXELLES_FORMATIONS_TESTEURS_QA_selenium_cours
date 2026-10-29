from tests.config import BASE_URL, ORGA_EMAIL, ORGA_PASSWORD, CLIENT_EMAIL, CLIENT_PASSWORD
from selenium.webdriver.common.by import By
import pytest
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

EMAIL_INPUT = (By.CSS_SELECTOR, "input[type=email]")
PASSWORD_INPUT = (By.CSS_SELECTOR, "input[type=password]")
LOGIN_BTN = (By.CSS_SELECTOR, "form button.btn-primary")
DECONNEXION = (By.XPATH, "//button[normalize-space()='Deconnexion']")
CELLULES_CODE = (By.CSS_SELECTOR, "table.table tbody td.mono")


def ouvrir_codes_promo(driver):
    # Ouvre la page de connexion
    driver.get(f"{BASE_URL}/login")
    # Minuterie reutilisable : chaque wait.until(...) attend au maximum 10 secondes
    wait = WebDriverWait(driver, 10)

    # GESTE 2 : connexion de l'organisateur (identifiants lus dans config.py)
    # On attend le champ email, on le vide (il est pre-rempli), puis on tape l'email
    email = wait.until(EC.visibility_of_element_located(EMAIL_INPUT))
    email.clear()
    email.send_keys(ORGA_EMAIL)

    # Meme chose pour le mot de passe
    password = wait.until(EC.visibility_of_element_located(PASSWORD_INPUT))
    password.clear()
    password.send_keys(ORGA_PASSWORD)

    # On clique sur "Se connecter"
    driver.find_element(*LOGIN_BTN).click()

    # On attend la fin de la connexion : "Deconnexion" n'apparait qu'une fois connecte
    wait.until(EC.visibility_of_element_located(DECONNEXION))

    # GESTE 3 : ouvrir la page des codes promo
    driver.get(f"{BASE_URL}/admin/promos")
    wait.until(EC.visibility_of_element_located(CELLULES_CODE))

def test_codes(driver):
    ouvrir_codes_promo(driver)
    codes = [cellule.text for cellule in driver.find_elements(*CELLULES_CODE)]
    assert "WELCOME10" in codes
    assert "VIP25" in codes
    assert "EXPIRED" in codes 


