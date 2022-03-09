from PyQt5.QtWidgets import *
from PyQt5 import QtWebEngineWidgets
from fonctions import *

app = QApplication([])

nb_parking = 5

def creation_liste_parking(dictionnaire_nb_parking: dict, adresse: str) -> None:
    """ Fonction créant l'objet de notre liste, et l'ajoute au programme"""
    
    # Création de notre objet liste
    
    for parking in dictionnaire_nb_parking:
        if parking[0] != "Votre position":
            # Certains parking, comme les parkings temporaires n'ont pas de places libre ou d'état
            # Ces tests sont nécessaires car, si le parking n'a pas ces informations, il y a une erreur
            # Car on essaie d'accéder à une clé inexistante
            try:
                p_libre = parking[1]['place_libre']
            except:
                p_libre = "Inconnu"

            try:
                etat = parking[1]['etat']
            except:
                etat = "Inconnu"

            # Pour chaque parkings, on ajoute un element dans notre liste avec les informations désirées
            liste.addItem(f"{parking[0].upper()}: {parking[1]['adresse']} - places libres: {p_libre}, status: {etat}")
    # On ajoute notre liste au programme

def creation_carte_parking(dictionnaire_nb_parking:dict ,adresse:str) -> None:
    """ Fonction créant notre objet QWebEngineView, permettant d'intégrer notre carte dans l'application,
        La carte sera fournie par la fonction creation_carte de notre module fonctions."""
    data = creation_carte(dictionnaire_nb_parking,adresse)
    # Data contient notre carte

    # Création de la carte dans l'application
    m = QtWebEngineWidgets.QWebEngineView()
    m.setHtml(data.getvalue().decode())
    m.resize(640,480)

    # On l'ajoute à l'application
    droite.removeWidget(map)
    droite.addWidget(m)

def action_bouton():
    """ Fonction appellée lorsque l'utilisateur clique sur le bouton,
        Elle génère notre carte et notre liste en fonction de l'adresse donnée"""
    # On récupère l'adresse saisie dans la boite
    adresse = str(champ.text())
    print(f"L'adresse désirée est : {adresse}")

    # Création de notre dictionnaire
    dictionnaire = recuperer_places_libre(recuperer_parking())
    dictionnaire = recuperer_position_utilisateur(dictionnaire, adresse)
    dictionnaire = distance_entre(dictionnaire, localisation_par_adresse_mapbox(adresse))
    dictionnaire_nb_parking = trouver_nb_parking(dictionnaire,nb_parking)

    # On crée notre carte et notre liste en fonction de cette adresse
    creation_liste_parking(dictionnaire_nb_parking,adresse)
    creation_carte_parking(dictionnaire_nb_parking,adresse)
    print("Carte crée")


#espace principal
fenetre = QWidget()
fenetre.setWindowTitle("Trouver votre parking")

# Nos sous espaces
box = QHBoxLayout()
gauche = QVBoxLayout()
droite= QVBoxLayout()

# Notre espace gauche
champ = QLineEdit()
bouton = QPushButton("Rechercher")
bouton.clicked.connect(action_bouton)
liste = QListWidget()

gauche.addWidget(champ)
gauche.addWidget(bouton)
gauche.addWidget(liste)

# On ajoute notre espace gauche à la box principal
box.addLayout(gauche)

# ---- espace droit
# Création de notre carte par défault
m = folium.Map(location=localisation_par_adresse_mapbox("strasbourg"),zoom_start=14)
data = io.BytesIO()
m.save(data,close_file=False)

map = QtWebEngineWidgets.QWebEngineView()
map.setHtml(data.getvalue().decode())
map.resize(1000,1000)
droite.addWidget(map)
box.addLayout(droite)



fenetre.setLayout(box)
fenetre.resize(1920,1080)

fenetre.show()
app.exec()