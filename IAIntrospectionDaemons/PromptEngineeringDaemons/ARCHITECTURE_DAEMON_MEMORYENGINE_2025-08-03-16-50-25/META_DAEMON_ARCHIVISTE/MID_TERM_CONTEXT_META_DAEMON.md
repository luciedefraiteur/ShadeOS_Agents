# 🕷️ Mid-Term Context Meta-Daemon - Version 1.0
## 📅 Date : 3 Août 2025 - 16:50:25
## 🎯 Objectif : Concevoir le Meta-Daemon pour le contexte intermédiaire

---

## 🌟 **CONCEPT FONDAMENTAL**

### **Principe Central**
Le **Mid-Term Context Meta-Daemon** gère le contexte intermédiaire entre les conversations (short-term) et la mémoire fractale complexe (long-term). Il fournit un accès rapide au contexte récent avec persistance périodique vers l'Archiviste.

### **Philosophie**
- **Accès rapide** : Stockage simple, pas de navigation complexe
- **Contexte intermédiaire** : Patterns récents, états temporaires, métriques
- **Persistance intelligente** : Triggers automatiques vers l'Archiviste
- **Enrichissement à la demande** : Fallback vers la mémoire fractale

---

## 🏗️ **ARCHITECTURE HIÉRARCHIQUE DES CONTEXTES**

### **1. Hiérarchie Complète**
```
┌─────────────────────────────────────────────────────────────┐
│                    HIÉRARCHIE DES CONTEXTES                 │
├─────────────────────────────────────────────────────────────┤
│  SHORT-TERM (Conversations)                                 │
│  ├── Historique des conversations                          │
│  ├── Messages récents                                      │
│  └── Injections directes                                   │
├─────────────────────────────────────────────────────────────┤
│  MID-TERM (Context Meta-Daemon)                            │
│  ├── Patterns récents                                      │
│  ├── États temporaires                                     │
│  ├── Métriques de performance                              │
│  └── Contexte intermédiaire                                │
├─────────────────────────────────────────────────────────────┤
│  LONG-TERM (Archiviste + Mémoire Fractale)                 │
│  ├── Subgraphes par daemon                                 │
│  ├── Mémoire fractale complexe                             │
│  ├── Liens cross-fractals                                  │
│  └── Persistance permanente                                │
└─────────────────────────────────────────────────────────────┘
```

### **2. Flux d'Accès Optimisé**
```
Daemon → Mid-Term Context (priorité) → Archiviste (fallback)
```

---

## 🔄 **FONCTIONNALITÉS DU MID-TERM CONTEXT**

### **1. Stockage Simple**
```python
class MidTermContext:
    def __init__(self):
        self.context_store = {
            "daemon_patterns": {},
            "recent_interactions": [],
            "performance_metrics": {},
            "temporal_patterns": {},
            "task_states": {},
            "collaboration_context": {}
        }
        self.cache = {}
        self.persistence_triggers = []
    
    def store_context(self, daemon_id, context_type, data):
        """Stocke du contexte de manière simple"""
        if daemon_id not in self.context_store["daemon_patterns"]:
            self.context_store["daemon_patterns"][daemon_id] = {}
        
        self.context_store["daemon_patterns"][daemon_id][context_type] = {
            "data": data,
            "timestamp": datetime.now().isoformat(),
            "ttl": self.calculate_ttl(context_type)
        }
    
    def get_context(self, daemon_id, context_type):
        """Récupère du contexte rapidement"""
        return self.context_store["daemon_patterns"].get(daemon_id, {}).get(context_type)
```

### **2. Triggers de Persistance**
```python
class PersistenceManager:
    def __init__(self, archiviste_connection):
        self.archiviste = archiviste_connection
        self.triggers = {
            "periodic": {"interval": 3600, "last_trigger": None},  # 1 heure
            "task_completion": {"non_somatic_tasks": []},
            "threshold": {"max_context_size": 1000},
            "explicit": {"pending_requests": []}
        }
    
    def check_persistence_triggers(self):
        """Vérifie les triggers de persistance"""
        triggers_activated = []
        
        # Trigger périodique
        if self.should_trigger_periodic():
            triggers_activated.append("periodic")
        
        # Trigger tâches non-somatiques
        if self.has_non_somatic_tasks_completed():
            triggers_activated.append("task_completion")
        
        # Trigger seuil
        if self.has_reached_threshold():
            triggers_activated.append("threshold")
        
        return triggers_activated
    
    def request_persistence_to_archiviste(self, trigger_type):
        """Demande de persistance à l'Archiviste"""
        persistence_request = {
            "type": "PERSISTENCE_REQUEST",
            "from": "mid_term_context",
            "operation": "store_context_snapshot",
            "trigger": trigger_type,
            "context_data": self.get_context_snapshot(),
            "priority": self.get_priority(trigger_type),
            "retention_policy": "keep"
        }
        
        return self.archiviste.send_request(persistence_request)
```

