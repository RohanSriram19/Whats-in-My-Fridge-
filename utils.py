import re
import os
from typing import Dict, List, Any

def clean_html(text: str) -> str:
    """Remove HTML tags from text"""
    if not text:
        return ""
    return re.sub('<.*?>', '', text)

def format_time(minutes: int) -> str:
    """Format cooking time in a readable way"""
    if minutes <= 0:
        return "Unknown"
    elif minutes < 60:
        return f"{minutes} min"
    else:
        hours = minutes // 60
        remaining_minutes = minutes % 60
        if remaining_minutes == 0:
            return f"{hours}h"
        else:
            return f"{hours}h {remaining_minutes}m"

def truncate_text(text: str, max_length: int = 150) -> str:
    """Truncate text to specified length with ellipsis"""
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    # Try to break at word boundary
    truncated = text[:max_length]
    last_space = truncated.rfind(' ')
    
    if last_space > max_length * 0.8:  # If we can break at a word boundary reasonably close
        return truncated[:last_space] + "..."
    else:
        return truncated + "..."

def extract_ingredient_names(ingredients: List[Dict]) -> List[str]:
    """Extract ingredient names from Spoonacular ingredient objects"""
    names = []
    for ingredient in ingredients:
        # Try different possible name fields
        name = (ingredient.get('name') or 
                ingredient.get('original') or 
                ingredient.get('originalName') or 
                str(ingredient))
        
        if name and name not in names:
            names.append(name)
    
    return names

def format_ingredient_list(ingredients: List[str], max_display: int = 5) -> str:
    """Format ingredient list for display"""
    if not ingredients:
        return "No ingredients listed"
    
    if len(ingredients) <= max_display:
        return ", ".join(ingredients)
    else:
        displayed = ingredients[:max_display]
        remaining = len(ingredients) - max_display
        return f"{', '.join(displayed)}, and {remaining} more"

