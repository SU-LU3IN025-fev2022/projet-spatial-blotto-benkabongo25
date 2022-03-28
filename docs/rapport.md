# Rapport de projet

## Groupe

Ben KABONGO BUZANGU

GitHub: https://github.com/BenKabongo25

## Description des choix importants d'implémentation

Nous avons basé notre projet sur le code et la documentation fournis initialement.

### Stratégies

Nous avons fait le choix de représenter les stratégies des joueurs par des classes. En effet, ce choix nous permet une gestion simple, dans une seule instance, des objets relatifs aux décisions des joueurs.

Toutes les stratégies ont été implémentées dans le fichier `strategy.py`.

#### Quelques fonctions utiles

Dans la suite, on appelera `distribution` ou `répartition`, le nombre de joueurs que chaque équipe a réparti entre les cibles. Si on a par exemple 3 cibles et une répartition (3, 2, 0), l'équipe a alors attribué 3 de ses joueurs à la première cible, 2 pour la seconde et aucune pour la troisième.

- `compare(r1, r2)`: effectue une comparaison entre 2 répartitions. Renvoie le numéro de la répartition gagante (1 ou 2) et le score associé à celle-ci. Elle retourne 0 en cas d'égalité.
- `generate_distrib(limit, size)`: génère récursivement des distributions. `limit` indique le nombre de joueurs restants et `size` le nombre de cibles restantes. Cette méthode retourne ainsi toutes les distributions possibles pour un nombre de joueurs et un nombre de cibles donnés.
- `better_answer(r, limit)`: renvoie une répartition qui est meilleure que `r`. `limit` indique toujours le nombre de joueurs maximum.
- `best_answer(r, limit)`: renvoie la meilleure répartition sur toutes les répartitions qui sont meilleures que `r`.
- `all_better_answers(r, limit)`: renvoie un dictionnaire de toutes les répartitions bien meilleures que `r` avec comme clés les répartitions et valeurs les scores face à `r`.

#### Classe de base : Strategy

Nous avons implémenté la classe de base `Strategy`, de laquelle héritent tous nos objets stratégies. Il s'agit d'une classe abstraite qui rassemble les informations génériques dont nous avons eu besoin pour l'élaboration des différentes stratégies.

Son interface est simple.
Nous sommes partis du principe qu'on utilise une stratégie par équipe. Pour chaque équipe, un objet `Strategy` est donc instancié.

Le constructeur prend en paramètres les éléments suivants :
- `name`: le nom de la stratégie. 
- `team_id`: l'identifiant de l'équipe qui utilise la stratégie (1 ou 2).
- `players_ids`: les indices des joueurs de l'équipe dans la liste des tous les joueurs. Cela a été utile, car la liste des positions initiales des joueurs fournie est aléatoire. Il est donc nécessaire de connaitre constamment l'indice de chaque joueur, même au sein de son équipe.
- `nb_goals`: le nombre de cibles (électeurs) à atteindre
- `dist_min`: la distance minimale que les joueurs de la team sont autorisés à dépasser. Par défaut cette distance est initialisée à `+inf` ; dans ce cas, les joueurs n'ont pas de contraintes de distances à respecter. Si la distance minimale fixée est 12, un joueur x de l'équipe ne pourra pas atteindre une cible y située à une distance de plus de 12. Nous avons utilisé la distance de Manhattan, qui est une très bonne heuristique dans notre cas, car nous utilisons A*.

#### Stratégie adversaire

Certaines stratégies ont besoin de connaître la stratégie adverse, car elle utilise les informations de celles-ci dans son processus de décision.
Nous avons ainsi pourvu la classe d'un attribut `adversary_strategy` qui est une référence de la stratégie adverse.

La méthode `set_adversary(self, adversary)` permet d'initialiser cette stratégie adverse.

#### Distances et accessibilités

La classe maintient également à jour deux dictionnaires dont les clés sont les identifiants des joueurs. Ces dictionnaires sont `distances` et `accessibles`.

Dans le premier, sont régulièrement mis à jour la distance de chaque joueur à chaque cible. Un item de ce dictionnaire ressemble donc à : `id_du_joueur : [distance cible 1, distance cible 2, ...]`.

