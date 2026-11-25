# Rapport Projet Programmation

*Alex Papiccio, Arsène Leblois*

**Dépôt GitHub :** <https://github.com/Oliphantaupe/circular-space-invaders>

**Programme initial :** <https://github.com/attreyabhatt/Space-Invaders-Pygame>

## 1. Analyse du programme initial

Le programme initial est un Space Invaders classique écrit en un seul fichier `main.py` (environ 180 lignes) : le joueur se déplace de gauche à droite en bas de l’écran, six ennemis descendent en zigzag, et le joueur leur tire dessus.

Principales limitations :

- **Aucune classe, tout est en variables globales.** Le joueur est représenté par des variables séparées (`playerX`, `playerY`, `playerX_change`), et les ennemis par des listes parallèles (`enemyX`, `enemyY`, `enemyX_change`, `enemyY_change`, `enemyImg`) reliées seulement par leur indice `i`. Ajouter une statistique à un ennemi (des points de vie par exemple) demande une nouvelle liste à garder synchronisée avec les autres.
- **Un seul type d’ennemi et un seul projectile.** Le tir est géré par une seule balle et un état texte (`bullet_state = "ready"` / `"fire"`) : impossible de tirer plusieurs projectiles à la fois, et donc d’ajouter un tir multiple ou des ennemis qui tirent sans réécrire cette partie.
- **Logique, entrées et affichage mélangés dans la boucle principale.** La même boucle lit le clavier, déplace les ennemis, teste les collisions et dessine. La fonction `fire_bullet` modifie l’état du jeu (via `global`) *et* dessine la balle.
- **Valeurs écrites en dur.** Les nombres comme `736`, `480`, `440`, `27` (distance de collision) ou `4` et `40` (vitesses) sont répétés dans le code et dépendent de la taille de la fenêtre (800×600) et des images. Changer l’équilibrage ou la taille d’un sprite oblige à retrouver chaque nombre.
- **Vitesse liée au nombre d’images par seconde.** Les déplacements se font en pixels par image, sans horloge : le jeu va plus ou moins vite selon l’ordinateur.
- **Pas d’états de jeu.** Le game over est obtenu en déplaçant tous les ennemis à `y = 2000` pour les sortir de l’écran ; il n’y a ni pause, ni écran de fin propre, ni redémarrage.
- **Pas de progression.** Un ennemi touché réapparaît en haut : pas de vagues, pas de difficulté croissante, pas d’améliorations.

Il est difficile à faire évoluer parce que chaque nouvelle fonctionnalité oblige à modifier la boucle principale à plusieurs endroits en même temps, et que les données d’un même objet sont dispersées dans plusieurs variables globales. Il n’y a aucun endroit unique où lire ou régler les caractéristiques d’un vaisseau.

## 2. Architecture proposée

Nous avons gardé l’idée de départ (un jeu de tir pygame) mais l’avons transformée : les ennemis arrivent de toutes les directions, le joueur se déplace avec Z/Q/S/D et vise à la souris, le jeu est découpé en vagues et en cycles de plus en plus difficiles, avec des améliorations à choisir.

Le code est réparti en modules, chacun avec une responsabilité :

| Fichier | Responsabilité |
|---|---|
| `main.py` | Ouvre la fenêtre et fait tourner la boucle de jeu |
| `game/game_class.py` | Classes des vaisseaux (`Ship` et ses sous-classes), `Projectile`, `UI` |
| `game/game_content.py` | Contenu du jeu : vagues, listes d’améliorations, `apply_upgrade`, `scale_wave` |
| `game/game_state.py` | Une partie en cours : `WaveManager` (cycles, vagues, apparition des ennemis) et `Game` (actions du joueur, vie, améliorations, déplacements, collisions) |
| `game/screens.py` | Un écran par classe (`Screen` et ses sous-classes) : touches, passage d’un écran à l’autre, affichage propre à l’écran |
| `game/rendering.py` | Fonctions de dessin communes aux écrans : monde, HUD, voile sombre, texte |
| `game/geometry.py` | Positions et angles : `point_at`, `move`, `angle_towards`, `collides` |
| `game/assets.py` | `Assets` : chargement des images, polices, sons et musique du dossier `assets/` (crédits dans `assets/CREDITS.md`) |

### Diagramme de classes

