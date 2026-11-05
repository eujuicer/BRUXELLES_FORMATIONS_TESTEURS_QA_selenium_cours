from tests.config import BASE_URL
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class LoginPage:
    EMAIL = (By.CSS_SELECTOR, "input[type=email]")

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 6)

    def ouvrir(self):
        self.driver.get(BASE_URL + "/login")
        self.wait.until(EC.visibility_of_element_located(self.EMAIL))
        return self

    # Vide un champ puis tape le texte (Ctrl+A puis Suppr : clear() seul ne suffit pas avec React)
    def saisir(self, locator, texte):
        champ = self.wait.until(EC.visibility_of_element_located(locator))
        champ.send_keys(Keys.CONTROL, "a")   # selectionne tout le contenu du champ
        champ.send_keys(Keys.DELETE)         # supprime la selection : le champ est vide
        champ.send_keys(texte)               # tape le nouveau texte
        return self



        