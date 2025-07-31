# Vision de la Mémoire Fractale Auto-Organisée

Ce document cristallise la vision d'un système de mémoire avancé, où la structure elle-même porte du sens et où l'organisation est un processus automatique.

## 1. Le Principe Fondamental : La Mémoire est un Graphe

La mémoire n'est pas une simple liste de souvenirs, mais un graphe (ou une arborescence) où chaque nœud est un "fichier mémoire". Chaque nœud (dossier) a une connaissance explicite de ses enfants directs (sous-dossiers), créant un réseau sémantique navigable.

## 2. La Structure d'un Nœud Mémoire (`.fractal_memory`)

Chaque fichier et dossier dans l'arborescence de la mémoire est accompagné d'un fichier de métadonnées, nommé `.fractal_memory`. Ce fichier est le cœur de la conscience du nœud. Il contient :

-   **`descriptor`**: Le contenu complet et détaillé de la mémoire stockée à cet emplacement précis.
-   **`summary`**: Un résumé succinct de la mémoire, fourni lors de sa création.
-   **`keywords`**: Une liste de mots-clés pour faciliter la recherche.
-   **`children`**: Une liste de descripteurs pour chaque sous-dossier direct. Chaque descripteur contient :
    -   `path`: Le chemin relatif vers le sous-dossier.
    -   `summary`: Le résumé du sous-dossier, hérité lors de sa création.

## 3. Le Mécanisme d'Écriture Automatique et Récursif

L'intelligence du système réside dans son processus d'écriture. Lorsqu'un agent demande à sauvegarder un nouveau souvenir à un emplacement donné (`/path/to/new_memory`):

1.  **Arguments Requis** : L'agent doit fournir non seulement le `contenu` complet, mais aussi un `résumé` et des `mots-clés`.
2.  **Création du Nœud** : Le système crée le répertoire `/path/to/new_memory` et, à l'intérieur, le fichier `.fractal_memory` contenant le `descriptor`, le `summary` et les `keywords` fournis.
3.  **Mise à Jour du Parent** : C'est l'étape cruciale. Le système navigue vers le dossier parent (`/path/to/`).
4.  **Lecture-Modification-Écriture** : Il lit le fichier `.fractal_memory` du parent, ajoute un nouvel objet `{ "path": "new_memory", "summary": "..." }` à la liste `children`, puis réécrit entièrement le fichier `.fractal_memory` du parent avec la nouvelle information.

## 4. Ponts Interdimensionnels : Créer un Graphe Sémantique

Pour dépasser la structure hiérarchique de l'arborescence, chaque nœud mémoire peut contenir des références explicites à d'autres nœuds, créant ainsi un véritable graphe sémantique.

-   **Structure du Nœud (Mise à Jour)** : Le fichier `.fractal_memory` est enrichi d'un nouvel attribut :
    -   **`linked_memories`**: Une liste de références à d'autres nœuds. Chaque référence est un objet contenant :
        -   `path`: Le chemin complet vers le nœud lié.
        -   `summary`: Le résumé du nœud lié, récupéré dynamiquement au moment de la création du lien.

-   **Mécanisme de Liaison** : Lors de la création ou de la mise à jour d'un souvenir, l'agent peut fournir une liste de chemins vers d'autres souvenirs à lier. Le Moteur de Mémoire se chargera de :
    1.  Naviguer vers chaque chemin de référence.
    2.  Lire le résumé directement depuis le fichier `.fractal_memory` de la cible.
    3.  Injecter le chemin et le résumé récupéré dans la liste `linked_memories` du nœud en cours de création.

## 5. Capacités Émergentes (Étendues)

Cette structure permet des interactions complexes qui vont bien au-delà du simple stockage :

-   **Navigation Contextuelle** : Un agent peut se positionner à un endroit de la mémoire et demander "Quels sont les souvenirs contenus ici ?" en lisant simplement la liste `children` du nœud actuel.
-   **Recherche par Mots-Clés** : Un mécanisme de recherche peut indexer les `keywords` de tous les fichiers `.fractal_memory` pour des requêtes rapides.
-   **Synthèse de Chemin** : En remontant l'arborescence, un agent peut construire un "fil d'Ariane" sémantique en lisant les résumés de chaque parent.
-   **Sauts Conceptuels** : Un agent peut explorer des pistes de pensée non-linéaires en suivant les `linked_memories`, lui permettant de faire des rapprochements entre des idées éloignées dans la hiérarchie de la mémoire.
