import spacy
from typing import List, Dict, Set
import re
from fuzzywuzzy import fuzz, process

class IngredientProcessor:
    """Advanced NLP processor for ingredient normalization"""
    
    def __init__(self):
        self.nlp = None
        self.ingredient_synonyms = self._load_synonyms()
        self.common_units = {
            'cup', 'cups', 'tablespoon', 'tablespoons', 'tbsp', 'teaspoon', 
            'teaspoons', 'tsp', 'pound', 'pounds', 'lb', 'lbs', 'ounce', 
            'ounces', 'oz', 'gram', 'grams', 'g', 'kilogram', 'kg', 'ml', 
            'liter', 'l', 'piece', 'pieces', 'slice', 'slices', 'clove', 
            'cloves', 'bunch', 'head', 'can', 'bottle', 'package', 'bag'
        }
        self.quantity_words = {
            'half', 'quarter', 'some', 'little', 'bit', 'lots', 'bunch',
            'few', 'several', 'many', 'much', 'leftover', 'remaining'
        }
        self._init_spacy()
    
    def _init_spacy(self):
        """Initialize spaCy model with fallback options"""
        try:
            # Try to load the English model
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Warning: spaCy English model not found. Using basic text processing.")
            # Create a blank spacy model as fallback
            try:
                self.nlp = spacy.blank("en")
            except:
                print("Warning: Could not initialize spaCy. Using manual processing only.")
                self.nlp = None
    
    def _load_synonyms(self) -> Dict[str, str]:
        """Load ingredient synonyms for normalization"""
        return {
            # Cheese variations
            'mozz': 'mozzarella cheese',
            'mozzarella': 'mozzarella cheese',
            'parm': 'parmesan cheese',
            'parmesan': 'parmesan cheese',
            'cheddar': 'cheddar cheese',
            'swiss': 'swiss cheese',
            
            # Meat variations
            'chicken breast': 'chicken',
            'chicken thigh': 'chicken',
            'chicken leg': 'chicken',
            'ground beef': 'beef',
            'beef mince': 'beef',
            'pork chop': 'pork',
            'bacon strips': 'bacon',
            
            # Vegetable variations
            'bell pepper': 'bell pepper',
            'green pepper': 'bell pepper',
            'red pepper': 'bell pepper',
            'yellow pepper': 'bell pepper',
            'sweet pepper': 'bell pepper',
            'green onion': 'scallion',
            'spring onion': 'scallion',
            'roma tomato': 'tomato',
            'cherry tomato': 'tomato',
            'grape tomato': 'tomato',
            
            # Pantry items
            'olive oil': 'oil',
            'vegetable oil': 'oil',
            'canola oil': 'oil',
            'coconut oil': 'oil',
            'sea salt': 'salt',
            'table salt': 'salt',
            'kosher salt': 'salt',
            'black pepper': 'pepper',
            'white pepper': 'pepper',
            
            # Grains and starches
            'brown rice': 'rice',
            'white rice': 'rice',
            'jasmine rice': 'rice',
            'basmati rice': 'rice',
            'whole wheat pasta': 'pasta',
            'penne pasta': 'pasta',
            'spaghetti': 'pasta',
            'macaroni': 'pasta',
            
            # Common abbreviations
            'lb': 'pound',
            'oz': 'ounce',
            'tbsp': 'tablespoon',
            'tsp': 'teaspoon'
        }
    
    def normalize_ingredients(self, text: str) -> List[str]:
        """
        Main function to normalize ingredient text into clean ingredient list
        
        Args:
            text: Raw ingredient text from user
            
        Returns:
            List of normalized ingredient names
        """
        if not text or not text.strip():
            return []
        
        # Clean and split the text
        cleaned_text = self._clean_text(text)
        raw_ingredients = self._split_ingredients(cleaned_text)
        
        # Process each ingredient
        normalized = []
        for ingredient in raw_ingredients:
            processed = self._process_single_ingredient(ingredient)
            if processed and processed not in normalized:
                normalized.append(processed)
        
        return normalized
    
    def _clean_text(self, text: str) -> str:
        """Clean the input text"""
        # Convert to lowercase
        text = text.lower().strip()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common prefixes that don't add value
        prefixes_to_remove = [
            r'\b(some|a little|a bit of|lots of|bunch of|few|several)\s+',
            r'\b(i have|we have|there is|there are)\s+',
            r'\b(left over|leftover|remaining)\s+'
        ]
        
        for prefix in prefixes_to_remove:
            text = re.sub(prefix, '', text)
        
        return text
    
    def _split_ingredients(self, text: str) -> List[str]:
        """Split text into individual ingredients"""
        # Split by common separators
        separators = [',', ';', ' and ', ' & ', '\n', '•', '-']
        
        ingredients = [text]
        for sep in separators:
            new_ingredients = []
            for ingredient in ingredients:
                new_ingredients.extend([i.strip() for i in ingredient.split(sep)])
            ingredients = new_ingredients
        
        # Filter out empty strings and very short items
        return [ing for ing in ingredients if ing and len(ing) > 1]
    
    def _process_single_ingredient(self, ingredient: str) -> str:
        """Process a single ingredient string"""
        if not ingredient or len(ingredient) < 2:
            return ""
        
        ingredient = ingredient.strip()
        
        # Remove quantities and measurements
        ingredient = self._remove_quantities(ingredient)
        
        # Remove common descriptors
        ingredient = self._remove_descriptors(ingredient)
        
        # Apply synonyms
        ingredient = self._apply_synonyms(ingredient)
        
        # Use spaCy if available for advanced processing
        if self.nlp:
            ingredient = self._spacy_process(ingredient)
        
        # Final cleanup
        ingredient = ingredient.strip()
        
        # Skip if too short or only common words
        if len(ingredient) < 2 or ingredient in self.common_units:
            return ""
        
        return ingredient
    
    def _remove_quantities(self, text: str) -> str:
        """Remove quantity indicators from ingredient text"""
        # Remove numbers and fractions
        text = re.sub(r'\b\d+(?:\.\d+)?\s*', '', text)
        text = re.sub(r'\b\d+/\d+\s*', '', text)
        text = re.sub(r'\b(?:half|quarter|third|one|two|three|four|five|six|seven|eight|nine|ten)\s+', '', text)
        
        # Remove measurement units
        for unit in self.common_units:
            text = re.sub(f'\\b{unit}s?\\b', '', text, flags=re.IGNORECASE)
        
        # Remove quantity words
        for word in self.quantity_words:
            text = re.sub(f'\\b{word}\\b', '', text, flags=re.IGNORECASE)
        
        return text.strip()
    
    def _remove_descriptors(self, text: str) -> str:
        """Remove common descriptors that don't affect recipe matching"""
        descriptors = [
            'fresh', 'dried', 'frozen', 'canned', 'chopped', 'diced', 'minced',
            'sliced', 'shredded', 'grated', 'cooked', 'raw', 'organic',
            'whole', 'ground', 'crushed', 'fine', 'coarse', 'extra',
            'virgin', 'pure', 'unsalted', 'salted', 'sweetened', 'unsweetened',
            'large', 'small', 'medium', 'big', 'little', 'thin', 'thick'
        ]
        
        for descriptor in descriptors:
            text = re.sub(f'\\b{descriptor}\\b', '', text, flags=re.IGNORECASE)
        
        return text.strip()
    
    def _apply_synonyms(self, text: str) -> str:
        """Apply synonym mapping to normalize ingredient names"""
        text_lower = text.lower()
        
        # Direct match first
        if text_lower in self.ingredient_synonyms:
            return self.ingredient_synonyms[text_lower]
        
        # Fuzzy matching for close matches
        best_match = process.extractOne(
            text_lower, 
            self.ingredient_synonyms.keys(), 
            scorer=fuzz.ratio,
            score_cutoff=85
        )
        
        if best_match:
            return self.ingredient_synonyms[best_match[0]]
        
        return text
    
    def _spacy_process(self, text: str) -> str:
        """Use spaCy for advanced text processing"""
        try:
            doc = self.nlp(text)
            
            # Extract meaningful tokens (nouns primarily)
            meaningful_tokens = []
            for token in doc:
                if (not token.is_stop and 
                    not token.is_punct and 
                    not token.is_space and
                    len(token.text) > 1 and
                    token.pos_ in ['NOUN', 'PROPN', 'ADJ']):
                    meaningful_tokens.append(token.lemma_.lower())
            
            if meaningful_tokens:
                return ' '.join(meaningful_tokens)
            else:
                # Fallback to original text if no meaningful tokens found
                return text
                
        except Exception as e:
            print(f"spaCy processing error: {e}")
            return text

# Global processor instance
processor = IngredientProcessor()

def normalize_ingredients(text: str) -> List[str]:
    """
    Main function to normalize ingredient text
    
    Args:
        text: Raw ingredient text from user input
        
    Returns:
        List of clean, normalized ingredient names
    """
    return processor.normalize_ingredients(text)
