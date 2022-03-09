import requests # Reqûete web
from math import cos,sin,acos,pi # Opérations mathématiques
import folium # Pour la carte
from urllib.parse import quote # Pour urlencoder
import io

# Creation de notre dictionnaire contenant toutes les données nécessaires

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
            
        dictionnaire[nom_parking]['place_libre'] = place_libre
        dictionnaire[nom_parking]['etat'] = etat

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
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{adresse}.json?access_token={token}&country=FR"
    
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


def distance_entre(dictionnaire: dict, coord_perso:tuple) -> dict:
    """Fonction renvoyant une version de "dictionnaire" avec la distance entre les coordonnées selectionnés et les parkings
    tuple => dict"""
    for emplacement in dictionnaire: #Parcours de "dictionnaire"
         #Exclu la position sélectionnée
        dictionnaire[emplacement]["distance"] = round(calculer_distance_coordonnees(coord_perso,dictionnaire[emplacement]["coordonnees"])) #Ajoute la distance pour chaque Parking dans "dictionnaire"
    return dictionnaire

def trouver_nb_parking(dic_distance_parking: dict, nb_park: int) -> dict:
    """ Fonction prennant un dictionnaire de parkings, et le nombre de parkings à retourner
        Retourne un dictionnaire des nb_park les plus proche de l'utilisateur """
    dict_proche = sorted(dic_distance_parking.items(),key=lambda x:x[1]['distance'],reverse=False) #Tri les parkings du plus proche au plus loin
    return dict_proche[0:nb_park+1] #Renvoi les nb_park parkings les plus proches

# Creation de la carte

def creation_carte(dictionnaire: dict, adresse: str,debug: bool=False) -> None:
    """ Fonctionne créant une carte en plaçant un point à chaques coordonnées ainsi que le nom des parking"""
   
    if __name__ == "__main__" and debug == True: # Si l'on lance directement ce fichier, et pas le programme
        map = folium.Map(location=dictionnaire['Votre position']['coordonnees'],zoom_start=14)
        for parking in dictionnaire:
            # Si le lieu est notre position
            if parking == "Votre position":
                folium.Marker(location=dictionnaire[parking]['coordonnees'],popup=f"<b>{parking}, {dictionnaire[parking]['adresse']}</b>", icon=folium.Icon(icon='glyphicon glyphicon-screenshot',color='red')).add_to(map)
            # Si le lieu est un parking
            else:
                icon_parking = folium.Icon(icon='fa-product-hunt',prefix="fa")
                folium.Marker(location=dictionnaire[parking]['coordonnees'],popup=f"<b>{parking}, {dictionnaire[parking]['adresse']}</b>",icon=icon_parking).add_to(map)
        map.save("Carte.html")
    else:
        """ Dans le cas où notre programme l'appelle, la carte ne va pas être sauvegardée dans un fichier"""

        # Endroit de départ
        map = folium.Map(location=dictionnaire[0][1]['coordonnees'],zoom_start=14)
        for parking in dictionnaire:
            # Si le lieu est notre position
            if parking[0] == "Votre position":
                folium.Marker(location=parking[1]['coordonnees'],popup=f"<b>{parking[0]}, {parking[1]['adresse']}</b>", icon=folium.Icon(icon='glyphicon glyphicon-screenshot',color='red')).add_to(map)
            # Si le lieu est un parking
            else:
                icon_parking = folium.Icon(icon='fa-product-hunt',prefix="fa")
                folium.Marker(location=parking[1]['coordonnees'],popup=f"<b>{parking[0]}, {parking[1]['adresse']}</b>",icon=icon_parking).add_to(map)
        
        # BytesIO permet de crée un espace mémoire dans lequel on mettra notre carte
        data = io.BytesIO()
    
        # On sauvegarde donc notre carte dans un espace mémoire au lieu d'un fichier
        
        
        map.save(data,close_file=False)
        return data


if __name__ == '__main__':
    adresse = "7 rue de palerme, strasbourg"


    """print(dictionnaire)
    creation_carte(dictionnaire)"""
    dictionnaire = recuperer_places_libre(recuperer_parking())
    dictionnaire = recuperer_position_utilisateur(dictionnaire, adresse)
    dictionnaire = distance_entre(dictionnaire, localisation_par_adresse_mapbox(adresse))
    print(trouver_nb_parking(dictionnaire, 5))
    creation_carte(trouver_nb_parking(dictionnaire, 5),adresse)