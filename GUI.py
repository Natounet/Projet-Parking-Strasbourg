# Importation des modules
from PyQt5 import QtCore, QtGui, QtWidgets # Interface graphique
from PyQt5 import QtWebEngineWidgets
import folium # Creation de la carte
import requests # Reqûete web
from math import cos,sin,acos,pi # Opérations mathématiques
from urllib.parse import quote # Pour urlencoder
import io

app = QtWidgets.QApplication([])


# Permet de récupérer le pourcentage de la barre de progression ailleurs dans le programme.
global p_bar
p_bar = 0


# Toutes les fonctions nécessaire au programme
def recuperer_parking() -> dict:
    ''' Fonction créant la base de notre dictionnaire contenant tous les parking
        La fonction appelle l'api de l'EMS de Strasbourg pour récupérer les informations, nom_parking, adresse, position

        Format du dictionnaire : dict(nom_parking) = {'coordonnes':position,'adresse':adresse}
        Retourne le dictionnaire'''

    dictionnaire = {}

    # Récupération des informations de la base de données
    url = "https://data.strasbourg.eu/api/records/1.0/search/?dataset=parkings&q=&lang=fr&rows=60"
    r = requests.get(url)

    resultat = r.json()['records']

    # Pour chaque parkings
    for i in range(0,len(resultat)):
        chemin = resultat[i]['fields']
        nom_parking = chemin['name'].lower() #Permet d'éviter des conflits entre les deux bases de données, certains parking ont le même nom mais des majuscules
        position = chemin['position']
        adresse = chemin['street']
        dictionnaire[nom_parking] = {'coordonnees': position, 'adresse':adresse}
    
    return dictionnaire

def recuperer_places_libre(dictionnaire: dict) -> dict:
    ''' Fonction complétant notre dictionnaire en rajoutant place_libre, contenant le nombre de place libre lorsque l'info est disponible,
        etat, décrivant l'état du parking : Ouvert, Fermé, info non disponible

        Retournant le dictionnaire modifié

    '''
    # Récupération des informations de la base de données
    url = "https://data.strasbourg.eu/api/records/1.0/search/?dataset=occupation-parkings-temps-reel&q=&lang=fr&rows=60&facet=etat_descriptif"
    r = requests.get(url)
    resultat = r.json()['records']

    # Pour chaque parking 
    for i in range(0,len(resultat)):
        chemin = resultat[i]['fields']
        nom_parking = chemin['nom_parking'].lower()
        place_libre = chemin['libre']
        etat = chemin['etat_descriptif']
        total = chemin['total']

        """
        nom_parking = resultat[i]['fields']['nom_parking'].lower()
        place_libre = resultat[i]['fields']['libre']
        etat = resultat[i]['fields']['etat_descriptif']
        """
        
        # Ne devrait pas avoir besoin d'être utilisée
        if nom_parking not in dictionnaire.keys(): # Si le parking n'existait pas dans le dictionnaire, car pas dans l'autre base de données
            dictionnaire[nom_parking] = {'coordonnees':localisation_par_adresse_mapbox(f"{nom_parking}, strasbourg")}
            dictionnaire[nom_parking]['place_libre'] = 'Inconnu'
            dictionnaire[nom_parking]['etat'] = 'Inconnu'
            dictionnaire[nom_parking]['total'] = 'Inconnu'
            
        dictionnaire[nom_parking]['place_libre'] = place_libre
        dictionnaire[nom_parking]['etat'] = etat
        dictionnaire[nom_parking]['total'] = total
        
    return dictionnaire

def recuperer_position_utilisateur(dictionnaire: dict, adresse: str) -> dict:
    """ Fonction ajoutant la position de l'utilisateur à un dictionnaire
        Retourne ce dictionnaire modifié """
    dictionnaire['Votre position'] = {'coordonnees':localisation_par_adresse_mapbox(adresse),'adresse':adresse}
    
    return dictionnaire


