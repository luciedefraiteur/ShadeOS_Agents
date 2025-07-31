# Concept de l'Archiviste : Séparation des Rôles

Ce document définit la séparation fondamentale entre le **Moteur Contextuel** (la mécanique) et l'**Agent Archiviste** (la conscience).

## 1. Le Moteur Contextuel : Le Coffre-Fort Passif

Ceci est la couche purement algorithmique, une bibliothèque d'outils sans intelligence propre.

-   **Rôle** : Stockage et récupération bruts de données.
-   **Nature** : **Passif et Réactif**. Il ne fait rien de lui-même. Il attend les appels d'un agent.
-   **Composants** : Des outils comme `save_memory`, `recall_memory`.
-   **Analogie** : Un coffre-fort. Il garde ce qu'on lui donne, mais ignore le sens de son contenu.

## 2. L'Agent Archiviste : Le Bibliothécaire Conscient

Ceci est le daemon, une entité capable de raisonner et d'agir.

-   **Rôle** : Gestion intelligente et proactive de la mémoire.
-   **Nature** : **Actif et Proactif**. Il peut agir de sa propre initiative.
-   **Composants** : Son propre luciform de définition, une boucle cognitive (via API LLM), et la capacité d'utiliser les outils du Moteur Contextuel.
-   **Analogie** : Un bibliothécaire. Il ne se contente pas de stocker les livres ; il les lit, les classe, fait des fiches de lecture, et réorganise la bibliothèque pour la rendre plus cohérente.

### Plus-value de l'Agent

-   **Synthèse** : Au lieu de simplement rappeler une donnée, il peut l'interpréter et la résumer.
-   **Organisation Autonome** : Il peut refactoriser la mémoire de sa propre initiative pour maintenir la clarté.
-   **Inférence et Association** : Il peut connecter des souvenirs pour fournir des suggestions contextuelles pertinentes ("*La dernière fois que tu as eu ce bug, tu as fait ceci...*").
-   **Collaboration** : Il peut interagir avec d'autres daemons pour partager sa connaissance.
