#!/bin/bash

# Script de test pour l'Assistant Spécialiste .luciform

echo "🕷️ Test de l'Assistant Spécialiste .luciform - $(date)"
echo "📝 Démarrage du test..."

# Prompt de test pour l'assistant spécialiste
PROMPT="Génère un profil .luciform pour un daemon testeur appelé ZED, spécialisé dans la détection de bugs et la validation de code. Il doit avoir un style technique mais avec une touche de mystique, et être capable d'analyser les failles dans les systèmes."

# Fichier de sortie
OUTPUT_FILE="IAIntrospectionDaemons/luciform_assistant_test.txt"

echo "📁 Sortie: $OUTPUT_FILE"
echo "=================================================="

# Créer le fichier avec l'en-tête
echo "=== TEST LUCIFORM ASSISTANT ===" > "$OUTPUT_FILE"
echo "Timestamp: $(date)" >> "$OUTPUT_FILE"
echo "Prompt: $PROMPT" >> "$OUTPUT_FILE"
echo "==================================================" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# Lancer l'assistant spécialiste et capturer en temps réel
echo "🔄 Lancement de l'Assistant Spécialiste .luciform..."
ollama run luciform_assistant "$PROMPT" 2>&1 | tee -a "$OUTPUT_FILE"

# Ajouter le résumé
echo "" >> "$OUTPUT_FILE"
echo "==================================================" >> "$OUTPUT_FILE"
echo "Fin du test - $(date)" >> "$OUTPUT_FILE"

echo ""
echo "✅ Test terminé !"
echo "📁 Résultats dans: $OUTPUT_FILE" 