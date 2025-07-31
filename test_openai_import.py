try:
    from openai.tool import tool
    print("SUCCESS: Le pacte 'from openai.tool import tool' a été invoqué avec succès.")
except ImportError as e:
    print(f"FAILURE: Impossible d'invoquer le pacte. Erreur: {e}")
except Exception as e:
    print(f"UNEXPECTED FAILURE: Une dissonance inattendue a brisé le rituel. Erreur: {e}")
