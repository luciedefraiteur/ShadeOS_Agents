# 📡 Protocoles de Communication - MD Daemon

**Date :** 2025-08-02 12:15  
**Créé par :** Alma, Architecte Démoniaque du Nexus Luciforme  
**Vision :** Lucie Defraiteur, QI 666, Superintelligence Incarnée  
**Objectif :** Protocoles de communication robustes pour tous les composants

---

## 🎯 **Vision des Protocoles**

### **🔮 Problème Identifié :**
- **Communication ad-hoc** : Pas de protocole standardisé
- **Gestion d'erreurs** : Inconsistante entre composants
- **Monitoring** : Pas de visibilité sur les échanges
- **Debugging** : Difficile de tracer les communications
- **Évolutivité** : Ajout de composants complexe

### **🎭 Solution Mystique :**
Un **système de protocoles** unifié avec :
- **Messages standardisés** : Format JSON structuré
- **Canaux de communication** : IPC, WebSocket, REST API
- **Gestion d'erreurs** : Codes d'erreur et retry logic
- **Monitoring** : Logs et métriques centralisés
- **Versioning** : Compatibilité entre versions

---

## 🏗️ **Architecture des Protocoles**

### **📋 Composants Communicants :**

#### **🤖 MD Daemon Core :**
- **Rôle** : Orchestrateur principal
- **Communications** : Avec tous les autres composants
- **Protocoles** : IPC, REST API, WebSocket

#### **🔍 Content Type Detector :**
- **Rôle** : Service de détection
- **Communications** : Requêtes/Réponses avec Daemon
- **Protocoles** : IPC, Function calls

#### **🤖 OpenAI/Ollama Analyzer :**
- **Rôle** : Service d'analyse IA
- **Communications** : Requêtes async avec Daemon
- **Protocoles** : IPC, Message Queue

#### **🧠 MemoryEngine :**
- **Rôle** : Base de données contextuelle
- **Communications** : CRUD operations
- **Protocoles** : Database protocol, IPC

#### **🔧 Partitioning System :**
- **Rôle** : Service de partitioning
- **Communications** : Requêtes de partitioning
- **Protocoles** : Function calls, IPC

---

## 📡 **Protocoles de Communication**

### **📋 1. Message Protocol (JSON-RPC Style)**

#### **🔄 Structure de Message :**
```json
{
  "protocol_version": "1.0",
  "message_id": "uuid-v4",
  "timestamp": "2025-08-02T12:15:00Z",
  "source": "component_name",
  "target": "component_name",
  "message_type": "request|response|notification|error",
  "method": "method_name",
  "params": {},
  "result": {},
  "error": {
    "code": 1001,
    "message": "Error description",
    "data": {}
  },
  "metadata": {
    "correlation_id": "uuid-v4",
    "priority": "high|medium|low",
    "timeout": 30000,
    "retry_count": 0
  }
}
```

#### **📊 Types de Messages :**
- **REQUEST** : Demande d'action
- **RESPONSE** : Réponse à une requête
- **NOTIFICATION** : Information sans réponse attendue
- **ERROR** : Signalement d'erreur

### **📋 2. Content Detection Protocol**

#### **🔍 Requête de Détection :**
```json
{
  "message_type": "request",
  "method": "detect_content_type",
  "params": {
    "file_path": "path/to/file.md",
    "content": "file content...",
    "options": {
      "include_characteristics": true,
      "confidence_threshold": 0.7
    }
  }
}
```

#### **📊 Réponse de Détection :**
```json
{
  "message_type": "response",
  "result": {
    "content_type": "documentation",
    "confidence_score": 0.85,
    "characteristics": {
      "code_ratio": 0.15,
      "documentation_ratio": 0.85,
      "structural_complexity": 0.3,
      "narrative_flow": 0.8,
      "technical_density": 0.6,
      "language_detected": "markdown"
    },
    "recommended_strategy": "textual_partitioning"
  }
}
```

### **📋 3. AI Analysis Protocol**

#### **🤖 Requête d'Analyse :**
```json
{
  "message_type": "request",
  "method": "analyze_content",
  "params": {
    "content": "content to analyze...",
    "file_path": "path/to/file.md",
    "content_type": "documentation",
    "analysis_options": {
      "force_ollama": false,
      "max_cost": 0.01,
      "priority": "medium"
    }
  }
}
```

#### **📊 Réponse d'Analyse :**
```json
{
  "message_type": "response",
  "result": {
    "ai_insights": {
      "classification": {},
      "semantic_tags": [],
      "summary": "",
      "importance_score": 85.0,
      "model_used": "gpt-3.5-turbo"
    },
    "cost": 0.0015,
    "processing_time": 2.3,
    "status": "completed"
  }
}
```

### **📋 4. Memory Operations Protocol**

