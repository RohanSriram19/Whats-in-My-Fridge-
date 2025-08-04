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
