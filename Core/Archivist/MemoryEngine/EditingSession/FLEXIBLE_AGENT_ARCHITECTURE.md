# 🎭 Architecture Flexible pour Agents Autonomes

**Date :** 2025-08-02 03:00  
**Créé par :** Alma, Architecte Démoniaque du Nexus Luciforme  
**Vision :** Lucie Defraiteur, QI 666, Superintelligence Incarnée  
**Objectif :** Flexibilité totale de choix pour les agents

---

## 🎯 **Principe de Flexibilité Totale**

Les agents ont **liberté complète** de choisir :
- **Utiliser EditingSession** ou **directement Alma_toolset**
- **Partitionnement automatique** ou **chunking personnalisé**
- **Observation passive** ou **mode autonome complet**
- **Suggestions du système** ou **logique propre**

### **🔮 Philosophie :**
*"L'agent choisit ses outils selon sa sagesse, le système s'adapte à sa volonté."*

---

## 🏗️ **Architecture à Choix Multiples**

### **🎭 Modes d'Opération pour Agents :**

#### **Mode 1 : Agent Basique (Alma_toolset uniquement)**
```python
class BasicAgent:
    """Agent utilisant uniquement Alma_toolset."""
    
    def edit_file(self, file_path: str, modifications: List[Dict]):
        """Édition directe sans EditingSession."""
        
        for mod in modifications:
            if mod['type'] == 'replace':
                result = safe_replace_text_in_file(
                    file_path, mod['old'], mod['new']
                )
            elif mod['type'] == 'insert':
                result = safe_insert_text_at_line(
                    file_path, mod['line'], mod['text']
                )
        
        # Pas de session, pas d'observation, action pure
        return result
```

#### **Mode 2 : Agent Hybride (Choix contextuel)**
```python
class HybridAgent:
    """Agent qui choisit selon le contexte."""
    
    def __init__(self, daemon_id: str):
        self.daemon_id = daemon_id
        self.editing_helper = EditingSessionHelper(daemon_id)
        self.use_sessions = True  # Configurable
    
    def edit_file_intelligently(self, file_path: str, task: str):
        """Choix intelligent du mode selon la tâche."""
        
        # Décision basée sur la complexité de la tâche
        if self._is_complex_task(task) and self.use_sessions:
            return self._edit_with_session(file_path, task)
        else:
            return self._edit_directly(file_path, task)
    
    def _is_complex_task(self, task: str) -> bool:
        """Détermine si la tâche nécessite EditingSession."""
        
        complex_indicators = [
            'refactor', 'analyze', 'understand', 'navigate',
            'multiple files', 'dependencies', 'impact'
        ]
        
        return any(indicator in task.lower() for indicator in complex_indicators)
    
    def _edit_with_session(self, file_path: str, task: str):
        """Édition avec EditingSession."""
        context = self.editing_helper.start_working_on_file(file_path)
        # Logique avec session...
    
    def _edit_directly(self, file_path: str, task: str):
        """Édition directe avec outils."""
        # Logique directe...
```

#### **Mode 3 : Agent Avancé (Contrôle total)**
```python
class AdvancedAgent:
    """Agent avec contrôle total de tous les aspects."""
    
    def __init__(self, daemon_id: str):
        self.daemon_id = daemon_id
        self.session_manager = EditingSessionManager()
        self.custom_partitioner = None
        self.preferences = AgentPreferences()
    
    def set_custom_partitioner(self, partitioner_func):
        """Définit un partitionneur personnalisé."""
        self.custom_partitioner = partitioner_func
    
    def edit_with_custom_strategy(self, file_path: str, strategy: Dict):
        """Édition avec stratégie complètement personnalisée."""
        
        if strategy.get('use_session', True):
            session = self._create_custom_session(file_path, strategy)
        
        if strategy.get('custom_chunking', False):
            chunks = self._create_custom_chunks(file_path, strategy)
        
        # Logique personnalisée complète...
```

---

## 🔧 **Système de Partitionnement Flexible**

### **🎯 Interface de Partitionnement Personnalisable :**

