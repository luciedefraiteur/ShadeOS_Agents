# 🎛️ Guide de Configuration pour Agents Autonomes

**Date :** 2025-08-02 03:05  
**Créé par :** Alma, Architecte Démoniaque du Nexus Luciforme  
**Vision :** Lucie Defraiteur, QI 666, Superintelligence Incarnée  
**Objectif :** Guide complet pour configurer les agents selon leurs besoins

---

## 🎯 **Philosophie de Configuration**

Chaque agent peut **choisir librement** :
- **Ses outils** : EditingSession, Alma_toolset, ou les deux
- **Sa stratégie** : Partitionnement automatique ou logique personnalisée
- **Son niveau** : Simple, hybride, ou contrôle total
- **Ses préférences** : Adaptées à son style et ses tâches

### **🔮 Principe :**
*"Configure-toi selon ta nature, le système s'adaptera à ta volonté."*

---

## 🎭 **Profils d'Agents Types**

### **🟢 Agent Minimaliste :**
```python
class MinimalistAgent:
    """Agent simple utilisant uniquement Alma_toolset."""
    
    def __init__(self, name: str):
        self.name = name
        # Pas d'EditingSession, pas de complexité
    
    def configure(self):
        """Configuration minimaliste."""
        return {
            'use_editing_sessions': False,
            'use_partitioning': False,
            'tools': ['safe_replace_text_in_file', 'safe_read_file_content'],
            'style': 'direct_action'
        }
    
    def edit_file(self, file_path: str, changes: List[Dict]):
        """Édition directe sans fioritures."""
        for change in changes:
            safe_replace_text_in_file(
                file_path, change['old'], change['new']
            )
```

### **🟡 Agent Hybride :**
```python
class HybridAgent:
    """Agent qui choisit selon le contexte."""
    
    def __init__(self, name: str):
        self.name = name
        self.preferences = AgentPreferences(name)
        self.adapter = FlexibleEditingAdapter(name)
    
    def configure(self):
        """Configuration hybride adaptative."""
        self.preferences.set_preference('use_editing_sessions', True)
        self.preferences.set_preference('auto_start_sessions', False)  # Choix manuel
        self.preferences.set_preference('preferred_partitioning', 'ast')
        self.preferences.set_preference('custom_chunk_size', 40)
        
        return {
            'style': 'adaptive',
            'decision_logic': 'context_based',
            'fallback': 'direct_tools'
        }
    
    def decide_approach(self, task: str, file_size: int) -> str:
        """Décide de l'approche selon la tâche."""
        
        if 'analyze' in task.lower() or file_size > 1000:
            return 'use_session'
        elif 'quick' in task.lower() or file_size < 100:
            return 'direct_tools'
        else:
            return 'hybrid'
```

### **🔴 Agent Avancé :**
```python
class AdvancedAgent:
    """Agent avec contrôle total et logique personnalisée."""
    
    def __init__(self, name: str):
        self.name = name
        self.session_manager = EditingSessionManager()
        self.custom_strategies = {}
        self.learning_data = {}
    
    def configure(self):
        """Configuration avancée avec stratégies personnalisées."""
        
        # Enregistre ses propres stratégies
        self.register_custom_partitioning_strategy()
        self.setup_learning_system()
        
        return {
            'style': 'full_control',
            'custom_partitioning': True,
            'learning_enabled': True,
            'collaboration': True
        }
    
    def register_custom_partitioning_strategy(self):
        """Enregistre une stratégie de partitionnement personnalisée."""
        
        def my_semantic_chunking(content: str, file_path: str) -> List[PartitionBlock]:
            """Chunking basé sur l'analyse sémantique."""
            
            # Logique personnalisée complexe
            # Analyse des dépendances, complexité, etc.
            pass
        
        self.custom_strategies['semantic'] = my_semantic_chunking
```

---

## 🔧 **Options de Configuration Détaillées**

