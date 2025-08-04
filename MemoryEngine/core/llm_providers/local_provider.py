#!/usr/bin/env python3
"""
⛧ Local Provider - Provider Ollama Local pour l'Archiviste ⛧

Provider Ollama local avec gestion d'erreurs, timeout configurable
et test de connexion robuste.
"""

import asyncio
import time
import subprocess
import json
from typing import Dict, Any, Optional
from .llm_provider import LLMProvider, ProviderStatus, LLMResponse, ProviderType, ErrorType


class LocalProvider(LLMProvider):
    """Provider Ollama local avec validation et gestion d'erreurs"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(ProviderType.LOCAL, config)
        
        # Configuration Ollama spécifique
        self.model = config.get('model', 'qwen2.5:7b-instruct')
        self.ollama_host = config.get('ollama_host', 'http://localhost:11434')
        self.ollama_binary = config.get('ollama_binary', 'ollama')
        
        # Validation du modèle
        if not self.model:
            raise ValueError("Modèle Ollama non spécifié")
    
    async def test_connection(self) -> ProviderStatus:
        """Test de connexion et validation du provider Ollama"""
        start_time = time.time()
        
        try:
            # Test de la commande ollama
            result = await self._execute_with_timeout(
                self._run_ollama_command(['list']),
                self.timeout
            )
            
            # Vérification que le modèle est disponible
            models = result.get('models', [])
            model_found = any(model['name'] == self.model for model in models)
            
            if not model_found:
                return ProviderStatus(
                    valid=False,
                    provider_type=self.provider_type,
                    capabilities=[],
                    error=f"Modèle Ollama '{self.model}' non trouvé. Modèles disponibles: {[m['name'] for m in models]}",
                    error_type=ErrorType.MODEL_UNAVAILABLE,
                    response_time=time.time() - start_time
                )
            
            # Test simple avec le modèle
            test_prompt = "Test de connexion Ollama - Réponds simplement 'OK'"
            test_response = await self._execute_with_timeout(
                self._run_ollama_command(['run', self.model, test_prompt]),
                self.timeout
            )
            
            response_time = time.time() - start_time
            
            return ProviderStatus(
                valid=True,
                provider_type=self.provider_type,
                capabilities=[
                    "text_generation",
                    "chat_completion",
                    "local_inference"
                ],
                response_time=response_time,
                model_info={
                    "model": self.model,
                    "ollama_host": self.ollama_host,
                    "available_models": [m['name'] for m in models],
                    "test_response": test_response
                }
            )
            
        except FileNotFoundError:
            return ProviderStatus(
                valid=False,
                provider_type=self.provider_type,
                capabilities=[],
                error=f"Binaire Ollama non trouvé: {self.ollama_binary}. Installez Ollama depuis https://ollama.ai",
                error_type=ErrorType.UNKNOWN_ERROR,
                response_time=time.time() - start_time
            )
            
        except asyncio.TimeoutError:
            return ProviderStatus(
                valid=False,
                provider_type=self.provider_type,
                capabilities=[],
                error=f"Timeout Ollama après {self.timeout} secondes",
                error_type=ErrorType.TIMEOUT,
                response_time=time.time() - start_time
            )
            
        except subprocess.CalledProcessError as e:
            return ProviderStatus(
                valid=False,
                provider_type=self.provider_type,
                capabilities=[],
                error=f"Erreur Ollama: {e.stderr.decode() if e.stderr else str(e)}",
                error_type=ErrorType.UNKNOWN_ERROR,
                response_time=time.time() - start_time
            )
            
        except Exception as e:
            return ProviderStatus(
                valid=False,
                provider_type=self.provider_type,
                capabilities=[],
                error=f"Erreur Ollama inconnue: {str(e)}",
                error_type=ErrorType.UNKNOWN_ERROR,
                response_time=time.time() - start_time
            )
    
    async def generate_response(self, prompt: str, **kwargs) -> LLMResponse:
        """Génération de réponse avec gestion d'erreurs Ollama"""
        start_time = time.time()
        
        try:
            # Paramètres de génération
            model = kwargs.get('model', self.model)
            temperature = kwargs.get('temperature', self.temperature)
            
            # Construction de la commande
            command = [self.ollama_binary, 'run', model]
            
            # Ajout des paramètres si supportés
            if temperature != 0.7:  # Valeur par défaut
                command.extend(['--temperature', str(temperature)])
            
            # Estimation de la taille du prompt
            prompt_size = self.estimate_prompt_size(prompt) if self.estimate_prompt_size else None
            
            # Génération de la réponse
            response = await self._execute_with_timeout(
                self._run_ollama_command(command, input_text=prompt),
                kwargs.get('timeout', self.timeout)
            )
            
            response_time = time.time() - start_time
            
            return self._create_success_response(
                content=response,
                model_used=model,
                response_time=response_time,
                prompt_size=prompt_size
            )
            
        except asyncio.TimeoutError:
            return self._create_error_response(
                f"Timeout Ollama après {self.timeout} secondes",
                ErrorType.TIMEOUT,
                time.time() - start_time
            )
            
        except subprocess.CalledProcessError as e:
            return self._create_error_response(
                f"Erreur Ollama: {e.stderr.decode() if e.stderr else str(e)}",
                ErrorType.UNKNOWN_ERROR,
                time.time() - start_time
            )
            
        except Exception as e:
            return self._create_error_response(
                f"Erreur Ollama inconnue: {str(e)}",
                ErrorType.UNKNOWN_ERROR,
                time.time() - start_time
            )
    
    async def _run_ollama_command(self, command: list, input_text: str = None) -> str:
        """Exécution d'une commande Ollama"""
        process = await asyncio.create_subprocess_exec(
            *command,
            stdin=asyncio.subprocess.PIPE if input_text else None,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        if input_text:
            stdout, stderr = await process.communicate(input_text.encode())
        else:
            stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise subprocess.CalledProcessError(
                process.returncode, command, stdout, stderr
            )
        
        # Pour la commande 'list', parser le JSON
        if 'list' in command:
            try:
                return json.loads(stdout.decode())
            except json.JSONDecodeError:
                return {"models": []}
        
        # Pour les autres commandes, retourner le texte
        return stdout.decode().strip()
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Informations spécifiques au provider Ollama"""
        base_info = super().get_provider_info()
        base_info.update({
            "model": self.model,
            "ollama_host": self.ollama_host,
            "ollama_binary": self.ollama_binary
        })
        return base_info 