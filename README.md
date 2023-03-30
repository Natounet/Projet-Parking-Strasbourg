# StrasPark 🚗🅿️

## Présentation

StrasPark est une application desktop conviviale et facile à utiliser qui vous permet de localiser rapidement les parkings disponibles les plus proches de vous à Strasbourg et ses environs.

Vous entrez simplement votre adresse actuelle ou le lieu où vous souhaitez vous rendre, et l'application vous affiche sur une carte interactive les 5 parkings les plus proches de votre emplacement, soit en distance réelle en voiture, soit en distance approximative à vol d'oiseau.

Les résultats affichés sont en 4 couleurs pour mieux comprendre la disponibilité des places :

- 🔴 Rouge : Il n'y a plus de places libres dans le parking
- 🟡 Jaune : Il reste moins de 15% de places libres dans le parking
- 🟢 Vert : Il reste plus de 15% de places libres dans le parking
- ⚫ Gris : Aucune information n'est disponible pour ce parking

## Interface utilisateur

![image](https://user-images.githubusercontent.com/70477133/214844108-de49764a-6659-483e-bae0-330d12ccd553.png)

1. Votre emplacement
2. Sélecteur de distance ( Distance en voiture ou distance à vol d'oiseau )
3. Résultat de votre recherche dans l'ordre croissant des distances

Si vous ne cochez pas de cases pour la distance, par défaut, la distance à vol d'oiseau sera utilisée

## Informations notables

Afin d'obtenir les informations relatives aux parkings, l'API de l'Eurométropole de Strasbourg a été utilisée. Elle est disponible [ici](https://data.strasbourg.eu/explore/dataset/occupation-parkings-temps-reel/api/).

L'API [Mapbox](https://docs.mapbox.com/api/overview/) a été utilisée pour convertir une adresse postale (ex: Place des Halles) en coordonnées géographiques, ce qui permet une meilleure précision dans la localisation des parkings.

L'API [OpenRouteServices](https://api.openrouteservice.org/) a été utilisée afin de calculer la distance en voiture entre un parking et une adresse. Cependant, la version gratuite possède un délai entre plusieurs requêtes, ce qui entraîne parfois des crashs de l'application. Il est recommandé de patienter quelques secondes entre chaque requête pour éviter ce problème.

### Installation

Les modules Python nécessaires à l'application peuvent être téléchargés à partir du [requirements.txt](requirements.txt)<br>
`python3 -m pip install -r requirements.txt`

sur Linux, il peut etre requis de télécharger les packages suivants : <br>
`apt-get install python3-pyqt5.qtwebengine`
