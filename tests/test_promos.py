from tests.config import BASE_URL, ORGA_EMAIL, ORGA_PASSWORD
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


# EXO 7 - Test 1 : les codes de demonstration sont listes
# On verifie la PRESENCE de 3 codes, pas le nombre de lignes : d'autres codes peuvent exister.
def test_codes(driver):
    # Connexion de l'orga + ouverture de /admin/promos + attente des vraies donnees
    ouvrir_codes_promo(driver)
    # On lit le texte de chaque cellule de code (td.mono) et on le range dans une liste
    codes = [cellule.text for cellule in driver.find_elements(*CELLULES_CODE)]
    assert "WELCOME10" in codes
    assert "VIP25" in codes
    assert "EXPIRED" in codes


# EXO 7 - Test 2 : statut et bouton "Desactiver" de chaque code
# parametrize : le test est lance une fois par cas (code, statut attendu, nombre de boutons attendu).
# Un code actif a un bouton "Desactiver" (1), un code inactif n'en a pas (0).
@pytest.mark.parametrize("code, statut, nb_boutons", [
    ("WELCOME10", "actif", 1),
    ("EXPIRED", "inactif", 0)
])
def test_statut_et_bouton(driver, code, statut, nb_boutons):
    ouvrir_codes_promo(driver)

    # On trouve la ligne du tableau qui contient ce code (f-string : {code} est remplace par la valeur du cas)
    ligne = driver.find_element(By.XPATH, f"//tr[td[normalize-space()='{code}']]")

    # On lit le badge du statut DANS cette ligne (ligne.find_element ne cherche que dans la ligne)
    statut_affiche = ligne.find_element(By.CSS_SELECTOR, ".badge").text
    assert statut_affiche == statut

    # On compte les boutons DANS cette ligne (find_elements renvoie une liste, vide s'il n'y en a pas)
    boutons = ligne.find_elements(By.TAG_NAME, "button")
    assert len(boutons) == nb_boutons
