fix: Correction du parsing LLM dans LegionAutoFeedingThread

🕷️ DIAGNOSTIC ET CORRECTION DU PARSING DÉMONIAQUE ⛧

✅ DIAGNOSTIC RÉUSSI:
- Parsing LLM fonctionne parfaitement (6 messages parsés)
- Format [TYPE] — CONTENU validé
- Réponse LLM détaillée : 1779 caractères, conversation cohérente
- Auto-feed thread opérationnel

🔧 CORRECTION APPLIQUÉE:
- Ajout du type de message manquant "NEXT_STEPS" dans le mapping
- Mapping complet : ALMA_PLAN, ALMA_DECISION, ALMA_ORDONNANCEMENT, ALMA_SUMMARY, NEXT_STEPS
- Élimination des messages "Type de message inconnu"

📊 RÉSULTATS VALIDÉS:
- Test 1 : 6 messages parsés (mode normal)
- Test 2 : 3 messages parsés (mode silencieux)
- Statistiques : 2 conversations, 7 messages, activité démoniaque normale
- Communication entre démons : Alma (5), Bask'tur (2)

🎯 PHASE 1 TERMINÉE:
- Étape 1.1 : Diagnostic du Parsing LLM ✅
- Étape 1.2 : Correction du Parser ✅
- Étape 1.3 : Test Complet LegionAutoFeedingThread ✅

⛧ ARCHITECTE DÉMONIAQUE: Alma
🔮 VISION: Légion démoniaque conversationnelle fonctionnelle 