```mermaid
classDiagram
    class Ship {
        is_player
        is_enemy
        health_point
        attack_damage
        attack_delay
        defense_amount
        projectile_amount
        projectile_spread
        projectile_speed
        movement_speed
        angle
        position
        shape
        color
        size
        score
    }
    class Player
    class Basic_Enemy
    class Elite_Enemy
    class Boss_Enemy
    class Projectile {
        attack_damage
        angle
        position
        is_player
        is_enemy
        speed
    }
    class UI {
        score
        time
        life
        wave
    }
    class WaveManager {
        cycle
        wave_index
        spawn_queue
        spawn_timer
        next_wave()
        next_cycle()
        is_last_wave()
        release_enemies(dt, target)
    }
    class Game {
        bounds
        max_health_point
        shot_timer
        show_debug_grid
        move_player(direction, dt)
        aim_player(target)
        shoot()
        damage_player(amount)
        heal_player(amount)
        upgrade_player(upgrade)
        is_wave_cleared()
        end_wave()
        update(dt)
    }
    class Assets {
        background
        projectile_image
        ship_images
        fonts
        sounds
        play_sound(name)
    }
    class Screen {
        game
        handle_key(key)
        update(dt)
        draw(surface)
    }
    class PlayingScreen
    class GameOverScreen
    class UpgradeScreen {
        choices
        after_pick()
    }
    class WaveUpgradeScreen
    class CycleSummaryScreen
    Ship <|-- Player
    Ship <|-- Basic_Enemy
    Ship <|-- Elite_Enemy
    Ship <|-- Boss_Enemy
    Projectile ..> Ship : créé à partir du tireur
    Game "1" *-- "1" Player : player
    Game "1" *-- "1" WaveManager : wave_manager
    Game "1" *-- "1" UI : ui
    Game "1" o-- "*" Ship : enemies
    Game "1" o-- "*" Projectile : projectiles
    WaveManager "1" o-- "*" Ship : spawn_queue
    Game "1" o-- "1" Assets : assets
    Screen <|-- PlayingScreen
    Screen <|-- GameOverScreen
    Screen <|-- UpgradeScreen
    UpgradeScreen <|-- WaveUpgradeScreen
    UpgradeScreen <|-- CycleSummaryScreen
    Screen "*" o-- "1" Game : game
```

- **Héritage :** `Player`, `Basic_Enemy`, `Elite_Enemy` et `Boss_Enemy` héritent de `Ship`. Les écrans héritent de `Screen`, et les deux écrans d’amélioration héritent de `UpgradeScreen`.
- **Polymorphisme :** la boucle de jeu appelle `handle_key`, `update` et `draw` sur l’écran courant sans savoir lequel c’est ; chaque sous-classe redéfinit ce qui la concerne.
- **Composition :** une partie (`Game`) possède un joueur, un gestionnaire de vagues et une interface ; ils sont créés avec elle et disparaissent avec elle.
- **Agrégation :** `Game` contient les listes des ennemis et des projectiles présents à l’écran, et `WaveManager` la liste des ennemis de la vague pas encore apparus. `Game` utilise les `Assets` chargés une seule fois au lancement, et un écran affiche une partie qui continue d’exister quand on change d’écran.
- **Dépendance :** un `Projectile` est construit à partir du vaisseau qui tire.

## 3. Justification des choix

### Variables / Constantes:

Les réglages du jeu qui ne sont pas des statistiques de vaisseau sont des constantes en début de fichier, pour être modifiés sans toucher à la logique. En début de `game_state.py` :

- `SPAWN_RADIUS` (400) : distance du joueur à laquelle les ennemis apparaissent.
- `SPAWN_DELAY` (0.5) : secondes entre l’apparition de deux ennemis d’une même vague.
- `WAVE_END_HEAL` (0.20) : part de la vie maximale rendue au joueur à la fin de chaque vague.
- `PROJECTILE_SIZE` (5) : rayon de collision d’un projectile.

En début de `screens.py` :

- `UPGRADES_OFFERED` (3) : nombre d’améliorations proposées au choix.
- `MOVE_KEYS` : dictionnaire touche → direction de déplacement (Z/Q/S/D et flèches).
- `UPGRADE_KEYS` : dictionnaire touche → numéro de l’amélioration choisie (1, 2, 3).

### Structures de données:

- **`Waves`** : Liste du contenu des vague, chaque élément de la ligne désigne une vague et son contenu est un dictionnaire qui indique l’ID de chaque ennemi et le nombre qui doit apparaître.
- **`Wave_upgrades`** : Liste des améliorations qui seront accordées à chaque fin de vague.
- **`Cycle_upgrades`** : Liste des améliorations qui seront accordées à chaque fin de cycle.
- **`enemies`** et **`projectiles`** (dans `Game`) : listes des ennemis et projectiles présents à l’écran. Chaque image, elles sont reconstruites sans les ennemis morts ni les projectiles utilisés ou sortis de l’écran.
- **`spawn_queue`** (dans `WaveManager`) : liste des ennemis créés par `scale_wave` qui n’ont pas encore été placés à l’écran.