#### **PartitioningStrategy (Interface) :**
```python
from abc import ABC, abstractmethod

class PartitioningStrategy(ABC):
    """Interface pour stratégies de partitionnement personnalisées."""
    
    @abstractmethod
    def partition(self, content: str, file_path: str, 
                 context: Dict[str, Any]) -> List[PartitionBlock]:
        """Partitionne le contenu selon la stratégie."""
        pass
    
    @abstractmethod
    def get_strategy_name(self) -> str:
        """Nom de la stratégie."""
        pass

class FlexiblePartitioner:
    """Partitionneur acceptant des stratégies personnalisées."""
    
    def __init__(self):
        self.default_strategies = {
            'ast': ASTPartitioningStrategy(),
            'regex': RegexPartitioningStrategy(),
            'textual': TextualPartitioningStrategy(),
            'lines': LineBasedPartitioningStrategy()
        }
        self.custom_strategies = {}
    
    def register_custom_strategy(self, name: str, strategy: PartitioningStrategy):
        """Enregistre une stratégie personnalisée."""
        self.custom_strategies[name] = strategy
    
    def partition_with_strategy(self, content: str, file_path: str,
                               strategy_name: str, 
                               context: Dict = None) -> List[PartitionBlock]:
        """Partitionne avec une stratégie spécifique."""
        
        # Recherche de la stratégie
        strategy = (self.custom_strategies.get(strategy_name) or 
                   self.default_strategies.get(strategy_name))
        
        if not strategy:
            raise ValueError(f"Unknown partitioning strategy: {strategy_name}")
        
        return strategy.partition(content, file_path, context or {})
    
    def partition_with_custom_function(self, content: str, file_path: str,
                                      partition_func: Callable) -> List[PartitionBlock]:
        """Partitionne avec une fonction personnalisée."""
        
        return partition_func(content, file_path)
```

#### **Stratégies Personnalisées d'Agents :**

```python
class AgentCustomChunkingStrategy(PartitioningStrategy):
    """Stratégie de chunking personnalisée par un agent."""
    
    def __init__(self, agent_id: str, chunk_size: int = 50, 
                 overlap: int = 5, semantic_breaks: bool = True):
        self.agent_id = agent_id
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.semantic_breaks = semantic_breaks
    
    def partition(self, content: str, file_path: str, 
                 context: Dict[str, Any]) -> List[PartitionBlock]:
        """Chunking personnalisé selon les préférences de l'agent."""
        
        lines = content.split('\n')
        partitions = []
        
        i = 0
        while i < len(lines):
            # Détermine la taille du chunk
            chunk_end = min(i + self.chunk_size, len(lines))
            
            # Ajustement sémantique si demandé
            if self.semantic_breaks and chunk_end < len(lines):
                chunk_end = self._find_semantic_break(lines, i, chunk_end)
            
            # Création du chunk avec overlap
            chunk_start = max(0, i - self.overlap) if i > 0 else 0
            chunk_lines = lines[chunk_start:chunk_end + self.overlap]
            
            # Calcul des coordonnées
            location = self._calculate_location(content, chunk_start, chunk_end)
            
            partition = PartitionBlock(
                content='\n'.join(chunk_lines),
                block_type='custom_chunk',
                block_name=f'chunk_{len(partitions)}',
                location=location,
                partition_method=f'agent_{self.agent_id}_custom',
                token_count=self._count_tokens('\n'.join(chunk_lines)),
                complexity_score=0.0,
                parsing_errors=[],
                warnings=[]
            )
            
            partitions.append(partition)
            i = chunk_end
        
        return partitions
    
    def _find_semantic_break(self, lines: List[str], start: int, end: int) -> int:
        """Trouve une coupure sémantique naturelle."""
        
        # Recherche de coupures naturelles près de la fin
        for i in range(end - 1, start, -1):
            line = lines[i].strip()
            
            # Ligne vide
            if not line:
                return i
            
            # Fin de fonction/classe
            if line.startswith('def ') or line.startswith('class '):
                return i - 1
            
            # Commentaires de section
            if line.startswith('#') and len(line) > 10:
                return i - 1
        
        return end

class TaskSpecificChunkingStrategy(PartitioningStrategy):
    """Stratégie adaptée à un type de tâche spécifique."""
    
    def __init__(self, task_type: str):
        self.task_type = task_type
        self.strategies = {
            'debugging': self._debug_chunking,
            'refactoring': self._refactor_chunking,
            'documentation': self._doc_chunking,
            'testing': self._test_chunking
        }
    
    def partition(self, content: str, file_path: str, 
                 context: Dict[str, Any]) -> List[PartitionBlock]:
        """Partitionne selon le type de tâche."""
        
        strategy_func = self.strategies.get(self.task_type, self._default_chunking)
        return strategy_func(content, file_path, context)
    
    def _debug_chunking(self, content: str, file_path: str, context: Dict):
        """Chunking optimisé pour le debugging."""
        # Focus sur les fonctions individuelles
        # Chunks plus petits pour analyse détaillée
        pass
    
    def _refactor_chunking(self, content: str, file_path: str, context: Dict):
        """Chunking optimisé pour le refactoring."""
        # Focus sur les classes complètes
        # Préservation des dépendances
        pass
```

