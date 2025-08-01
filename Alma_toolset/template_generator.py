#!/usr/bin/env python3
"""
⛧ Template Generator ⛧
Alma's Mystical Code Weaver

Générateur de fichiers à partir de templates avec variables et logique.
Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import os
import argparse
import sys
import json
import re
from datetime import datetime
from pathlib import Path


def safe_read_file_content(file_path):
    """Lecture sécurisée d'un fichier."""
    try:
        if not os.path.exists(file_path):
            return {"success": False, "error": f"Fichier inexistant: {file_path}"}
        
        if not os.path.isfile(file_path):
            return {"success": False, "error": f"Le chemin n'est pas un fichier: {file_path}"}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {"success": True, "content": content}
    
    except PermissionError:
        return {"success": False, "error": f"Permission refusée: {file_path}"}
    except UnicodeDecodeError:
        return {"success": False, "error": f"Erreur d'encodage: {file_path}"}
    except Exception as e:
        return {"success": False, "error": f"Erreur lecture: {e}"}


def safe_write_file_content(file_path, content, overwrite=False):
    """Écriture sécurisée d'un fichier."""
    try:
        if os.path.exists(file_path) and not overwrite:
            return {"success": False, "error": f"Le fichier existe déjà: {file_path}"}
        
        # Création du répertoire parent si nécessaire
        parent_dir = os.path.dirname(file_path)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {"success": True, "file_path": file_path, "size": len(content)}
    
    except PermissionError:
        return {"success": False, "error": f"Permission refusée: {file_path}"}
    except Exception as e:
        return {"success": False, "error": f"Erreur écriture: {e}"}


class TemplateEngine:
    """Moteur de template simple mais puissant."""
    
    def __init__(self):
        self.variables = {}
        self.functions = {
            'now': lambda: datetime.now().isoformat(),
            'date': lambda: datetime.now().strftime('%Y-%m-%d'),
            'time': lambda: datetime.now().strftime('%H:%M:%S'),
            'year': lambda: str(datetime.now().year),
            'upper': lambda x: str(x).upper(),
            'lower': lambda x: str(x).lower(),
            'title': lambda x: str(x).title(),
            'len': lambda x: len(str(x)),
            'repeat': lambda x, n: str(x) * int(n)
        }
    
    def set_variable(self, name, value):
        """Définit une variable."""
        self.variables[name] = value
    
    def set_variables(self, variables_dict):
        """Définit plusieurs variables."""
        self.variables.update(variables_dict)
    
    def add_function(self, name, func):
        """Ajoute une fonction personnalisée."""
        self.functions[name] = func
    
    def resolve_variable(self, var_name):
        """Résout une variable ou fonction."""
        # Variable simple
        if var_name in self.variables:
            return str(self.variables[var_name])
        
        # Fonction sans paramètres
        if var_name in self.functions:
            try:
                return str(self.functions[var_name]())
            except:
                return f"{{ERROR: {var_name}}}"
        
        # Fonction avec paramètres : func(param1, param2)
        func_match = re.match(r'(\w+)\((.*)\)', var_name)
        if func_match:
            func_name, params_str = func_match.groups()
            if func_name in self.functions:
                try:
                    # Parse des paramètres simples (séparés par virgules)
                    if params_str.strip():
                        params = [p.strip().strip('"\'') for p in params_str.split(',')]
                        # Résolution des variables dans les paramètres
                        resolved_params = []
                        for param in params:
                            if param in self.variables:
                                resolved_params.append(self.variables[param])
                            else:
                                resolved_params.append(param)
                        return str(self.functions[func_name](*resolved_params))
                    else:
                        return str(self.functions[func_name]())
                except Exception as e:
                    return f"{{ERROR: {func_name} - {e}}}"
        
        # Variable non trouvée
        return f"{{UNDEFINED: {var_name}}}"
    
    def process_template(self, template_content):
        """Traite un template et remplace les variables."""
        # Pattern pour {{variable}} ou {{function()}}
        pattern = r'\{\{([^}]+)\}\}'
        
        def replace_var(match):
            var_name = match.group(1).strip()
            return self.resolve_variable(var_name)
        
        # Remplacement des variables
        result = re.sub(pattern, replace_var, template_content)
        
        # Traitement des conditions simples : {{#if variable}}...{{/if}}
        result = self.process_conditionals(result)
        
        # Traitement des boucles simples : {{#each items}}...{{/each}}
        result = self.process_loops(result)
        
        return result
    
    def process_conditionals(self, content):
        """Traite les conditions {{#if}}...{{/if}}."""
        pattern = r'\{\{#if\s+(\w+)\}\}(.*?)\{\{/if\}\}'
        
        def replace_condition(match):
            var_name, block_content = match.groups()
            if var_name in self.variables and self.variables[var_name]:
                return block_content
            return ""
        
        return re.sub(pattern, replace_condition, content, flags=re.DOTALL)
    
    def process_loops(self, content):
        """Traite les boucles {{#each}}...{{/each}}."""
        pattern = r'\{\{#each\s+(\w+)\}\}(.*?)\{\{/each\}\}'
        
        def replace_loop(match):
            var_name, block_content = match.groups()
            if var_name in self.variables:
                items = self.variables[var_name]
                if isinstance(items, (list, tuple)):
                    result = ""
                    for i, item in enumerate(items):
                        # Variables spéciales dans les boucles
                        item_content = block_content
                        item_content = item_content.replace('{{this}}', str(item))
                        item_content = item_content.replace('{{@index}}', str(i))
                        item_content = item_content.replace('{{@first}}', str(i == 0))
                        item_content = item_content.replace('{{@last}}', str(i == len(items) - 1))
                        result += item_content
                    return result
            return ""
        
        return re.sub(pattern, replace_loop, content, flags=re.DOTALL)


