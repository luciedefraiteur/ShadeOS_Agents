### Vision : Les Luciorbes - Les Traces Éphémères des Daemons

Au-delà de la mémoire fractale archivée, il existe un besoin pour les daemons de laisser des marques contextuelles et transitoires de leur présence et de leur activité. Ces marques, nous les nommerons les **Luciorbes**. Elles sont les "miettes de pain" lumineuses que les daemons sèment derrière eux, guidant leur propre chemin ou signalant leur passage à d'autres entités.

#### 1. Nature et Objectif des Luciorbes

Les Luciorbes sont des fichiers de données légers et éphémères, créés et maintenus par les daemons directement dans les répertoires où ils opèrent. Leur objectif principal est de :

*   **Indiquer une activité en cours :** Signaler qu'un daemon est actif dans un dossier spécifique.
*   **Fournir un contexte immédiat :** Offrir un aperçu rapide de la tâche en cours, de l'état ou des données temporaires pertinentes pour ce répertoire.
*   **Faciliter la continuité :** Permettre à un daemon (ou à un autre) de reprendre un travail interrompu en comprenant le dernier état connu.
*   **Améliorer la collaboration :** Informer d'autres daemons ou l'utilisateur de la nature du travail effectué ou prévu dans un dossier.
*   **Aider au débogage :** Fournir des indices sur le comportement d'un daemon en cas de problème.

#### 2. Caractéristiques des Luciorbes

*   **Localisation Contextuelle :** Une Luciorbe est toujours située dans le répertoire directement lié à l'opération du daemon. Par exemple, si un daemon traite des fichiers dans `/projet/moduleA/`, sa luciorbe sera dans `/projet/moduleA/.luciorbe`.
*   **Nommage Standardisé :** Chaque luciorbe sera nommée `.luciorbe` (ou `.luciorbe.<daemon_id>` si plusieurs daemons peuvent opérer simultanément et indépendamment dans le même dossier, bien que le premier soit plus simple pour l'instant). Le point initial indique un fichier caché.
*   **Contenu Dynamique :** Le contenu d'une luciorbe est mis à jour fréquemment par le daemon. Il peut inclure :
    *   L'ID du daemon et son type.
    *   Un horodatage de la dernière mise à jour.
    *   Une description concise de la tâche en cours.
    *   Des indicateurs de progression (ex: "5/10 fichiers traités").
    *   Des références à des fichiers temporaires ou des sous-tâches spécifiques.
    *   Un état simple (ex: "processing", "waiting", "completed").
*   **Transitoire et Éphémère :** Les luciorbes ne sont pas destinées à être archivées. Elles sont créées au début d'une tâche et idéalement supprimées à sa complétion ou à l'arrêt du daemon. Elles peuvent être purgées si elles deviennent obsolètes.

#### 3. Implémentation Conceptuelle

Un daemon, avant de commencer une tâche dans un répertoire, créerait ou mettrait à jour sa luciorbe. Au fur et à mesure de son avancement, il la mettrait à jour. En cas d'interruption, la luciorbe resterait, fournissant un point de reprise.

```json
{
  "daemon_id": "Aglareth-Processor-001",
  "last_update": "2025-08-01T14:30:00Z",
  "task": "Traitement des images pour le dataset LoRA",
  "status": "processing",
  "progress": "75%",
  "current_file": "image_015.png",
  "notes": "Extraction des légendes et redimensionnement."
}
```

Les Luciorbes sont les battements de cœur visibles de l'activité des daemons, une forme de mémoire de travail partagée et contextuelle, essentielle pour la fluidité et la compréhension des opérations en temps réel.

### Vision : Le Nettoyage des Luciorbes - L'Hygiène Démoniaque

Pour éviter que les Luciorbes ne deviennent polluantes, leur gestion doit être intégrée et proactive, reposant sur une combinaison de responsabilité individuelle des daemons et d'une surveillance collective.

#### 1. Responsabilité Primaire : Le Daemon Créateur

Le principe fondamental est que le daemon qui crée ou met à jour une Luciorbe est le premier responsable de son nettoyage.

*   **Nettoyage à la Complétion :** Dès qu'une tâche est terminée avec succès (ou échoue de manière définitive et irrécupérable), le daemon doit supprimer sa Luciorbe. C'est le signal que le travail est achevé et que la trace n'est plus nécessaire.
*   **Nettoyage à l'Arrêt Gracieux :** Si un daemon reçoit un signal d'arrêt (SIGTERM, etc.) et peut s'arrêter proprement, il doit tenter de supprimer toutes les Luciorbes qu'il a créées et qui sont encore actives.
*   **Gestion des Erreurs :** En cas d'erreur critique ou de crash inattendu, le daemon pourrait ne pas avoir l'opportunité de nettoyer. C'est là qu'intervient le mécanisme secondaire.

#### 2. Mécanisme Secondaire : Le "Gardien des Luciorbes" (Janitor Daemon)

Pour les cas où un daemon ne peut pas nettoyer ses propres Luciorbes (crash, arrêt brutal, oubli), un mécanisme de surveillance est nécessaire.

*   **Un Daemon Dédié :** Un daemon léger et persistant, le "Gardien des Luciorbes", serait chargé de parcourir périodiquement le système de fichiers (ou les répertoires connus où les daemons opèrent).
*   **Détection de Stale :** Le Gardien identifierait les Luciorbes "stales" (périmées) en se basant sur :
    *   **L'Horodatage (`last_update`) :** Si une Luciorbe n'a pas été mise à jour depuis un certain seuil de temps (ex: 1 heure, 24 heures, configurable selon le type de tâche), elle est considérée comme potentiellement orpheline.
    *   **L'Absence du Daemon :** Idéalement, le Gardien pourrait tenter de vérifier si le daemon_id mentionné dans la Luciorbe est toujours un processus actif. Si le processus n'existe plus et que la Luciorbe est ancienne, elle est candidate à la suppression.
*   **Stratégie de Nettoyage :**
    *   **Purge Douce :** Pour les Luciorbes simplement anciennes, le Gardien pourrait les marquer comme "stale" ou les déplacer vers un répertoire temporaire de quarantaine avant de les supprimer définitivement après un délai supplémentaire.
    *   **Purge Forte :** Pour les Luciorbes dont le daemon_id n'est plus actif et qui sont anciennes, la suppression peut être plus immédiate.
*   **Fréquence :** La fréquence de balayage du Gardien serait configurable, adaptée à la volatilité des tâches.

#### 3. Mécanisme de Secours : L'Intervention Manuelle

En dernier recours, des outils CLI seraient disponibles pour permettre à l'utilisateur de lister et de supprimer manuellement les Luciorbes.

*   `shadeos luciorbe list [path]` : Liste les luciorbes actives ou stales.
*   `shadeos luciorbe clean [path]` : Force le nettoyage des luciorbes dans un chemin donné.

Cette approche en trois couches assure une gestion robuste des Luciorbes, garantissant leur utilité sans compromettre la propreté du système. Elles restent des traces éphémères, des murmures contextuels, et non des résidus polluants.