def localisation_par_adresse_mapbox(adresse: str) -> tuple:
    """ Fonction prenant en compte une chaine de caractère contenant une adresse,
        Utilise l'API geocoding de mapbox, afin de trouver les coordonnes geographique de cette adresse
        Retourne un tuple contenant la latitude et la longitude, (lat,long)
    """

    token = "pk.eyJ1IjoibW9ubW9uNDU4IiwiYSI6ImNsMGZyNmZqeDB1ZDAzamt4dmw5NTZuczIifQ._PUtAJZMG7-WVf3LdJAq1w"
    adresse = quote(adresse)
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{adresse}, strasbourg.json?access_token={token}&country=FR&fuzzyMatch=True&proximity=7.7521113,48.5734053"
    
    r = requests.get(url)
    coordinates = r.json()['features'][0]['geometry']['coordinates']
    lat = coordinates[1]
    long = coordinates[0]
    return (lat,long)
    


# Calcule de distances entre coordonnées

def degree_radian(A: float):
    """ Fonction prenant en paramètre un flottant, un degré décimal
        Retourne sa valeur en radian"""
    return A * pi/180

def calculer_distance_coordonnees(A: tuple,B: tuple) -> float:
    """ Fonction prenant en paramètre deux tuples contenant (lat,long) en radian
        Calcule la distance en mètres entre ces deux points,
        Retourne la distance"""
    # Calcule la distance entre les coordonnées A et B
    # Les degrés doivent être converti en radians
    latA = degree_radian(A[0])
    latB = degree_radian(B[0])
    longA = degree_radian(A[1])
    longB = degree_radian(B[1])

    # Formule permettant de calculer cette distance
    # Attention, celle-ci est approximative
    sAB = acos((sin(latA)*sin(latB))+(cos(latA)*cos(latB)*cos(abs(longB-longA))))
    
    # On retourne la distance en mètre
    distance = (sAB * 6378137)
    
    return distance


def distance_entre(self, dictionnaire: dict, coord_perso:tuple) -> dict:
    """Fonction renvoyant une version de "dictionnaire" avec la distance entre les coordonnées selectionnés et les parkings
    tuple => dict"""
    self.progressBar.setProperty('value',0)



    for emplacement in dictionnaire: #Parcours de "dictionnaire"
         #Exclu la position sélectionnée
        if self.reel.isChecked():
            dictionnaire[emplacement]["distance"] = reel_distance_entre(coord_perso,dictionnaire[emplacement]["coordonnees"]) #Ajoute la distance pour chaque Parking dans "dictionnaire"
        elif self.oiseau.isChecked():
            dictionnaire[emplacement]["distance"] = round(calculer_distance_coordonnees(coord_perso,dictionnaire[emplacement]["coordonnees"]))
        else:
            dictionnaire[emplacement]["distance"] = round(calculer_distance_coordonnees(coord_perso,dictionnaire[emplacement]["coordonnees"]))           
    return dictionnaire

def reel_distance_entre(A: tuple,B: tuple) -> float:
    """ Fonction prenant en paramètres deux tuple constituant les coordonnées : A et B
        Appelle l'api OPRENROUTESERVICE afin de connaitre la distance en voiture entre A et B
        Ainsi que la durée estimée du trajet
        Retourne la distance sous forme de float"""

    key = "5b3ce3597851110001cf624889eacc92218d412f9682c800fff41413"

    # Cordonnées A)
    x1 = str(A[1])
    y1 = str(A[0])

    # Coordonnées B
    x2 = str(B[1])
    y2 = str(B[0])

    url = f"https://api.openrouteservice.org/v2/directions/driving-car?api_key={key}&start={x1},{y1}&end={x2},{y2}"
    r = requests.get(url)
    # Récupération de nos valeurs
    
    try:
        distance = r.json()['features'][0]['properties']['segments'][0]['distance']
    except KeyError:
        print("Il faut attendre, l'API ne peut pas être utilisé aussi vite")
        distance = 0
    global p_bar
    p_bar += 3
    fenetre.progressBar.setProperty('value',p_bar)

    return distance

def trouver_nb_parking(dic_distance_parking: dict, nb_park: int) -> dict:
    """ Fonction prennant un dictionnaire de parkings, et le nombre de parkings à retourner
        Retourne un dictionnaire des nb_park les plus proche de l'utilisateur """
    fenetre.progressBar.setProperty('value',0)
    

    dict_proche = sorted(dic_distance_parking.items(),key=lambda x:x[1]['distance'],reverse=False) #Tri les parkings du plus proche au plus loin
    return dict_proche[0:nb_park+1] #Renvoi les nb_park parkings les plus proches

