import sys

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

TOUT_SELECTIONNER = Keys.COMMAND if sys.platform == "darwin" else Keys.CONTROL


# EXO 11 - La classe de base de toutes les pages (BasePage)
# Elle contient ce qui sert a TOUTES les pages : le navigateur, l'attente, les gestes de base
# (trouver, cliquer, saisir, texte) et les elements communs (barre de navigation, titre).
# Les autres pages (LoginPage, PromosPage...) en HERITENT : elles recoivent tout ca sans le recopier.
class BasePage:
    # Locators communs : attributs de classe, accessibles par self.NOM dans toutes les pages.
    # Le lien "Back-office" et le bouton "Deconnexion" sont dans la barre de navigation,
    # presente sur toutes les pages une fois connecte. Le titre est celui des pages du back-office.
    LIEN_BACK_OFFICE = (By.PARTIAL_LINK_TEXT, "Back-office")
    DECONNEXION = (By.XPATH, "//button[normalize-space()='Deconnexion']")
    TITRE = (By.CSS_SELECTOR, "h1.page-title")

    # Constructeur : appele automatiquement a la creation d'une page, par exemple LoginPage(driver).
    # On range le navigateur et la minuterie (10 secondes max) dans l'objet, une seule fois.
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    # ---- Gestes de base ----

    # Attend qu'une condition soit vraie (EC.url_contains(...), une lambda...) et renvoie son resultat.
    # Toutes les autres methodes passent par elle : la minuterie n'est ecrite qu'a un seul endroit.
    def attendre(self, condition):
        return self.wait.until(condition)

    # Attend qu'un element soit visible, puis le renvoie
    def trouver(self, locator):
        return self.attendre(EC.visibility_of_element_located(locator))

    # Attend qu'un element soit cliquable (affiche ET actif), puis clique dessus
    def cliquer(self, locator):
        self.attendre(EC.element_to_be_clickable(locator)).click()

    # Vide un champ puis tape le texte.
    # clear() seul ne suffit pas avec React : on vide aussi au clavier (Ctrl+A puis Suppr).
    def saisir(self, locator, texte):
        champ = self.trouver(locator)
        champ.send_keys(Keys.CONTROL, "a")   # selectionne tout le contenu du champ
        champ.send_keys(Keys.DELETE)         # supprime la selection : le champ est vide
        champ.send_keys(texte)               # tape le nouveau texte

    # Attend un element visible et renvoie son texte
    def texte(self, locator):
        return self.trouver(locator).text

    # Construit le locator d'un champ de formulaire a partir du texte de son <label>.
    # Tous les formulaires d'EventFlow ont la meme structure : <label>Code</label><input>.
    # Exemple : self.champ("Usages max") -> le champ place juste apres le label "Usages max".
    # Le f devant les guillemets remplace {libelle} par la valeur recue.
    def champ(self, libelle):
        return (By.XPATH, f"//label[normalize-space()='{libelle}']/following-sibling::input")

    # ---- Barre de navigation et titre (communs a toutes les pages) ----

    # Clique sur "Back-office" dans la navbar et attend d'etre arrive : ce sont les 3 etapes de l'exo 5.
    # Renvoie self pour pouvoir enchainer un appel derriere (page.aller_au_back_office().titre()).
    def aller_au_back_office(self):
        self.cliquer(self.LIEN_BACK_OFFICE)        # 1. cliquer sur le lien
        self.attendre(EC.url_contains("/admin"))   # 2. attendre que l'URL change
        self.trouver(self.TITRE)                   # 3. attendre le titre : la page est prete
        return self

    # Renvoie le texte du titre de la page (h1.page-title)
    def titre(self):
        return self.texte(self.TITRE)

    # Dit si le lien "Back-office" est present dans la navbar (True ou False).
    # AUCUNE attente, volontairement : on ne peut pas attendre qu'un element absent apparaisse.
    # find_elements renvoie une liste vide s'il n'y a rien (find_element planterait).
    # C'est au test de l'appeler au bon moment, par exemple apres avoir attendu une redirection.
    def a_le_lien_back_office(self):
        return self.driver.find_elements(*self.LIEN_BACK_OFFICE) != []


