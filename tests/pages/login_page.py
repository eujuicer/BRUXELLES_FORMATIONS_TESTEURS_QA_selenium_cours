from selenium.webdriver.common.by import By

from tests.config import BASE_URL
from tests.pages.base_page import BasePage


# EXO 10 / 11 - La page de connexion (Page Object), qui HERITE de BasePage.
# class LoginPage(BasePage) : LoginPage recoit le constructeur (self.driver, self.wait) et tous
# les gestes de base (attendre, trouver, cliquer, saisir, texte...) sans les recopier.
# Elle ne garde que ce qui est propre a la page de connexion : ses locators et ses actions.
class LoginPage(BasePage):
    # Attributs de classe : les locators du formulaire, partages par tous les objets LoginPage.
    # On y accede avec self.EMAIL dans les methodes.
    # (DECONNEXION n'est pas ici : il est herite de BasePage, c'est un element de la navbar.)
    EMAIL = (By.CSS_SELECTOR, "input[type=email]")
    PASSWORD = (By.CSS_SELECTOR, "input[type=password]")
    SUBMIT = (By.CSS_SELECTOR, "form button.btn-primary")
    ERREUR = (By.CSS_SELECTOR, ".notice-err")

    # ---- Ce que fait l'utilisateur ----
    # ouvrir, soumettre et se_connecter renvoient self : on peut les enchainer
    # (LoginPage(driver).ouvrir().soumettre(...)).

    # Ouvre /login et attend que le formulaire soit affiche
    def ouvrir(self):
        self.driver.get(BASE_URL + "/login")
        self.trouver(self.EMAIL)   # trouver() vient de BasePage
        return self

    # Remplit et envoie le formulaire, SANS rien attendre ensuite.
    # Indispensable pour le test du mauvais mot de passe : il n'y aura jamais de "Deconnexion".
    def soumettre(self, email, password):
        self.saisir(self.EMAIL, email)      # saisir() vient de BasePage
        self.saisir(self.PASSWORD, password)
        self.cliquer(self.SUBMIT)           # cliquer() vient de BasePage
        return self

    # Soumet, puis attend le bouton "Deconnexion" : il n'apparait qu'une fois connecte.
    def se_connecter(self, email, password):
        self.soumettre(email, password)
        self.trouver(self.DECONNEXION)      # DECONNEXION vient de BasePage
        return self

    # Attend le message d'erreur et renvoie son texte (texte() vient de BasePage)
    def message_erreur(self):
        return self.texte(self.ERREUR)
