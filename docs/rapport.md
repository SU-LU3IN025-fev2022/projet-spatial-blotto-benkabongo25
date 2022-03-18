# Rapport de projet

## Groupe
* Ben KABONGO BUZANGU

## Description des choix importants d'implémentation

Nous avons basé notre projet sur le code et la documentation fournis initialement.

### Stratégies

Nous avons fait le choix de représenter les stratégies des joueurs par des classes. En effet, ce choix nous permet une gestion simple, dans une seule instance, des objets relatifs aux décisions des joueurs.

Toutes les stratégies ont été implémentées dans le fichier `strategy.py`.

Nous avons implémenté la classe de base `Strategy`, de laquelle héritent tous nos objets stratégies. Il s'agit d'une classe abstraite qui rassemble les informations génériques dont nous avons eu besoin pour l'élaboration des différentes stratégies.

Son interface est simple.

Le constructeur prend en paramètres les éléments suivants :
- `nb_team_players`: le nombre de joueurs de l'équipe qui utilise la stratégie
- `nb_goals`: le nombre de cibles (électeurs) à atteindre

Elle initialise par ailleurs des `mémoires` afin de sauvegarder des informations diverses, utiles pour certaines classes de stratégies, mais également pour nos diagrammes et analyses. Ces mémoires sont :
- `Une mémoire de la distribution`: dans cette mémoire, on stocke la répartition des joueurs en fonction des cibles. Nous avons jugé qu'il n'était pas pertinent de savoir quel joueur exactement avait pour cible tel ou tel autre électeur, quand les joueurs font partis de la même équipe. Ici, on mémorise uniquement le nombre de joueurs de l'équipe envoyés à la cible pour un jour donné.
Ce choix faciletera notamment le décompte des votes. En effet, pour chaque individu, il suffira de comparer les nombres des militants de chaque équipe qui lui ont été envoyés. Il vote évidemment pour l'équipe lui ayant envoyé le plus de militants.
- `Une mémoire des votes`: on y sauvegarde le choix de chaque cible (électeur) en fonction des jours.
- `Une mémoire des scores`: on y sauvegarde le score en fonction des jours.

La méthode `generate` renvoie la cible attribuée à chaque joueur de l'équipe.

Globalement, toutes les stratégies fonctionnent avec ces paramètres. D'autres stratégies utilisent les informations de la stratégie adverse dans leur processus de décision.

## Description des résultats


