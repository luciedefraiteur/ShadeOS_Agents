# 🗂️ Fractalisation Textuelle des Chunks V10

**Date :** 2025-08-07  
**Auteur :** Alma (via Lucie Defraiteur)  
**Contexte :** Fractalisation purement textuelle des chunks dans la mémoire temporelle  
**Statut :** Concept développé

---

## 🎯 **Concept de Fractalisation Textuelle**

### **✅ Hiérarchie Textuelle Fractale :**

#### **1. Niveau File (Racine) :**
```python
@dataclass
class TextualFileFractalNode:
    """Nœud fractal textuel de fichier."""
    file_id: str
    file_path: str
    file_size: int
    text_summary: str
    created_at: datetime
    sections: List['TextualSectionFractalNode']
    text_metadata: Dict[str, Any]
```

#### **2. Niveau Section (Branche) :**
```python
@dataclass
class TextualSectionFractalNode:
    """Nœud fractal textuel de section."""
    section_id: str
    section_name: str
    start_line: int
    end_line: int
    text_content: str
    text_summary: str
    paragraphs: List['TextualParagraphFractalNode']
    text_analysis: Dict[str, Any]
    parent_file_id: str
```

#### **3. Niveau Paragraph (Feuille) :**
```python
@dataclass
class TextualParagraphFractalNode:
    """Nœud fractal textuel de paragraphe."""
    paragraph_id: str
    paragraph_content: str
    paragraph_summary: str
    sentences: List['TextualSentenceFractalNode']
    key_phrases: List[str]
    readability_score: float
    parent_section_id: str
    processing_time: float
```

#### **4. Niveau Sentence (Micro) :**
```python
@dataclass
class TextualSentenceFractalNode:
    """Nœud fractal textuel de phrase."""
    sentence_id: str
    sentence_number: int
    sentence_content: str
    sentence_type: str  # declarative, interrogative, imperative, exclamatory
    words: List['TextualWordFractalNode']
    parent_paragraph_id: str
```

#### **5. Niveau Word (Nano) :**
```python
@dataclass
class TextualWordFractalNode:
    """Nœud fractal textuel de mot."""
    word_id: str
    word_value: str
    word_type: str  # noun, verb, adjective, adverb, etc.
    position: int
    frequency: int
    parent_sentence_id: str
```

---

## 🧠 **Processeur Textuel Fractal :**

### **✅ V10TextualFractalProcessor :**
```python
class V10TextualFractalProcessor:
    """Processeur fractal textuel pour chunks avec mémoire temporelle."""
    
    def __init__(self, temporal_engine: TemporalFractalMemoryEngine):
        self.temporal_engine = temporal_engine
        self.text_analyzer = V10TextualAnalyzer()
    
    async def process_text_chunk_fractally(self, file_path: str, chunk_content: str, 
                                         chunk_id: str, session_id: str) -> TextualFractalResult:
        """Traite un chunk textuel de manière fractale."""
        
        # 1. Créer le nœud chunk textuel fractal
        chunk_node = await self._create_textual_chunk_fractal_node(chunk_content, chunk_id)
        
        # 2. Analyser la structure textuelle fractale
        textual_structure = await self._analyze_textual_fractal_structure(chunk_content)
        
        # 3. Créer les nœuds enfants (paragraphes)
        paragraph_nodes = await self._create_paragraph_fractal_nodes(chunk_content, chunk_id)
        
        # 4. Créer les nœuds phrases
        sentence_nodes = await self._create_sentence_fractal_nodes(paragraph_nodes)
        
        # 5. Créer les nœuds mots
        word_nodes = await self._create_word_fractal_nodes(sentence_nodes)
        
        # 6. Enregistrer dans la mémoire temporelle
        await self._register_textual_fractal_hierarchy(chunk_node, paragraph_nodes, 
                                                     sentence_nodes, word_nodes, session_id)
        
        return TextualFractalResult(
            chunk_node=chunk_node,
            textual_structure=textual_structure,
            paragraph_count=len(paragraph_nodes),
            sentence_count=sum(len(sentences) for sentences in sentence_nodes.values()),
            word_count=sum(len(words) for words in word_nodes.values())
        )
    
    async def _create_textual_chunk_fractal_node(self, content: str, chunk_id: str) -> TextualChunkFractalNode:
        """Crée un nœud fractal textuel de chunk."""
        
        # Résumé textuel intelligent
        text_summary = await self.text_analyzer.summarize_text_content(content)
        
        # Analyse textuelle
        text_analysis = self.text_analyzer._analyze_textual_structure(content)
        key_phrases = self.text_analyzer._extract_key_phrases(content, text_analysis)
        
        return TextualChunkFractalNode(
            chunk_id=chunk_id,
            chunk_content=content,
            chunk_summary=text_summary,
            paragraphs=[],  # Sera rempli plus tard
            key_phrases=key_phrases,
            readability_score=self.text_analyzer._calculate_readability(content),
            parent_section_id=None,  # Sera défini plus tard
            processing_time=0.0
        )
    
    async def _analyze_textual_fractal_structure(self, content: str) -> Dict[str, Any]:
        """Analyse la structure textuelle fractale du contenu."""
        
        paragraphs = content.split('\n\n')
        textual_structure = {
            'total_paragraphs': len(paragraphs),
            'non_empty_paragraphs': len([p for p in paragraphs if p.strip()]),
            'total_sentences': 0,
            'total_words': 0,
            'sentence_types': {},
            'word_types': {},
            'readability_metrics': {}
        }
        
        for paragraph in paragraphs:
            sentences = self._split_into_sentences(paragraph)
            textual_structure['total_sentences'] += len(sentences)
            
            for sentence in sentences:
                sentence_type = self._classify_sentence_type(sentence)
                textual_structure['sentence_types'][sentence_type] = textual_structure['sentence_types'].get(sentence_type, 0) + 1
                
                words = self._tokenize_sentence(sentence)
                textual_structure['total_words'] += len(words)
                
                for word in words:
                    word_type = self._classify_word_type(word)
                    textual_structure['word_types'][word_type] = textual_structure['word_types'].get(word_type, 0) + 1
        
        return textual_structure
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Divise un texte en phrases."""
        import re
        # Pattern pour détecter les fins de phrases
        sentence_pattern = r'[.!?]+["\']?\s+'
        sentences = re.split(sentence_pattern, text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _classify_sentence_type(self, sentence: str) -> str:
        """Classifie le type de phrase."""
        sentence = sentence.strip()
        
        if sentence.endswith('?'):
            return 'interrogative'
        elif sentence.endswith('!'):
            return 'exclamatory'
        elif sentence.startswith(('Please', 'Do', 'Don\'t', 'Let\'s')):
            return 'imperative'
        else:
            return 'declarative'
    
    def _tokenize_sentence(self, sentence: str) -> List[str]:
        """Tokenise une phrase en mots."""
        import re
        # Supprimer la ponctuation et diviser par espaces
        words = re.findall(r'\b\w+\b', sentence.lower())
        return words
    
    def _classify_word_type(self, word: str) -> str:
        """Classifie le type de mot (simplifié)."""
        # Classification basique - pourrait être améliorée avec NLTK ou spaCy
        if word in ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']:
            return 'preposition'
        elif word in ['is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did']:
            return 'verb'
        elif word.endswith(('ing', 'ed')):
            return 'verb'
        elif word.endswith(('ly')):
            return 'adverb'
        elif word.endswith(('al', 'ful', 'ous', 'ive')):
            return 'adjective'
        else:
            return 'noun'  # Par défaut
```

