import requests
import os
import time
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

class SpoonacularAPI:
    """Wrapper for Spoonacular API interactions"""
    
    def __init__(self):
        self.api_key = os.getenv('SPOONACULAR_API_KEY')
        self.base_url = "https://api.spoonacular.com/recipes"
        self.rate_limit_delay = 0.1  # Delay between API calls
        
        if not self.api_key:
            print("Warning: SPOONACULAR_API_KEY not found in environment variables")
    
    def fetch_recipes(self, ingredients: List[str], max_results: int = 10, 
                     cuisine: Optional[str] = None) -> List[Dict]:
        """
        Fetch recipes from Spoonacular API based on ingredients
        
        Args:
            ingredients: List of ingredient names
            max_results: Maximum number of recipes to return
            cuisine: Optional cuisine filter
            
        Returns:
            List of recipe dictionaries
        """
        if not self.api_key:
            return self._get_mock_recipes(ingredients, max_results)
        
        try:
            # Prepare parameters
            params = {
                'apiKey': self.api_key,
                'ingredients': ','.join(ingredients),
                'number': max_results,
                'limitLicense': True,
                'ranking': 2,  # Maximize used ingredients
                'ignorePantry': True
            }
            
            if cuisine:
                params['cuisine'] = cuisine.lower()
            
            # Make API request
            url = f"{self.base_url}/findByIngredients"
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                recipes = response.json()
                
                # Enhance recipes with additional details
                enhanced_recipes = []
                for recipe in recipes:
                    enhanced = self._enhance_recipe(recipe)
                    if enhanced:
                        enhanced_recipes.append(enhanced)
                    time.sleep(self.rate_limit_delay)  # Rate limiting
                
                return enhanced_recipes
            else:
                print(f"Spoonacular API error: {response.status_code}")
                return self._get_mock_recipes(ingredients, max_results)
                
        except Exception as e:
            print(f"Error fetching recipes: {str(e)}")
            return self._get_mock_recipes(ingredients, max_results)
    
    def _enhance_recipe(self, recipe: Dict) -> Optional[Dict]:
        """Enhance recipe with additional details from Spoonacular"""
        try:
            recipe_id = recipe.get('id')
            if not recipe_id:
                return recipe
            
            # Get recipe information
            info_url = f"{self.base_url}/{recipe_id}/information"
            params = {
                'apiKey': self.api_key,
                'includeNutrition': False
            }
            
            response = requests.get(info_url, params=params, timeout=10)
            
            if response.status_code == 200:
                detailed_info = response.json()
                
                # Merge the information
                recipe.update({
                    'sourceUrl': detailed_info.get('sourceUrl', ''),
                    'readyInMinutes': detailed_info.get('readyInMinutes', 0),
                    'servings': detailed_info.get('servings', 0),
                    'summary': detailed_info.get('summary', ''),
                    'instructions': detailed_info.get('instructions', ''),
                    'healthScore': detailed_info.get('healthScore', 0)
                })
            
            return recipe
            
        except Exception as e:
            print(f"Error enhancing recipe {recipe.get('id', 'unknown')}: {str(e)}")
            return recipe
    
    def _get_mock_recipes(self, ingredients: List[str], max_results: int) -> List[Dict]:
        """Return mock recipes when API is not available"""
        
        mock_recipes = [
            {
                'id': 1,
                'title': 'Quick Veggie Scramble',
                'image': 'https://images.unsplash.com/photo-1525351484163-7529414344d8?w=300',
                'usedIngredients': [
                    {'name': ing} for ing in ingredients[:3]
                ],
                'missedIngredients': [
                    {'name': 'salt'}, {'name': 'pepper'}
                ],
                'readyInMinutes': 15,
                'servings': 2,
                'sourceUrl': 'https://example.com/recipe1',
                'summary': 'A quick and easy scramble using your available ingredients.'
            },
            {
                'id': 2,
                'title': 'Simple Stir Fry',
                'image': 'https://images.unsplash.com/photo-1512058564366-18510be2db19?w=300',
                'usedIngredients': [
                    {'name': ing} for ing in ingredients[:4]
                ],
                'missedIngredients': [
                    {'name': 'soy sauce'}, {'name': 'garlic'}
                ],
                'readyInMinutes': 20,
                'servings': 3,
                'sourceUrl': 'https://example.com/recipe2',
                'summary': 'A delicious stir fry that makes great use of your ingredients.'
            },
            {
                'id': 3,
                'title': 'One-Pot Wonder',
                'image': 'https://images.unsplash.com/photo-1547592180-85f173990554?w=300',
                'usedIngredients': [
                    {'name': ing} for ing in ingredients[:2]
                ],
                'missedIngredients': [
                    {'name': 'broth'}, {'name': 'herbs'}
                ],
                'readyInMinutes': 30,
                'servings': 4,
                'sourceUrl': 'https://example.com/recipe3',
                'summary': 'A hearty one-pot meal perfect for using up ingredients.'
            }
        ]
        
        # Filter mock recipes based on max_results
        return mock_recipes[:min(max_results, len(mock_recipes))]

# Create global instance
spoonacular_api = SpoonacularAPI()

def fetch_recipes(ingredients: List[str], max_results: int = 10, 
                 cuisine: Optional[str] = None) -> List[Dict]:
    """
    Main function to fetch recipes from external APIs
    
    Args:
        ingredients: List of normalized ingredient names
        max_results: Maximum number of recipes to return
        cuisine: Optional cuisine filter
        
    Returns:
        List of recipe dictionaries
    """
    return spoonacular_api.fetch_recipes(ingredients, max_results, cuisine)

def fetch_nutrition(recipe_id: int) -> Optional[Dict]:
    """
    Fetch nutrition information for a specific recipe
    
    Args:
        recipe_id: Spoonacular recipe ID
        
    Returns:
        Nutrition information dictionary or None
    """
    if not spoonacular_api.api_key:
        return None
    
    try:
        url = f"{spoonacular_api.base_url}/{recipe_id}/nutritionWidget.json"
        params = {
            'apiKey': spoonacular_api.api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Nutrition API error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Error fetching nutrition for recipe {recipe_id}: {str(e)}")
        return None
