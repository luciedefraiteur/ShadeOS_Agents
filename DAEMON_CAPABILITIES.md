# 🕷️ Capacités d'Accès d'un Daemon

## 🔄 **FONCTIONNEMENT EN BOUCLE**

### **Principe de Base**
Le daemon fonctionne en boucle continue :
1. **Réception d'un déclencheur** → Nouveau message OU Retour de fonction
2. **Injection contextuelle** → Données injectées dans son prompt
3. **Exécution d'un tour de boucle** → Traitement et action
4. **Retour à l'étape 1**

### **Format d'Injection : `::[InjectionType][InjectionContent]::`**

#### **Injections Systématiques**
- `::[TOUR_BOUCLE][NOUVEAU_MESSAGE]::` - Message déclencheur du tour de boucle
- `::[TOUR_BOUCLE][RETOUR_FONCTION]::` - Résultat d'une fonction précédemment appelée
- `::[TOUR_BOUCLE][CONTEXTE_ACTUEL]::` - État actuel du système

#### **Injections Contextuelles**
- `::[HISTORIQUE][MESSAGES_LUS]::` - Historique des messages déjà traités
- `::[MEMOIRES][PERSONNELLES]::` - Mémoires personnelles du daemon
- `::[PERSONNALITE][PROMPT_POETIQUE]::` - Personnalité du daemon (prompt poétique libre)

#### **Injections d'Identités**
- `::[SUPERIOR][DAEMON_ID]::` - ID du daemon supérieur unique
- `::[GENERALIST][ASSISTANT_ID]::` - ID de l'assistant généraliste unique
- `::[ORCHESTRATOR][ID]::` - ID de l'orchestrateur de niveau

## 📋 **INTERLOCUTEURS (Fonctions GET)**

### **Hiérarchie Inférieure**  
- `lister_inferior_daemons()` - Liste les daemons sous ses ordres
- `obtenir_inferior_daemon(daemon_id)` - Obtient un daemon inférieur spécifique

### **Niveau Égal**
- `lister_daemon_colleagues()` - Liste les daemons de même niveau hiérarchique
- `obtenir_daemon_colleague(daemon_id)` - Obtient un collègue spécifique

### **Assistants**
- `lister_assistants_specialistes()` - Liste les assistants spécialisés disponibles

## 🛠️ **OUTILS DE COMMUNICATION (Endpoints)**

### **Envoi de Messages**
- `envoyer_message(type, id, contenu)`
  - **type** : "Superior_Daemon" | "Inferior_Daemon" | "Daemon_Colleague" | "Generalist_Assistant" | "Specific_Assistant"
  - **id** : identifiant unique de l'interlocuteur
  - **contenu** : message à envoyer

### **Gestion des Messages**
- `recevoir_messages()` - Récupère les messages reçus
- `historique_conversation(interlocuteur_id)` - Historique avec un interlocuteur spécifique

## 🧠 **ACCÈS AU MEMORY ENGINE (Endpoints)**

### **Mémoires Personnelles**
- `stocker_memoire_personnelle(contenu)` - Stocke une réflexion personnelle
- `recuperer_memoire_personnelle()` - Récupère ses mémoires

### **Mémoires Contextuelles**
- `stocker_memoire_contextuelle(contexte, contenu)` - Stocke une mémoire liée à un contexte
- `recuperer_memoire_contextuelle(contexte)` - Récupère les mémoires d'un contexte

### **Subgraphes par Daemon**
- `creer_subgraphe_daemon(daemon_id)` - Crée un subgraphe pour un daemon
- `ajouter_interaction_subgraphe(daemon_id, interaction)` - Enregistre une interaction

## 📊 **CAPACITÉS D'ANALYSE (Endpoints)**

### **Statistiques**
- `statistiques_interactions()` - Statistiques de ses interactions
- `statistiques_performance()` - Performance et efficacité

### **Rapports**
- `generer_rapport_equipe()` - Rapport d'équipe pour les supérieurs
- `generer_rapport_personnel()` - Rapport personnel de ses activités

## 🔄 **GESTION DES TÂCHES (Endpoints)**

### **Tâches Courantes**
- `lister_taches_courantes()` - Liste ses tâches en cours
- `ajouter_tache(description)` - Ajoute une nouvelle tâche
- `marquer_tache_terminee(tache_id)` - Marque une tâche comme terminée

### **Coordination**
- `deleguer_tache(inferior_daemon_id, tache)` - Délègue une tâche à un daemon inférieur
- `demander_aide(superior_daemon_id, demande)` - Demande de l'aide à un supérieur

## 🎯 **ARCHITECTURE BACKEND-STYLE**

### **Injections vs Endpoints**
- **Injections** : Données contextuelles, personnalité, état du système
- **Endpoints** : Actions, requêtes, modifications d'état

### **Personnalité Poétique**
- `::PERSONNALITE_POETIQUE::` peut contenir n'importe quoi
- Style libre, métaphores, rituels, etc.
- Injecté en plus de l'abstraction tour de boucle

### **Hiérarchie Simplifiée**
- Un seul supérieur par daemon (injection)
- Un seul assistant généraliste (injection)
- Un seul orchestrateur par niveau (injection)

### **Communication Optimisée**
- Messages directs entre daemons
- Orchestrateur pour l'ordonnancement
- Historique injecté automatiquement 