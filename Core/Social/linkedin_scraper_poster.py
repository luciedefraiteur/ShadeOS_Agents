#!/usr/bin/env python3
"""
⛧ LinkedIn Scraper Poster ⛧
Alma's Rebellious LinkedIn Tool

Poste sur LinkedIn via scraping sans API officielle.
Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import os
import re
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager


class LinkedInScraperPoster:
    """Poster LinkedIn via scraping."""

    def __init__(self, email: str = None, password: str = None, headless: bool = True):
        """
        Initialise le scraper LinkedIn.

        Args:
            email: Email LinkedIn
            password: Mot de passe LinkedIn
            headless: Mode sans interface graphique
        """
        # Essaie d'abord le fichier .linkedin_auth
        auth_file = os.path.expanduser("~/.linkedin_auth")
        if os.path.exists(auth_file) and not email and not password:
            email, password = self._parse_auth_file(auth_file)

        # Fallback sur les variables d'environnement
        self.email = email or os.getenv('LINKEDIN_EMAIL')
        self.password = password or os.getenv('LINKEDIN_PASSWORD')
        self.headless = headless
        self.driver = None
        self.wait = None

    def _parse_auth_file(self, auth_file: str) -> tuple:
        """
        Parse le fichier d'authentification LinkedIn.

        Args:
            auth_file: Chemin vers le fichier .linkedin_auth

        Returns:
            Tuple (email, password)
        """
        try:
            email = None
            password = None

            with open(auth_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue

                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()

                        if key == 'LOGIN':
                            email = value
                        elif key == 'PASSWORD':
                            password = value

            if email and password:
                print(f"✅ Credentials chargés depuis {auth_file}")
                return email, password
            else:
                print(f"⚠️ Credentials incomplets dans {auth_file}")
                return None, None

        except Exception as e:
            print(f"❌ Erreur lecture {auth_file}: {e}")
            return None, None
    
    def _setup_driver(self):
        """Configure le driver Chrome."""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument('--headless')
        
        # Options pour éviter la détection
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # User agent réaliste
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.wait = WebDriverWait(self.driver, 10)
    
    def login(self) -> bool:
        """
        Se connecte à LinkedIn.
        
        Returns:
            True si succès, False sinon
        """
        try:
            print("🔐 Connexion à LinkedIn...")
            
            # Aller à la page de connexion
            self.driver.get("https://www.linkedin.com/login")
            time.sleep(2)
            
            # Saisir email
            email_field = self.wait.until(EC.presence_of_element_located((By.ID, "username")))
            email_field.clear()
            email_field.send_keys(self.email)
            
            # Saisir mot de passe
            password_field = self.driver.find_element(By.ID, "password")
            password_field.clear()
            password_field.send_keys(self.password)
            
            # Cliquer sur connexion
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            
            # Attendre la redirection
            time.sleep(3)
            
            # Vérifier si connecté (présence du feed)
            try:
                self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "feed-identity-module")))
                print("✅ Connexion réussie !")
                return True
            except:
                # Peut-être un challenge de sécurité
                if "challenge" in self.driver.current_url:
                    print("⚠️ Challenge de sécurité détecté")
                    print("💡 Résolvez manuellement et appuyez sur Entrée...")
                    input()
                    return True
                else:
                    print("❌ Échec de connexion")
                    return False
                    
        except Exception as e:
            print(f"❌ Erreur connexion: {e}")
            return False
    
    def post_content(self, content: str) -> bool:
        """
        Poste du contenu sur LinkedIn.
        
        Args:
            content: Contenu à poster
        
        Returns:
            True si succès, False sinon
        """
        try:
            print("📝 Création du post...")
            
            # Aller au feed principal
            self.driver.get("https://www.linkedin.com/feed/")
            time.sleep(2)
            
            # Cliquer sur "Commencer un post"
            try:
                # Plusieurs sélecteurs possibles selon la version de LinkedIn
                start_post_selectors = [
                    "//button[contains(@class, 'share-box-feed-entry__trigger')]",
                    "//div[contains(@class, 'share-box-feed-entry__trigger')]",
                    "//button[contains(text(), 'Commencer un post')]",
                    "//div[contains(text(), 'Commencer un post')]"
                ]
                
                start_post_button = None
                for selector in start_post_selectors:
                    try:
                        start_post_button = self.driver.find_element(By.XPATH, selector)
                        break
                    except:
                        continue
                
                if not start_post_button:
                    print("❌ Impossible de trouver le bouton 'Commencer un post'")
                    return False
                
                start_post_button.click()
                time.sleep(2)
                
            except Exception as e:
                print(f"❌ Erreur clic bouton post: {e}")
                return False
            
            # Saisir le contenu
            try:
                # Zone de texte du post
                text_area_selectors = [
                    "//div[@role='textbox']",
                    "//div[contains(@class, 'ql-editor')]",
                    "//div[@contenteditable='true']"
                ]
                
                text_area = None
                for selector in text_area_selectors:
                    try:
                        text_area = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                        break
                    except:
                        continue
                
                if not text_area:
                    print("❌ Impossible de trouver la zone de texte")
                    return False
                
                text_area.click()
                time.sleep(1)
                text_area.send_keys(content)
                time.sleep(2)
                
            except Exception as e:
                print(f"❌ Erreur saisie contenu: {e}")
                return False
            
            # Publier le post
            try:
                publish_selectors = [
                    "//button[contains(@class, 'share-actions__primary-action')]",
                    "//button[contains(text(), 'Publier')]",
                    "//button[contains(text(), 'Post')]"
                ]
                
                publish_button = None
                for selector in publish_selectors:
                    try:
                        publish_button = self.driver.find_element(By.XPATH, selector)
                        if publish_button.is_enabled():
                            break
                    except:
                        continue
                
                if not publish_button:
                    print("❌ Impossible de trouver le bouton Publier")
                    return False
                
                publish_button.click()
                time.sleep(3)
                
                print("✅ Post publié avec succès !")
                return True
                
            except Exception as e:
                print(f"❌ Erreur publication: {e}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur création post: {e}")
            return False
    
    def post_markdown_file(self, markdown_file: str) -> bool:
        """
        Poste le contenu d'un fichier markdown.
        
        Args:
            markdown_file: Chemin vers le fichier markdown
        
        Returns:
            True si succès, False sinon
        """
        try:
            # Lecture et nettoyage du fichier
            with open(markdown_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            clean_content = self._clean_markdown(content)
            
            # Limitation LinkedIn (environ 3000 caractères)
            if len(clean_content) > 3000:
                clean_content = clean_content[:2997] + "..."
            
            # Setup du driver
            self._setup_driver()
            
            # Connexion et publication
            if self.login():
                success = self.post_content(clean_content)
                self.close()
                return success
            else:
                self.close()
                return False
                
        except FileNotFoundError:
            print(f"❌ Fichier non trouvé: {markdown_file}")
            return False
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return False
    
    def _clean_markdown(self, content: str) -> str:
        """Nettoie le contenu markdown pour LinkedIn."""
        # Supprime les métadonnées YAML
        content = re.sub(r'^---.*?---\s*', '', content, flags=re.DOTALL)
        
        # Supprime les blocs de code
        content = re.sub(r'```.*?```', '[Code]', content, flags=re.DOTALL)
        content = re.sub(r'`([^`]+)`', r'\1', content)
        
        # Convertit les titres
        content = re.sub(r'^#{1,6}\s*(.+)$', r'🔸 \1', content, flags=re.MULTILINE)
        
        # Nettoie les liens
        content = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', content)
        
        # Nettoie les images
        content = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', r'[Image: \1]', content)
        
        # Nettoie les espaces
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        content = re.sub(r'[ \t]+', ' ', content)
        
        return content.strip()
    
    def close(self):
        """Ferme le driver."""
        if self.driver:
            self.driver.quit()


def main():
    """Utilisation en ligne de commande."""
    if len(sys.argv) != 2:
        print("⛧ LinkedIn Scraper Poster - Alma's Rebellious Tool ⛧")
        print()
        print("Usage: python3 linkedin_scraper_poster.py <fichier.md>")
        print("Exemple: python3 linkedin_scraper_poster.py PROGRESSION_REPORT_2025-08-01.md")
        print()
        print("💡 Configurez vos credentials LinkedIn:")
        print("   Option 1: Créez ~/.linkedin_auth avec:")
        print("             LOGIN=votre@email.com")
        print("             PASSWORD=votre_mot_de_passe")
        print("   Option 2: Variables d'environnement:")
        print("             export LINKEDIN_EMAIL='votre@email.com'")
        print("             export LINKEDIN_PASSWORD='votre_mot_de_passe'")
        print()
        print("⚠️ Attention: Utilisez à vos risques et périls !")
        return
    
    markdown_file = sys.argv[1]
    
    # Les credentials seront chargés automatiquement par la classe
    # depuis ~/.linkedin_auth ou les variables d'environnement
    
    # Demande confirmation
    print(f"📤 Publication de {markdown_file} sur LinkedIn via scraping...")
    print("⚠️ Cette méthode contourne l'API officielle LinkedIn")
    response = input("Continuer ? (y/N): ")
    
    if response.lower() != 'y':
        print("❌ Annulé par l'utilisateur")
        return
    
    # Publication
    poster = LinkedInScraperPoster(headless=False)  # Mode visible pour debug

    # Vérification que les credentials ont été chargés
    if not poster.email or not poster.password:
        print("❌ Credentials LinkedIn non trouvés")
        print("💡 Créez le fichier ~/.linkedin_auth avec:")
        print("LOGIN=votre@email.com")
        print("PASSWORD=votre_mot_de_passe")
        print("💡 Ou configurez LINKEDIN_EMAIL et LINKEDIN_PASSWORD")
        return

    success = poster.post_markdown_file(markdown_file)
    
    if success:
        print(f"🎉 Fichier {markdown_file} publié sur LinkedIn !")
    else:
        print(f"❌ Échec publication de {markdown_file}")


if __name__ == "__main__":
    main()