Dans le second, sont régulièrement mis à jour les cibles accessibles de chaque joueur. Une `cible accessible` pour un joueur est une cible qui se trouve à portée de ce joueur, soit à une distance inférieure à la distance minimale fixée par la stratégie. Si cette distance est l'infini, toutes les cibles sont accessibles pour tous les joueurs.

La méthode `update_distances(team_positions_dict, goals_positions_list)` prend en paramètres un dictionnaire des positions courantes des joueurs de l'équipe (les clés sont les indices des joueurs et les valeurs sont les positions courantes) et une liste des positions courantes des cibles, et calcule pour chaque joueur la distance avec chaque cible.

#### Mémoires

Elle initialise par ailleurs des `mémoires` afin de sauvegarder des informations diverses, utiles pour certaines classes de stratégies, mais également pour nos diagrammes et analyses. Ces mémoires sont :
- `Une mémoire de la distribution`: dans cette mémoire, on stocke la répartition des joueurs en fonction des cibles. Nous avons jugé qu'il n'était pas pertinent de savoir quel joueur exactement avait pour cible tel ou tel autre électeur, quand les joueurs font partis de la même équipe. Ici, on mémorise uniquement le nombre de joueurs de l'équipe envoyés à la cible pour un jour donné.
Ce choix faciletera notamment le décompte des votes. En effet, pour chaque individu, il suffira de comparer les nombres des militants de chaque équipe qui lui ont été envoyés. Il vote évidemment pour l'équipe lui ayant envoyé le plus de militants.
- `Une mémoire des votes`: on y sauvegarde le choix de chaque cible (électeur) en fonction des jours.
- `Une mémoire des scores et des scores cumulés`: on y sauvegarde le score en fonction des jours.
- `Une mémoire des distances et des distances cumulées`: on y sauvegarde la somme des distances parcourues par jour par tous les joueurs pour atteindre leurs cibles.

#### Génération de distribution

La méthode `generate` renvoie la cible attribuée à chaque joueur de l'équipe.
Chaque classe de stratégie rédéfini cette méthode afin de renvoyer la répartition correspondante après décision.

Plusieurs mises à jour, des mémoires notamment, sont faites au moment de la génération de la répartition.

#### Mise à jour des informations

La méthode `save_day_result(votes)` prend en paramètres une liste des votes des cibles et met à jour les informations par rapport aux votes et aux scores. Une liste de votes a pour taille le nombre de cibles, et contient les valeurs 0, 1 ou 2. 0 correspond à une cible qui n'a voté pour aucune équipe ; 1 si la cible a voté pour la première équipe ; 2 si la cible a voté pour la seconde équipe.

#### Autres paramètres

Globalement, toutes les stratégies fonctionnent avec ces paramètres. D'autres stratégies ont besoin de paramètres supplémentaires particuliers :
- une `distribution` pour le cas de la stratégie du tétu.
- une valeur `epsilon` pour différentes stratégies, qui avec une probabilité `epsilon` choisiront par exemple une répartition aléatoire et avec une probabilité `1-epsilon` effectueront leur choix différemment.

### Présentation des stratégies

#### Aléatoire (RandomStrategy)
Les cibles sont choisies de manière aléatoire pour chaque joueur.

#### Cible la plus proche (NearStrategy)
Chaque joueur choisit la cible accessible la plus proche.

#### Cible la plus éloignée (FarStrategy)
Chaque joueur choisit la cible accessible la plus éloignée.

#### Déterministe : toujours les mêmes cibles pour les joueurs (StubbornStrategy1)
Première version de la stratégie tétu. Les joueurs ont toujours les mêmes cibles, sous critère d'accessibilité.

#### Déterministe : toujours le même nombre de joueurs par cible (StubbornStrategy2)
Seconde version de la stratégie tétu. Les cibles se voient toujours attribués un même nombre de joueurs.

#### Epsilon-greedy (EpsilonStrategy)
Avec une probabilité *epsilon*, la stratégie choisie est aléatoire ; avec une probabilité *1-epsilon*, la stratégie choisie est la meilleure parmi toutes les stratégies jouées précédemment.

#### Imitateur d'adversaire
Stratégie qui rejoue le dernier coup de l'adversaire.

#### Epsilon-greedy imitateur d'adversaire
Avec une probabilité *epsilon*, la stratégie choisie est aléatoire ; avec une probabilité *1-epsilon*, la stratégie choisie est la meilleure parmi toutes les stratégies de l'adversaire jouées précédemment.