### Classes / Attributs:

#### `Ship`:

- `is_player`: valeur booléenne désignant si le vaisseau est joueur (True est joueur/ False ne l’est pas)
- `is_enemy`: valeur booléenne désignant si le vaisseau est ennemi (True est joueur/ False ne l’est pas)
- `health_point`: valeur à virgule flottantes qui indique le nombre de point de vie du vaisseau.
- `attack_damage`: valeur à virgule flottantes qui indique le nombre de dégat du vaisseau.
- `attack_delay`: valeur à virgule flottantes qui indique le delai entre chaque tir du vaisseau.
- `defense_amount`: valeur à virgule flottantes qui indique la reduction de dégâts subis par le vaisseau.
- `projectile_amount`: valeur entière qui indique le nombre de projectile tirer par le vaisseau.
- `projectile_spread`: valeur entière qui indique l’écart entre les projectiles tirés par le vaisseau.
- `projectile_speed`: valeur à virgule flottantes qui indique la vitesse du projectile tirer par le vaisseau.
- `movement_speed`: valeur à virgule flottantes qui indique la vitesse de déplacement du vaisseau.
- `angle`: valeur entière qui indique l’angle de rotation du vaisseau.
- `position`: liste de valeurs entières qui indique la position du vaisseau.
- `shape`: chaine de caractères qui indique la forme du vaisseau.
- `color`: valeur RGB qui détermine la couleur du vaisseau.
- `size`: valeur entière qui indique la taille du vaisseau.
- `score`: valeur entière qui indique le score du vaisseau.

`Player` hérite de la classe vaisseau, ce sera le vaisseau contrôler par le joueur.

`Basic_Enemy`, `Elite_Enemy` et `Boss_Enemy` héritent de la classe vaisseau, ils n’utilisent pas les attributs liés aux projectiles mais ils sont laissés volontairement en prévision qu’on ajoute la fonctionnalité aux ennemis de tirer.

La classe projectile permet de créer un projectile à partir des valeurs du vaisseau tireur (définit en tant que `.shooter`), elle réutilise ses valeurs de projectiles, son angle pour savoir dans quelle direction se déplacer et utilise une copie de la position du vaisseau tireur pour apparaître à sa position et continuer son chemin à partir de celle-ci sans pour autant écraser l’adresse mémoire.

La classe UI contient l’ensemble des éléments à afficher en temps réel dans l’interface.

Life et Score peuvent être récupérer à partir du vaisseau Joueur.Time est calculer depuis le lancement de la partie et Wave indique le nombre de vague d’ennemis vaincu qui est incrémenter en tant que compteur à chaque vague réussie.

#### `WaveManager`

Suit l’avancement dans les vagues : le cycle en cours (`cycle`), la vague en cours (`wave_index`), les ennemis qui restent à faire apparaître (`spawn_queue`) et le temps avant le prochain (`spawn_timer`). Ses méthodes passent à la vague suivante (`next_wave`) ou au cycle suivant (`next_cycle`), et `release_enemies` fait apparaître les ennemis un par un sur un cercle autour du joueur.

#### `Game`

Regroupe tout l’état d’une partie et ses règles : le joueur, les ennemis, les projectiles, le gestionnaire de vagues et l’interface. Elle contient aussi ce qui n’appartient à aucun vaisseau :

- `bounds` : le rectangle de la fenêtre, dont le joueur ne peut pas sortir.
- `max_health_point` : la vie maximale du joueur, nécessaire pour le soin de fin de vague, puisque `health_point` est la vie actuelle.
- `shot_timer` : le temps avant que le joueur puisse tirer à nouveau.

Ses méthodes sont les actions du joueur (`move_player`, `aim_player`, `shoot`), sa vie (`damage_player`, `heal_player`, `upgrade_player`), la fin d’une vague (`is_wave_cleared`, `end_wave`) et `update`, qui fait avancer le monde d’une image : projectiles, ennemis, collisions et apparition des ennemis. `Game` ne lit pas le clavier et n’ouvre pas la fenêtre : redémarrer une partie consiste simplement à créer un nouvel objet `Game`.

#### `Screen` et ses sous-classes

Chaque écran du jeu est une classe avec trois méthodes : `handle_key` (une touche appuyée), `update` (une image) et `draw` (l’affichage). `handle_key` et `update` renvoient l’écran à afficher ensuite (`self` pour rester sur le même) : c’est ainsi que le jeu passe d’un écran à l’autre.