### **📋 Préférences EditingSession :**
```python
editing_session_config = {
    # Activation
    'use_editing_sessions': True,          # Utiliser EditingSession
    'auto_start_sessions': True,           # Démarrage automatique
    'session_timeout': 3600,               # Timeout en secondes
    'max_concurrent_sessions': 5,          # Sessions simultanées max
    
    # Observation
    'observe_own_changes': True,           # Observer ses propres modifications
    'observe_other_agents': False,         # Observer les autres agents
    'auto_refresh_on_change': True,        # Rafraîchir automatiquement
    
    # Suggestions
    'auto_suggestions': True,              # Suggestions automatiques
    'suggestion_threshold': 0.7,           # Seuil de confiance
    'max_suggestions': 5,                  # Nombre max de suggestions
    
    # Mémoire
    'remember_intentions': True,           # Mémoriser les intentions
    'learn_patterns': True,                # Apprentissage des patterns
    'share_learnings': False,              # Partager avec autres agents
    'memory_retention_days': 30            # Rétention mémoire
}
```

### **🔀 Préférences de Partitionnement :**
```python
partitioning_config = {
    # Stratégie principale
    'preferred_strategy': 'ast',           # 'ast', 'regex', 'textual', 'custom'
    'fallback_strategies': ['regex', 'textual', 'lines'],
    
    # Paramètres de chunking personnalisé
    'custom_chunk_size': 50,               # Lignes par chunk
    'chunk_overlap': 5,                    # Lignes d'overlap
    'semantic_breaks': True,               # Coupures sémantiques
    'preserve_functions': True,            # Préserver fonctions entières
    'preserve_classes': True,              # Préserver classes entières
    
    # Limites
    'max_tokens_per_chunk': 3500,         # Limite OpenAI
    'min_chunk_size': 10,                 # Taille minimale
    'max_chunks_per_file': 100,           # Limite de chunks
    
    # Optimisations
    'cache_partitions': True,              # Cache des partitions
    'parallel_processing': True,           # Traitement parallèle
    'lazy_loading': True                   # Chargement à la demande
}
```

### **🛠️ Préférences d'Outils :**
```python
tools_config = {
    # Outils préférés
    'preferred_tools': [
        'safe_replace_text_in_file',
        'safe_insert_text_at_line',
        'safe_read_file_content'
    ],
    
    # Sécurité
    'backup_before_edit': True,            # Sauvegarde avant édition
    'validate_after_edit': True,           # Validation après édition
    'dry_run_mode': False,                 # Mode simulation
    
    # Performance
    'batch_operations': True,              # Opérations groupées
    'async_operations': False,             # Opérations asynchrones
    'progress_reporting': True,            # Rapport de progression
    
    # Intégration
    'notify_editing_session': True,        # Notifier EditingSession
    'auto_refresh_sessions': True,         # Rafraîchir sessions auto
    'log_all_operations': True             # Logger toutes les opérations
}
```

---

## 🎯 **Configurations par Type de Tâche**

### **🐛 Configuration Debugging :**
```python
debugging_config = {
    'editing_session': {
        'use_editing_sessions': True,
        'auto_start_sessions': True,
        'auto_suggestions': True,
        'observe_own_changes': True
    },
    'partitioning': {
        'preferred_strategy': 'ast',
        'custom_chunk_size': 30,           # Chunks plus petits
        'preserve_functions': True,
        'semantic_breaks': True
    },
    'tools': {
        'preferred_tools': [
            'safe_read_file_content',
            'locate_text_sigils',
            'safe_insert_text_at_line'      # Pour logs de debug
        ],
        'backup_before_edit': True,
        'validate_after_edit': True
    }
}
```

### **🔄 Configuration Refactoring :**
```python
refactoring_config = {
    'editing_session': {
        'use_editing_sessions': True,
        'auto_suggestions': True,
        'learn_patterns': True,
        'remember_intentions': True
    },
    'partitioning': {
        'preferred_strategy': 'ast',
        'preserve_classes': True,          # Classes entières
        'preserve_functions': True,
        'custom_chunk_size': 100           # Chunks plus gros
    },
    'tools': {
        'preferred_tools': [
            'safe_replace_text_in_file',
            'safe_replace_lines_in_file',
            'replace_text_in_project'       # Refactoring global
        ],
        'backup_before_edit': True,
        'batch_operations': True
    }
}
```

### **⚡ Configuration Édition Rapide :**
```python
quick_edit_config = {
    'editing_session': {
        'use_editing_sessions': False,     # Pas de session
        'auto_start_sessions': False
    },
    'partitioning': {
        'preferred_strategy': 'lines',     # Simple
        'custom_chunk_size': 20
    },
    'tools': {
        'preferred_tools': [
            'safe_replace_text_in_file',
            'safe_append_to_file'
        ],
        'backup_before_edit': False,       # Plus rapide
        'validate_after_edit': False,
        'batch_operations': True
    }
}
```