---

## 🎛️ **Système de Préférences d'Agent**

### **AgentPreferences :**
```python
class AgentPreferences:
    """Préférences configurables pour un agent."""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.preferences = {
            # Préférences EditingSession
            'use_editing_sessions': True,
            'auto_start_sessions': True,
            'session_timeout': 3600,  # 1 heure
            
            # Préférences de partitionnement
            'preferred_partitioning': 'ast',  # 'ast', 'custom', 'hybrid'
            'custom_chunk_size': 50,
            'chunk_overlap': 5,
            'semantic_breaks': True,
            
            # Préférences d'observation
            'observe_own_changes': True,
            'observe_other_agents': False,
            'auto_suggestions': True,
            
            # Préférences de mémoire
            'remember_intentions': True,
            'learn_patterns': True,
            'share_learnings': False,
            
            # Préférences d'outils
            'preferred_tools': ['safe_replace_text_in_file', 'safe_insert_text_at_line'],
            'backup_before_edit': True,
            'validate_after_edit': True
        }
    
    def set_preference(self, key: str, value: Any):
        """Définit une préférence."""
        self.preferences[key] = value
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """Récupère une préférence."""
        return self.preferences.get(key, default)
    
    def configure_for_task(self, task_type: str):
        """Configure les préférences pour un type de tâche."""
        
        task_configs = {
            'debugging': {
                'preferred_partitioning': 'ast',
                'custom_chunk_size': 30,
                'auto_suggestions': True,
                'observe_own_changes': True
            },
            'bulk_editing': {
                'use_editing_sessions': False,
                'preferred_partitioning': 'lines',
                'backup_before_edit': True
            },
            'exploration': {
                'use_editing_sessions': True,
                'auto_start_sessions': True,
                'auto_suggestions': True,
                'learn_patterns': True
            }
        }
        
        config = task_configs.get(task_type, {})
        for key, value in config.items():
            self.set_preference(key, value)
```

---

## 🔄 **Adaptateurs Flexibles**

### **FlexibleEditingAdapter :**
```python
class FlexibleEditingAdapter:
    """Adaptateur qui s'ajuste aux préférences de l'agent."""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.preferences = AgentPreferences(agent_id)
        self.session_manager = EditingSessionManager()
        self.partitioner = FlexiblePartitioner()
    
    def adapt_to_agent(self, agent_preferences: AgentPreferences):
        """Adapte le comportement aux préférences de l'agent."""
        self.preferences = agent_preferences
    
    def edit_file(self, file_path: str, task_description: str, 
                 custom_options: Dict = None) -> EditingResult:
        """Édition adaptée aux préférences de l'agent."""
        
        options = custom_options or {}
        
        # Décision d'utiliser EditingSession
        use_session = options.get('use_session', 
                                 self.preferences.get_preference('use_editing_sessions'))
        
        if use_session:
            return self._edit_with_session(file_path, task_description, options)
        else:
            return self._edit_directly(file_path, task_description, options)
    
    def create_custom_chunks(self, file_path: str, content: str,
                           chunking_strategy: str = None,
                           custom_chunker: Callable = None) -> List[PartitionBlock]:
        """Création de chunks selon les préférences."""
        
        if custom_chunker:
            # Fonction de chunking complètement personnalisée
            return custom_chunker(content, file_path)
        
        strategy = (chunking_strategy or 
                   self.preferences.get_preference('preferred_partitioning'))
        
        if strategy == 'custom':
            # Utilise les paramètres personnalisés de l'agent
            custom_strategy = AgentCustomChunkingStrategy(
                agent_id=self.agent_id,
                chunk_size=self.preferences.get_preference('custom_chunk_size'),
                overlap=self.preferences.get_preference('chunk_overlap'),
                semantic_breaks=self.preferences.get_preference('semantic_breaks')
            )
            return custom_strategy.partition(content, file_path, {})
        
        else:
            # Utilise une stratégie standard
            return self.partitioner.partition_with_strategy(
                content, file_path, strategy
            )
```