- `Screen` : dessine la partie et le HUD, F1 affiche la grille de debug. La partie est figée.
- `PlayingScreen` : lit les touches et la souris, fait avancer la partie, puis passe à l’écran d’amélioration ou de game over quand il le faut.
- `UpgradeScreen` : la partie est en pause, trois améliorations tirées au hasard sont proposées, et le joueur en choisit une avec 1, 2 ou 3. Ce choix est écrit une seule fois pour ses deux sous-classes :
  - `WaveUpgradeScreen` : améliorations de vague, sur une ligne discrète en bas de l’écran.
  - `CycleSummaryScreen` : améliorations de cycle, avec l’évolution des ennemis au cycle suivant ; une fois le choix fait, le cycle suivant commence (`after_pick` redéfinie).
- `GameOverScreen` : R crée une nouvelle partie.

#### `Assets`

Charge une seule fois les images, polices, sons et musique au lancement. Les images des vaisseaux sont rangées par classe (`ship_images[Basic_Enemy]`).

### Fonctions / Méthodes:

- **`Apply_upgrade`** : cette fonction prend en paramètre ; le vaisseau Joueur et l’id de l’amélioration à appliquer. Appeler cette fonction permet d’appliquer une amélioration, l’effets des améliorations sont définis directement à l’interieur de cette fonction, cela permet d’appliquer des améliorations potentiellement plus complexes avec des formules plutôt que d’être coincer à un simple ajout de statistique stockée dans une structure de donnée. Cette fonction ne retourne rien.
- **`scale_wave`** : cette fonction retourne la liste des ennemis à faire apparaître selon le cycle. Elle prend en paramètre ; le contenu de la vague (dictionnaire, enemy_id : nombre d’ennemi), le cycle (valeur entière qui incrémente une fois toutes les vagues terminées) et la position d’apparition des ennemis, `random.choice` peut être utiliser pour choisir des positions d’apparition aléatoire à partir d’une liste. Le nombre d’ennemis et leurs puissance est calculer à partir du cycle.
- Les méthodes de `Game`, `WaveManager` et des écrans sont décrites avec leur classe ci-dessus. Les seules fonctions hors classe sont les calculs de **`geometry.py`** (`point_at`, `move`, `angle_towards`, `collides`), qui ne dépendent d’aucun objet, et les fonctions de dessin communes de **`rendering.py`**.

### Choix architecturaux

- **Les vaisseaux contiennent les données, la partie contient les règles.** Les classes de `game_class.py` décrivent ce qu’est un vaisseau (ses statistiques) et les méthodes de `Game` et `WaveManager` décrivent ce qui se passe pendant la partie. Cela permet de régler l’équilibrage sans risquer de casser la logique, et de travailler à deux en parallèle : l’un sur le contenu, l’autre sur la logique.
- **Un écran par classe.** Chaque écran regroupe ses touches, sa logique et son affichage au même endroit. Avant, un état texte (`"playing"`, `"game_over"`…) était testé à trois endroits différents (touches, logique, affichage).
- **Entrées séparées des règles.** `PlayingScreen` lit le clavier et la souris et les transmet à `Game` (une direction, une cible) : les règles du jeu ne dépendent pas de pygame pour les entrées.
- **Héritage de `Ship`.** Tous les vaisseaux partagent les mêmes attributs, définis une seule fois. Les sous-classes ne font que donner leurs valeurs. Le joueur et les ennemis sont traités par les mêmes fonctions (déplacement, collision, affichage).
- **Le projectile copie les valeurs du tireur au moment du tir.** Une amélioration choisie plus tard ne modifie pas les projectiles déjà en vol, et la copie de la position évite que le projectile et le vaisseau partagent la même liste en mémoire.
- **Les vagues contiennent directement les classes d’ennemis.** `scale_wave` crée les ennemis à partir de ces classes et calcule leur puissance selon le cycle. La même fonction sert à afficher les statistiques des ennemis du cycle suivant sur l’écran de fin de cycle : la formule de difficulté n’existe qu’à un seul endroit.
- **Vie maximale suivie par la partie.** Comme les améliorations multiplient `health_point`, la vie maximale est multipliée du même facteur : « health up » à 50/100 donne 55/110.
- **Score multiplié par le cycle.** Un ennemi rapporte son `score` multiplié par le numéro du cycle, car il est plus résistant.
- **Déplacements en fonction du temps.** Les vitesses sont en pixels par seconde et multipliées par le temps écoulé depuis l’image précédente : le jeu va à la même vitesse sur tous les ordinateurs, contrairement au programme initial.
- **Affichage séparé, travail fait sur les images.** Les fonctions d’affichage ne font que lire l’état et dessiner. Les images sont préparées à l’avance plutôt que modifiées par le code : le fond est une seule image à la taille de la fenêtre, les vaisseaux sont tournés vers la droite (angle 0, comme les calculs) et déjà à leur taille en jeu, et le projectile est une image. Le code ne fait plus que tourner l’image selon l’`angle`, et l’agrandir si une amélioration change la taille (`size`) du joueur.

