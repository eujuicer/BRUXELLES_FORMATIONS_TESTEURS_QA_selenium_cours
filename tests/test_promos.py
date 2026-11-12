import uuid

import pytest

from tests.config import ORGA_EMAIL, ORGA_PASSWORD
from tests.pages.login_page import LoginPage
from tests.pages.promos_page import PromosPage

# Les trois tests passent par LoginPage et PromosPage : aucun locator, aucune attente ici.
# Chaque test commence par la meme preparation (connexion de l'orga + ouverture des codes promo).


# EXO 7 - Test 1 : les codes de demonstration sont listes
# On verifie la PRESENCE de 3 codes, pas le nombre de lignes : d'autres codes peuvent exister.
def test_codes(driver):
    # Connexion de l'orga, puis ouverture de /admin/promos (attend les vraies donnees)
    LoginPage(driver).ouvrir().se_connecter(ORGA_EMAIL, ORGA_PASSWORD)
    promos = PromosPage(driver).ouvrir()

    # codes() renvoie la liste du texte de chaque code affiche
    codes = promos.codes()
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
    LoginPage(driver).ouvrir().se_connecter(ORGA_EMAIL, ORGA_PASSWORD)
    promos = PromosPage(driver).ouvrir()

    # Le badge du statut de CE code, puis le nombre de boutons "Desactiver" de sa ligne
    assert promos.statut(code) == statut
    assert promos.nombre_de_boutons_desactiver(code) == nb_boutons


# EXO 8 - Creer un code promo, puis le desactiver
# Scenario : l'orga cree un code (15 %, 20 usages max), verifie sa ligne, le desactive,
# et verifie que son statut passe a "inactif" et que son bouton disparait.
def test_creer_puis_desactiver(driver):
    LoginPage(driver).ouvrir().se_connecter(ORGA_EMAIL, ORGA_PASSWORD)
    promos = PromosPage(driver).ouvrir()

    # Code unique, genere a chaque lancement (jamais ecrit en dur).
    # Le code reste en base apres le test, et l'appli le met en majuscules : .upper().
    code = "TEST" + uuid.uuid4().hex[:6].upper()

    # creer() remplit les 3 champs, clique sur "Creer" et attend la ligne du nouveau code
    promos.creer(code, 15, 20)

    # Les 5 premieres cellules : code, reduction, utilisation, expiration (tiret long), statut
    assert promos.cellules(code) == [code, "-15%", "0/20", "—", "actif"]

    # desactiver() clique sur "Desactiver" et attend que le statut passe a "inactif"
    promos.desactiver(code)

    # Le statut est "inactif" et la ligne n'a plus de bouton
    assert promos.statut(code) == "inactif"
    assert promos.nombre_de_boutons_desactiver(code) == 0
