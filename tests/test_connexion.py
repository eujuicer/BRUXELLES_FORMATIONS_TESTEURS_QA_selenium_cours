import time

from tests.config import BASE_URL, ORGA_EMAIL, ORGA_PASSWORD
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



# EXO 3 - Un mauvais mot de passe
# Un organisateur saisit son email et un mauvais mot de passe : la page doit afficher
# "Incorrect email or password" et rester sur /login.
# (Pas d'attente ici volontairement : le test peut echouer, c'est l'objet de l'exo 4.)
def test_mauvais_mot_de_passe(driver):
    driver.get(f"{BASE_URL}/login")
    wait = WebDriverWait(driver, 10)

    # Les champs arrivent pre-remplis (compte client) : on les vide avant de taper
    email = wait.until(EC.visibility_of_element_located(EMAIL_INPUT))
    email.clear()
    email.send_keys("orga@eventflow.test")
    

    mot_de_passe = wait.until(EC.visibility_of_element_located(PASSWORD_INPUT))
    mot_de_passe.clear()
    mot_de_passe.send_keys("mauvais-mot-de-passe")
    

    driver.find_element(*LOGIN_BTN).click()
   

    # Lecture immediate du message : il peut ne pas etre encore affiche
    message = wait.until(EC.visibility_of_element_located(ERREUR))
    assert message.text == "Incorrect email or password"
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
