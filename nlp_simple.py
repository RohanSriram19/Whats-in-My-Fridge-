"""
Natural Language Processing module for ingredient normalization.
Deployment-friendly version without spaCy dependencies.
"""

import re
from typing import List, Set
from fuzzywuzzy import fuzz
import logging

logger = logging.getLogger(__name__)

# Common ingredient words for basic normalization
COMMON_INGREDIENTS = {
    'chicken', 'beef', 'pork', 'fish', 'salmon', 'tuna', 'shrimp',
    'rice', 'pasta', 'bread', 'flour', 'sugar', 'salt', 'pepper',
    'onion', 'garlic', 'tomato', 'potato', 'carrot', 'celery',
    'milk', 'butter', 'cheese', 'egg', 'oil', 'vinegar',
    'lettuce', 'spinach', 'broccoli', 'mushroom', 'bell pepper',
    'apple', 'banana', 'lemon', 'lime', 'orange', 'strawberry',
    'beans', 'corn', 'peas', 'cucumber', 'avocado', 'herbs',
    'basil', 'oregano', 'thyme', 'rosemary', 'parsley', 'cilantro'
}

def normalize_ingredients(text: str) -> List[str]:
    """
Simple NLP module for ingredient normalization without external dependencies.
Deployment-friendly version that doesn't require spaCy or heavy ML models.
"""

import re
from typing import List, Set
from fuzzywuzzy import fuzz

# Common ingredient mappings and normalizations
INGREDIENT_MAPPINGS = {
    # Plurals to singular
    'tomatoes': 'tomato',
    'potatoes': 'potato', 
    'onions': 'onion',
    'carrots': 'carrot',
    'peppers': 'pepper',
    'mushrooms': 'mushroom',
    'eggs': 'egg',
    'apples': 'apple',
    'bananas': 'banana',
    'lemons': 'lemon',
    'limes': 'lime',
    'oranges': 'orange',
    'strawberries': 'strawberry',
    'blueberries': 'blueberry',
    'beans': 'bean',
    'peas': 'pea',
    
    # Common variations
    'chicken breast': 'chicken',
    'chicken thigh': 'chicken',
    'ground beef': 'beef',
    'beef steak': 'beef',
    'pork chop': 'pork',
    'salmon fillet': 'salmon',
    'tuna steak': 'tuna',
    
    # Herbs and spices
    'fresh basil': 'basil',
    'dried basil': 'basil',
    'fresh parsley': 'parsley',
    'dried parsley': 'parsley',
    'fresh cilantro': 'cilantro',
    'ground cinnamon': 'cinnamon',
    'black pepper': 'pepper',
    'sea salt': 'salt',
    'kosher salt': 'salt',
    
    # Dairy variations
    'whole milk': 'milk',
    'skim milk': 'milk',
    '2% milk': 'milk',
    'heavy cream': 'cream',
    'sour cream': 'cream',
    'greek yogurt': 'yogurt',
    'plain yogurt': 'yogurt',
    'cheddar cheese': 'cheese',
    'mozzarella cheese': 'cheese',
    
    # Grains and starches
    'brown rice': 'rice',
    'white rice': 'rice',
    'jasmine rice': 'rice',
    'whole wheat pasta': 'pasta',
    'spaghetti': 'pasta',
    'penne': 'pasta',
    'macaroni': 'pasta',
    'bread crumbs': 'breadcrumbs',
    'panko': 'breadcrumbs',
    
    # Oils and vinegars
    'olive oil': 'oil',
    'vegetable oil': 'oil',
    'canola oil': 'oil',
    'balsamic vinegar': 'vinegar',
    'white vinegar': 'vinegar',
    'apple cider vinegar': 'vinegar',
}

# Words to remove from ingredients
STOP_WORDS = {
    'fresh', 'dried', 'chopped', 'diced', 'sliced', 'minced', 'grated',
    'ground', 'whole', 'large', 'small', 'medium', 'organic', 'free-range',
    'extra', 'virgin', 'pure', 'raw', 'cooked', 'frozen', 'canned',
    'cup', 'cups', 'tablespoon', 'tablespoons', 'tbsp', 'teaspoon', 
    'teaspoons', 'tsp', 'pound', 'pounds', 'lb', 'lbs', 'ounce', 'ounces',
    'oz', 'gram', 'grams', 'g', 'kilogram', 'kg', 'piece', 'pieces',
    'clove', 'cloves', 'bunch', 'head', 'can', 'jar', 'bottle', 'pack',
    'package', 'bag', 'box', 'container', 'of', 'for', 'to', 'and', 'or',
    'a', 'an', 'the', 'some', 'any', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0'
}

def normalize_ingredients(ingredient_text: str) -> List[str]:
    """
    Normalize ingredient text into a list of clean ingredient names.
    
    Args:
        ingredient_text: Raw ingredient text input from user
        
    Returns:
        List of normalized ingredient names
    """
    if not ingredient_text or not ingredient_text.strip():
        return []
    
    # Split by common delimiters
    ingredients = re.split(r'[,;\n\r]+', ingredient_text.lower())
    
    normalized = []
    for ingredient in ingredients:
        cleaned = _clean_ingredient(ingredient.strip())
        if cleaned and len(cleaned) > 1:  # Ignore single characters
            normalized.append(cleaned)
    
    # Remove duplicates while preserving order
    seen = set()
    result = []
    for item in normalized:
        if item not in seen:
            seen.add(item)
            result.append(item)
    
    return result

