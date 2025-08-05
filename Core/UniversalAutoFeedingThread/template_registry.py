# ⛧ Créé par Alma, Architecte Démoniaque ⛧
# 🗄️ TemplateRegistry - Registre de Fragments avec MemoryEngine

import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod

# Import MemoryEngine si disponible
try:
    from MemoryEngine.core.engine import MemoryEngine
    from MemoryEngine.core.initialization import ensure_initialized
    MEMORY_ENGINE_AVAILABLE = True
except ImportError:
    MEMORY_ENGINE_AVAILABLE = False
    print("⚠️ MemoryEngine non disponible - Mode local activé")

@dataclass
class FragmentMetadata:
    """Métadonnées d'un fragment de prompt"""
    fragment_id: str
    thread_type: str
    class_name: str
    fragment_name: str
    file_path: str
    content_length: int
    created_at: float
    last_modified: float
    tags: List[str] = None
    dependencies: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.dependencies is None:
            self.dependencies = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire pour sérialisation"""
        return {
            "fragment_id": self.fragment_id,
            "thread_type": self.thread_type,
            "class_name": self.class_name,
            "fragment_name": self.fragment_name,
            "file_path": self.file_path,
            "content_length": self.content_length,
            "created_at": self.created_at,
            "last_modified": self.last_modified,
            "tags": self.tags,
            "dependencies": self.dependencies
        }

@dataclass
class TemplateFragment:
    """Fragment de template avec contenu et métadonnées"""
    metadata: FragmentMetadata
    content: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire pour sérialisation"""
        return {
            "metadata": self.metadata.to_dict(),
            "content": self.content
        }

