# Spoonacular API Configuration
SPOONACULAR_API_KEY = "your_spoonacular_api_key_here"

# You can get a free API key from: https://spoonacular.com/food-api
# Free tier includes 150 requests per day
# Add your API key to a .env file or set as environment variable

# Cache Configuration
CACHE_DIRECTORY = ".cache"
CACHE_DURATION_HOURS = 24
MAX_CACHE_ENTRIES = 1000

# Database Configuration
DATABASE_PATH = "data/app_database.json"

# ML Model Configuration
MODEL_DIRECTORY = "models"
MIN_FEEDBACK_FOR_ML = 10

# Application Configuration
MAX_RECIPES_PER_SEARCH = 20
DEFAULT_RECIPES_COUNT = 10

# UI Configuration
RECIPES_PER_PAGE = 10
MAX_INGREDIENT_DISPLAY = 5

# Search Configuration
DEFAULT_SEARCH_TIMEOUT = 10  # seconds
API_RATE_LIMIT_DELAY = 0.1   # seconds between API calls

# NLP Configuration
SPACY_MODEL = "en_core_web_sm"
USE_FUZZY_MATCHING = True
FUZZY_MATCH_THRESHOLD = 85

# Dietary Preferences
SUPPORTED_DIETS = [
    "vegetarian",
    "vegan", 
    "gluten-free",
    "dairy-free",
    "keto",
    "paleo",
    "low-carb",
    "low-fat"
]

SUPPORTED_CUISINES = [
    "african",
    "american", 
    "british",
    "cajun",
    "caribbean",
    "chinese",
    "eastern european",
    "european",
    "french",
    "german",
    "greek",
    "indian",
    "irish",
    "italian",
    "japanese",
    "jewish",
    "korean",
    "latin american",
    "mediterranean",
    "mexican",
    "middle eastern",
    "nordic",
    "southern",
    "spanish",
    "thai",
    "vietnamese"
]

# Ingredient Categories (for better processing)
PROTEIN_KEYWORDS = [
    "chicken", "beef", "pork", "fish", "salmon", "tuna", "shrimp", 
    "turkey", "lamb", "eggs", "tofu", "beans", "lentils", "chickpeas"
]

VEGETABLE_KEYWORDS = [
    "onion", "garlic", "tomato", "pepper", "carrot", "celery", 
    "spinach", "lettuce", "broccoli", "cauliflower", "mushroom"
]

GRAIN_KEYWORDS = [
    "rice", "pasta", "bread", "quinoa", "oats", "barley", "wheat",
    "noodles", "couscous", "bulgur"
]

DAIRY_KEYWORDS = [
    "milk", "cheese", "butter", "cream", "yogurt", "sour cream",
    "mozzarella", "cheddar", "parmesan", "ricotta"
]

# Error Messages
ERROR_MESSAGES = {
    "no_api_key": "No Spoonacular API key found. Please add your API key to the .env file.",
    "api_error": "Error connecting to recipe API. Using cached results or sample data.",
    "no_ingredients": "Please enter some ingredients to search for recipes.",
    "no_recipes_found": "No recipes found with those ingredients. Try different ingredients.",
    "cache_error": "Error accessing cache. Recipes may load slower.",
    "nlp_error": "Error processing ingredients. Using basic text processing.",
    "ml_error": "Error in recipe ranking. Using default ranking."
}

# Success Messages
SUCCESS_MESSAGES = {
    "recipes_found": "Found {count} delicious recipes for you!",
    "cached_results": "Found cached results - loading fast!",
    "feedback_saved": "Thanks for your feedback!",
    "recipe_saved": "Recipe saved to favorites!",
    "preferences_saved": "Preferences updated successfully!"
}