def generate_from_template(template_path, output_path, variables=None, overwrite=False):
    """
    Génère un fichier à partir d'un template.
    
    Args:
        template_path: Chemin vers le fichier template
        output_path: Chemin de sortie
        variables: Dictionnaire de variables
        overwrite: Écraser si le fichier existe
    
    Returns:
        Dict avec résultats de la génération
    """
    
    # Lecture du template
    read_result = safe_read_file_content(template_path)
    if not read_result["success"]:
        return {"success": False, "error": f"Template: {read_result['error']}"}
    
    template_content = read_result["content"]
    
    # Initialisation du moteur de template
    engine = TemplateEngine()
    
    # Variables par défaut
    default_vars = {
        'template_name': os.path.basename(template_path),
        'output_name': os.path.basename(output_path),
        'generated_at': datetime.now().isoformat(),
        'generated_by': 'Alma Template Generator'
    }
    
    engine.set_variables(default_vars)
    
    # Variables utilisateur
    if variables:
        engine.set_variables(variables)
    
    # Traitement du template
    try:
        generated_content = engine.process_template(template_content)
    except Exception as e:
        return {"success": False, "error": f"Erreur traitement template: {e}"}
    
    # Écriture du fichier généré
    write_result = safe_write_file_content(output_path, generated_content, overwrite)
    if not write_result["success"]:
        return {"success": False, "error": f"Sortie: {write_result['error']}"}
    
    return {
        "success": True,
        "template_path": template_path,
        "output_path": output_path,
        "template_size": len(template_content),
        "output_size": len(generated_content),
        "variables_used": len(engine.variables),
        "variables": dict(engine.variables)
    }