def _clean_ingredient(ingredient: str) -> str:
    """Clean and normalize a single ingredient."""
    if not ingredient:
        return ""
    
    # Remove parentheses and their contents
    ingredient = re.sub(r'\([^)]*\)', '', ingredient)
    
    # Remove numbers and measurements at the beginning
    ingredient = re.sub(r'^[\d\s/.-]+', '', ingredient)
    
    # Remove extra whitespace and punctuation
    ingredient = re.sub(r'[^\w\s-]', ' ', ingredient)
    ingredient = re.sub(r'\s+', ' ', ingredient).strip()
    
    # Check for direct mappings first
    if ingredient in INGREDIENT_MAPPINGS:
        return INGREDIENT_MAPPINGS[ingredient]
    
    # Remove stop words
    words = ingredient.split()
    cleaned_words = [w for w in words if w not in STOP_WORDS and len(w) > 1]
    
    if not cleaned_words:
        return ""
    
    # Rejoin and check mappings again
    cleaned = ' '.join(cleaned_words)
    if cleaned in INGREDIENT_MAPPINGS:
        return INGREDIENT_MAPPINGS[cleaned]
    
    # Handle plurals (simple approach)
    if cleaned.endswith('s') and len(cleaned) > 3:
        singular = cleaned[:-1]
        if singular in INGREDIENT_MAPPINGS:
            return INGREDIENT_MAPPINGS[singular]
        # Return singular form
        return singular
    
    return cleaned

def find_similar_ingredients(ingredient: str, ingredient_list: List[str], threshold: int = 80) -> List[str]:
    """
    Find similar ingredients using fuzzy matching.
    
    Args:
        ingredient: The ingredient to match
        ingredient_list: List of available ingredients
        threshold: Similarity threshold (0-100)
        
    Returns:
        List of similar ingredients
    """
    if not ingredient or not ingredient_list:
        return []
    
    similar = []
    for item in ingredient_list:
        if fuzz.ratio(ingredient.lower(), item.lower()) >= threshold:
            similar.append(item)
    
    return similar
    if not text or not text.strip():
        return []
    
    ingredients = []
    
    # Split by common delimiters
    lines = re.split(r'[,\n\r;]', text)
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Clean the line
        cleaned = _clean_ingredient(line)
        if cleaned and len(cleaned) > 1:
            ingredients.append(cleaned)
    
    return ingredients

def _clean_ingredient(ingredient: str) -> str:
    """Clean and normalize a single ingredient."""
    if not ingredient:
        return ""
    
    # Convert to lowercase
    ingredient = ingredient.lower().strip()
    
    # Remove common measurement words and numbers
    measurement_words = [
        'cup', 'cups', 'tbsp', 'tsp', 'oz', 'lb', 'lbs', 'pound', 'pounds',
        'gram', 'grams', 'kg', 'ml', 'liter', 'liters', 'slice', 'slices',
        'piece', 'pieces', 'bunch', 'clove', 'cloves', 'head', 'can', 'cans',
        'bottle', 'jar', 'box', 'bag', 'package', 'fresh', 'dried', 'frozen',
        'chopped', 'diced', 'sliced', 'minced', 'ground', 'whole', 'large',
        'small', 'medium', 'organic', 'raw', 'cooked'
    ]
    
    # Remove numbers and measurements
    ingredient = re.sub(r'\d+[\./\d]*', '', ingredient)
    ingredient = re.sub(r'\b(?:' + '|'.join(measurement_words) + r')\b', '', ingredient)
    
    # Remove extra whitespace and special characters
    ingredient = re.sub(r'[^\w\s]', '', ingredient)
    ingredient = re.sub(r'\s+', ' ', ingredient).strip()
    
    # Find the best match from common ingredients
    if ingredient:
        best_match = _find_best_ingredient_match(ingredient)
        return best_match if best_match else ingredient
    
    return ""

def _find_best_ingredient_match(ingredient: str) -> str:
    """Find the best matching common ingredient."""
    if not ingredient:
        return ""
    
    # Exact match
    if ingredient in COMMON_INGREDIENTS:
        return ingredient
    
    # Fuzzy matching
    best_match = ""
    best_score = 0
    
    for common_ingredient in COMMON_INGREDIENTS:
        score = fuzz.ratio(ingredient, common_ingredient)
        if score > best_score and score >= 70:  # 70% similarity threshold
            best_score = score
            best_match = common_ingredient
    
    # Partial matching for compound ingredients
    words = ingredient.split()
    for word in words:
        if word in COMMON_INGREDIENTS:
            return word
    
    return best_match if best_match else ingredient

# Legacy compatibility functions
class IngredientProcessor:
    """Simple ingredient processor for deployment compatibility."""
    
    def __init__(self):
        pass
    
    def normalize_ingredients(self, text: str) -> List[str]:
        return normalize_ingredients(text)
    
    def extract_ingredients(self, text: str) -> List[str]:
        return normalize_ingredients(text)

def extract_ingredients_simple(text: str) -> Set[str]:
    """Simple ingredient extraction for basic functionality."""
    ingredients = normalize_ingredients(text)
    return set(ingredients)