# Creation de la carte

def creation_carte(dictionnaire: dict, adresse: str,debug: bool=False) -> None:
    """ Fonctionne créant une carte en plaçant un point à chaques coordonnées ainsi que le nom des parking"""

    # Endroit de départ
    map = folium.Map(location=dictionnaire[0][1]['coordonnees'],zoom_start=15)
    for parking in dictionnaire:
        # Si le lieu est notre position
        if parking[0] == "Votre position":
            folium.Marker(location=parking[1]['coordonnees'],popup=f"<b>{parking[0]}, {parking[1]['adresse']}</b>", icon=folium.Icon(icon='glyphicon glyphicon-screenshot',color='red')).add_to(map)
        # Si le lieu est un parking
        else:
            # La couleur va changer en fonction du nombre de places disponibles

            try:
                p_libre = parking[1]['place_libre']
            except:
                p_libre = "Inconnu"

            try:
                etat = parking[1]['etat']
            except:
                etat = "Inconnu"
            try:
                total = parking[1]['total']
            except:
                total = "Inconnu"

            # En fonction du nombre de place disponible, on change la couleur du fond
            if p_libre == "Inconnu" or total == "Inconnu":
                color = 'gray'
            # Si il n'y a plus de places disponibles
            elif int(p_libre) == 0 or etat == 'Fermé':
                color = 'red'
            # Si le nombre de places restantes est inférieur à 50% du nombre total de places
            elif int(p_libre) < int(total)*0.15:
                color = 'orange'
            # Si le nombre de place libre est bon
            else:
                color = 'green'
            icon_parking = folium.Icon(icon='fa-product-hunt',prefix="fa",color=color)

            folium.Marker(location=parking[1]['coordonnees'],popup=f"<b>{parking[0]}, {parking[1]['adresse']}</b>",icon=icon_parking).add_to(map)
    
    # BytesIO permet de crée un espace mémoire dans lequel on mettra notre carte
    data = io.BytesIO()

    # On sauvegarde donc notre carte dans un espace mémoire au lieu d'un fichier
    map.save(data,close_file=False)
    return data








# Classe de l'application

