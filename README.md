# StrasPark

### Présentation 

StrasPark est une application qui permet de connaître les parkings disponible les plus proche de son emplacement.<br><br>
Vous entrez votre adresse actuelle, et l'application vous affiche sur une carte les 5 parkings les plus proches de votre emplacement, soit par rapport à une <strong>distance réelle</strong> en voiture, soit par une <strong>distance approximative</strong> à vol d'oiseau.

Les résultats affichés sont en 4 couleurs : 
 - Rouge : Il n'y a plus de places libre dans le parking
 - Jaune : Il restes moins de 15% de places libre dans le parking
 - Vert : Il reste plus de 15% de places libre dans le parking
 - Gris : Aucune information n'est disponible pour ce parking

### Interface 

![image](https://user-images.githubusercontent.com/70477133/214844108-de49764a-6659-483e-bae0-330d12ccd553.png)
1. Votre emplacement
2. Sélecteur de distance ( Distance en voiture ou distance à vol d'oiseau )
3. Résultat de votre recherche dans l'ordre croissant des distances

Si vous ne cochez pas de cases pour la distance, par défaut, la distance à vol d'oiseau sera utilisée


### Informations notables
 
Afin d'obtenir les informations relatives aux parkings, l'API de l'Eurometrople de Strasbourg a été utilisée.<br>
L'api est disponible [ici](https://data.strasbourg.eu/explore/dataset/occupation-parkings-temps-reel/api/)

L'api [mapbox](https://docs.mapbox.com/api/overview/) a été utilisée pour convertir une adresse postal (ex: Place des Halles) en coordonnées géographique

L'api [OpenRouteServices](https://api.openrouteservice.org/) a été utilisée afin de calculer la distance en voiture entre un parking et une adresse.
Cependant, la version gratuite possède un délai entre plusieurs requêtes, ce qui peut causer des crash de l'application

### Installation

Les modules pythons nécessaires à l'application peuvent être téléchargés à partir du [requirements.txt](requirements.txt)<br>
`python3 -m pip install -r requirements.txt`

sur Linux, il peut etre requis de télécharger les packages suivants : <br>
`apt-get install python3-pyqt5.qtwebengine`