#### Epsilon-greedy mix
Avec une probabilité *epsilon*, la stratégie choisie est aléatoire ; avec une probabilité *1-epsilon*, la stratégie choisie est la meilleure parmi toutes les stratégies jouées précédemment, y compris celles de l'adversaire.

#### Réponse améliorante au dernier coup de l'adversaire
La stratégie choisie est une réponse meilleure (une stratégie qui domine faiblement) la dernière stratégie de l'adversaire.

#### Meilleure réponse au dernier coup de l'adversaire
La stratégie choisie est la meilleure réponse possible à la dernière stratégie de l'adversaire.

#### Meilleure réponse au meilleur coup
La stratégie choisie est la meilleure réponse au meilleur coup joué jusqu'à lors par l'adversaire.

#### Ficticious play
Implémentation du ficticious play.

#### Stochastique expert
Aggrégat de plusieurs stratégies de jeu. A chaque coup, avec une probabilité donnée, une certaine stratégie est choisie.

## Description des résultats

Nous avons lancé des tournois et comparé toutes les stratégies que nous avons implémentées entre elles.
Nous allons ici présenter les résultats que nous avons obtenus.

Nous nous sommes intéressés à deux critères pour nos comparaisons : **le score cumulé** et **le coût de trajet cumulé** au fil des jours de campagne. Nous avons fixé le nombre de jours à 100.

Nous avons ainsi représenté pour chaque affrontement les deux courbes associées.
Nous avons également représenté les courbes des **scores/coûts**. Plus les valeurs de la courbe est haute, plus la stratégie rapporte des bons scores avec un coût raisonnable.

### Ficticious play

#### Ficticious play - Aléatoire
<div>
  <img style='display:inline;' src='/out/scores/ficticious_play_random_days_100_dist_inf.png' width='33%'>
  <img style='display:inline;' src='/out/coasts/ficticious_play_random_days_100_dist_inf.png' width='33%'>
  <img style='display:inline;' src='/out/scores_coasts/ficticious_play_random_days_100_dist_inf.png' width='33%'>
</div>

**Ficticious play** est meilleure que **Random**. Leurs distances parcourues sont quasi équivalentes.
On verra par la suite que, face à **Ficticious play**, **Random** n'est pas la pire.

#### Ficticious play - Tétu
<div>
  <img style='display:inline;' src='/out/scores/ficticious_play_stubborn_2_days_100_dist_inf.png' width='33%'>
  <img style='display:inline;' src='/out/coasts/ficticious_play_stubborn_2_days_100_dist_inf.png' width='33%'>
  <img style='display:inline;' src='/out/scores_coasts/ficticious_play_stubborn_2_days_100_dist_inf.png' width='33%'>
</div>

**Ficticious play** apprend la stratégie du **Stubborn** ; et avec des trajets plus longs en comparaison, elle la bat à tous les coups.

#### Ficticous play - Plus proche
<div>
  <img style='display:inline;' src='/out/scores/ficticious_play_near_days_100_dist_inf.png' width='33%'>
  <img style='display:inline;' src='/out/coasts/ficticious_play_near_days_100_dist_inf.png' width='33%'>
  <img style='display:inline;' src='/out/scores_coasts/ficticious_play_near_days_100_dist_inf.png' width='33%'>
</div>

**Ficticious play** cumule un score bien meilleur que **Near**.
Cependant, le coût cumulé de ses différents trajets est supérieur à ce dernier.

#### Ficticous play - Plus loin
<div>
  <img style='display:inline;' src='/out/scores/ficticious_play_far_days_100_dist_inf.png' width='33%'>
  <img style='display:inline;' src='/out/coasts/ficticious_play_far_days_100_dist_inf.png' width='33%'>
  <img style='display:inline;' src='/out/scores_coasts/ficticious_play_far_days_100_dist_inf.png' width='33%'>
</div>

**Ficticious play** bat **Far**, et en terme du score et de coût de trajet.
EN effet, elle parcourt des distances inférieures à **Far**.

#### Ficticous play - Imitateur
<div>
  <img style='display:inline;' src='/out/scores/imitator_ficticious_play_days_100_dist_inf.png' width='33%'>
  <img style='display:inline;' src='/out/coasts/imitator_ficticious_play_days_100_dist_inf.png' width='33%'>
  <img style='display:inline;' src='/out/scores_coasts/imitator_ficticious_play_days_100_dist_inf.png' width='33%'>