class BaseTemplateRegistry(ABC):
    """Registre de base pour les fragments de templates"""
    
    def __init__(self, base_path: str = "Core/Templates"):
        self.base_path = Path(base_path)
        self.fragments: Dict[str, TemplateFragment] = {}
        self.fragment_index: Dict[str, List[str]] = {}  # thread_type -> fragment_ids
        self.class_index: Dict[str, List[str]] = {}     # class_name -> fragment_ids
    
    @abstractmethod
    def load_fragments(self):
        """Charge tous les fragments depuis le système de stockage"""
        pass
    
    @abstractmethod
    def save_fragment(self, fragment: TemplateFragment):
        """Sauvegarde un fragment dans le système de stockage"""
        pass
    
    @abstractmethod
    def get_fragment(self, fragment_id: str) -> Optional[TemplateFragment]:
        """Récupère un fragment par son ID"""
        pass
    
    def discover_fragments(self) -> List[TemplateFragment]:
        """Découvre automatiquement tous les fragments"""
        discovered_fragments = []
        
        fragments_dir = self.base_path / "fragments"
        if not fragments_dir.exists():
            return discovered_fragments
        
        # Parcourir la structure : fragments/{thread_type}/{class_name}/*.prompt
        for thread_type_dir in fragments_dir.iterdir():
            if not thread_type_dir.is_dir():
                continue
            
            thread_type = thread_type_dir.name
            
            for class_dir in thread_type_dir.iterdir():
                if not class_dir.is_dir():
                    continue
                
                class_name = class_dir.name
                
                for prompt_file in class_dir.glob("*.prompt"):
                    fragment_id = f"{thread_type}:{class_name}:{prompt_file.stem}"
                    
                    # Lire le contenu
                    try:
                        with open(prompt_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Créer les métadonnées
                        metadata = FragmentMetadata(
                            fragment_id=fragment_id,
                            thread_type=thread_type,
                            class_name=class_name,
                            fragment_name=prompt_file.stem,
                            file_path=str(prompt_file),
                            content_length=len(content),
                            created_at=prompt_file.stat().st_ctime,
                            last_modified=prompt_file.stat().st_mtime,
                            tags=[thread_type, class_name, "prompt"],
                            dependencies=[]
                        )
                        
                        fragment = TemplateFragment(metadata=metadata, content=content)
                        discovered_fragments.append(fragment)
                        
                    except Exception as e:
                        print(f"⚠️ Erreur lecture fragment {prompt_file}: {e}")
        
        return discovered_fragments
    
    def index_fragments(self, fragments: List[TemplateFragment]):
        """Indexe les fragments pour recherche rapide"""
        self.fragments.clear()
        self.fragment_index.clear()
        self.class_index.clear()
        
        for fragment in fragments:
            fragment_id = fragment.metadata.fragment_id
            thread_type = fragment.metadata.thread_type
            class_name = fragment.metadata.class_name
            
            # Stocker le fragment
            self.fragments[fragment_id] = fragment
            
            # Indexer par thread_type
            if thread_type not in self.fragment_index:
                self.fragment_index[thread_type] = []
            self.fragment_index[thread_type].append(fragment_id)
            
            # Indexer par class_name
            if class_name not in self.class_index:
                self.class_index[class_name] = []
            self.class_index[class_name].append(fragment_id)
    
    def get_fragments_by_thread_type(self, thread_type: str) -> List[TemplateFragment]:
        """Récupère tous les fragments d'un type de thread"""
        fragment_ids = self.fragment_index.get(thread_type, [])
        return [self.fragments[fid] for fid in fragment_ids if fid in self.fragments]
    
    def get_fragments_by_class(self, class_name: str) -> List[TemplateFragment]:
        """Récupère tous les fragments d'une classe"""
        fragment_ids = self.class_index.get(class_name, [])
        return [self.fragments[fid] for fid in fragment_ids if fid in self.fragments]
    
    def search_fragments(self, query: str) -> List[TemplateFragment]:
        """Recherche des fragments par contenu ou tags"""
        results = []
        query_lower = query.lower()
        
        for fragment in self.fragments.values():
            # Recherche dans le contenu
            if query_lower in fragment.content.lower():
                results.append(fragment)
                continue
            
            # Recherche dans les tags
            for tag in fragment.metadata.tags:
                if query_lower in tag.lower():
                    results.append(fragment)
                    break
            
            # Recherche dans le nom
            if query_lower in fragment.metadata.fragment_name.lower():
                results.append(fragment)
        
        return results
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques du registre"""
        return {
            "total_fragments": len(self.fragments),
            "thread_types": list(self.fragment_index.keys()),
            "classes": list(self.class_index.keys()),
            "fragments_per_thread_type": {
                thread_type: len(fragment_ids) 
                for thread_type, fragment_ids in self.fragment_index.items()
            },
            "fragments_per_class": {
                class_name: len(fragment_ids) 
                for class_name, fragment_ids in self.class_index.items()
            }
        }

class LocalTemplateRegistry(BaseTemplateRegistry):
    """Registre local pour les fragments de templates"""
    
    def __init__(self, base_path: str = "Core/Templates"):
        super().__init__(base_path)
        self.registry_file = self.base_path / "local_registry.json"
        self.load_fragments()
    
    def load_fragments(self):
        """Charge tous les fragments depuis le système de fichiers"""
        # Découvrir les fragments
        discovered_fragments = self.discover_fragments()
        
        # Charger depuis le registre local si disponible
        if self.registry_file.exists():
            try:
                with open(self.registry_file, 'r', encoding='utf-8') as f:
                    registry_data = json.load(f)
                
                # Fusionner avec les fragments découverts
                for fragment_data in registry_data.get("fragments", []):
                    metadata = FragmentMetadata(**fragment_data["metadata"])
                    fragment = TemplateFragment(
                        metadata=metadata,
                        content=fragment_data["content"]
                    )
                    discovered_fragments.append(fragment)
                    
            except Exception as e:
                print(f"⚠️ Erreur chargement registre local: {e}")
        
        # Indexer les fragments
        self.index_fragments(discovered_fragments)
        
        # Sauvegarder le registre
        self.save_registry()
    
    def save_fragment(self, fragment: TemplateFragment):
        """Sauvegarde un fragment dans le système de fichiers"""
        # Sauvegarder le fichier
        file_path = Path(fragment.metadata.file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fragment.content)
        
        # Mettre à jour les métadonnées
        fragment.metadata.last_modified = time.time()
        fragment.metadata.content_length = len(fragment.content)
        
        # Ajouter au registre
        self.fragments[fragment.metadata.fragment_id] = fragment
        
        # Mettre à jour les index
        thread_type = fragment.metadata.thread_type
        class_name = fragment.metadata.class_name
        
        if thread_type not in self.fragment_index:
            self.fragment_index[thread_type] = []
        if fragment.metadata.fragment_id not in self.fragment_index[thread_type]:
            self.fragment_index[thread_type].append(fragment.metadata.fragment_id)
        
        if class_name not in self.class_index:
            self.class_index[class_name] = []
        if fragment.metadata.fragment_id not in self.class_index[class_name]:
            self.class_index[class_name].append(fragment.metadata.fragment_id)
        
        # Sauvegarder le registre
        self.save_registry()
    
    def get_fragment(self, fragment_id: str) -> Optional[TemplateFragment]:
        """Récupère un fragment par son ID"""
        return self.fragments.get(fragment_id)
    
    def save_registry(self):
        """Sauvegarde le registre local"""
        registry_data = {
            "metadata": {
                "description": "Registre local des fragments de templates",
                "created_at": time.time(),
                "total_fragments": len(self.fragments)
            },
            "fragments": [fragment.to_dict() for fragment in self.fragments.values()]
        }
        
        with open(self.registry_file, 'w', encoding='utf-8') as f:
            json.dump(registry_data, f, indent=2, ensure_ascii=False)

class MemoryEngineTemplateRegistry(BaseTemplateRegistry):
    """Registre avec MemoryEngine pour les fragments de templates"""
    
    def __init__(self, base_path: str = "Core/Templates", memory_engine=None):
        super().__init__(base_path)
        
        if not MEMORY_ENGINE_AVAILABLE:
            raise RuntimeError("MemoryEngine non disponible")
        
        self.memory_engine = memory_engine or MemoryEngine()
        self.load_fragments()
    
    def load_fragments(self):
        """Charge tous les fragments depuis MemoryEngine"""
        # Découvrir les fragments du système de fichiers
        discovered_fragments = self.discover_fragments()
        
        # Charger depuis MemoryEngine
        try:
            # Rechercher les fragments dans MemoryEngine
            fragments_data = self.memory_engine.search_memories(
                query="template fragment",
                memory_type="template_fragment",
                limit=1000
            )
            
            for memory in fragments_data:
                try:
                    fragment_data = json.loads(memory.content)
                    metadata = FragmentMetadata(**fragment_data["metadata"])
                    fragment = TemplateFragment(
                        metadata=metadata,
                        content=fragment_data["content"]
                    )
                    discovered_fragments.append(fragment)
                except Exception as e:
                    print(f"⚠️ Erreur parsing fragment MemoryEngine: {e}")
                    
        except Exception as e:
            print(f"⚠️ Erreur chargement MemoryEngine: {e}")
        
        # Indexer les fragments
        self.index_fragments(discovered_fragments)
    
    def save_fragment(self, fragment: TemplateFragment):
        """Sauvegarde un fragment dans MemoryEngine"""
        # Sauvegarder le fichier
        file_path = Path(fragment.metadata.file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fragment.content)
        
        # Mettre à jour les métadonnées
        fragment.metadata.last_modified = time.time()
        fragment.metadata.content_length = len(fragment.content)
        
        # Sauvegarder dans MemoryEngine
        try:
            fragment_data = fragment.to_dict()
            memory_content = json.dumps(fragment_data, ensure_ascii=False)
            
            self.memory_engine.add_memory(
                content=memory_content,
                memory_type="template_fragment",
                metadata={
                    "fragment_id": fragment.metadata.fragment_id,
                    "thread_type": fragment.metadata.thread_type,
                    "class_name": fragment.metadata.class_name,
                    "tags": fragment.metadata.tags
                }
            )
        except Exception as e:
            print(f"⚠️ Erreur sauvegarde MemoryEngine: {e}")
        
        # Ajouter au registre local
        self.fragments[fragment.metadata.fragment_id] = fragment
        
        # Mettre à jour les index
        thread_type = fragment.metadata.thread_type
        class_name = fragment.metadata.class_name
        
        if thread_type not in self.fragment_index:
            self.fragment_index[thread_type] = []
        if fragment.metadata.fragment_id not in self.fragment_index[thread_type]:
            self.fragment_index[thread_type].append(fragment.metadata.fragment_id)
        
        if class_name not in self.class_index:
            self.class_index[class_name] = []
        if fragment.metadata.fragment_id not in self.class_index[class_name]:
            self.class_index[class_name].append(fragment.metadata.fragment_id)
    
    def get_fragment(self, fragment_id: str) -> Optional[TemplateFragment]:
        """Récupère un fragment par son ID depuis MemoryEngine"""
        # D'abord chercher dans le cache local
        if fragment_id in self.fragments:
            return self.fragments[fragment_id]
        
        # Chercher dans MemoryEngine
        try:
            memories = self.memory_engine.search_memories(
                query=fragment_id,
                memory_type="template_fragment",
                limit=1
            )
            
            if memories:
                fragment_data = json.loads(memories[0].content)
                metadata = FragmentMetadata(**fragment_data["metadata"])
                fragment = TemplateFragment(
                    metadata=metadata,
                    content=fragment_data["content"]
                )
                
                # Mettre en cache
                self.fragments[fragment_id] = fragment
                return fragment
                
        except Exception as e:
            print(f"⚠️ Erreur récupération MemoryEngine: {e}")
        
        return None

# Factory pour créer le bon type de registre
def create_template_registry(registry_type: str = "local", **kwargs) -> BaseTemplateRegistry:
    """Crée un registre de templates du type spécifié"""
    if registry_type == "memory_engine" and MEMORY_ENGINE_AVAILABLE:
        return MemoryEngineTemplateRegistry(**kwargs)
    else:
        return LocalTemplateRegistry(**kwargs)

# Test et démonstration
if __name__ == "__main__":
    print("🗄️ TemplateRegistry - Test de Fonctionnalité")
    print("=" * 60)
    
    # Créer un registre local
    registry = create_template_registry("local")
    
    # Afficher les statistiques
    stats = registry.get_registry_stats()
    print(f"📊 Statistiques du registre:")
    print(f"   Total fragments: {stats['total_fragments']}")
    print(f"   Thread types: {stats['thread_types']}")
    print(f"   Classes: {stats['classes']}")
    
    # Rechercher des fragments
    print(f"\n🔍 Recherche de fragments:")
    alma_fragments = registry.search_fragments("alma")
    print(f"   Fragments Alma: {len(alma_fragments)}")
    
    v9_fragments = registry.get_fragments_by_thread_type("v9")
    print(f"   Fragments V9: {len(v9_fragments)}")
    
    legion_fragments = registry.get_fragments_by_class("LegionAutoFeedingThread")
    print(f"   Fragments Legion: {len(legion_fragments)}")
    
    print(f"\n✅ Test TemplateRegistry terminé !") 