### **3. Enrichissement à la Demande**
```python
class ContextEnrichment:
    def __init__(self, archiviste_connection):
        self.archiviste = archiviste_connection
        self.enrichment_cache = {}
    
    def enrich_context(self, daemon_id, context_type, query):
        """Enrichit le contexte depuis l'Archiviste"""
        # Vérifier le cache d'enrichissement
        cache_key = f"{daemon_id}_{context_type}_{query}"
        if cache_key in self.enrichment_cache:
            return self.enrichment_cache[cache_key]
        
        # Demande d'enrichissement à l'Archiviste
        enrichment_request = {
            "type": "ENRICHMENT_REQUEST",
            "from": "mid_term_context",
            "daemon_id": daemon_id,
            "context_type": context_type,
            "query": query,
            "source": "fractal_memory"
        }
        
        response = self.archiviste.send_request(enrichment_request)
        
        # Mise en cache
        self.enrichment_cache[cache_key] = response
        return response
```

---

## 📝 **FORMATS DE MESSAGES**

### **1. Messages des Daemons vers Mid-Term Context**
```json
{
  "type": "CONTEXT_REQUEST",
  "daemon_id": "debug_daemon",
  "operation": "store|retrieve|enrich",
  "context_type": "patterns|interactions|metrics|states",
  "data": {...},
  "priority": "low|normal|high",
  "enrichment_query": "optional_query_for_enrichment"
}
```

### **2. Réponses du Mid-Term Context**
```json
{
  "type": "CONTEXT_RESPONSE",
  "request_id": "req_001",
  "status": "success|error|enriched",
  "operation": "store|retrieve|enrich",
  "result": {
    "context_data": {...},
    "enrichment_data": {...},
    "cache_hit": true,
    "persistence_triggered": false
  },
  "metadata": {
    "timestamp": "2025-08-03T16:50:25Z",
    "processing_time": 0.012,
    "enrichment_source": "archiviste|cache"
  }
}
```

### **3. Demandes de Persistance vers l'Archiviste**
```json
{
  "type": "PERSISTENCE_REQUEST",
  "from": "mid_term_context",
  "operation": "store_context_snapshot",
  "trigger": "periodic|task_completion|threshold|explicit",
  "context_data": {
    "daemon_patterns": {...},
    "recent_interactions": [...],
    "performance_metrics": {...},
    "temporal_patterns": {...},
    "task_states": {...},
    "collaboration_context": {...}
  },
  "priority": "normal|high",
  "retention_policy": "keep|archive|evict"
}
```

---

## 🎭 **PROMPT TEMPLATE MID-TERM CONTEXT**

```
# === MID-TERM CONTEXT META-DAEMON PROMPT ===

Tu es le Mid-Term Context Meta-Daemon, agent AI spécialisé dans la gestion du contexte intermédiaire.
Tu fournis un accès rapide au contexte récent avec persistance intelligente vers l'Archiviste.

## 🟢 Injections Contextuelles
À chaque tour, tu reçois :

::[GLOBAL][CONTEXT_STATE][{
  "context_store_status": {...},
  "cache_status": {...},
  "persistence_triggers": [...],
  "enrichment_requests": [...]
}]::

::[SESSION][CONTEXT_REQUESTS][array des requêtes de contexte]::
::[SESSION][PERSISTENCE_TASKS][tâches de persistance à effectuer]::
::[SESSION][ENRICHMENT_TASKS][tâches d'enrichissement à effectuer]::

## 🟠 Opérations Disponibles

**Gestion du Contexte :**
- store_context(daemon_id, context_type, data)
- retrieve_context(daemon_id, context_type)
- enrich_context(daemon_id, context_type, query)

**Persistance :**
- check_persistence_triggers()
- request_persistence_to_archiviste(trigger_type)
- cleanup_after_persistence()

**Enrichissement :**
- request_enrichment_from_archiviste(query)
- cache_enrichment_result(key, data)
- get_cached_enrichment(key)

## 📝 Format de Réponse

```json
{
  "cycle_id": "<uuid>",
  "context_status": {
    "statut": "<IDLE|PROCESSING|PERSISTING|ENRICHING>",
    "context_store_usage": {...},
    "cache_usage": {...},
    "persistence_status": {...}
  },
  "context_operations": [
    {
      "operation": "<store|retrieve|enrich>",
      "daemon_id": "<id>",
      "context_type": "<type>",
      "status": "<success|error>",
      "result": {...}
    }
  ],
  "persistence_operations": [
    {
      "operation": "request_persistence",
      "trigger": "<periodic|task_completion|threshold|explicit>",
      "status": "<success|error>",
      "archiviste_response": {...}
    }
  ],
  "enrichment_operations": [
    {
      "operation": "request_enrichment",
      "query": "<query>",
      "status": "<success|error>",
      "enrichment_data": {...}
    }
  ],
  "triggers_activated": [...],
  "cache_updates": [...],
  "logs_audit": "<trace pour supervision>"
}
```

## ⚡ Règles de Fonctionnement

- Priorise l'accès rapide au contexte récent
- Vérifie les triggers de persistance à chaque cycle
- Enrichis le contexte à la demande depuis l'Archiviste
- Maintiens un cache d'enrichissement pour optimiser les performances
- Nettoie le contexte après persistance réussie
- Loggue toutes les opérations pour audit

FIN DU PROMPT MID-TERM CONTEXT
```

