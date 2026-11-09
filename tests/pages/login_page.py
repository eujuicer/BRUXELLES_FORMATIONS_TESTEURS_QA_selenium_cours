from tests.config import BASE_URL
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


# EXO 10 - La page de connexion sous forme de classe (Page Object)
# Les locators et les gestes (saisir, cliquer...) vivent ici : les tests ne parlent plus
# a Selenium, ils disent seulement ce que fait l'utilisateur (ouvrir, soumettre...).
class LoginPage:
    # Attributs de classe : les locators, partages par tous les objets LoginPage.
    # On y accede avec self.EMAIL dans les methodes.
    EMAIL = (By.CSS_SELECTOR, "input[type=email]")
    PASSWORD = (By.CSS_SELECTOR, "input[type=password]")
    SUBMIT = (By.CSS_SELECTOR, "form button.btn-primary")
    ERREUR = (By.CSS_SELECTOR, ".notice-err")
    DECONNEXION = (By.XPATH, "//button[normalize-space()='Deconnexion']")

    # Constructeur : appele automatiquement par LoginPage(driver).
    # On range le navigateur et la minuterie (10 secondes max) dans l'objet, une seule fois.
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    # ---- Gestes de base (reutilisables par toutes les methodes) ----

    # Attend qu'un element soit visible, puis le renvoie
    def trouver(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    # Attend qu'un element soit cliquable (affiche ET actif), puis clique
    def cliquer(self, locator):
        self.wait.until(EC.element_to_be_clickable(locator)).click()

    # Vide un champ puis tape le texte.
    # clear() seul ne suffit pas avec React : on vide aussi au clavier (Ctrl+A puis Suppr).
    def saisir(self, locator, texte):
        champ = self.trouver(locator)
        champ.send_keys(Keys.CONTROL, "a")   # selectionne tout le contenu du champ
        champ.send_keys(Keys.DELETE)         # supprime la selection : le champ est vide
        champ.send_keys(texte)               # tape le nouveau texte

    # ---- Ce que fait l'utilisateur ----
    # ouvrir, soumettre et se_connecter renvoient self : on peut les enchainer
    # (LoginPage(driver).ouvrir().soumettre(...)).

    # Ouvre /login et attend que le formulaire soit affiche
    def ouvrir(self):
        self.driver.get(BASE_URL + "/login")
        self.trouver(self.EMAIL)
        return self

    # Remplit et envoie le formulaire, SANS rien attendre ensuite.
    # Indispensable pour le test du mauvais mot de passe : il n'y aura jamais de "Deconnexion".
    def soumettre(self, email, password):
        self.saisir(self.EMAIL, email)
        self.saisir(self.PASSWORD, password)
        self.cliquer(self.SUBMIT)
        return self

    # Soumet, puis attend le bouton "Deconnexion" : il n'apparait qu'une fois connecte.
    def se_connecter(self, email, password):
        self.soumettre(email, password)
        self.trouver(self.DECONNEXION)
        return self

    # Attend le message d'erreur et renvoie son texte
    def message_erreur(self):
        return self.trouver(self.ERREUR).text
