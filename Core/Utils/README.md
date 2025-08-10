# Core/Utils — Documentation basée sur le code (2025-08-09)

Utilitaires généraux (manipulation de chaînes).

## `string_utils.py`
- Remplacements:
  - `_perform_string_replacement(source, old, new, all_occurrences=False, debug=False)`
  - `_perform_word_boundary_replacement(source, old_word, new_word, all_occurrences=False, debug=False)`
- Recherche:
  - `_simple_text_search(text, pattern, case_sensitive=True)`
  - `_find_all_occurrences(text, pattern, case_sensitive=True)`
- Tokenisation XML simple:
  - `_simple_xml_tokenizer(content) -> list[dict]`
  - `_parse_simple_attributes(attr_string) -> dict`

Note: ces helpers sont utilisés par les outils d’édition/analyse pour des traitements textuels légers.
