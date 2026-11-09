from tests.config import BASE_URL, ORGA_EMAIL, ORGA_PASSWORD, CLIENT_EMAIL, CLIENT_PASSWORD
from tests.pages.login_page import LoginPage

# Les trois tests de ce fichier passent par LoginPage (qui herite de BasePage) :
# ils ne contiennent ni locator, ni attente, ni find_element. Tout est dans les pages.


# EXO 3 / EXO 10 - Un mauvais mot de passe, reecrit avec LoginPage
# Un organisateur saisit son email et un mauvais mot de passe : la page doit afficher
# "Incorrect email or password" et rester sur /login.
def test_mauvais_mot_de_passe_affiche_une_erreur(driver):
    # Ouvre /login puis envoie le formulaire (soumettre n'attend pas de connexion reussie)
    page = LoginPage(driver).ouvrir().soumettre(ORGA_EMAIL, "mauvais-mot-de-passe")

    # message_erreur() attend le message, puis renvoie son texte
    assert page.message_erreur() == "Incorrect email or password"
    # On est toujours sur la page de connexion
    assert driver.current_url == f"{BASE_URL}/login"


# EXO 5 / EXO 11 - L'organisateur accede au back-office, reecrit avec les pages
# Scenario : l'orga se connecte, clique sur "Back-office" dans la navbar,
# et arrive sur la page /admin dont le titre est "Back-office".
def test_organisateur_accede_au_back_office(driver):
    # Ouvre /login, se connecte avec le compte orga et attend "Deconnexion" (connexion terminee)
    page = LoginPage(driver).ouvrir().se_connecter(ORGA_EMAIL, ORGA_PASSWORD)

    # Clique sur "Back-office" puis attend l'URL /admin et le titre de la page
    page.aller_au_back_office()

    # Le titre de la page doit etre "Back-office"
    assert page.titre() == "Back-office"


# EXO 6 / EXO 11 - Un client ne peut pas entrer dans le back-office, reecrit avec les pages
# Scenario : un client connecte ouvre /admin, il est renvoye vers le catalogue (/)
# et sa navbar n'a pas de lien "Back-office".
def test_client_est_redirige_hors_du_back_office(driver):
    # ETAPE 1 : ouvrir /login et se connecter avec le compte CLIENT (attend "Deconnexion")
    page = LoginPage(driver).ouvrir().se_connecter(CLIENT_EMAIL, CLIENT_PASSWORD)

    # ETAPE 2 : ouvrir /admin directement dans l'URL (un client n'a pas le lien, donc pas de clic)
    driver.get(f"{BASE_URL}/admin")

    # ETAPE 3 : attendre la redirection.
    # Aucune condition "EC" ne fait ca : on ecrit la notre avec une lambda.
    # d = le navigateur ; la lambda renvoie True quand l'URL ne se termine plus par "/admin".
    page.attendre(lambda d: not d.current_url.endswith("/admin"))

    # ETAPE 4 : verifier l'URL finale : on doit etre sur le catalogue
    assert driver.current_url == f"{BASE_URL}/"

    # ETAPE 5 : verifier que le lien "Back-office" est ABSENT de la navbar.
    # a_le_lien_back_office() renvoie True/False et n'attend rien : on l'appelle APRES la
    # redirection (etape 3). Juste apres driver.get("/admin"), la navbar n'est pas encore a jour :
    # verifier trop tot donnerait "absent" a coup sur, un test qui passe sans rien prouver.
    assert not page.a_le_lien_back_office()
    
