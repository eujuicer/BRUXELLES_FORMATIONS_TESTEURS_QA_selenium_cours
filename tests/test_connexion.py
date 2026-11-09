import time

from tests.config import BASE_URL, ORGA_EMAIL, ORGA_PASSWORD, CLIENT_EMAIL, CLIENT_PASSWORD
from tests.pages.login_page import LoginPage
from selenium.webdriver.common.by import By
import pytest
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait




EMAIL_INPUT = (By.CSS_SELECTOR, "input[type=email]")
PASSWORD_INPUT = (By.CSS_SELECTOR, "input[type=password]")
LOGIN_BTN = (By.CSS_SELECTOR, "form button.btn-primary")
ERREUR = (By.CSS_SELECTOR, ".notice-err")
DECONNEXION = (By.XPATH, "//button[normalize-space()='Deconnexion']")
BACK_OFFICE = (By.PARTIAL_LINK_TEXT, "Back-office")
TITRE = (By.CSS_SELECTOR, "h1.page-title")



# EXO 3 / EXO 10 - Un mauvais mot de passe, reecrit avec LoginPage
# Un organisateur saisit son email et un mauvais mot de passe : la page doit afficher
# "Incorrect email or password" et rester sur /login.
# Le test ne contient ni locator, ni attente, ni find_element : tout est dans LoginPage.
def test_mauvais_mot_de_passe_affiche_une_erreur(driver):
    # Ouvre /login puis envoie le formulaire (soumettre n'attend pas de connexion reussie)
    page = LoginPage(driver).ouvrir().soumettre(ORGA_EMAIL, "mauvais-mot-de-passe")

    # message_erreur() attend le message, puis renvoie son texte
    assert page.message_erreur() == "Incorrect email or password"
    # On est toujours sur la page de connexion
    assert driver.current_url == f"{BASE_URL}/login"


# EXO 5 - L'organisateur accede au back-office
# Scenario : l'orga se connecte, clique sur "Back-office" dans la navbar,
# et arrive sur la page /admin dont le titre est "Back-office".
def test_orga_acces_back_office(driver):
    # Ouvre la page de connexion
    driver.get(f"{BASE_URL}/login")
    # Minuterie reutilisable : chaque wait.until(...) attend au maximum 10 secondes
    wait = WebDriverWait(driver, 10)

    # ETAPE 1 : remplir et envoyer le formulaire avec le compte organisateur
    # On attend que le champ email soit affiche, on le vide (il est pre-rempli), puis on tape
    # l'email lu dans config.py (pas ecrit en dur dans le test)
    email = wait.until(EC.visibility_of_element_located(EMAIL_INPUT))
    email.clear()
    email.send_keys(ORGA_EMAIL)

    # Meme chose pour le mot de passe
    password = wait.until(EC.visibility_of_element_located(PASSWORD_INPUT))
    password.clear()
    password.send_keys(ORGA_PASSWORD)

    # On clique sur "Se connecter"
    driver.find_element(*LOGIN_BTN).click()

    # ETAPE 2 : attendre la fin de la connexion
    # Le bouton "Deconnexion" n'apparait dans la navbar que quand la connexion est terminee
    wait.until(EC.visibility_of_element_located(DECONNEXION))

    # ETAPE 3 : attendre que le lien "Back-office" soit cliquable (affiche et actif), puis cliquer
    lien = wait.until(EC.element_to_be_clickable(BACK_OFFICE))
    lien.click()

    # ETAPE 4 : attendre que l'URL contienne /admin (la page a fini de changer)
    wait.until(EC.url_contains("/admin"))

    # ETAPE 5 : attendre le titre de la page (h1.page-title), puis verifier son texte
    # Le titre n'apparait qu'une fois la session verifiee, c'est un bon signe que la page est prete
    titre = wait.until(EC.visibility_of_element_located(TITRE))
    assert titre.text == "Back-office"


# EXO 6 - Un client ne peut pas entrer dans le back-office
# Scenario : un client connecte ouvre /admin, il est renvoye vers le catalogue (/)
# et sa navbar n'a pas de lien "Back-office".
def test_client_refuse_back_office(driver):
    # Ouvre la page de connexion
    driver.get(f"{BASE_URL}/login")
    # Minuterie reutilisable : chaque wait.until(...) attend au maximum 10 secondes
    wait = WebDriverWait(driver, 10)

    # ETAPE 1 : se connecter avec le compte CLIENT (identifiants lus dans config.py)
    email = wait.until(EC.visibility_of_element_located(EMAIL_INPUT))
    email.clear()
    email.send_keys(CLIENT_EMAIL)

    password = wait.until(EC.visibility_of_element_located(PASSWORD_INPUT))
    password.clear()
    password.send_keys(CLIENT_PASSWORD)

    driver.find_element(*LOGIN_BTN).click()

    # Attendre la fin de la connexion : le bouton "Deconnexion" apparait dans la navbar
    wait.until(EC.visibility_of_element_located(DECONNEXION))

    # ETAPE 2 : ouvrir /admin directement dans l'URL (un client n'a pas le lien, donc pas de clic)
    driver.get(f"{BASE_URL}/admin")

    # ETAPE 3 : attendre que l'URL ne se termine plus par /admin (= la redirection a eu lieu)
    # Aucune condition "EC" ne fait ca : on ecrit la notre avec une lambda.
    # d = le navigateur, la lambda renvoie True quand l'etat attendu est atteint.
    wait.until(lambda d: not d.current_url.endswith("/admin"))

    # ETAPE 4 : verifier l'URL finale (on doit etre sur le catalogue)
    assert driver.current_url == f"{BASE_URL}/"

    # ... et verifier que le lien "Back-office" est ABSENT de la navbar.
    # find_elements renvoie une liste vide si rien n'est trouve (find_element planterait)
    # Pourquoi apres l'attente de la redirection ? Juste apres driver.get("/admin"), la page n'a pas
    # encore redirige : la navbar n'affiche pas encore le lien, meme si un orga l'aurait ensuite.
    # Verifier trop tot donnerait "absent" a coup sur : un test qui passe sans rien prouver.
    assert driver.find_elements(*BACK_OFFICE) == []
