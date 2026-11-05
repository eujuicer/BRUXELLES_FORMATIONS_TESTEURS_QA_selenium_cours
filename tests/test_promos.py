from tests.config import BASE_URL, ORGA_EMAIL, ORGA_PASSWORD
from selenium.webdriver.common.by import By
import pytest, uuid 
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys

EMAIL_INPUT = (By.CSS_SELECTOR, "input[type=email]")
PASSWORD_INPUT = (By.CSS_SELECTOR, "input[type=password]")
LOGIN_BTN = (By.CSS_SELECTOR, "form button.btn-primary")
DECONNEXION = (By.XPATH, "//button[normalize-space()='Deconnexion']")
CELLULES_CODE = (By.CSS_SELECTOR, "table.table tbody td.mono")
CHAMP_CODE = (By.XPATH, "//label[normalize-space()='Code']/following-sibling::input")
CHAMP_REDUCTION = (By.XPATH, "//label[normalize-space()='Reduction (%)']/following-sibling::input")
CHAMP_USAGES = (By.XPATH, "//label[normalize-space()='Usages max']/following-sibling::input")
BTN_CREER = (By.XPATH, "//form//button[normalize-space()='Creer']")




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


# Vide un champ puis tape le texte.
# clear() seul ne suffit pas : EventFlow est en React, qui garde sa propre copie de la valeur.
# On vide donc aussi au clavier (Ctrl+A puis Suppr), comme le ferait un vrai utilisateur.
def saisir(driver, locator, texte):
    champ = driver.find_element(*locator)
    champ.send_keys(Keys.CONTROL, "a")   # selectionne tout le contenu du champ
    champ.send_keys(Keys.DELETE)         # supprime la selection : le champ est vide
    champ.send_keys(texte)               # tape le nouveau texte


# EXO 8 : creer un code promo, puis le desactiver
# Scenario : l'orga cree un code (15 %, 20 usages max), verifie sa ligne, le desactive,
# et verifie que son statut passe a "inactif" et que son bouton disparait.
def test_creer_puis_desactiver(driver):
    # Connexion de l'orga + ouverture de /admin/promos
    ouvrir_codes_promo(driver)
    wait = WebDriverWait(driver, 10)

    # ETAPE 1 : code unique, genere a chaque lancement (jamais ecrit en dur).
    # Le code reste en base apres le test : le meme code echouerait au 2e lancement.
    # .upper() car l'appli met le champ en majuscules : sinon la comparaison echouerait.
    code = "TEST" + uuid.uuid4().hex[:6].upper()

    # ETAPE 2 : remplir les 3 champs, puis cliquer sur "Creer"
    # Reduction (10) et Usages max (100) sont pre-remplis : saisir() les vide avant de taper.
    saisir(driver, CHAMP_CODE, code)
    saisir(driver, CHAMP_REDUCTION, "15")
    saisir(driver, CHAMP_USAGES, "20")
    driver.find_element(*BTN_CREER).click()

    # ETAPE 3 : attendre la ligne du nouveau code (le tableau se recharge apres la creation)
    # Le locator est dans le test car il depend de la variable code.
    LIGNE = (By.XPATH, f"//tr[td[normalize-space()='{code}']]")
    ligne = wait.until(EC.visibility_of_element_located(LIGNE))

    # On lit le texte des 5 premieres cellules (la 6e contient le bouton) et on les compare
    cellules = [td.text for td in ligne.find_elements(By.TAG_NAME, "td")[:5]]
    assert cellules == [code, "-15%", "0/20", "—", "actif"]

    # ETAPE 4 : cliquer sur "Desactiver" DANS cette ligne
    # Le "." au debut du XPath limite la recherche a la ligne (sans lui : toute la page).
    ligne.find_element(By.XPATH, ".//button[normalize-space()='Desactiver']").click()

    # Le tableau se recharge : on attend que le badge de CETTE ligne passe a "inactif".
    # On utilise un locator plutot que "ligne", qui pointe vers un element remplace par le rechargement.
    BADGE = (By.XPATH, f"//tr[td[normalize-space()='{code}']]//span[contains(@class,'badge')]")
    wait.until(EC.text_to_be_present_in_element(BADGE, "inactif"))

    # ETAPE 5 : plus aucun bouton dans la ligne
    # On relit la ligne (rechargee) ; find_elements renvoie une liste vide s'il n'y a rien.
    ligne = driver.find_element(*LIGNE)
    assert ligne.find_elements(By.TAG_NAME, "button") == []
