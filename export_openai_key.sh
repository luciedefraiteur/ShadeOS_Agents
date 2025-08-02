#!/bin/bash
# ⛧ Export OpenAI API Key ⛧
# Script pour exporter automatiquement la clé API OpenAI depuis ~/.env
# 
# Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
#
# Usage:
#   source ./export_openai_key.sh    # Pour exporter dans le shell actuel
#   ./export_openai_key.sh           # Pour exporter dans un sous-shell

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fichier .env dans le répertoire home de l'utilisateur
ENV_FILE="$HOME/.env"

echo -e "${BLUE}⛧ Export OpenAI API Key ⛧${NC}"
echo "=================================================="

# Vérifier si le fichier .env existe
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}❌ Fichier .env non trouvé: $ENV_FILE${NC}"
    echo "   Créez le fichier avec votre clé API OpenAI:"
    echo "   echo 'OPENAI_API_KEY=sk-...' > ~/.env"
    exit 1
fi

echo -e "${YELLOW}📁 Fichier .env trouvé: $ENV_FILE${NC}"

# Chercher la clé API OpenAI dans le fichier .env
OPENAI_KEY=$(grep "^OPENAI_API_KEY=" "$ENV_FILE" | cut -d'=' -f2-)

# Vérifier si la clé a été trouvée
if [ -z "$OPENAI_KEY" ]; then
    echo -e "${RED}❌ Clé API OpenAI non trouvée dans $ENV_FILE${NC}"
    echo "   Ajoutez la ligne suivante dans votre fichier .env:"
    echo "   OPENAI_API_KEY=sk-..."
    exit 1
fi

# Vérifier le format de la clé (doit commencer par sk-)
if [[ ! "$OPENAI_KEY" =~ ^sk-[a-zA-Z0-9]+ ]]; then
    echo -e "${YELLOW}⚠️  Format de clé suspect: $OPENAI_KEY${NC}"
    echo "   La clé API OpenAI doit commencer par 'sk-'"
    echo "   Vérifiez le format dans votre fichier .env"
fi

# Exporter la clé dans l'environnement
export OPENAI_API_KEY="$OPENAI_KEY"

echo -e "${GREEN}✅ Clé API OpenAI exportée avec succès !${NC}"
echo -e "${BLUE}   Clé: ${OPENAI_KEY:0:10}...${NC}"

# Vérifier que l'export a fonctionné
if [ -n "$OPENAI_API_KEY" ]; then
    echo -e "${GREEN}✅ Variable d'environnement OPENAI_API_KEY définie${NC}"
    echo -e "${BLUE}   Longueur: ${#OPENAI_API_KEY} caractères${NC}"
else
    echo -e "${RED}❌ Erreur lors de l'export de la variable d'environnement${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}🚀 Vous pouvez maintenant tester l'agent OpenAI :${NC}"
echo "   python test_openai_assistants_integration.py"
echo "   python test_agent_debugging_demo.py"
echo ""
echo -e "${BLUE}⛧ L'agent est prêt à corriger les bugs ! ⛧${NC}"

# Afficher un avertissement si le script n'est pas sourcé
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo ""
    echo -e "${YELLOW}💡 Pour que les variables persistent, utilisez :${NC}"
    echo "   source ./export_openai_key.sh"
fi 