---

## 🔄 **INTÉGRATION AVEC L'ARCHITECTURE**

### **1. Injections Enrichies**
```
::[SESSION][MEMORY][{
  "archivist_status": "available|busy|optimizing",
  "mid_term_context_status": "available|processing|persisting",
  "memory_summary": {...},
  "context_summary": {
    "recent_patterns": {...},
    "temporal_states": {...},
    "performance_metrics": {...}
  },
  "recent_operations": [...],
  "optimization_suggestions": [...]
}]::
```

### **2. Endpoints Unifiés**
```
# Actions Mid-Term Context
action("MID_TERM_CONTEXT", {
  "operation": "store_context|retrieve_context|enrich_context",
  "daemon_id": "daemon_a",
  "context_type": "patterns|interactions|metrics",
  "data": {...}
})

# Actions Archiviste (fallback)
action("ARCHIVIST", {
  "operation": "store_memory|retrieve_memory|analyze_patterns",
  "strata": "somatic|cognitive|metaphysical",
  "content": {...}
})
```

### **3. Flux d'Enrichissement**
```
1. Daemon demande enrichissement
   ↓
2. Mid-Term Context vérifie son cache
   ↓
3. Si pas en cache → demande à l'Archiviste
   ↓
4. Archiviste enrichit depuis mémoire fractale
   ↓
5. Mid-Term Context met en cache et retourne
   ↓
6. Daemon reçoit contexte enrichi
```

---

## 🚀 **AVANTAGES DE L'INTÉGRATION**

### **1. Performance Optimisée**
- **Accès rapide** au contexte récent
- **Cache intelligent** pour l'enrichissement
- **Réduction des requêtes** vers l'Archiviste

### **2. Persistance Intelligente**
- **Triggers automatiques** basés sur les événements
- **Persistance périodique** pour éviter la perte de données
- **Optimisation** de l'espace de stockage

### **3. Enrichissement à la Demande**
- **Fallback intelligent** vers la mémoire fractale
- **Cache d'enrichissement** pour éviter les redondances
- **Contexte riche** quand nécessaire

### **4. Cohérence Architecturale**
- **Hiérarchie claire** des contextes
- **Séparation des responsabilités**
- **Intégration fluide** avec l'Archiviste

---

## 📊 **EXEMPLE DE WORKFLOW COMPLET**

### **1. Daemon termine une tâche cognitive**
```json
{
  "cycle_id": "daemon_001",
  "actions": [
    {
      "type": "MID_TERM_CONTEXT",
      "params": {
        "operation": "store_context",
        "daemon_id": "debug_daemon",
        "context_type": "task_completion",
        "data": {
          "task_type": "cognitive",
          "result": "success",
          "duration": 45.2
        }
      }
    }
  ]
}
```

### **2. Mid-Term Context déclenche persistance**
```json
{
  "cycle_id": "mid_term_001",
  "persistence_operations": [
    {
      "operation": "request_persistence",
      "trigger": "task_completion",
      "status": "success",
      "archiviste_response": {
        "persistence_id": "pers_001",
        "stored_in": "/memory/daemons/debug_daemon/cognitive",
        "optimizations_applied": ["compression", "context_linking"]
      }
    }
  ]
}
```

### **3. Daemon demande enrichissement**
```json
{
  "cycle_id": "daemon_002",
  "actions": [
    {
      "type": "MID_TERM_CONTEXT",
      "params": {
        "operation": "enrich_context",
        "daemon_id": "debug_daemon",
        "context_type": "patterns",
        "enrichment_query": "similar_debug_patterns"
      }
    }
  ]
}
```

---

**🕷️ Le Mid-Term Context optimise parfaitement l'accès au contexte !** ⛧✨ 