def calculate_ingredient_match_score(recipe_ingredients: List[str], 
                                   user_ingredients: List[str]) -> float:
    """Calculate how well recipe ingredients match user's ingredients"""
    if not recipe_ingredients or not user_ingredients:
        return 0.0
    
    # Normalize ingredient names for comparison
    recipe_normalized = [ing.lower().strip() for ing in recipe_ingredients]
    user_normalized = [ing.lower().strip() for ing in user_ingredients]
    
    # Count exact matches
    matches = sum(1 for ing in recipe_normalized if ing in user_normalized)
    
    # Calculate match percentage
    return matches / len(recipe_normalized)

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file system storage"""
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove multiple underscores
    filename = re.sub(r'_+', '_', filename)
    
    # Remove leading/trailing underscores and dots
    filename = filename.strip('_.')
    
    # Limit length
    if len(filename) > 255:
        filename = filename[:255]
    
    return filename

def validate_environment() -> Dict[str, bool]:
    """Validate that required environment variables and dependencies are available"""
    validation_results = {
        'spoonacular_api_key': bool(os.getenv('SPOONACULAR_API_KEY')),
        'cache_directory': True,  # Will be created if needed
        'data_directory': True,   # Will be created if needed
    }
    
    # Check for optional dependencies
    try:
        import spacy
        validation_results['spacy_available'] = True
    except ImportError:
        validation_results['spacy_available'] = False
    
    try:
        import sklearn
        validation_results['sklearn_available'] = True
    except ImportError:
        validation_results['sklearn_available'] = False
    
    return validation_results

def get_app_info() -> Dict[str, Any]:
    """Get application information and status"""
    validation = validate_environment()
    
    return {
        'app_name': "What's In My Fridge",
        'version': '1.0.0',
        'description': 'Find recipes using ingredients you already have',
        'environment_status': validation,
        'features': {
            'nlp_processing': validation['spacy_available'],
            'ml_ranking': validation['sklearn_available'],
            'api_integration': validation['spoonacular_api_key'],
            'caching': True,
            'user_preferences': True,
            'search_history': True
        }
    }

def format_recipe_summary(recipe: Dict) -> str:
    """Format a recipe summary for display"""
    title = recipe.get('title', 'Unknown Recipe')
    
    # Format time
    time_str = ""
    if recipe.get('readyInMinutes'):
        time_str = f" • {format_time(recipe['readyInMinutes'])}"
    
    # Format servings
    servings_str = ""
    if recipe.get('servings'):
        servings_str = f" • Serves {recipe['servings']}"
    
    # Format ingredients
    used_ingredients = extract_ingredient_names(recipe.get('usedIngredients', []))
    missed_ingredients = extract_ingredient_names(recipe.get('missedIngredients', []))
    
    ingredients_str = ""
    if used_ingredients:
        ingredients_str = f"\n✅ Using: {format_ingredient_list(used_ingredients, 3)}"
    
    if missed_ingredients:
        ingredients_str += f"\n🛒 Need: {format_ingredient_list(missed_ingredients, 2)}"
    
    return f"**{title}**{time_str}{servings_str}{ingredients_str}"

def create_recipe_url(recipe_id: int, source: str = "spoonacular") -> str:
    """Create a URL to view the full recipe"""
    if source.lower() == "spoonacular":
        return f"https://spoonacular.com/recipes/{recipe_id}"
    else:
        return f"https://example.com/recipe/{recipe_id}"

def parse_cooking_time(time_string: str) -> int:
    """Parse cooking time string into minutes"""
    if not time_string:
        return 0
    
    # Extract numbers and time units
    time_parts = re.findall(r'(\d+)\s*(h|hour|hours|m|min|minute|minutes)', time_string.lower())
    
    total_minutes = 0
    for amount, unit in time_parts:
        amount = int(amount)
        if unit.startswith('h'):
            total_minutes += amount * 60
        elif unit.startswith('m'):
            total_minutes += amount
    
    return total_minutes

def generate_shopping_list(recipes: List[Dict]) -> List[str]:
    """Generate a shopping list from missing ingredients in recipes"""
    shopping_items = set()
    
    for recipe in recipes:
        missed_ingredients = recipe.get('missedIngredients', [])
        for ingredient in missed_ingredients:
            name = ingredient.get('name') or ingredient.get('original', '')
            if name:
                shopping_items.add(name.lower().strip())
    
    return sorted(list(shopping_items))

def estimate_recipe_difficulty(recipe: Dict) -> str:
    """Estimate recipe difficulty based on various factors"""
    # Factors that contribute to difficulty
    prep_time = recipe.get('readyInMinutes', 30)
    instruction_count = len(recipe.get('analyzedInstructions', []))
    ingredient_count = len(recipe.get('extendedIngredients', []))
    
    # Simple scoring system
    difficulty_score = 0
    
    # Time factor
    if prep_time > 60:
        difficulty_score += 2
    elif prep_time > 30:
        difficulty_score += 1
    
    # Ingredient complexity
    if ingredient_count > 15:
        difficulty_score += 2
    elif ingredient_count > 10:
        difficulty_score += 1
    
    # Instruction complexity
    if instruction_count > 10:
        difficulty_score += 2
    elif instruction_count > 5:
        difficulty_score += 1
    
    # Classify difficulty
    if difficulty_score <= 1:
        return "Easy"
    elif difficulty_score <= 3:
        return "Medium"
    else:
        return "Hard"

def format_nutrition_info(nutrition: Dict) -> str:
    """Format nutrition information for display"""
    if not nutrition:
        return "Nutrition information not available"
    
    info_parts = []
    
    # Key nutrition facts
    key_nutrients = ['calories', 'protein', 'carbohydrates', 'fat', 'fiber']
    
    for nutrient in key_nutrients:
        if nutrient in nutrition:
            value = nutrition[nutrient]
            if isinstance(value, dict) and 'amount' in value:
                amount = value['amount']
                unit = value.get('unit', '')
                info_parts.append(f"{nutrient.title()}: {amount}{unit}")
            elif isinstance(value, (int, float)):
                info_parts.append(f"{nutrient.title()}: {value}")
    
    return " • ".join(info_parts) if info_parts else "Nutrition information not available"
