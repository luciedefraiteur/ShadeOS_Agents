#!/bin/bash

# Script générique pour tester n'importe quel modèle Ollama

# Vérifier les arguments
if [ $# -lt 2 ]; then
    echo "Usage: $0 <modèle> <prompt> [fichier_sortie]"
    echo "Exemple: $0 luciform_assistant 'Crée un profil pour un daemon testeur appelé ZED'"
    exit 1
fi

MODEL=$1
PROMPT=$2
OUTPUT_FILE=${3:-"test_output.txt"}

echo "🕷️ Test du modèle $MODEL - $(date)"
echo "📝 Prompt: $PROMPT"
echo "📁 Sortie: $OUTPUT_FILE"
echo "=================================================="

# Créer le fichier avec l'en-tête
echo "=== TEST OLLAMA MODEL ===" > "$OUTPUT_FILE"
echo "Modèle: $MODEL" >> "$OUTPUT_FILE"
echo "Timestamp: $(date)" >> "$OUTPUT_FILE"
echo "Prompt: $PROMPT" >> "$OUTPUT_FILE"
echo "==================================================" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# Lancer Ollama et capturer en temps réel
echo "🔄 Lancement d'Ollama..."
ollama run "$MODEL" "$PROMPT" 2>&1 | tee -a "$OUTPUT_FILE"

# Ajouter le résumé
echo "" >> "$OUTPUT_FILE"
echo "==================================================" >> "$OUTPUT_FILE"
echo "Fin du test - $(date)" >> "$OUTPUT_FILE"

echo ""
echo "✅ Test terminé !"
echo "📁 Résultats dans: $OUTPUT_FILE" 