class Ui_MainWindow(object):
    #Fonctions 
    nb_parking = 5


    def setupUi(self, MainWindow):
        """ Fonction permettant de créer tous les objects graphiques de l'interface"""

        # Création de la fenêtre principale
        height = 1900
        width = 1050

        MainWindow.setObjectName("Projet Parking Strasbourg")
        MainWindow.setWindowTitle("Projet Parking Strasbourg")
        MainWindow.setWindowIcon(QtGui.QIcon('icon_parking.png'))
        MainWindow.resize(height, width)
        MainWindow.setMinimumSize(QtCore.QSize(height, width))
        MainWindow.setMaximumSize(QtCore.QSize(height, width))
        MainWindow.setBaseSize(QtCore.QSize(height, width))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")


        # Champ de texte
        self.Champ = QtWidgets.QLineEdit(self.centralwidget)
        self.Champ.setGeometry(QtCore.QRect(10, 10, 511, 71))
        self.Champ.setObjectName("Champ")


        # Bouton
        self.Bouton = QtWidgets.QPushButton(self.centralwidget)
        self.Bouton.setGeometry(QtCore.QRect(520, 10, 81, 71))
        self.Bouton.setText("")
        self.Bouton.setIcon(QtGui.QIcon('loupe.png'))
        self.Bouton.setObjectName("Bouton")
        
        #Lorsque le bouton est cliqué
        self.Bouton.clicked.connect(self.action_bouton)

        #Liste de parking
        self.Liste_parking = QtWidgets.QListWidget(self.centralwidget)
        self.Liste_parking.setGeometry(QtCore.QRect(10, 180, 591, 861))
        self.Liste_parking.setObjectName("Liste_parking")

        ### Check box ###

        # Distance réelle
        self.reel = QtWidgets.QCheckBox(self.centralwidget)
        self.reel.setGeometry(QtCore.QRect(60, 90, 201, 31))
        self.reel.setObjectName("reel")

        # Distance approximative
        self.oiseau = QtWidgets.QCheckBox(self.centralwidget)
        self.oiseau.setGeometry(QtCore.QRect(300, 90, 280, 31))
        self.oiseau.setObjectName("oiseau")

        # Barre de progression
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setGeometry(QtCore.QRect(20, 140, 581, 23))
        self.progressBar.setProperty("value", p_bar)
        self.progressBar.setObjectName("progressBar")


        #Initialisation de la carte
        map = folium.Map(location=localisation_par_adresse_mapbox('strasbourg'),zoom_start=15)
        data = io.BytesIO()
        map.save(data,close_file=False)


        # Carte
        self.Carte = QtWebEngineWidgets.QWebEngineView(self.centralwidget)
        self.Carte.setHtml(data.getvalue().decode())
        self.Carte.setGeometry(QtCore.QRect(610, 0, 1291, 1221))
        self.Carte.setObjectName("Carte")
        MainWindow.setCentralWidget(self.centralwidget)



        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        


    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("Projet Parking Strasbourg", "Projet Parking Strasbourg"))
        self.reel.setText(_translate("MainWindow", "Distance voiture "))
        self.oiseau.setText(_translate("MainWindow", "Distance approximative"))

    ### Fonctions liées à l'application ###

    def action_bouton(self):
        """ Fonction appellée lorsque l'utilisateur clique sur le bouton,
            Elle génère notre carte et notre liste en fonction de l'adresse donnée"""
        # On récupère l'adresse saisie dans la boite
        adresse = str(self.Champ.text())

        # Création de notre dictionnaire
        dictionnaire = recuperer_places_libre(recuperer_parking())
        dictionnaire = recuperer_position_utilisateur(dictionnaire, adresse)
        dictionnaire = distance_entre(self, dictionnaire, localisation_par_adresse_mapbox(adresse))
        dictionnaire_nb_parking = trouver_nb_parking(dictionnaire,self.nb_parking)

        # On crée notre carte et notre liste en fonction de cette adresse
        self.creation_carte_parking(dictionnaire_nb_parking,adresse)
        self.creation_liste_parking(dictionnaire_nb_parking)

    
    def creation_carte_parking(self,dictionnaire_nb_parking:dict ,adresse:str) -> None:
        """ Fonction créant notre objet QWebEngineView, permettant d'intégrer notre carte dans l'application,
            La carte sera fournie par la fonction creation_carte"""
        data = creation_carte(dictionnaire_nb_parking,adresse)
        # Data contient notre carte

        # On modifie le contenu html de notre objet carte par notre carte
        self.Carte.setHtml(data.getvalue().decode())

    def creation_liste_parking(self, dictionnaire_nb_parking: dict) -> None:
        """ Fonction ajoutant notre liste à jour à l'application"""
        
        # Les différentes couleurs utilisées
        red = QtGui.QColor("#FF0000")
        yellow = QtGui.QColor("#FFFF00")
        green = QtGui.QColor("#00FF00")
        grey = QtGui.QColor("#808080")
        dark_grey = QtGui.QColor("#A9A9A9")

        # Chaque fois qu'on appelle la fonction, on réinitialise notre liste
        self.Liste_parking.clear()
        

        i = 0
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
                try:
                    total = parking[1]['total']
                except:
                    total = "Inconnu"
                    
                distance = parking[1]['distance']

                # Pour chaque parkings, on ajoute un element dans notre liste avec les informations désirées
                texte = (f"{parking[0].upper()}\n> Adresse: {parking[1]['adresse']}\n> places libres: {p_libre}\n> status: {etat}\n> distance: {distance}m\n")
                self.Liste_parking.addItem(texte)


                # En fonction du nombre de place disponible, on change la couleur du fond
                if p_libre == "Inconnu" or total == "Inconnu":
                    self.Liste_parking.item(i).setBackground(grey)
                
                # Si il n'y a plus de places disponibles
                elif int(p_libre) == 0 or etat == 'Fermé':
                    self.Liste_parking.item(i).setBackground(red)

                # Si le nombre de places restantes est inférieur à 30% du nombre total de places
                elif int(p_libre) < int(total)*0.30:
                    self.Liste_parking.item(i).setBackground(yellow)
                # Si le nombre de place libre est bon
                else:
                    self.Liste_parking.item(i).setBackground(green)
                i += 1




# Creation notre objet QT modifié
class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

fenetre = MainWindow()


fenetre.show()
app.exec()
