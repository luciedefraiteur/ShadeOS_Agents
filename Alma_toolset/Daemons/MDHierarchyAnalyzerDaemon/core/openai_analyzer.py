#!/usr/bin/env python3
"""
🤖 OpenAI Analyzer pour MD Daemon

Analyseur intelligent utilisant OpenAI avec chargement automatique .env
et gestion intelligente du budget.

Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import os
import sys
import json
import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path

# Ajout du path pour les imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import de la logique de chargement .env d'Alma
try:
    from ....load_env import EnvLoader
except ImportError:
    try:
        from load_env import EnvLoader
    except ImportError:
        # Fallback si load_env n'est pas disponible
        class EnvLoader:
            @staticmethod
            def load_env():
                import os
                from pathlib import Path
                env_file = Path.home() / '.env'
                if env_file.exists():
                    with open(env_file) as f:
                        for line in f:
                            if '=' in line and not line.startswith('#'):
                                key, value = line.strip().split('=', 1)
                                os.environ[key] = value


@dataclass
class AIInsights:
    """Insights générés par OpenAI."""
    
    classification: Dict[str, str]
    semantic_tags: List[str]
    summary: str
    importance_score: float
    complexity_level: str
    domain: str
    key_concepts: List[str]
    relationships: List[str]
    quality_score: float
    recommendations: List[str]
    estimated_cost: float
    processing_time: float
    model_used: str


@dataclass
class CostTracker:
    """Tracker des coûts OpenAI."""
    
    total_cost: float = 0.0
    daily_cost: float = 0.0
    hourly_cost: float = 0.0
    last_reset_hour: int = 0
    last_reset_day: str = ""
    requests_count: int = 0
    tokens_used: int = 0


class OpenAIAnalyzer:
    """Analyseur intelligent utilisant OpenAI avec fallback Ollama."""

    def __init__(self, budget_per_hour: float = 2.0, budget_per_day: float = 20.0,
                 use_ollama_fallback: bool = True, ollama_model: str = "qwen2.5:7b-instruct",
                 force_ollama: bool = False):
        self.budget_per_hour = budget_per_hour
        self.budget_per_day = budget_per_day
        self.use_ollama_fallback = use_ollama_fallback
        self.ollama_model = ollama_model
        self.force_ollama = force_ollama

        # Chargement automatique de l'environnement
        self._load_environment()

        # Initialisation conditionnelle selon force_ollama
        if self.force_ollama:
            print("🦙 Force Ollama mode enabled - skipping OpenAI initialization")
            self.openai_available = False
            self.client = None
        else:
            # Initialisation OpenAI
            self._initialize_openai()

        # Initialisation Ollama
        self._initialize_ollama()

        # Tracker des coûts
        self.cost_tracker = CostTracker()
        self._reset_cost_trackers()

        # Configuration des modèles
        self.models = {
            'fast': 'gpt-3.5-turbo',
            'smart': 'gpt-4o-mini',
            'premium': 'gpt-4o'
        }

        # Coûts par modèle (par 1K tokens)
        self.model_costs = {
            'gpt-3.5-turbo': {'input': 0.0015, 'output': 0.002},
            'gpt-4o-mini': {'input': 0.00015, 'output': 0.0006},
            'gpt-4o': {'input': 0.005, 'output': 0.015}
        }
    
    def _load_environment(self):
        """Charge automatiquement les variables d'environnement."""
        
        try:
            print("🤖 Loading environment variables for OpenAI...")
            
            # Utilisation de la logique d'Alma
            loader = EnvLoader()
            loaded_count = loader.load_to_os_environ(overwrite=False)
            
            print(f"✅ Loaded {loaded_count} environment variables")
            
            # Vérification de la clé OpenAI
            if not os.environ.get('OPENAI_API_KEY'):
                print("⚠️ OPENAI_API_KEY not found in environment")
                print("💡 Make sure your ~/.env file contains: OPENAI_API_KEY=your_key_here")
                self.openai_available = False
            else:
                key = os.environ.get('OPENAI_API_KEY')
                masked_key = f"{key[:8]}...{key[-4:]}" if len(key) > 12 else "***"
                print(f"🔑 OpenAI API Key loaded: {masked_key}")
                self.openai_available = True
                
        except Exception as e:
            print(f"❌ Error loading environment: {e}")
            self.openai_available = False
    
    def _initialize_openai(self):
        """Initialise le client OpenAI."""
        
        if not self.openai_available:
            print("⚠️ OpenAI not available - running in simulation mode")
            self.client = None
            return
        
        try:
            # Import dynamique d'OpenAI
            import openai
            
            # Configuration du client
            self.client = openai.OpenAI(
                api_key=os.environ.get('OPENAI_API_KEY')
            )
            
            print("✅ OpenAI client initialized successfully")
            
        except ImportError:
            print("⚠️ OpenAI package not installed - running in simulation mode")
            print("💡 Install with: pip install openai")
            self.openai_available = False
            self.client = None
            
        except Exception as e:
            print(f"❌ Error initializing OpenAI: {e}")
            self.openai_available = False
            self.client = None

    def _initialize_ollama(self):
        """Initialise le client Ollama."""

        if not self.use_ollama_fallback:
            print("🦙 Ollama fallback disabled")
            self.ollama_available = False
            self.ollama_client = None
            return

        try:
            # Test de disponibilité d'Ollama
            import subprocess
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=5)

            if result.returncode == 0:
                # Vérification du modèle
                if self.ollama_model in result.stdout:
                    print(f"🦙 Ollama available with model: {self.ollama_model}")
                    self.ollama_available = True
                else:
                    print(f"🦙 Ollama available but model {self.ollama_model} not found")
                    print(f"💡 Run: ollama pull {self.ollama_model}")
                    self.ollama_available = False
            else:
                print("🦙 Ollama not available")
                self.ollama_available = False

        except subprocess.TimeoutExpired:
            print("🦙 Ollama check timeout")
            self.ollama_available = False
        except FileNotFoundError:
            print("🦙 Ollama not installed")
            print("💡 Install from: https://ollama.ai")
            self.ollama_available = False
        except Exception as e:
            print(f"🦙 Ollama check failed: {e}")
            self.ollama_available = False
    
    def _reset_cost_trackers(self):
        """Reset les trackers de coût selon l'heure/jour."""
        
        now = datetime.now()
        current_hour = now.hour
        current_day = now.strftime('%Y-%m-%d')
        
        # Reset hourly
        if current_hour != self.cost_tracker.last_reset_hour:
            self.cost_tracker.hourly_cost = 0.0
            self.cost_tracker.last_reset_hour = current_hour
        
        # Reset daily
        if current_day != self.cost_tracker.last_reset_day:
            self.cost_tracker.daily_cost = 0.0
            self.cost_tracker.last_reset_day = current_day
    
    def can_afford_analysis(self, content: str, model: str = 'fast') -> bool:
        """Vérifie si l'analyse est dans le budget."""
        
        self._reset_cost_trackers()
        
        # Estimation du coût
        estimated_cost = self._estimate_cost(content, model)
        
        # Vérifications budgétaires
        if self.cost_tracker.hourly_cost + estimated_cost > self.budget_per_hour:
            print(f"💰 Hourly budget exceeded: {self.cost_tracker.hourly_cost:.4f} + {estimated_cost:.4f} > {self.budget_per_hour}")
            return False
        
        if self.cost_tracker.daily_cost + estimated_cost > self.budget_per_day:
            print(f"💰 Daily budget exceeded: {self.cost_tracker.daily_cost:.4f} + {estimated_cost:.4f} > {self.budget_per_day}")
            return False
        
        return True
    
    def _estimate_cost(self, content: str, model: str) -> float:
        """Estime le coût d'une analyse."""
        
        # Estimation des tokens (approximative)
        input_tokens = len(content) // 4  # Approximation
        output_tokens = 200  # Estimation pour la réponse
        
        if model not in self.model_costs:
            model = 'gpt-3.5-turbo'  # Fallback
        
        costs = self.model_costs[model]
        
        input_cost = (input_tokens / 1000) * costs['input']
        output_cost = (output_tokens / 1000) * costs['output']
        
        return input_cost + output_cost
    
    async def analyze_content(self, content: str, file_path: str = "") -> AIInsights:
        """Analyse complète du contenu."""
        
        start_time = time.time()
        
        # Sélection du modèle selon la taille
        if len(content) > 10000:
            model = 'fast'  # Gros contenu = modèle rapide
        elif len(content) > 5000:
            model = 'smart'  # Contenu moyen = modèle équilibré
        else:
            model = 'fast'  # Petit contenu = modèle rapide
        
        # Vérification du budget
        if not self.can_afford_analysis(content, model):
            return await self._simulate_analysis(content, "budget_exceeded")
        
        # Cascade d'analyse : Force Ollama → OpenAI → Ollama → Simulation
        if self.force_ollama and self.ollama_available:
            print("🦙 Force Ollama mode: using Ollama directly")
            return await self._ollama_analysis(content, file_path)
        elif self.openai_available and self.client:
            return await self._real_analysis(content, file_path, model)
        elif self.ollama_available:
            return await self._ollama_analysis(content, file_path)
        else:
            return await self._simulate_analysis(content, "no_ai_available")
    
    async def _real_analysis(self, content: str, file_path: str, model: str) -> AIInsights:
        """Analyse réelle avec OpenAI."""
        
        start_time = time.time()
        
        try:
            # Prompt pour l'analyse complète
            prompt = self._create_analysis_prompt(content, file_path)
            
            # Appel à OpenAI
            response = self.client.chat.completions.create(
                model=self.models[model],
                messages=[
                    {"role": "system", "content": "You are an expert document analyzer. Analyze the provided Markdown document and return a structured JSON response."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            # Parsing de la réponse
            response_text = response.choices[0].message.content
            analysis_data = self._parse_openai_response(response_text)
            
            # Calcul du coût réel
            usage = response.usage
            actual_cost = self._calculate_actual_cost(usage, model)
            
            # Mise à jour des trackers
            self._update_cost_trackers(actual_cost, usage.total_tokens)
            
            processing_time = time.time() - start_time
            
            return AIInsights(
                classification=analysis_data.get('classification', {}),
                semantic_tags=analysis_data.get('semantic_tags', []),
                summary=analysis_data.get('summary', ''),
                importance_score=analysis_data.get('importance_score', 50.0),
                complexity_level=analysis_data.get('complexity_level', 'medium'),
                domain=analysis_data.get('domain', 'general'),
                key_concepts=analysis_data.get('key_concepts', []),
                relationships=analysis_data.get('relationships', []),
                quality_score=analysis_data.get('quality_score', 70.0),
                recommendations=analysis_data.get('recommendations', []),
                estimated_cost=actual_cost,
                processing_time=processing_time,
                model_used=self.models[model]
            )
            
        except Exception as e:
            print(f"❌ OpenAI analysis failed: {e}")
            # Fallback vers Ollama si disponible
            if self.ollama_available:
                print("🦙 Falling back to Ollama...")
                return await self._ollama_analysis(content, file_path)
            else:
                return await self._simulate_analysis(content, f"openai_error: {e}")

    async def _ollama_analysis(self, content: str, file_path: str) -> AIInsights:
        """Analyse avec Ollama (local)."""

        start_time = time.time()

        try:
            # Prompt pour Ollama
            prompt = self._create_ollama_prompt(content, file_path)

            # Appel à Ollama via subprocess
            import subprocess
            import json

            # Commande Ollama
            cmd = [
                'ollama', 'run', self.ollama_model,
                prompt
            ]

            print(f"🦙 Running Ollama {self.ollama_model}...")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30  # Timeout de 30 secondes
            )

            if result.returncode == 0:
                response_text = result.stdout.strip()
                analysis_data = self._parse_ollama_response(response_text)

                processing_time = time.time() - start_time

                return AIInsights(
                    classification=analysis_data.get('classification', {}),
                    semantic_tags=analysis_data.get('semantic_tags', []),
                    summary=analysis_data.get('summary', ''),
                    importance_score=analysis_data.get('importance_score', 50.0),
                    complexity_level=analysis_data.get('complexity_level', 'medium'),
                    domain=analysis_data.get('domain', 'general'),
                    key_concepts=analysis_data.get('key_concepts', []),
                    relationships=analysis_data.get('relationships', []),
                    quality_score=analysis_data.get('quality_score', 70.0),
                    recommendations=analysis_data.get('recommendations', []),
                    estimated_cost=0.0,  # Ollama est gratuit
                    processing_time=processing_time,
                    model_used=f"ollama:{self.ollama_model}"
                )
            else:
                print(f"🦙 Ollama error: {result.stderr}")
                return await self._simulate_analysis(content, f"ollama_error: {result.stderr}")

        except subprocess.TimeoutExpired:
            print("🦙 Ollama timeout")
            return await self._simulate_analysis(content, "ollama_timeout")
        except Exception as e:
            print(f"🦙 Ollama analysis failed: {e}")
            return await self._simulate_analysis(content, f"ollama_error: {e}")
    
    async def _simulate_analysis(self, content: str, reason: str) -> AIInsights:
        """Analyse simulée quand OpenAI n'est pas disponible."""
        
        start_time = time.time()
        
        # Simulation basique
        await asyncio.sleep(0.1)  # Simule le temps d'API
        
        # Analyse basique du contenu
        words = content.split()
        
        # Classification simulée
        classification = {
            'type': 'documentation',
            'level': 'intermediate' if len(words) > 500 else 'basic',
            'domain': 'technical' if any(word in content.lower() for word in ['code', 'function', 'class', 'api']) else 'general',
            'priority': 'medium',
            'status': 'active'
        }
        
        # Tags simulés
        semantic_tags = []
        if 'plan' in content.lower():
            semantic_tags.append('planning')
        if 'architecture' in content.lower():
            semantic_tags.append('architecture')
        if 'implementation' in content.lower():
            semantic_tags.append('implementation')
        if not semantic_tags:
            semantic_tags = ['documentation', 'markdown']
        
        processing_time = time.time() - start_time
        
        return AIInsights(
            classification=classification,
            semantic_tags=semantic_tags,
            summary=content[:200] + "..." if len(content) > 200 else content,
            importance_score=min(100, len(words) / 10),
            complexity_level=classification['level'],
            domain=classification['domain'],
            key_concepts=semantic_tags,
            relationships=[],
            quality_score=70.0,
            recommendations=[f"Simulated analysis - {reason}"],
            estimated_cost=0.0,
            processing_time=processing_time,
            model_used="simulation"
        )
    
    def _create_analysis_prompt(self, content: str, file_path: str) -> str:
        """Crée le prompt pour l'analyse OpenAI."""
        
        return f"""Analyze this Markdown document and provide a structured analysis in JSON format.

File: {file_path}
Content length: {len(content)} characters

Document content:
{content[:3000]}{"..." if len(content) > 3000 else ""}

Please provide a JSON response with these fields:
- classification: {{type, level, domain, priority, status}}
- semantic_tags: [list of relevant tags]
- summary: brief summary (max 200 chars)
- importance_score: 0-100 score
- complexity_level: basic/intermediate/advanced
- domain: main domain/category
- key_concepts: [main concepts discussed]
- relationships: [related topics/documents]
- quality_score: 0-100 quality assessment
- recommendations: [improvement suggestions]

Focus on technical accuracy and practical insights."""

    def _create_ollama_prompt(self, content: str, file_path: str) -> str:
        """Crée le prompt pour l'analyse Ollama."""

        return f"""Analyze this Markdown document and provide a structured analysis.

File: {file_path}
Content length: {len(content)} characters

Document content:
{content[:2000]}{"..." if len(content) > 2000 else ""}

Please analyze this document and provide:
1. Classification (type, level, domain, priority, status)
2. Semantic tags (relevant keywords)
3. Brief summary (max 200 characters)
4. Importance score (0-100)
5. Complexity level (basic/intermediate/advanced)
6. Main domain/category
7. Key concepts discussed
8. Quality assessment (0-100)

Respond in a structured format that can be parsed."""

    def _parse_ollama_response(self, response_text: str) -> Dict:
        """Parse la réponse Ollama."""

        try:
            # Tentative de parsing JSON si présent
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                import json
                return json.loads(json_match.group())
        except:
            pass

        # Parsing textuel basique
        analysis = {
            'classification': {'type': 'document', 'level': 'intermediate', 'domain': 'general'},
            'semantic_tags': [],
            'summary': '',
            'importance_score': 50.0,
            'complexity_level': 'medium',
            'domain': 'general',
            'key_concepts': [],
            'relationships': [],
            'quality_score': 70.0,
            'recommendations': ['Analyzed with Ollama']
        }

        # Extraction basique depuis le texte
        lines = response_text.lower().split('\n')

        for line in lines:
            if 'summary' in line and ':' in line:
                summary = line.split(':', 1)[1].strip()
                analysis['summary'] = summary[:200]
            elif 'importance' in line and any(char.isdigit() for char in line):
                import re
                numbers = re.findall(r'\d+', line)
                if numbers:
                    analysis['importance_score'] = min(100, float(numbers[0]))
            elif 'domain' in line and ':' in line:
                domain = line.split(':', 1)[1].strip()
                analysis['domain'] = domain[:50]
            elif 'tags' in line and ':' in line:
                tags_text = line.split(':', 1)[1].strip()
                tags = [tag.strip() for tag in tags_text.split(',')]
                analysis['semantic_tags'] = tags[:10]

        # Fallback summary
        if not analysis['summary']:
            analysis['summary'] = response_text[:200] + "..." if len(response_text) > 200 else response_text

        return analysis
    
    def _parse_openai_response(self, response_text: str) -> Dict:
        """Parse la réponse OpenAI."""
        
        try:
            # Tentative de parsing JSON direct
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Extraction du JSON depuis le texte
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass
            
            # Fallback : analyse basique
            return {
                'classification': {'type': 'document', 'level': 'unknown'},
                'semantic_tags': ['analyzed'],
                'summary': 'OpenAI analysis completed',
                'importance_score': 50.0,
                'complexity_level': 'medium',
                'domain': 'general',
                'key_concepts': [],
                'relationships': [],
                'quality_score': 70.0,
                'recommendations': ['Response parsing failed']
            }
    
    def _calculate_actual_cost(self, usage, model: str) -> float:
        """Calcule le coût réel basé sur l'usage."""
        
        if model not in self.model_costs:
            model = 'gpt-3.5-turbo'
        
        costs = self.model_costs[model]
        
        input_cost = (usage.prompt_tokens / 1000) * costs['input']
        output_cost = (usage.completion_tokens / 1000) * costs['output']
        
        return input_cost + output_cost
    
    def _update_cost_trackers(self, cost: float, tokens: int):
        """Met à jour les trackers de coût."""
        
        self.cost_tracker.total_cost += cost
        self.cost_tracker.daily_cost += cost
        self.cost_tracker.hourly_cost += cost
        self.cost_tracker.requests_count += 1
        self.cost_tracker.tokens_used += tokens
        
        print(f"💰 Cost: ${cost:.4f} | Daily: ${self.cost_tracker.daily_cost:.4f}/{self.budget_per_day} | Hourly: ${self.cost_tracker.hourly_cost:.4f}/{self.budget_per_hour}")
    
    def get_cost_summary(self) -> Dict:
        """Retourne un résumé des coûts."""
        
        self._reset_cost_trackers()
        
        return {
            'total_cost': self.cost_tracker.total_cost,
            'daily_cost': self.cost_tracker.daily_cost,
            'hourly_cost': self.cost_tracker.hourly_cost,
            'daily_budget': self.budget_per_day,
            'hourly_budget': self.budget_per_hour,
            'requests_count': self.cost_tracker.requests_count,
            'tokens_used': self.cost_tracker.tokens_used,
            'daily_remaining': self.budget_per_day - self.cost_tracker.daily_cost,
            'hourly_remaining': self.budget_per_hour - self.cost_tracker.hourly_cost
        }


async def test_analyzer():
    """Test de l'analyseur OpenAI avec fallback Ollama."""

    print("🧪 Testing AI Analyzer (OpenAI + Ollama fallback)...")

    # Test avec force Ollama si argument fourni
    import sys
    force_ollama = "--force-ollama" in sys.argv

    analyzer = OpenAIAnalyzer(
        budget_per_hour=1.0,
        budget_per_day=5.0,
        use_ollama_fallback=True,
        ollama_model="mistral",
        force_ollama=force_ollama
    )
    
    # Test content
    test_content = """
# Test Document

This is a test document for analyzing with OpenAI.
It contains some technical content about software architecture.

## Features
- Document analysis
- AI integration
- Cost management

The system should be able to classify this document appropriately.
"""
    
    # Analyse
    insights = await analyzer.analyze_content(test_content, "test.md")
    
    print("\n📊 Analysis Results:")
    print(f"  🏷️ Classification: {insights.classification}")
    print(f"  🔖 Tags: {insights.semantic_tags}")
    print(f"  📝 Summary: {insights.summary}")
    print(f"  ⭐ Importance: {insights.importance_score}")
    print(f"  🎯 Domain: {insights.domain}")
    print(f"  💰 Cost: ${insights.estimated_cost:.4f}")
    print(f"  ⏱️ Time: {insights.processing_time:.3f}s")
    print(f"  🤖 Model: {insights.model_used}")
    
    # Résumé des coûts
    cost_summary = analyzer.get_cost_summary()
    print(f"\n💰 Cost Summary:")
    print(f"  Daily: ${cost_summary['daily_cost']:.4f} / ${cost_summary['daily_budget']}")
    print(f"  Hourly: ${cost_summary['hourly_cost']:.4f} / ${cost_summary['hourly_budget']}")
    print(f"  Requests: {cost_summary['requests_count']}")


if __name__ == "__main__":
    asyncio.run(test_analyzer())