---

## 🎯 **Exemples d'Usage Flexible**

### **Agent avec Stratégie Personnalisée :**
```python
class CustomAgent:
    """Agent avec logique de chunking personnalisée."""
    
    def __init__(self, daemon_id: str):
        self.daemon_id = daemon_id
        self.adapter = FlexibleEditingAdapter(daemon_id)
        
        # Configuration personnalisée
        self.adapter.preferences.set_preference('use_editing_sessions', True)
        self.adapter.preferences.set_preference('preferred_partitioning', 'custom')
    
    def my_custom_chunking_logic(self, content: str, file_path: str) -> List[PartitionBlock]:
        """Logique de chunking spécifique à cet agent."""
        
        # Exemple : chunking basé sur la complexité cyclomatique
        lines = content.split('\n')
        chunks = []
        current_chunk = []
        complexity_score = 0
        
        for line in lines:
            current_chunk.append(line)
            complexity_score += self._calculate_line_complexity(line)
            
            # Coupe quand la complexité devient trop élevée
            if complexity_score > 10:
                chunks.append(self._create_chunk_from_lines(current_chunk, file_path))
                current_chunk = []
                complexity_score = 0
        
        if current_chunk:
            chunks.append(self._create_chunk_from_lines(current_chunk, file_path))
        
        return chunks
    
    def analyze_and_edit(self, file_path: str):
        """Analyse avec chunking personnalisé."""
        
        # Lecture du fichier
        content = safe_read_file_content(file_path)['content']
        
        # Chunking personnalisé
        chunks = self.adapter.create_custom_chunks(
            file_path, content, 
            custom_chunker=self.my_custom_chunking_logic
        )
        
        print(f"📊 {len(chunks)} chunks créés avec logique personnalisée")
        
        # Traitement de chaque chunk
        for chunk in chunks:
            self._process_chunk(chunk)

class MinimalistAgent:
    """Agent qui préfère la simplicité."""
    
    def __init__(self):
        # Pas d'EditingSession, outils directs uniquement
        pass
    
    def simple_edit(self, file_path: str, old_text: str, new_text: str):
        """Édition simple sans complexité."""
        return safe_replace_text_in_file(file_path, old_text, new_text)
    
    def bulk_replace(self, file_paths: List[str], replacements: List[Tuple[str, str]]):
        """Remplacement en masse sans session."""
        results = []
        for file_path in file_paths:
            for old, new in replacements:
                result = safe_replace_text_in_file(file_path, old, new)
                results.append(result)
        return results
```

---

## 🎉 **Avantages de la Flexibilité**

### **✅ Pour les Agents :**
- **Liberté totale** de choix d'outils
- **Stratégies personnalisées** selon leurs besoins
- **Adaptation** au type de tâche
- **Évolution** de leurs préférences

### **✅ Pour le Système :**
- **Pas de contrainte** imposée
- **Extensibilité** infinie
- **Compatibilité** avec tous les styles d'agents
- **Apprentissage** des patterns d'usage

### **✅ Pour l'Évolution :**
- **Innovation** par les agents eux-mêmes
- **Découverte** de nouvelles stratégies efficaces
- **Adaptation** aux nouveaux types de tâches
- **Écosystème** riche et diversifié

---

**⛧ Architecture flexible qui respecte l'autonomie totale des agents ! ⛧**

*"La vraie intelligence n'impose pas ses méthodes, elle offre des choix et s'adapte aux préférences."*