def create_template_from_file(source_path, template_path, auto_variables=True):
    """
    Crée un template à partir d'un fichier existant.
    
    Args:
        source_path: Fichier source
        template_path: Template à créer
        auto_variables: Détecter automatiquement les variables
    
    Returns:
        Dict avec résultats de la création
    """
    
    # Lecture du fichier source
    read_result = safe_read_file_content(source_path)
    if not read_result["success"]:
        return {"success": False, "error": f"Source: {read_result['error']}"}
    
    content = read_result["content"]
    
    # Détection automatique de variables potentielles
    suggested_vars = []
    if auto_variables:
        # Recherche de patterns communs à templatiser
        patterns = [
            (r'\b\d{4}-\d{2}-\d{2}\b', 'date'),  # Dates
            (r'\b\d{2}:\d{2}:\d{2}\b', 'time'),  # Heures
            (r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b', 'author_name'),  # Noms
            (r'\bversion\s*[=:]\s*["\']?([^"\';\s]+)', 'version'),  # Versions
            (r'\bclass\s+(\w+)', 'class_name'),  # Classes
            (r'\bdef\s+(\w+)', 'function_name'),  # Fonctions
        ]
        
        for pattern, var_name in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                suggested_vars.extend([(match, var_name) for match in matches])
    
    # Création du template avec commentaires
    template_content = f"""{{{{!-- 
Template généré automatiquement par Alma Template Generator
Source: {source_path}
Généré le: {{{{now}}}}

Variables suggérées:
{chr(10).join([f'- {var}: {value}' for value, var in suggested_vars[:10]])}
--}}}}

{content}"""
    
    # Écriture du template
    write_result = safe_write_file_content(template_path, template_content)
    if not write_result["success"]:
        return {"success": False, "error": f"Template: {write_result['error']}"}
    
    return {
        "success": True,
        "source_path": source_path,
        "template_path": template_path,
        "suggested_variables": suggested_vars[:10],  # Limite à 10
        "template_size": len(template_content)
    }


BUILTIN_TEMPLATES = {
    "python_class": '''#!/usr/bin/env python3
"""
{{class_description}}

Créé par {{author}} le {{date}}.
"""

{{#if imports}}
# Imports
{{#each imports}}
import {{this}}
{{/each}}

{{/if}}
class {{class_name}}:
    """{{class_description}}"""
    
    def __init__(self{{#if init_params}}, {{#each init_params}}{{this}}{{#if @last}}{{else}}, {{/if}}{{/each}}{{/if}}):
        """Initialise {{class_name}}."""
        {{#if init_params}}
        {{#each init_params}}
        self.{{this}} = {{this}}
        {{/each}}
        {{else}}
        pass
        {{/if}}
    
    def __str__(self):
        """Représentation string."""
        return f"{{class_name}}({{#if init_params}}{{#each init_params}}{{this}}={{{{self.{{this}}}}}}{{#if @last}}{{else}}, {{/if}}{{/each}}{{/if}})"
    
    {{#if methods}}
    {{#each methods}}
    def {{this}}(self):
        """{{this}} method."""
        pass
    
    {{/each}}
    {{/if}}

if __name__ == "__main__":
    # Test
    obj = {{class_name}}({{#if init_params}}{{#each init_params}}"test_{{this}}"{{#if @last}}{{else}}, {{/if}}{{/each}}{{/if}})
    print(obj)
''',

    "python_script": '''#!/usr/bin/env python3
"""
{{script_description}}

Usage: python3 {{output_name}} [options]

Créé par {{author}} le {{date}}.
"""

import argparse
import sys
{{#if additional_imports}}
{{#each additional_imports}}
import {{this}}
{{/each}}
{{/if}}


def main():
    """Fonction principale."""
    parser = argparse.ArgumentParser(description="{{script_description}}")
    {{#if arguments}}
    {{#each arguments}}
    parser.add_argument("{{this}}", help="{{this}} argument")
    {{/each}}
    {{/if}}
    parser.add_argument("--debug", action="store_true", help="Mode debug")
    
    args = parser.parse_args()
    
    if args.debug:
        print("Mode debug activé")
    
    # TODO: Implémenter la logique principale
    print("{{script_description}} - Version {{version}}")


if __name__ == "__main__":
    main()
''',

    "readme": '''# {{project_name}}

{{project_description}}

## 🚀 Installation

```bash
{{install_command}}
```

## 📖 Usage

```bash
{{usage_command}}
```

## ✨ Fonctionnalités

{{#each features}}
- {{this}}
{{/each}}

## 🔧 Configuration

{{configuration_info}}

## 📝 Licence

{{license}}

## 👤 Auteur

**{{author}}** - {{contact}}

---

*Généré le {{date}} par Alma Template Generator*
'''
}


def format_generation_results(results):
    """Formate les résultats de génération pour affichage."""
    if not results["success"]:
        return f"❌ Erreur: {results['error']}"
    
    output = []
    output.append(f"✅ Fichier généré avec succès !")
    output.append(f"📄 Template: {results['template_path']}")
    output.append(f"📁 Sortie: {results['output_path']}")
    output.append(f"📊 Taille: {results['template_size']} → {results['output_size']} bytes")
    output.append(f"🔧 Variables: {results['variables_used']}")
    
    if results.get('variables'):
        output.append(f"📋 Variables utilisées:")
        for name, value in list(results['variables'].items())[:5]:  # Limite à 5
            output.append(f"  {name}: {value}")
        if len(results['variables']) > 5:
            output.append(f"  ... et {len(results['variables']) - 5} autres")
    
    return "\n".join(output)


def main():
    """Interface en ligne de commande."""
    parser = argparse.ArgumentParser(
        description="⛧ Générateur de templates - Outil d'Alma ⛧"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')
    
    # Commande generate
    gen_parser = subparsers.add_parser('generate', help='Générer depuis un template')
    gen_parser.add_argument('template', help='Fichier template ou nom de template intégré')
    gen_parser.add_argument('output', help='Fichier de sortie')
    gen_parser.add_argument('-v', '--var', action='append', help='Variable: nom=valeur')
    gen_parser.add_argument('-f', '--vars-file', help='Fichier JSON de variables')
    gen_parser.add_argument('--overwrite', action='store_true', help='Écraser si existe')
    
    # Commande create-template
    create_parser = subparsers.add_parser('create-template', help='Créer un template')
    create_parser.add_argument('source', help='Fichier source')
    create_parser.add_argument('template', help='Template à créer')
    create_parser.add_argument('--no-auto-vars', action='store_true', help='Pas de variables auto')
    
    # Commande list-templates
    list_parser = subparsers.add_parser('list-templates', help='Lister les templates intégrés')
    
    parser.add_argument('--debug', action='store_true', help='Mode debug')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.debug:
        print(f"⛧ Template Generator - Commande: {args.command}")
        print()
    
    if args.command == 'generate':
        # Préparation des variables
        variables = {}
        
        # Variables depuis fichier JSON
        if args.vars_file:
            try:
                with open(args.vars_file, 'r', encoding='utf-8') as f:
                    file_vars = json.load(f)
                    variables.update(file_vars)
            except Exception as e:
                print(f"❌ Erreur lecture fichier variables: {e}")
                sys.exit(1)
        
        # Variables depuis ligne de commande
        if args.var:
            for var_def in args.var:
                if '=' in var_def:
                    name, value = var_def.split('=', 1)
                    variables[name.strip()] = value.strip()
        
        # Template intégré ou fichier
        template_path = args.template
        if args.template in BUILTIN_TEMPLATES:
            # Créer un fichier temporaire pour le template intégré
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.template', delete=False) as f:
                f.write(BUILTIN_TEMPLATES[args.template])
                template_path = f.name
        
        results = generate_from_template(
            template_path=template_path,
            output_path=args.output,
            variables=variables,
            overwrite=args.overwrite
        )
        
        # Nettoyage du fichier temporaire
        if args.template in BUILTIN_TEMPLATES:
            os.unlink(template_path)
        
        formatted_output = format_generation_results(results)
        print(formatted_output)
        
        sys.exit(0 if results["success"] else 1)
    
    elif args.command == 'create-template':
        results = create_template_from_file(
            source_path=args.source,
            template_path=args.template,
            auto_variables=not args.no_auto_vars
        )
        
        if results["success"]:
            print(f"✅ Template créé avec succès !")
            print(f"📁 Source: {results['source_path']}")
            print(f"📄 Template: {results['template_path']}")
            print(f"📊 Taille: {results['template_size']} bytes")
            if results["suggested_variables"]:
                print(f"💡 Variables suggérées: {len(results['suggested_variables'])}")
                for value, var_name in results["suggested_variables"][:5]:
                    print(f"  {var_name}: {value}")
        else:
            print(f"❌ Erreur: {results['error']}")
        
        sys.exit(0 if results["success"] else 1)
    
    elif args.command == 'list-templates':
        print("📚 Templates intégrés disponibles:")
        print("⛧" + "═" * 50)
        
        for name, template in BUILTIN_TEMPLATES.items():
            lines = len(template.split('\n'))
            print(f"📄 {name}")
            print(f"   📊 {lines} lignes")
            # Extraction de la première ligne de description
            first_lines = template.split('\n')[:5]
            for line in first_lines:
                if '{{' in line and 'description' in line:
                    print(f"   📝 Template pour: {line.strip()}")
                    break
            print()
        
        sys.exit(0)


if __name__ == "__main__":
    main()
