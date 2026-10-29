# EXO 2 - Les locators de la page de connexion
# But : verifier que chaque locator designe EXACTEMENT un element sur /login.
# Un bon locator en trouve un seul : s'il en trouve plusieurs, Selenium prend le premier
# sans prevenir (risque de cliquer sur le mauvais) ; s'il n'en trouve aucun, le test plante.

import time

import pytest
from selenium.webdriver.common.by import By

from tests.config import BASE_URL

# EXO 2 - LOCATORS
# Champ email
EMAIL = (By.CSS_SELECTOR, "input[type=email]")

# Champ mot de passe : une version CSS (par le type) et une version XPath (par le label)
PASSWORD_CSS = (By.CSS_SELECTOR, "input[type=password]")
PASSWORD_LABEL = (By.XPATH, "//label[normalize-space()='Mot de passe']/following-sibling::input")

# Bouton "Se connecter" : une version CSS et une version XPath (par le texte)
# On ecrit "form button.btn-primary" et pas ".btn-primary" tout seul : sur /login, ".btn-primary"
# correspond aussi au lien "Connexion" de la navbar, donc 2 elements.
SUBMIT_CSS = (By.CSS_SELECTOR, "form button.btn-primary")
SUBMIT_XPATH = (By.XPATH, "//button[normalize-space()='Se connecter']")

LOCATORS = [EMAIL, PASSWORD_CSS, PASSWORD_LABEL, SUBMIT_CSS, SUBMIT_XPATH]


# EXO 2 - Un seul test, execute une fois par locator grace a parametrize
# ids=lambda loc: loc[1] : le nom de chaque cas dans "pytest -v" est la valeur du locator
@pytest.mark.parametrize("locator", LOCATORS, ids=lambda loc: loc[1])
def test_locator_designe_un_seul_element(driver, locator):
    driver.get(f"{BASE_URL}/login")
    time.sleep(2)  # pause pour voir la page (a retirer ensuite)

    # find_elements (au pluriel) renvoie une liste, vide si rien n'est trouve : ideal pour compter
    elements = driver.find_elements(*locator)

    # Le message apres la virgule s'affiche si le test echoue : il donne le nombre trouve
    assert len(elements) == 1, f"{locator[1]} : {len(elements)} element(s) trouve(s)"