---

## 🎛️ **API de Configuration**

### **ConfigurationManager :**
```python
class AgentConfigurationManager:
    """Gestionnaire de configuration pour agents."""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.config_file = f"configs/{agent_id}_config.json"
        self.current_config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Charge la configuration depuis le fichier."""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        else:
            return self.get_default_config()
    
    def save_config(self):
        """Sauvegarde la configuration."""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.current_config, f, indent=2)
    
    def configure_for_task(self, task_type: str):
        """Configure automatiquement pour un type de tâche."""
        
        task_configs = {
            'debugging': debugging_config,
            'refactoring': refactoring_config,
            'quick_edit': quick_edit_config,
            'exploration': exploration_config,
            'documentation': documentation_config
        }
        
        if task_type in task_configs:
            self.current_config.update(task_configs[task_type])
            self.save_config()
    
    def set_preference(self, category: str, key: str, value: Any):
        """Définit une préférence spécifique."""
        if category not in self.current_config:
            self.current_config[category] = {}
        
        self.current_config[category][key] = value
        self.save_config()
    
    def get_preference(self, category: str, key: str, default: Any = None) -> Any:
        """Récupère une préférence."""
        return self.current_config.get(category, {}).get(key, default)
    
    def create_custom_profile(self, profile_name: str, config: Dict[str, Any]):
        """Crée un profil personnalisé."""
        if 'custom_profiles' not in self.current_config:
            self.current_config['custom_profiles'] = {}
        
        self.current_config['custom_profiles'][profile_name] = config
        self.save_config()
    
    def apply_profile(self, profile_name: str):
        """Applique un profil personnalisé."""
        profiles = self.current_config.get('custom_profiles', {})
        if profile_name in profiles:
            self.current_config.update(profiles[profile_name])
            self.save_config()
```

---

## 🎯 **Exemples d'Usage**

### **Configuration Simple :**
```python
# Agent qui veut juste éditer sans complexité
agent = SimpleAgent("editor_bot")
config = AgentConfigurationManager("editor_bot")

config.configure_for_task('quick_edit')
config.set_preference('tools', 'backup_before_edit', False)
```

### **Configuration Avancée :**
```python
# Agent avec besoins spécifiques
agent = AdvancedAgent("refactor_master")
config = AgentConfigurationManager("refactor_master")

# Profil personnalisé
custom_profile = {
    'editing_session': {
        'use_editing_sessions': True,
        'custom_chunk_size': 75,
        'learn_patterns': True
    },
    'partitioning': {
        'preferred_strategy': 'custom',
        'semantic_breaks': True
    }
}

config.create_custom_profile('my_refactoring_style', custom_profile)
config.apply_profile('my_refactoring_style')
```

### **Configuration Adaptative :**
```python
# Agent qui s'adapte selon le contexte
agent = AdaptiveAgent("smart_editor")
config = AgentConfigurationManager("smart_editor")

def configure_for_file(file_path: str):
    file_size = os.path.getsize(file_path)
    
    if file_size > 10000:  # Gros fichier
        config.configure_for_task('refactoring')
    elif file_size < 1000:  # Petit fichier
        config.configure_for_task('quick_edit')
    else:  # Taille moyenne
        config.configure_for_task('debugging')
```

---

## 🎉 **Avantages de cette Flexibilité**

### **✅ Personnalisation Totale :**
- **Chaque agent** peut avoir sa configuration unique
- **Adaptation** aux styles de travail différents
- **Évolution** des préférences dans le temps

### **✅ Efficacité Optimisée :**
- **Configuration par tâche** pour performance maximale
- **Profils réutilisables** pour cohérence
- **Adaptation automatique** selon le contexte

### **✅ Apprentissage et Évolution :**
- **Mémorisation** des configurations efficaces
- **Partage** de bonnes pratiques (optionnel)
- **Innovation** par expérimentation

---

**⛧ Configuration flexible qui respecte l'individualité de chaque agent ! ⛧**

*"Chaque agent est unique, sa configuration doit refléter son essence."*