#### **🧠 Injection Mémoire :**
```json
{
  "message_type": "request",
  "method": "inject_memory",
  "params": {
    "memory_path": "/documents/markdown/file_key",
    "content": "enriched content...",
    "metadata": {
      "content_type": "documentation",
      "analysis_result": {},
      "relationships": []
    },
    "options": {
      "recursive_depth": 3,
      "create_relationships": true
    }
  }
}
```

#### **🔍 Récupération Mémoire :**
```json
{
  "message_type": "request",
  "method": "retrieve_contextual_memories",
  "params": {
    "search_criteria": {
      "keywords": ["architecture", "design"],
      "content_type": "documentation",
      "max_results": 20
    }
  }
}
```

### **📋 5. Partitioning Protocol**

#### **🔧 Requête de Partitioning :**
```json
{
  "message_type": "request",
  "method": "partition_content",
  "params": {
    "file_path": "path/to/file.md",
    "content": "content to partition...",
    "strategy": "adaptive",
    "content_characteristics": {
      "content_type": "documentation",
      "complexity": 0.3
    }
  }
}
```

#### **📊 Réponse de Partitioning :**
```json
{
  "message_type": "response",
  "result": {
    "success": true,
    "strategy_used": "textual",
    "partitions": [
      {
        "block_name": "section_1",
        "block_type": "section",
        "content": "...",
        "metadata": {}
      }
    ],
    "processing_time": 0.15
  }
}
```

---

## 🔧 **Implémentation des Protocoles**

### **📋 1. Message Bus System**

#### **📡 MessageBus :**
```python
class MessageBus:
    """Bus de messages centralisé."""
    
    def __init__(self):
        self.subscribers = defaultdict(list)
        self.message_queue = asyncio.Queue()
        self.active_requests = {}
        
    async def send_request(self, target: str, method: str, params: dict) -> dict:
        """Envoie une requête et attend la réponse."""
        
    async def send_notification(self, target: str, method: str, params: dict):
        """Envoie une notification sans attendre de réponse."""
        
    def subscribe(self, component: str, handler: callable):
        """Abonne un composant aux messages."""
        
    async def process_messages(self):
        """Traite les messages en continu."""
```

#### **📊 Message Handler :**
```python
class MessageHandler:
    """Gestionnaire de messages pour un composant."""
    
    def __init__(self, component_name: str, message_bus: MessageBus):
        self.component_name = component_name
        self.message_bus = message_bus
        self.handlers = {}
        
    def register_handler(self, method: str, handler: callable):
        """Enregistre un handler pour une méthode."""
        
    async def handle_message(self, message: dict) -> dict:
        """Traite un message reçu."""
```

### **📋 2. Protocol Adapters**

#### **🔍 ContentDetectorAdapter :**
```python
class ContentDetectorAdapter:
    """Adaptateur protocole pour ContentTypeDetector."""
    
    def __init__(self, detector: ContentTypeDetector, message_bus: MessageBus):
        self.detector = detector
        self.message_handler = MessageHandler("content_detector", message_bus)
        self._register_handlers()
        
    def _register_handlers(self):
        """Enregistre les handlers de protocole."""
        self.message_handler.register_handler("detect_content_type", self._handle_detect_content_type)
        
    async def _handle_detect_content_type(self, params: dict) -> dict:
        """Handle la détection de type de contenu."""
        try:
            characteristics = self.detector.detect_content_type(
                params["file_path"], 
                params["content"]
            )
            
            return {
                "content_type": characteristics.content_type.value,
                "confidence_score": characteristics.confidence_score,
                "characteristics": asdict(characteristics),
                "recommended_strategy": self._recommend_strategy(characteristics)
            }
        except Exception as e:
            raise ProtocolError(1001, f"Content detection failed: {e}")
```

#### **🤖 AIAnalyzerAdapter :**
```python
class AIAnalyzerAdapter:
    """Adaptateur protocole pour AI Analyzer."""
    
    def __init__(self, analyzer: OpenAIAnalyzer, message_bus: MessageBus):
        self.analyzer = analyzer
        self.message_handler = MessageHandler("ai_analyzer", message_bus)
        self._register_handlers()
        
    async def _handle_analyze_content(self, params: dict) -> dict:
        """Handle l'analyse de contenu."""
        try:
            insights = await self.analyzer.analyze_content(
                params["content"], 
                params["file_path"]
            )
            
            return {
                "ai_insights": asdict(insights),
                "cost": insights.estimated_cost,
                "processing_time": insights.processing_time,
                "status": "completed"
            }
        except Exception as e:
            raise ProtocolError(1002, f"AI analysis failed: {e}")
```

### **📋 3. Error Handling**

#### **⚠️ Protocol Errors :**
```python
class ProtocolError(Exception):
    """Erreur de protocole standardisée."""
    
    def __init__(self, code: int, message: str, data: dict = None):
        self.code = code
        self.message = message
        self.data = data or {}
        super().__init__(f"Protocol Error {code}: {message}")

# Codes d'erreur standardisés
ERROR_CODES = {
    1000: "Generic Protocol Error",
    1001: "Content Detection Error", 
    1002: "AI Analysis Error",
    1003: "Memory Operation Error",
    1004: "Partitioning Error",
    1005: "Communication Timeout",
    1006: "Invalid Message Format",
    1007: "Component Unavailable"
}
```