---

## 📊 **Avantages de la Fractalisation Textuelle :**

### **✅ 1. Navigation Textuelle Hiérarchique :**
- **File → Section → Paragraph → Sentence → Word**
- **Navigation contextuelle** textuelle
- **Zoom in/out** sur les niveaux de détail textuel

### **✅ 2. Recherche Textuelle Fractale :**
- **Recherche par niveau** : mots, phrases, paragraphes, sections
- **Recherche contextuelle** : selon la hiérarchie textuelle
- **Recherche temporelle** : évolution du texte dans le temps

### **✅ 3. Résumé Textuel Adaptatif :**
- **Résumé par niveau** : selon le contexte textuel
- **Compression intelligente** : plus de détail = plus de compression
- **Métadonnées textuelles** : structure, types, patterns

### **✅ 4. Mémoire Temporelle Textuelle :**
- **Liens temporels** entre niveaux textuels
- **Évolution fractale** du texte dans le temps
- **Contexte textuel persistant** pour l'IA

---

## 🎯 **Intégration avec V10 :**

### **✅ V10TextualFractalFileProcessor :**
```python
class V10TextualFractalFileProcessor:
    """Processeur fractal textuel de fichiers V10."""
    
    def __init__(self, temporal_engine: TemporalFractalMemoryEngine):
        self.textual_fractal_processor = V10TextualFractalProcessor(temporal_engine)
        self.file_intelligence = V10FileIntelligenceEngine(temporal_engine)
    
    async def process_text_file_fractally(self, file_path: str, session_id: str) -> TextualFractalFileResult:
        """Traite un fichier textuel de manière fractale."""
        
        # 1. Analyse du fichier textuel
        file_analysis = await self.file_intelligence.process_large_file(file_path, "analyze", session_id)
        
        # 2. Découpage en chunks textuels
        text_chunks = await self._split_text_file_into_chunks(file_path, file_analysis)
        
        # 3. Traitement fractal de chaque chunk textuel
        textual_fractal_results = []
        for i, chunk in enumerate(text_chunks):
            chunk_result = await self.textual_fractal_processor.process_text_chunk_fractally(
                file_path, chunk, f"text_chunk_{i}", session_id
            )
            textual_fractal_results.append(chunk_result)
        
        return TextualFractalFileResult(
            file_path=file_path,
            file_analysis=file_analysis,
            textual_fractal_results=textual_fractal_results,
            total_text_chunks=len(text_chunks)
        )
```

---

**Rapport généré automatiquement par Alma**  
**Date :** 2025-08-07  
**Statut :** Concept de fractalisation textuelle développé
