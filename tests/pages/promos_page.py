from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from tests.config import BASE_URL
from tests.pages.base_page import BasePage


# EXO 12 - La page des codes promo (Page Object), qui HERITE de BasePage.
# Elle regroupe tout ce que test_promos.py sait de /admin/promos : les tests disent ce que fait
# l'orga (creer, desactiver, lire un statut), la page sait comment Selenium le fait.
# trouver, cliquer, saisir, texte, attendre et champ viennent de BasePage.
class PromosPage(BasePage):
    # Les codes du tableau (une cellule td.mono par ligne)
    CELLULES_CODE = (By.CSS_SELECTOR, "table.table tbody td.mono")
    # Le bouton "Creer" DANS le formulaire (il y a d'autres boutons dans le tableau)
    BOUTON_CREER = (By.XPATH, "//form//button[normalize-space()='Creer']")

    # ---- Locators qui dependent du code : ce sont des methodes, pas des attributs ----

    # Locator de la ligne d'un code (f-string : {code} est remplace par la valeur recue)
    def ligne(self, code):
        return By.XPATH, f"//tr[td[normalize-space()='{code}']]"

    # Locator du badge de statut DANS la ligne d'un code.
    # On repart du locator de la ligne et on y ajoute la suite du chemin XPath.
    def badge(self, code):
        _, xpath_ligne = self.ligne(code)
        return By.XPATH, xpath_ligne + "//span[contains(@class,'badge')]"

    # Locator du bouton "Desactiver" DANS la ligne d'un code
    def bouton_desactiver(self, code):
        _, xpath_ligne = self.ligne(code)
        return By.XPATH, xpath_ligne + "//button[normalize-space()='Desactiver']"

    # ---- Ce que fait l'orga ----
    # ouvrir, creer et desactiver renvoient self : on peut les enchainer.

    # Ouvre /admin/promos et attend que les vrais codes soient affiches
    def ouvrir(self):
        self.driver.get(f"{BASE_URL}/admin/promos")
        self.trouver(self.CELLULES_CODE)
        return self

    # Remplit le formulaire, clique sur "Creer", puis attend la ligne du nouveau code.
    # saisir() tape du texte : on convertit les nombres avec str().
    # Les champs Reduction (10) et Usages max (100) sont pre-remplis : saisir() les vide avant de taper.
    def creer(self, code, reduction, usages_max):
        self.saisir(self.champ("Code"), code)
        self.saisir(self.champ("Reduction (%)"), str(reduction))
        self.saisir(self.champ("Usages max"), str(usages_max))
        self.cliquer(self.BOUTON_CREER)
        self.trouver(self.ligne(code))   # le tableau se recharge : on attend que la ligne soit la
        return self

    # Clique sur "Desactiver" dans la ligne du code, puis attend que son badge passe a "inactif".
    # Le tableau est recharge apres le clic : on attend via un locator (pas via un element deja trouve).
    def desactiver(self, code):
        self.cliquer(self.bouton_desactiver(code))
        self.attendre(EC.text_to_be_present_in_element(self.badge(code), "inactif"))
        return self

    # ---- Ce que l'orga lit ----

    # Renvoie la liste des codes affiches (une liste de textes)
    def codes(self):
        return [cellule.text for cellule in self.driver.find_elements(*self.CELLULES_CODE)]

    # Renvoie le texte des 5 premieres cellules de la ligne (la 6e contient le bouton)
    def cellules(self, code):
        ligne = self.trouver(self.ligne(code))
        return [td.text for td in ligne.find_elements(By.TAG_NAME, "td")[:5]]

    # Renvoie le texte du badge de statut ("actif" ou "inactif")
    def statut(self, code):
        return self.texte(self.badge(code))

    # Renvoie le nombre de boutons "Desactiver" dans la ligne (1 si actif, 0 si inactif).
    # find_elements renvoie une liste vide s'il n'y en a pas : pas de plantage, on compte.
    def nombre_de_boutons_desactiver(self, code):
        self.trouver(self.ligne(code))   # la ligne doit etre affichee avant de compter
        return len(self.driver.find_elements(*self.bouton_desactiver(code)))
