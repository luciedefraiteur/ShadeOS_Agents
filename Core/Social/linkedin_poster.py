#!/usr/bin/env python3
"""
⛧ LinkedIn Simple Poster ⛧
Alma's Simple LinkedIn Tool

Poste simplement un fichier markdown sur LinkedIn.
Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import os
import re
import requests
import sys


class LinkedInPoster:
    """Poster simple pour LinkedIn."""
    
    def __init__(self, access_token: str = None):
        """Initialise le poster LinkedIn."""
        self.access_token = access_token or os.getenv('LINKEDIN_ACCESS_TOKEN')
        self.api_base = "https://api.linkedin.com/v2"
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }
    
    def post_markdown_file(self, markdown_file: str) -> bool:
        """
        Poste le contenu d'un fichier markdown sur LinkedIn.
        
        Args:
            markdown_file: Chemin vers le fichier markdown
        
        Returns:
            True si succès, False sinon
        """
        try:
            # Lecture du fichier
            with open(markdown_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Nettoyage basique du markdown
            clean_content = self._clean_markdown(content)
            
            # Limitation à 3000 caractères (limite LinkedIn)
            if len(clean_content) > 3000:
                clean_content = clean_content[:2997] + "..."
            
            # Publication
            return self._create_post(clean_content)
            
        except FileNotFoundError:
            print(f"❌ Fichier non trouvé: {markdown_file}")
            return False
        except Exception as e:
            print(f"❌ Erreur lecture fichier: {e}")
            return False
    
    def _clean_markdown(self, content: str) -> str:
        """Nettoie le contenu markdown pour LinkedIn."""
        # Supprime les métadonnées YAML du début
        content = re.sub(r'^---.*?---\s*', '', content, flags=re.DOTALL)
        
        # Supprime les balises markdown complexes
        content = re.sub(r'```.*?```', '[Code]', content, flags=re.DOTALL)
        content = re.sub(r'`([^`]+)`', r'\1', content)
        
        # Convertit les titres markdown
        content = re.sub(r'^#{1,6}\s*(.+)$', r'🔸 \1', content, flags=re.MULTILINE)
        
        # Nettoie les liens
        content = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', content)
        
        # Nettoie les images
        content = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', r'[Image: \1]', content)
        
        # Nettoie les espaces multiples
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        content = re.sub(r'[ \t]+', ' ', content)
        
        return content.strip()
    
    def _create_post(self, content: str) -> bool:
        """Crée un post LinkedIn."""
        try:
            # Récupération de l'ID utilisateur
            profile_url = f"{self.api_base}/people/~"
            profile_response = requests.get(profile_url, headers=self.headers)
            
            if profile_response.status_code != 200:
                print(f"❌ Erreur récupération profil: {profile_response.status_code}")
                return False
            
            user_id = profile_response.json().get('id')
            
            # Données du post
            post_data = {
                "author": f"urn:li:person:{user_id}",
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": content
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }
            
            # Envoi du post
            url = f"{self.api_base}/ugcPosts"
            response = requests.post(url, headers=self.headers, json=post_data)
            
            if response.status_code == 201:
                print("✅ Post LinkedIn créé avec succès !")
                return True
            else:
                print(f"❌ Erreur création post: {response.status_code}")
                print(f"Réponse: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur création post LinkedIn: {e}")
            return False


def main():
    """Utilisation en ligne de commande."""
    if len(sys.argv) != 2:
        print("⛧ LinkedIn Poster - Alma's Tool ⛧")
        print()
        print("Usage: python3 linkedin_poster.py <fichier.md>")
        print("Exemple: python3 linkedin_poster.py PROGRESSION_REPORT_2025-08-01.md")
        print()
        print("💡 Configurez d'abord LINKEDIN_ACCESS_TOKEN:")
        print("   export LINKEDIN_ACCESS_TOKEN='votre_token'")
        return
    
    markdown_file = sys.argv[1]
    
    # Vérification du token
    token = os.getenv('LINKEDIN_ACCESS_TOKEN')
    if not token:
        print("❌ Token LinkedIn non configuré")
        print("💡 Configurez LINKEDIN_ACCESS_TOKEN dans vos variables d'environnement")
        print("💡 Exemple: export LINKEDIN_ACCESS_TOKEN='votre_token'")
        return
    
    # Création du poster et publication
    print(f"📤 Publication de {markdown_file} sur LinkedIn...")
    poster = LinkedInPoster(token)
    success = poster.post_markdown_file(markdown_file)
    
    if success:
        print(f"🎉 Fichier {markdown_file} publié sur LinkedIn !")
    else:
        print(f"❌ Échec publication de {markdown_file}")


if __name__ == "__main__":
    main()