</div>

**Ficticious play** bat la stratégie **Imitator**. Les coûts de leurs trajets parcourus sont quasi équivalents.
Nous constatons cependant que la stratégie **Imitator** est intéressante quand on la mesure à **Ficticious play**. En effet, elle imite la meilleure réponse que **Ficticious play** donne sur l'ensemble des coups précédents.

Ce duel rappelle un peu l'apprentissage par renforcement. En permanence, **Ficticious play** cherchera à jouer des stratégies bien meilleures comparées à celles qu'elle avait déjà jouées.
On retrouve cet aspect dans des duels avec les stratégies *epsilon* et *imitatrices*.

#### Ficticous play - Epsilon
<div>
  <img style='display:inline;' src='/out/scores/ficticious_play_epsilon_0.4_days_100_dist_inf.png' width='33%'>
  <img style='display:inline;' src='/out/coasts/ficticious_play_epsilon_0.4_days_100_dist_inf.png' width='33%'>
  <img style='display:inline;' src='/out/scores_coasts/ficticious_play_epsilon_0.4_days_100_dist_inf.png' width='33%'>
</div>

#### Ficticous play - Epsilon imitateur
<div>
  <img style='display:inline;' src='/out/scores/ficticious_play_epsilon_imitator_0.4_days_100_dist_inf.png' width='33%'>
  <img style='display:inline;' src='/out/coasts/ficticious_play_epsilon_imitator_0.4_days_100_dist_inf.png' width='33%'>
  <img style='display:inline;' src='/out/scores_coasts/ficticious_play_epsilon_0.4_days_100_dist_inf.png' width='33%'>
</div>

#### Ficticous play - Epsilon imitateur mix
<div>
  <img style='display:inline;' src='/out/scores/ficticious_play_epsilon_imitator_mix_0.4_days_100_dist_inf.png' width='33%'>
  <img style='display:inline;' src='/out/coasts/ficticious_play_epsilon_imitator_mix_0.4_days_100_dist_inf.png' width='33%'>
  <img style='display:inline;' src='/out/scores_coasts/ficticious_play_epsilon_imitator_mix_0.4_days_100_dist_inf.png' width='33%'>
</div>

#### Ficticous play - Meilleure réponse au dernier coup
<div>
  <img style='display:inline;' src='/out/scores/ficticious_play_best_answer_last_adversary_days_100_dist_inf.png' width='33%'>
  <img style='display:inline;' src='/out/coasts/ficticious_play_best_answer_last_adversary_days_100_dist_inf.png' width='33%'>
  <img style='display:inline;' src='/out/scores_coasts/ficticious_play_best_answer_last_adversary_days_100_dist_inf.png' width='33%'>
</div>


### Stratégies de meilleure réponse


### Stratégies imitatrices


### Stratégies epsilon-greedy


### Aléatoire

Nous allons lister les stratégies dominées par la stratégie aléatoire, en terme de scores cumulés.

#### Aléatoire - Plus proche
<div>
  <img style='display:inline;' src='/out/scores/random_near_days_100_dist_inf.png' width='33%'>
  <img style='display:inline;' src='/out/coasts/random_near_days_100_dist_inf.png' width='33%'>
  <img style='display:inline;' src='/out/scores_coasts/random_near_days_100_dist_inf.png' width='33%'>
</div>

#### Aléatoire - Plus loin
<div>
  <img style='display:inline;' src='/out/scores/random_far_days_100_dist_inf.png' width='33%'>
  <img style='display:inline;' src='/out/coasts/random_far_days_100_dist_inf.png' width='33%'>
  <img style='display:inline;' src='/out/scores_coasts/random_far_days_100_dist_inf.png' width='33%'>
</div>

#### Alétoire - Tétu
<div>
  <img style='display:inline;' src='/out/scores/random_stubborn_2_days_100_dist_inf.png' width='33%'>
  <img style='display:inline;' src='/out/coasts/random_stubborn_2_days_100_dist_inf.png' width='33%'>
  <img style='display:inline;' src='/out/scores_coasts/random_stubborn_2_days_100_dist_inf.png' width='33%'>
</div>


### Stochastique expert