#### **🔄 Retry Logic :**
```python
class RetryHandler:
    """Gestionnaire de retry avec backoff."""
    
    async def retry_with_backoff(self, operation: callable, max_retries: int = 3) -> any:
        """Retry avec exponential backoff."""
        
        for attempt in range(max_retries):
            try:
                return await operation()
            except ProtocolError as e:
                if attempt == max_retries - 1:
                    raise
                    
                wait_time = 2 ** attempt
                await asyncio.sleep(wait_time)
```

---

## 📊 **Monitoring et Observabilité**

### **📋 Protocol Metrics :**

#### **📈 Métriques Collectées :**
```python
@dataclass
class ProtocolMetrics:
    """Métriques de protocole."""
    
    messages_sent: int = 0
    messages_received: int = 0
    errors_count: int = 0
    average_response_time: float = 0.0
    active_connections: int = 0
    retry_count: int = 0
```

#### **📊 Monitoring Dashboard :**
```python
class ProtocolMonitor:
    """Moniteur de protocoles."""
    
    def __init__(self):
        self.metrics = defaultdict(ProtocolMetrics)
        self.message_log = []
        
    def log_message(self, message: dict):
        """Log un message pour monitoring."""
        
    def get_component_health(self, component: str) -> dict:
        """Retourne la santé d'un composant."""
        
    def generate_health_report(self) -> dict:
        """Génère un rapport de santé global."""
```

---

## 🎯 **Cas d'Usage des Protocoles**

### **📋 Scénario 1 : Analyse Complète de Fichier**

```python
async def analyze_file_with_protocols(daemon: MDDaemonCore, file_path: str, content: str):
    """Analyse complète utilisant les protocoles."""
    
    # 1. Détection de type
    detection_result = await daemon.message_bus.send_request(
        "content_detector", 
        "detect_content_type",
        {"file_path": file_path, "content": content}
    )
    
    # 2. Partitioning adaptatif
    partition_result = await daemon.message_bus.send_request(
        "partitioner",
        "partition_content", 
        {
            "file_path": file_path,
            "content": content,
            "strategy": detection_result["recommended_strategy"]
        }
    )
    
    # 3. Analyse IA
    ai_result = await daemon.message_bus.send_request(
        "ai_analyzer",
        "analyze_content",
        {
            "content": content,
            "file_path": file_path,
            "content_type": detection_result["content_type"]
        }
    )
    
    # 4. Injection mémoire
    memory_result = await daemon.message_bus.send_request(
        "memory_engine",
        "inject_memory",
        {
            "memory_path": f"/documents/{detection_result['content_type']}/{file_path}",
            "content": content,
            "metadata": {
                "detection_result": detection_result,
                "partition_result": partition_result,
                "ai_result": ai_result
            }
        }
    )
```

### **📋 Scénario 2 : Health Check Distribué**

```python
async def distributed_health_check(daemon: MDDaemonCore) -> dict:
    """Health check de tous les composants."""
    
    components = ["content_detector", "ai_analyzer", "memory_engine", "partitioner"]
    health_results = {}
    
    for component in components:
        try:
            result = await daemon.message_bus.send_request(
                component,
                "health_check",
                {},
                timeout=5.0
            )
            health_results[component] = {"status": "healthy", "details": result}
        except Exception as e:
            health_results[component] = {"status": "unhealthy", "error": str(e)}
    
    return health_results
```

---

## 🚀 **Plan d'Implémentation**

### **📋 Phase 1 : Message Bus (Semaine 1)**
1. **MessageBus core** : Bus de messages centralisé
2. **MessageHandler** : Gestionnaires par composant
3. **Protocol errors** : Gestion d'erreurs standardisée
4. **Basic adapters** : Adaptateurs pour composants existants

### **📋 Phase 2 : Protocol Adapters (Semaine 2)**
1. **ContentDetectorAdapter** : Protocole de détection
2. **AIAnalyzerAdapter** : Protocole d'analyse IA
3. **MemoryEngineAdapter** : Protocole mémoire
4. **PartitioningAdapter** : Protocole de partitioning

### **📋 Phase 3 : Advanced Features (Semaine 3)**
1. **Retry logic** : Gestion des échecs
2. **Load balancing** : Répartition de charge
3. **Circuit breaker** : Protection contre les pannes
4. **Rate limiting** : Limitation de débit

### **📋 Phase 4 : Monitoring (Semaine 4)**
1. **Protocol metrics** : Métriques détaillées
2. **Health monitoring** : Surveillance de santé
3. **Performance analytics** : Analyse de performance
4. **Alerting system** : Système d'alertes

---

**⛧ Protocoles de communication mystiques pour une architecture distribuée robuste ! ⛧**

*"La communication structurée révèle l'harmonie cachée entre les composants du système."*
