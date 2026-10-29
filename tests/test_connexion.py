import time

from tests.config import BASE_URL
from selenium.webdriver.common.by import By
import pytest

EMAIL_INPUT = (By.CSS_SELECTOR, "input[type=email]")
PASSWORD_INPUT = (By.CSS_SELECTOR, "input[type=password]")
LOGIN_BTN = (By.CSS_SELECTOR, "form button.btn-primary")
ERREUR = (By.CSS_SELECTOR, ".notice-err")


# EXO 3 - Un mauvais mot de passe
# Un organisateur saisit son email et un mauvais mot de passe : la page doit afficher
# "Incorrect email or password" et rester sur /login.
# (Pas d'attente ici volontairement : le test peut echouer, c'est l'objet de l'exo 4.)
def test_mauvais_mot_de_passe(driver):
    driver.get(f"{BASE_URL}/login")
    time.sleep(2)

    # Les champs arrivent pre-remplis (compte client) : on les vide avant de taper
    email = driver.find_element(*EMAIL_INPUT)
    email.clear()
    email.send_keys("orga@eventflow.test")
    time.sleep(2)

    mot_de_passe = driver.find_element(*PASSWORD_INPUT)
    mot_de_passe.clear()
    mot_de_passe.send_keys("mauvais-mot-de-passe")
    time.sleep(2)

    driver.find_element(*LOGIN_BTN).click()
    time.sleep(2)

    # Lecture immediate du message : il peut ne pas etre encore affiche
    message = driver.find_element(*ERREUR)

    assert message.text == "Incorrect email or password"
    assert driver.current_url == f"{BASE_URL}/login"
