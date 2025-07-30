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
                     meal_type: Optional[str] = None, cuisine: Optional[str] = None) -> List[Dict]:
        """
        Fetch recipes from Spoonacular API based on ingredients
        
        Args:
            ingredients: List of ingredient names
            max_results: Maximum number of recipes to return
            meal_type: Optional meal type filter (breakfast, lunch, dinner, dessert)
            cuisine: Optional cuisine filter
            
        Returns:
            List of recipe dictionaries
        """
        if not self.api_key:
            return self._get_mock_recipes(ingredients, max_results, meal_type)
        
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
            
            if meal_type:
                # Map meal types to Spoonacular API types
                meal_type_mapping = {
                    'breakfast': 'breakfast',
                    'lunch': 'main course',
                    'dinner': 'main course',
                    'dessert': 'dessert'
                }
                if meal_type.lower() in meal_type_mapping:
                    params['type'] = meal_type_mapping[meal_type.lower()]
            
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
    
    def _get_mock_recipes(self, ingredients: List[str], max_results: int, meal_type: Optional[str] = None) -> List[Dict]:
        """Return dynamic mock recipes based on ingredients and meal type"""
        import random
        import hashlib
        
        # Create a seed based on ingredients to get consistent but different results
        ingredients_str = ','.join(sorted(ingredients))
        seed = int(hashlib.md5(ingredients_str.encode()).hexdigest()[:8], 16)
        random.seed(seed)
        
        # Recipe templates organized by meal type
        breakfast_templates = [
            {
                'title_patterns': ['{} Scramble', '{} and {} Omelet', 'Morning {} Bowl'],
                'base_title': 'Breakfast Scramble',
                'cook_time_range': (5, 15),
                'servings_range': (1, 2),
                'health_score_range': (70, 85)
            },
            {
                'title_patterns': ['{} Pancakes', '{} French Toast', 'Quick {} Breakfast'],
                'base_title': 'Breakfast Stack',
                'cook_time_range': (10, 20),
                'servings_range': (2, 4),
                'health_score_range': (60, 75)
            }
        ]
        
        lunch_templates = [
            {
                'title_patterns': ['{} Salad', '{} and {} Bowl', 'Fresh {} Lunch'],
                'base_title': 'Garden Lunch Bowl',
                'cook_time_range': (10, 20),
                'servings_range': (1, 2),
                'health_score_range': (80, 95)
            },
            {
                'title_patterns': ['{} Sandwich', '{} and {} Wrap', 'Quick {} Lunch'],
                'base_title': 'Lunch Wrap',
                'cook_time_range': (5, 15),
                'servings_range': (1, 2),
                'health_score_range': (65, 80)
            }
        ]
        
        dinner_templates = [
            {
                'title_patterns': ['{} Stir Fry', '{} and {} Sauté', 'Pan-Fried {}'],
                'base_title': 'Dinner Stir Fry',
                'cook_time_range': (20, 35),
                'servings_range': (2, 4),
                'health_score_range': (70, 85)
            },
            {
                'title_patterns': ['{} Casserole', '{} and {} Bake', 'Baked {}'],
                'base_title': 'Dinner Casserole',
                'cook_time_range': (35, 60),
                'servings_range': (3, 6),
                'health_score_range': (65, 80)
            }
        ]
        
        dessert_templates = [
            {
                'title_patterns': ['{} Cookies', '{} and {} Cake', 'Sweet {} Treat'],
                'base_title': 'Sweet Dessert',
                'cook_time_range': (20, 45),
                'servings_range': (4, 8),
                'health_score_range': (30, 50)
            },
            {
                'title_patterns': ['{} Parfait', '{} and {} Smoothie', 'Fresh {} Dessert'],
                'base_title': 'Fruit Parfait',
                'cook_time_range': (5, 15),
                'servings_range': (2, 4),
                'health_score_range': (60, 75)
            }
        ]
        
        # Select templates based on meal type
        if meal_type:
            meal_type_lower = meal_type.lower()
            if meal_type_lower == 'breakfast':
                recipe_templates = breakfast_templates
            elif meal_type_lower == 'lunch':
                recipe_templates = lunch_templates
            elif meal_type_lower == 'dinner':
                recipe_templates = dinner_templates
            elif meal_type_lower == 'dessert':
                recipe_templates = dessert_templates
            else:
                # Default to general templates
                recipe_templates = breakfast_templates + lunch_templates + dinner_templates[:2]
        else:
            # General recipe templates for "Any" meal type
            recipe_templates = [
                {
                    'title_patterns': ['{} Scramble', '{} and {} Bowl', 'Quick {} Mix'],
                    'base_title': 'Fresh Ingredient Scramble',
                    'cook_time_range': (10, 20),
                    'servings_range': (1, 3),
                    'health_score_range': (70, 85)
                },
                {
                    'title_patterns': ['{} Stir Fry', '{} and {} Sauté', 'Pan-Fried {}'],
                    'base_title': 'Simple Stir Fry',
                    'cook_time_range': (15, 25),
                    'servings_range': (2, 4),
                    'health_score_range': (65, 80)
                },
                {
                    'title_patterns': ['{} Soup', '{} and {} Broth', 'Hearty {} Soup'],
                    'base_title': 'Comfort Soup',
                    'cook_time_range': (30, 60),
                'servings_range': (3, 6),
                'health_score_range': (75, 90)
            },
            {
                'title_patterns': ['{} Salad', 'Fresh {} Bowl', '{} and {} Salad'],
                'base_title': 'Garden Fresh Salad',
                'cook_time_range': (5, 15),
                'servings_range': (1, 2),
                'health_score_range': (85, 95)
            },
            {
                'title_patterns': ['{} Pasta', '{} and {} Pasta', 'Creamy {} Pasta'],
                'base_title': 'One-Pot Pasta',
                'cook_time_range': (20, 35),
                'servings_range': (3, 5),
                'health_score_range': (60, 75)
            },
            {
                'title_patterns': ['{} Curry', 'Spiced {} Dish', '{} and {} Curry'],
                'base_title': 'Aromatic Curry',
                'cook_time_range': (25, 45),
                'servings_range': (3, 4),
                'health_score_range': (70, 85)
            }
        ]
        
        # Recipe URLs that actually work
        recipe_urls = [
            'https://www.allrecipes.com/recipe/scrambled-eggs/',
            'https://www.foodnetwork.com/recipes/simple-stir-fry-recipe',
            'https://www.tasteofhome.com/recipes/one-pot-pasta/',
            'https://www.simplyrecipes.com/recipes/basic_green_salad/',
            'https://www.bonappetit.com/recipe/simple-vegetable-soup',
            'https://www.epicurious.com/recipes/food/views/quick-curry',
            'https://www.delish.com/cooking/recipe-ideas/easy-pasta-recipes/',
            'https://www.bbcgoodfood.com/recipes/collection/quick-healthy-recipes'
        ]
        
        # Food images from Unsplash
        food_images = [
            'https://images.unsplash.com/photo-1525351484163-7529414344d8?w=300',
            'https://images.unsplash.com/photo-1512058564366-18510be2db19?w=300',
            'https://images.unsplash.com/photo-1547592180-85f173990554?w=300',
            'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=300',
            'https://images.unsplash.com/photo-1547592166-23ac45744acd?w=300',
            'https://images.unsplash.com/photo-1551782450-17144efb9c50?w=300',
            'https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=300'
        ]
        
        mock_recipes = []
        
        for i in range(min(max_results, len(recipe_templates))):
            template = recipe_templates[i]
            
            # Generate title based on ingredients
            if len(ingredients) >= 2:
                title_pattern = random.choice(template['title_patterns'])
                if '{}' in title_pattern:
                    if title_pattern.count('{}') == 2:
                        title = title_pattern.format(ingredients[0].title(), ingredients[1].title())
                    else:
                        title = title_pattern.format(ingredients[0].title())
                else:
                    title = template['base_title']
            else:
                title = template['base_title']
            
            # Generate random but consistent values
            cook_time = random.randint(*template['cook_time_range'])
            servings = random.randint(*template['servings_range'])
            health_score = random.randint(*template['health_score_range'])
            
            # Select ingredients to use (more variety)
            num_used = min(len(ingredients), random.randint(2, 4))
            used_ingredients = random.sample(ingredients, num_used)
            
            # Common missing ingredients
            missing_options = ['salt', 'pepper', 'olive oil', 'garlic', 'onion', 'herbs', 'lemon', 'butter']
            num_missing = random.randint(1, 3)
            missing_ingredients = random.sample(missing_options, num_missing)
            
            recipe = {
                'id': i + 1,
                'title': title,
                'image': random.choice(food_images),
                'usedIngredients': [{'name': ing} for ing in used_ingredients],
                'missedIngredients': [{'name': ing} for ing in missing_ingredients],
                'readyInMinutes': cook_time,
                'servings': servings,
                'sourceUrl': random.choice(recipe_urls),
                'summary': f'A delicious {title.lower()} that makes great use of your {", ".join(used_ingredients[:2])} and more!',
                'healthScore': health_score
            }
            
            mock_recipes.append(recipe)
        
        return mock_recipes

# Create global instance
spoonacular_api = SpoonacularAPI()

def fetch_recipes(ingredients: List[str], max_results: int = 10, 
                 meal_type: Optional[str] = None, cuisine: Optional[str] = None) -> List[Dict]:
    """
    Main function to fetch recipes from external APIs
    
    Args:
        ingredients: List of normalized ingredient names
        max_results: Maximum number of recipes to return
        meal_type: Optional meal type filter (breakfast, lunch, dinner, dessert)
        cuisine: Optional cuisine filter
        
    Returns:
        List of recipe dictionaries
    """
    return spoonacular_api.fetch_recipes(ingredients, max_results, meal_type, cuisine)

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
