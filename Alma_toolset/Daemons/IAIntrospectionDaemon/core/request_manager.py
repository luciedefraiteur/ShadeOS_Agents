"""
Gestionnaire de requêtes d'injection contextuelle pour le Daemon Introspectif
Utilise le dictionnaire JSON des requêtes et permet de les lister par type
"""

import json
import re
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass


@dataclass
class RequestInfo:
    """Informations sur une requête d'injection contextuelle"""
    request_type: str
    description: str
    parameters: List[str]
    example: str
    return_type: str
    category: str


class RequestManager:
    """Gestionnaire des requêtes d'injection contextuelle"""
    
    def __init__(self, request_dict_path: str = "prompts/request_dictionary.json"):
        self.request_dict_path = Path(request_dict_path)
        self.request_dictionary = self._load_request_dictionary()
        self.request_pattern = re.compile(r'::([A-Z_]+)::\s*(.*)')
    
    def _load_request_dictionary(self) -> Dict[str, Any]:
        """Charge le dictionnaire des requêtes depuis le fichier JSON"""
        try:
            with open(self.request_dict_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️  Dictionnaire de requêtes non trouvé: {self.request_dict_path}")
            return {"request_types": {}, "metadata": {}}
        except json.JSONDecodeError as e:
            print(f"❌ Erreur de parsing JSON: {e}")
            return {"request_types": {}, "metadata": {}}
    
    def list_requests_by_type(self, request_type: str = None) -> List[RequestInfo]:
        """Liste les requêtes par type ou toutes les requêtes"""
        requests = []
        
        for category, category_data in self.request_dictionary.get("request_types", {}).items():
            if request_type and category != request_type:
                continue
                
            for req_name, req_data in category_data.get("requests", {}).items():
                request_info = RequestInfo(
                    request_type=req_name,
                    description=req_data.get("description", ""),
                    parameters=req_data.get("parameters", []),
                    example=req_data.get("example", ""),
                    return_type=req_data.get("return_type", ""),
                    category=category
                )
                requests.append(request_info)
        
        return requests
    
    def get_request_info(self, request_name: str) -> Optional[RequestInfo]:
        """Récupère les informations d'une requête spécifique"""
        for category, category_data in self.request_dictionary.get("request_types", {}).items():
            if request_name in category_data.get("requests", {}):
                req_data = category_data["requests"][request_name]
                return RequestInfo(
                    request_type=request_name,
                    description=req_data.get("description", ""),
                    parameters=req_data.get("parameters", []),
                    example=req_data.get("example", ""),
                    return_type=req_data.get("return_type", ""),
                    category=category
                )
        return None
    
    def parse_request_from_text(self, text: str) -> List[Tuple[str, List[str]]]:
        """Parse les requêtes depuis un texte"""
        requests = []
        matches = self.request_pattern.findall(text)
        
        for match in matches:
            request_type = match[0]
            params_str = match[1].strip()
            
            # Parse les paramètres
            params = []
            if params_str:
                # Supprime les crochets et divise par virgules
                params_str = params_str.strip('[]')
                if params_str:
                    params = [p.strip() for p in params_str.split(',')]
            
            requests.append((request_type, params))
        
        return requests
    
    def validate_request(self, request_type: str, parameters: List[str]) -> Tuple[bool, str]:
        """Valide une requête et ses paramètres"""
        request_info = self.get_request_info(request_type)
        
        if not request_info:
            return False, f"Type de requête inconnu: {request_type}"
        
        expected_params = request_info.parameters
        actual_params = parameters
        
        if len(actual_params) != len(expected_params):
            return False, f"Nombre de paramètres incorrect. Attendu: {len(expected_params)}, Reçu: {len(actual_params)}"
        
        return True, "Requête valide"
    
    def format_request(self, request_type: str, parameters: List[str] = None) -> str:
        """Formate une requête selon le format standard"""
        if parameters is None:
            parameters = []
        
        if parameters:
            params_str = " ".join(parameters)
            return f"::REQUEST_{request_type}:: {params_str}"
        else:
            return f"::REQUEST_{request_type}::"
    
    def get_available_categories(self) -> List[str]:
        """Retourne la liste des catégories de requêtes disponibles"""
        return list(self.request_dictionary.get("request_types", {}).keys())
    
    def get_category_description(self, category: str) -> str:
        """Récupère la description d'une catégorie"""
        return self.request_dictionary.get("request_types", {}).get(category, {}).get("description", "")
    
    def search_requests(self, search_term: str) -> List[RequestInfo]:
        """Recherche des requêtes par terme"""
        search_term = search_term.lower()
        matching_requests = []
        
        for request_info in self.list_requests_by_type():
            if (search_term in request_info.request_type.lower() or
                search_term in request_info.description.lower() or
                search_term in request_info.category.lower()):
                matching_requests.append(request_info)
        
        return matching_requests
    
    def get_request_examples(self, category: str = None) -> List[str]:
        """Récupère des exemples de requêtes"""
        examples = []
        
        for request_info in self.list_requests_by_type(category):
            if request_info.example:
                examples.append(request_info.example)
        
        return examples
    
    def generate_request_suggestions(self, context: str) -> List[str]:
        """Génère des suggestions de requêtes basées sur un contexte"""
        suggestions = []
        context_lower = context.lower()
        
        # Suggestions basées sur des mots-clés dans le contexte
        keyword_mapping = {
            "mémoire": ["REQUEST_MEMORY_STATISTICS", "REQUEST_MEMORY_NODES", "REQUEST_MEMORY_STRATA_DISTRIBUTION"],
            "outil": ["REQUEST_TOOL_LIST", "REQUEST_TOOL_SCAN_RESULTS", "REQUEST_TOOL_KEYWORDS"],
            "édition": ["REQUEST_EDITING_PARTITION_PATTERNS", "REQUEST_EDITING_NAVIGATION_STATS"],
            "statistique": ["REQUEST_MEMORY_STATISTICS", "REQUEST_EDITING_NAVIGATION_STATS"],
            "mots-clés": ["REQUEST_MEMORY_KEYWORDS", "REQUEST_TOOL_KEYWORDS"],
            "partition": ["REQUEST_EDITING_PARTITION_PATTERNS", "REQUEST_EDITING_PARTITION_SCHEMAS"],
            "lien": ["REQUEST_MEMORY_LINKS", "REQUEST_MEMORY_TRANSCENDENCE_LINKS"],
            "nœud": ["REQUEST_MEMORY_NODE_DETAILS", "REQUEST_MEMORY_CHILDREN"]
        }
        
        for keyword, request_types in keyword_mapping.items():
            if keyword in context_lower:
                for req_type in request_types:
                    request_info = self.get_request_info(req_type)
                    if request_info and request_info.example:
                        suggestions.append(request_info.example)
        
        return list(set(suggestions))  # Supprime les doublons
    
    def get_request_statistics(self) -> Dict[str, Any]:
        """Récupère des statistiques sur les requêtes disponibles"""
        stats = {
            "total_requests": 0,
            "categories": {},
            "parameters_distribution": {},
            "return_types": {}
        }
        
        for category, category_data in self.request_dictionary.get("request_types", {}).items():
            category_requests = len(category_data.get("requests", {}))
            stats["total_requests"] += category_requests
            stats["categories"][category] = category_requests
            
            for req_name, req_data in category_data.get("requests", {}).items():
                # Distribution des paramètres
                param_count = len(req_data.get("parameters", []))
                stats["parameters_distribution"][param_count] = stats["parameters_distribution"].get(param_count, 0) + 1
                
                # Types de retour
                return_type = req_data.get("return_type", "unknown")
                stats["return_types"][return_type] = stats["return_types"].get(return_type, 0) + 1
        
        return stats 