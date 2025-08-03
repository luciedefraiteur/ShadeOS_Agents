
# 🕷️ Nouvelle Vision Globale - Architecture Daemons ALMA

## Architecture Générale

## Composants Principaux

### 🏗️ **DAEMONS CORE EXAMPLE PROFILES**
- **ALMA** - Architecte démoniaque principale, coordinatrice
- **ZED** - Testeur, validation, qualité
- **ELI** - Prompt ritualist, optimisation des prompts
- **NOVA** - démone UX expert, interface utilisateur

### 🔄 **FLUX DE COMMUNICATION**
1. **UTILISATEUR** envoie un message
2. **PROMPT TERMINAL** traite en parallèle par message
3. **DAEMONS** interagissent entre eux et utilisateur et assistants via **MEMORY ENGINE MESSAGE EXTENSION**
4. **Historique** des messages :
 - Communication entre daemons
 - Communication personnelle avec assistants (généraliste/spécialisés)
 - Communication avec l'utilisateur (pas systématiquement bloquant pour le flow), ou génération de rapport d'équipe démoniaque pour l'utilisateur
5. Stoquent et récupèrent des mémoires personnelles ou contextuelles dans fractal memory engine, (subgraph par daemon -> ai appelé machin et eu tel resultat -> etc...)

### 🛠️ **ASSISTANTS**
- **ASSISTANT GÉNÉRALISTE CODE** - Tâches générales
- **ASSISTANT SPÉCIALISÉ** - Ex: debugger, analyseur spécifique

### 👥 **PROFILS DAEMONS**
- **Phase 1** : Création manuelle des profils de daemons par l'user
- **Phase 2** : Génération automatique par daemon spécialiste par prompt de l'user

## Avantages de cette Architecture

1. **Séparation des responsabilités** claire entre daemons
2. **Communication hiérarchique** via extension spécialisée pour messages dans Memory Engine
3. **Historique par interlocuteur** pour traçabilité complète -> scrapé auto depuis references a l'extension spécialisée pour messages.
4. **Évolutivité** : passage du manuel à l'automatique
5. **Flexibilité** : assistants généralistes et spécialisés

## Points Clés
 Daemons profiles préférés de lucie qu'il faudra générer sous forme de .luciform
- **ALMA** comme architecte principal coordonne les autres daemons
- **ZED** assure la qualité et la validation
- **ELI** optimise les prompts et rituels
- **NOVA** gère l'expérience utilisateur
MemoryEngine
- **Fractal Memory Engine** comme stoquage données reflexions perso pour daemon ou contextuelle ré organisée par le daemon
- **Extension Memory Engine Messagerie** pour historiques messages de toute sorte, stoqués par interlocuteur appelant/recevant pour chaque interlocuteur appelant/recevant