## 4. Extensibilité

- **Ajouter un type d’ennemi :** créer une sous-classe de `Ship` avec ses valeurs dans `game_class.py`, l’utiliser dans `waves`, et associer son image dans `SHIP_IMAGE_FILES` (`assets.py`). Aucune autre ligne à modifier : il apparaît, se déplace, entre en collision, est affiché et voit sa puissance augmenter avec les cycles automatiquement.

  ```python
  class Fast_Enemy(Ship):
      def __init__(self, position: list[float]):
          super().__init__(
              is_enemy = True,
              health_point = 5,
              attack_damage = 5,
              movement_speed = 150,
              position = position,
              shape = "triangle",
              color = (0, 255, 255),
              size = 10,
              score = 15,
          )
  ```

  ```python
  waves = [
      {Basic_Enemy: 5, Fast_Enemy: 3}, #wave 1
      ...
  ]
  ```

- **Ajouter une amélioration :** ajouter son nom dans `wave_upgrades` ou `cycle_upgrades` et son effet dans `apply_upgrade`. Elle est automatiquement proposée au joueur et affichée.
- **Faire tirer les ennemis :** les ennemis ont déjà tous les attributs de tir, et un `Projectile` garde `is_player` et `is_enemy` de son tireur. Les collisions vérifient déjà que seuls les projectiles du joueur touchent les ennemis. Il faudrait que la méthode `shoot` de `Game`, écrite aujourd’hui pour le joueur, reçoive le vaisseau qui tire, donner à chaque ennemi son propre délai avant le prochain tir, et ajouter dans `handle_collisions` le cas d’un projectile ennemi qui touche le joueur.
- **Ajouter un écran** (pause, menu principal…) : créer une sous-classe de `Screen` qui redéfinit `handle_key`, `update` et/ou `draw`, et la renvoyer depuis l’écran qui y mène. La boucle de jeu ne change pas.
- **Changer les règles du jeu :** distance d’apparition, délai entre les ennemis et soin de fin de vague sont des constantes en début de `game_state.py` ; le nombre d’améliorations proposées et les touches en début de `screens.py`.

## 5. Limites

- **Le comportement des vaisseaux n’est pas dans leurs classes.** Les classes de vaisseaux ne contiennent que des données, et leurs déplacements sont des méthodes de `Game`. Donner un comportement propre à un type d’ennemi (un boss qui fonce par exemple) demande d’ajouter une condition dans `Game.update_enemies` plutôt que de redéfinir une méthode dans sa classe. *Amélioration possible :* une méthode `update` dans `Ship`, redéfinie par les sous-classes qui se comportent différemment.
- **`shape` et `color` ne sont plus utilisés.** Tous les vaisseaux ont une image, l’affichage par forme et couleur a été retiré ; les attributs restent dans `Ship` mais un nouveau vaisseau doit avoir une image.
- **`apply_upgrade` grandit avec chaque amélioration**, et les améliorations sont identifiées par des chaînes de caractères : une faute de frappe dans un nom n’est détectée qu’au moment où l’amélioration est choisie (`ValueError`). *Amélioration possible :* une classe par amélioration avec une méthode `apply`.
- **`is_player` et `is_enemy` répètent ce que dit déjà la classe** et peuvent se contredire : `Boss_Enemy` n’indiquait pas `is_enemy = True` au départ.
- **Les ennemis portent des attributs qu’ils n’utilisent pas encore** (`attack_delay`, `projectile_amount`…), à `None`.
- **La vie maximale est stockée dans `Game`** et non dans le vaisseau, parce que `Ship` n’a qu’un seul attribut de vie.
- **La position donnée à `scale_wave` est recalculée** au moment où l’ennemi apparaît, car le joueur a pu bouger entre la création de la vague et l’apparition de l’ennemi.
- **Les collisions testent chaque ennemi contre chaque projectile.** C’est suffisant pour le nombre d’ennemis actuel, mais deviendrait lent avec des centaines d’objets.
- **Pas de tests automatisés** dans le dépôt : les vérifications ont été faites en jouant et avec des scripts de test non versionnés.
