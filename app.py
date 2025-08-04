import streamlit as st
import time
from typing import List, Dict
from nlp_simple import normalize_ingredients
from api import fetch_recipes
from cache import get_cached_recipes, store_cached_recipes
from ranker import rank_recipes
from db import save_user_feedback, get_user_history, save_recipe_to_favorites, save_user_preferences, get_user_favorites
import uuid
import hashlib

# Page configuration
st.set_page_config(
    page_title="What's In My Fridge",
    page_icon="🥘",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced aesthetics
st.markdown("""
<style>
    /* Import professional fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Source+Sans+Pro:wght@300;400;600;700&display=swap');
    
    /* Global styling - Sleek dark red design */
    .main {
        background: #1a0b0b;
        font-family: 'Inter', sans-serif;
        color: #f3e8e8;
        min-height: 100vh;
    }
    
    .stApp {
        background: #1a0b0b;
    }
    
    /* Remove white backgrounds from containers */
    .stApp > div > div > div > div {
        background: transparent !important;
    }
    
    .block-container {
        background: transparent !important;
        padding-top: 1rem !important;
        max-width: 1400px !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    
    div[data-testid="stVerticalBlock"] {
        background: transparent !important;
    }
    
    div[data-testid="stHorizontalBlock"] {
        background: transparent !important;
    }
    
    .element-container {
        background: transparent !important;
    }
    
    /* Header styling - Sleek dark red */
    .main-header {
        background: transparent;
        padding: 2rem 0 1rem 0;
        margin-bottom: 2rem;
        text-align: left;
        border-bottom: 1px solid #4a1a1a;
    }
    
    .main-header h1 {
        color: #fdf2f2;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        font-family: 'Source Sans Pro', sans-serif;
        letter-spacing: -0.75px;
    }
    
    .main-header p {
        color: #d69e9e;
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
        font-weight: 400;
    }
    
    /* Recipe cards - Sleek dark red flat */
    .recipe-card {
        background: transparent;
        border: none;
        border-radius: 0;
        padding: 1.5rem 0;
        margin: 0;
        border-bottom: 1px solid #4a1a1a;
        transition: background-color 0.2s ease;
    }
    
    .recipe-card:hover {
        background: rgba(74, 26, 26, 0.1);
        transform: none;
        box-shadow: none;
        border-color: #5a2020;
    }
    
    .recipe-card:last-child {
        border-bottom: none;
    }
    
    /* Input styling - Dark red theme */
    .stTextArea textarea {
        background: #2a1010 !important;
        border: 1px solid #5a2020 !important;
        border-radius: 8px !important;
        padding: 1rem !important;
        font-size: 14px !important;
        font-family: 'Inter', sans-serif !important;
        color: #f3e8e8 !important;
        transition: border-color 0.2s ease !important;
        line-height: 1.5 !important;
        box-shadow: none !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #dc2626 !important;
        background: #2a1010 !important;
        box-shadow: none !important;
        outline: none !important;
    }
    
    .stTextArea textarea::placeholder {
        color: #a87070 !important;
    }
    
    /* Text input styling */
    .stTextInput > div > div > input {
        background: #2a1010 !important;
        border: 1px solid #5a2020 !important;
        border-radius: 8px !important;
        padding: 0.75rem 1rem !important;
        font-size: 14px !important;
        font-family: 'Inter', sans-serif !important;
        color: #f3e8e8 !important;
        transition: border-color 0.2s ease !important;
        box-shadow: none !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #a87070 !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #dc2626 !important;
        background: #2a1010 !important;
        box-shadow: none !important;
        outline: none !important;
    }
    
    /* Button styling - Sleek red accent */
    .stButton > button {
        background: #dc2626 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.75rem 1.5rem !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        transition: background-color 0.2s ease !important;
        box-shadow: none !important;
        letter-spacing: 0.025em !important;
    }
    
    .stButton > button:hover {
        background: #b91c1c !important;
        transform: none !important;
        box-shadow: none !important;
    }
    
    /* Headers and text - Dark red theme */
    h1, h2, h3 {
        font-family: 'Source Sans Pro', sans-serif !important;
        color: #fdf2f2 !important;
        font-weight: 600 !important;
        letter-spacing: -0.5px !important;
        margin-bottom: 0.5rem !important;
    }
    
    h1 {
        font-size: 1.875rem !important;
    }
    
    h2 {
        font-size: 1.5rem !important;
        color: #f3e8e8 !important;
    }
    
    h3 {
        font-size: 1.25rem !important;
        color: #e8d5d5 !important;
    }
    
    p, div, span, label {
        color: #d69e9e !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 14px !important;
        line-height: 1.5 !important;
    }
    
    /* Sidebar styling - Dark red theme */
    .css-1d391kg {
        background: #2a1010 !important;
        border-right: 1px solid #4a1a1a !important;
    }
    
    .css-1d391kg .css-1v0mbdj {
        color: #f3e8e8 !important;
    }
    
    /* Tags - Dark red theme */
    .ingredient-tag {
        background: #3f1e1e;
        color: #f9cccc;
        padding: 0.25rem 0.75rem;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 500;
        margin: 0.125rem;
        display: inline-block;
        border: 1px solid #5c2626;
    }
    
    .missing-tag {
        background: #451a03;
        color: #fed7aa;
        padding: 0.25rem 0.75rem;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 500;
        margin: 0.125rem;
        display: inline-block;
        border: 1px solid #9a3412;
    }
    
    /* Dark red themed components */
    .stSuccess, .stInfo, .stWarning, .stError {
        background: #2a1010 !important;
        border: 1px solid #5a2020 !important;
        border-radius: 8px !important;
        color: #f3e8e8 !important;
        box-shadow: none !important;
    }
    
    /* Select and other inputs - Dark red theme */
    .stSelectbox > div > div {
        background: #2a1010 !important;
        border: 1px solid #5a2020 !important;
        border-radius: 8px !important;
        color: #f3e8e8 !important;
        box-shadow: none !important;
    }
    
    .stNumberInput > div > div > input {
        background: #2a1010 !important;
        border: 1px solid #5a2020 !important;
        border-radius: 8px !important;
        color: #f3e8e8 !important;
        box-shadow: none !important;
    }
    
    .stMultiSelect > div > div {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%) !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 10px !important;
        box-shadow: 0 1px 3px rgba(30, 41, 59, 0.05) !important;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Cool scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f5f9;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #94a3b8, #64748b);
        border-radius: 3px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #64748b, #475569);
    }
    
    /* Spacing adjustments */
    .stContainer > div {
        padding-top: 0.5rem !important;
    }
    
    /* Cool links */
    a {
        color: #3b82f6 !important;
        text-decoration: none !important;
        transition: color 0.2s ease !important;
    }
    
    a:hover {
        color: #1d4ed8 !important;
        text-decoration: underline !important;
    }
    
    /* Remove any remaining visual noise */
    .stAlert {
        background: #2a1010 !important;
        border: 1px solid #5a2020 !important;
        border-radius: 6px !important;
        box-shadow: none !important;
        color: #f3e8e8 !important;
    }
    
    /* Minimal metric displays */
    [data-testid="metric-container"] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0.5rem 0 !important;
    }
    
    /* Remove expander styling */
    .streamlit-expanderHeader {
        background: transparent !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 6px !important;
    }
    
    /* Clean columns */
    .stColumn {
        background: transparent !important;
        padding: 0.25rem !important;
    }
    
    /* Remove any card-like styling */
    .element-container > div {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
</style>
""", unsafe_allow_html=True)

def get_session_id():
    """Generate a unique session ID for the user"""
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    return st.session_state.session_id

# Initialize session state
if 'user_id' not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())
if 'current_recipes' not in st.session_state:
    st.session_state.current_recipes = []
if 'current_ingredients' not in st.session_state:
    st.session_state.current_ingredients = []

def main():
    # Clean, professional header
    st.markdown("""
    <div class="main-header">
        <h1>What's In My Fridge</h1>
        <p>Find recipes based on your available ingredients</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Clean sidebar navigation
    with st.sidebar:
        st.markdown("### Navigation")
        page = st.selectbox(
            "",
            ["Find Recipes", "Recipe History", "Favorites", "Settings"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Clean stats without emojis
        st.markdown("### Statistics")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Searches", len(st.session_state.get('search_history', [])))
        with col2:
            st.metric("Favorites", len(st.session_state.get('favorites', [])))
    
    if page == "Find Recipes":
        show_recipe_finder()
    elif page == "Recipe History":
        show_history()
    elif page == "Favorites":
        show_favorites()
    elif page == "Settings":
        show_settings()

def show_recipe_finder():
    # Clean section header
    st.markdown("""
    <div style="padding: 1.5rem 0; border-bottom: 1px solid #e5e7eb; margin-bottom: 2rem;">
        <h2 style="color: #1a202c; margin: 0; font-weight: 600;">Recipe Discovery</h2>
        <p style="color: #6b7280; margin: 0.5rem 0 0 0;">
            Enter your available ingredients to find matching recipes
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Clean instructions
    with st.expander("How to get the best results", expanded=False):
        st.markdown("""
        <div style="padding: 1rem;">
            <h4>Tips for Best Results</h4>
            <ul>
                <li><strong>Be natural:</strong> "leftover chicken, half bell pepper, some cheese"</li>
                <li><strong>Include variety:</strong> Mix proteins, vegetables, and pantry items</li>
                <li><strong>Don't worry about amounts:</strong> We understand "a little" and "some"</li>
                <li><strong>Use common names:</strong> "mozz" works just as well as "mozzarella"</li>
            </ul>
            
            <h4>🔗 Accessing Full Recipes</h4>
            <ul>
                <li><strong>Click recipe links:</strong> They open in a new browser tab</li>
                <li><strong>Use the big blue button:</strong> "View Full Recipe & Instructions"</li>
                <li><strong>If links don't work:</strong> Try right-click → "Open in new tab"</li>
                <li><strong>Mobile users:</strong> Long press the link to open</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Ingredient input with enhanced styling
    st.markdown("### What's in your kitchen?")
    
    ingredient_input = st.text_area(
        "",
        placeholder="e.g., eggs, leftover chicken, half a bell pepper, shredded mozzarella cheese, spinach...",
        height=120,
        help="Type ingredients separated by commas. Be as natural as you like!",
        label_visibility="collapsed"
    )
    
    # Search options
    st.markdown("### Customize Your Search")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        max_recipes = st.slider("Number of recipes:", 5, 20, 10)
    
    with col2:
        meal_type = st.selectbox(
            "Meal type:",
            ["Any", "Breakfast", "Lunch", "Dinner", "Dessert"]
        )
    
    with col3:
        cuisine_filter = st.selectbox(
            "Cuisine:",
            ["Any", "Italian", "Mexican", "Asian", "American", "Mediterranean", "Indian"]
        )
    
    with col4:
        diet_filter = st.selectbox(
            "Diet:",
            ["Any", "Vegetarian", "Vegan", "Gluten-Free", "Keto"]
        )
    
    # Clean search button
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        search_clicked = st.button(
            "Find Recipes", 
            type="primary", 
            use_container_width=True
        )
    
    if search_clicked:
        if ingredient_input.strip():
            search_recipes(ingredient_input, max_recipes, meal_type, cuisine_filter, diet_filter)
        else:
            st.error("Please enter your available ingredients first.")
    
    # Display current recipes if any
    if st.session_state.current_recipes:
        display_recipes(st.session_state.current_recipes)

def search_recipes(ingredient_input: str, max_recipes: int, meal_type: str, cuisine_filter: str, diet_filter: str = "Any"):
    """Search for recipes based on user input"""
    
    with st.spinner("Understanding your ingredients..."):
        # Normalize ingredients using NLP
        try:
            normalized_ingredients = normalize_ingredients(ingredient_input)
            st.session_state.current_ingredients = normalized_ingredients
            
            # Show processed ingredients with clean styling
            if normalized_ingredients:
                ingredient_tags = ""
                for ing in normalized_ingredients:
                    ingredient_tags += f'<span class="ingredient-tag">{ing}</span>'
                
                st.markdown(f"""
                <div style="padding: 1rem; background: #f0fff4; border: 1px solid #c6f6d5; border-radius: 6px; margin: 1rem 0;">
                    <h4>Found these ingredients:</h4>
                    {ingredient_tags}
                </div>
                """, unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"Error processing ingredients: {str(e)}")
            return
    
    with st.spinner("Finding recipes for you..."):
        try:
            # Create cache key including meal type
            cache_key = hashlib.md5(
                f"{','.join(sorted(normalized_ingredients))}_{max_recipes}_{meal_type}_{cuisine_filter}_{diet_filter}".encode()
            ).hexdigest()
            
            # Try to get from cache first
            cached_recipes = get_cached_recipes(cache_key)
            
            if cached_recipes:
                st.success("Found cached results")
                recipes = cached_recipes
            else:
                # Fetch from API with meal type
                recipes = fetch_recipes(
                    ingredients=normalized_ingredients,
                    max_results=max_recipes,
                    meal_type=meal_type if meal_type != "Any" else None,
                    cuisine=cuisine_filter if cuisine_filter != "Any" else None
                )
                
                # Cache the results
                store_cached_recipes(cache_key, recipes)
            
            if recipes:
                # Rank recipes based on user preferences (if available)
                ranked_recipes = rank_recipes(recipes, st.session_state.user_id)
                st.session_state.current_recipes = ranked_recipes
                
                # Success message
                st.markdown(f"""
                <div style="padding: 1rem; background: #f0fff4; border: 1px solid #c6f6d5; border-radius: 6px; margin: 1rem 0;">
                    <h3>Found {len(ranked_recipes)} recipes</h3>
                    <p>Ranked by how well they match your ingredients and preferences</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("No recipes found with those ingredients. Try different ingredients or check your API configuration.")
                
        except Exception as e:
            st.error(f"Error fetching recipes: {str(e)}")

def display_recipes(recipes: List[Dict]):
    """Display recipe results in a clean list"""
    
    st.markdown(f"""
    <div style="padding: 1.5rem 0; border-bottom: 1px solid #e5e7eb; margin-bottom: 1rem;">
        <h2 style="color: #1a202c; margin: 0; font-weight: 600;">
            Recipe Suggestions ({len(recipes)} found)
        </h2>
        <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0;">
            Scroll through these delicious options crafted just for you! 
            <strong>Click recipe titles to view full instructions.</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create a more sophisticated grid layout
    for i in range(0, len(recipes), 2):
        col1, col2 = st.columns(2, gap="large")
        
        with col1:
            if i < len(recipes):
                display_recipe_card(recipes[i], i)
        
        with col2:
            if i + 1 < len(recipes):
                display_recipe_card(recipes[i + 1], i + 1)

def display_recipe_card(recipe: Dict, idx: int):
    """Display individual recipe card with enhanced styling"""
    
    st.markdown(f"""
    <div class="recipe-card">
        <div style="margin-bottom: 1rem;">
    """, unsafe_allow_html=True)
    
    # Recipe image with better styling
    if recipe.get('image'):
        st.image(recipe['image'], use_container_width=True)
    
    # Recipe title with gradient
    title = recipe.get('title', 'Unknown Recipe')
    st.markdown(f"""
        <h3 style="background: linear-gradient(45deg, #667eea, #764ba2); 
                   background-clip: text; -webkit-background-clip: text; 
                   -webkit-text-fill-color: transparent; font-weight: 600; 
                   margin: 1rem 0 0.5rem 0;">{title}</h3>
    """, unsafe_allow_html=True)
    
    # Recipe metrics in a beautiful layout
    col1, col2, col3 = st.columns(3)
    with col1:
        if recipe.get('readyInMinutes'):
            st.markdown(f"""
            <div class="metric-container">
                <div style="font-size: 14px; color: #6b7280;">Time</div>
                <div style="font-size: 1.2rem; font-weight: 600;">{recipe['readyInMinutes']}</div>
                <div style="font-size: 0.8rem;">minutes</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        if recipe.get('servings'):
            st.markdown(f"""
            <div class="metric-container">
                <div style="font-size: 1.5rem;">👥</div>
                <div style="font-size: 1.2rem; font-weight: 600;">{recipe['servings']}</div>
                <div style="font-size: 0.8rem;">servings</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        health_score = recipe.get('healthScore')
        if health_score and health_score > 0:
            st.markdown(f"""
            <div class="metric-container">
                <div style="font-size: 1.5rem;">💚</div>
                <div style="font-size: 1.2rem; font-weight: 600;">{health_score}</div>
                <div style="font-size: 0.8rem;">health</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Show recipe difficulty instead if no health score
            difficulty = "Easy" if recipe.get('readyInMinutes', 60) <= 30 else "Medium"
            st.markdown(f"""
            <div class="metric-container">
                <div style="font-size: 14px; color: #6b7280;">Health</div>
                <div style="font-size: 1.2rem; font-weight: 600;">{difficulty}</div>
                <div style="font-size: 0.8rem;">difficulty</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Ingredients with beautiful tags
    if recipe.get('usedIngredients'):
        used = [ing.get('name', ing.get('original', '')) for ing in recipe['usedIngredients']]
        used_tags = ""
        for ing in used[:4]:  # Show max 4 ingredients
            used_tags += f'<span class="ingredient-tag">✅ {ing}</span>'
        
        st.markdown(f"""
        <div style="margin: 1rem 0;">
            <strong>Using your ingredients:</strong><br>
            {used_tags}
        </div>
        """, unsafe_allow_html=True)
    
    # Missing ingredients
    if recipe.get('missedIngredients'):
        missed = [ing.get('name', ing.get('original', '')) for ing in recipe['missedIngredients']]
        if missed:
            missed_tags = ""
            for ing in missed[:3]:  # Show max 3 missing ingredients
                missed_tags += f'<span class="missing-tag">{ing}</span>'
            
            st.markdown(f"""
            <div style="margin: 1rem 0;">
                <strong>�️ You'll also need:</strong><br>
                {missed_tags}
            </div>
            """, unsafe_allow_html=True)
    
    # Action buttons with enhanced styling
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("👍", key=f"like_{idx}", help="Love this recipe!"):
            save_user_feedback(st.session_state.user_id, recipe['id'], 'like')
            st.success("❤️ Liked!")
    
    with col2:
        if st.button("⭐", key=f"save_{idx}", help="Save to favorites"):
            save_recipe_to_favorites(st.session_state.user_id, recipe)
            st.success("💾 Saved!")
    
    with col3:
        if st.button("👎", key=f"dislike_{idx}", help="Not for me"):
            save_user_feedback(st.session_state.user_id, recipe['id'], 'dislike')
            st.success("👌 Thanks!")
    
    with col4:
        if recipe.get('sourceUrl'):
            st.markdown(f"""
            <a href="{recipe['sourceUrl']}" target="_blank" rel="noopener noreferrer" style="
                display: inline-block; background: linear-gradient(45deg, #4facfe, #00f2fe);
                color: white; padding: 0.5rem 1rem; border-radius: 20px; 
                text-decoration: none; font-weight: 600; text-align: center;
                transition: transform 0.2s ease;">
                🔗 Recipe
            </a>
            """, unsafe_allow_html=True)
        else:
            st.markdown("🔗 *No link available*")
    
    # Add a more prominent full recipe button
    if recipe.get('sourceUrl'):
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="text-align: center; margin: 1rem 0;">
            <a href="{recipe['sourceUrl']}" target="_blank" rel="noopener noreferrer" style="
                display: inline-block; 
                background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
                color: white; 
                padding: 1rem 2rem; 
                border-radius: 30px; 
                text-decoration: none; 
                font-weight: 700;
                font-size: 1.1rem;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                transition: all 0.3s ease;
                text-transform: uppercase;
                letter-spacing: 1px;">
                View Full Recipe
            </a>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div></div>", unsafe_allow_html=True)

def show_history():
    """Show user's recipe history with enhanced styling"""
    st.markdown("""
    <div style="background: linear-gradient(90deg, #a8edea 0%, #fed6e3 100%); 
                padding: 1.5rem; border-radius: 15px; margin: 2rem 0;">
        <h2 style="color: #333; margin: 0; font-weight: 600;">Your Recipe History</h2>
        <p style="color: #555; margin: 0.5rem 0 0 0;">
            Track your culinary adventures and discoveries
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    history = get_user_history(st.session_state.user_id)
    
    if history:
        st.markdown(f"""
        <div class="success-message">
            <h4>🎉 You've been busy in the kitchen!</h4>
            <p>You've searched for recipes <strong>{len(history)} times</strong> - keep exploring!</p>
        </div>
        """, unsafe_allow_html=True)
        
        for i, entry in enumerate(history[-10:]):  # Show last 10 searches
            ingredients = entry.get('ingredients', [])
            ingredients_display = ', '.join(ingredients[:4])
            if len(ingredients) > 4:
                ingredients_display += f" and {len(ingredients)-4} more"
            
            st.markdown(f"""
            <div class="recipe-card" style="margin: 1rem 0;">
                <h4>🔍 Search #{len(history)-i}</h4>
                <p><strong>🥘 Ingredients:</strong> {ingredients_display}</p>
                <p><strong>📅 Date:</strong> {entry.get('timestamp', 'Unknown date')}</p>
                <p><strong>🍽️ Recipes found:</strong> {entry.get('recipe_count', 0)}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="info-box">
            <h4>🌟 Ready to start your culinary journey?</h4>
            <p>No search history yet! Head over to the Recipe Finder to discover amazing meals with your ingredients.</p>
        </div>
        """, unsafe_allow_html=True)

def show_favorites():
    """Show user's favorite recipes with enhanced styling"""
    st.markdown("""
    <div style="background: linear-gradient(90deg, #ffecd2 0%, #fcb69f 100%); 
                padding: 1.5rem; border-radius: 15px; margin: 2rem 0;">
        <h2 style="color: #333; margin: 0; font-weight: 600;">⭐ Your Favorite Recipes</h2>
        <p style="color: #555; margin: 0.5rem 0 0 0;">
            Your collection of beloved culinary creations
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    favorites = get_user_favorites(st.session_state.user_id)
    
    if favorites:
        st.markdown(f"""
        <div class="success-message">
            <h4>❤️ You have {len(favorites)} favorite recipes!</h4>
            <p>These are the recipes that captured your heart</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Display favorites in a grid
        for i in range(0, len(favorites), 2):
            col1, col2 = st.columns(2, gap="large")
            
            with col1:
                if i < len(favorites):
                    display_favorite_card(favorites[i], i)
            
            with col2:
                if i + 1 < len(favorites):
                    display_favorite_card(favorites[i + 1], i + 1)
    else:
        st.markdown("""
        <div class="info-box">
            <h4>💝 Start building your recipe collection!</h4>
            <p>No favorite recipes yet! When you find recipes you love, click the ⭐ button to save them here.</p>
        </div>
        """, unsafe_allow_html=True)

def display_favorite_card(recipe: Dict, idx: int):
    """Display a favorite recipe card"""
    st.markdown(f"""
    <div class="recipe-card">
    """, unsafe_allow_html=True)
    
    if recipe.get('image'):
        st.image(recipe['image'], use_container_width=True)
    
    title = recipe.get('title', 'Unknown Recipe')
    st.markdown(f"""
    <h4 style="color: #667eea; font-weight: 600; margin: 1rem 0 0.5rem 0;">{title}</h4>
    """, unsafe_allow_html=True)
    
    # Recipe details
    col1, col2 = st.columns(2)
    with col1:
        if recipe.get('readyInMinutes'):
            st.markdown(f"**{recipe['readyInMinutes']} min**")
    with col2:
        if recipe.get('servings'):
            st.markdown(f"👥 **{recipe['servings']} servings**")
    
    # Recipe link
    if recipe.get('sourceUrl'):
        st.markdown(f"""
        <div style="text-align: center; margin-top: 1rem;">
            <a href="{recipe['sourceUrl']}" target="_blank" rel="noopener noreferrer" style="
                display: inline-block; background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
                color: white; padding: 0.75rem 1.5rem; border-radius: 25px; 
                text-decoration: none; font-weight: 600; 
                transition: all 0.3s ease;">
                � View Full Recipe
            </a>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

def show_settings():
    """Show app settings with enhanced styling"""
    st.markdown("""
    <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
                padding: 1.5rem; border-radius: 15px; margin: 2rem 0;">
        <h2 style="color: white; margin: 0; font-weight: 600;">⚙️ Settings & Preferences</h2>
        <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0;">
            Customize your recipe discovery experience
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Dietary Preferences with enhanced styling
    st.markdown("### 🥗 Dietary Preferences")
    
    col1, col2 = st.columns(2)
    with col1:
        vegetarian = st.checkbox("🥬 Vegetarian", help="Exclude meat and fish")
        vegan = st.checkbox("🌱 Vegan", help="Exclude all animal products")
        keto = st.checkbox("🥑 Keto", help="Low-carb, high-fat recipes")
    
    with col2:
        gluten_free = st.checkbox("🌾 Gluten Free", help="Exclude gluten-containing ingredients")
        dairy_free = st.checkbox("🥛 Dairy Free", help="Exclude dairy products")
        low_sodium = st.checkbox("🧂 Low Sodium", help="Heart-healthy options")
    
    st.markdown("### 🍳 Cooking Preferences")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        max_prep_time = st.slider("⏰ Max prep time (minutes):", 10, 120, 60)
    
    with col2:
        difficulty = st.selectbox(
            "Difficulty level:", 
            ["Any", "Easy", "Medium", "Hard"]
        )
    
    with col3:
        meal_type = st.selectbox(
            "🍽️ Preferred meal type:",
            ["Any", "Breakfast", "Lunch", "Dinner", "Snack", "Dessert"]
        )
    
    # Save preferences button
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("💾 Save Preferences", type="primary", use_container_width=True):
        preferences = {
            'vegetarian': vegetarian,
            'vegan': vegan,
            'keto': keto,
            'gluten_free': gluten_free,
            'dairy_free': dairy_free,
            'low_sodium': low_sodium,
            'max_prep_time': max_prep_time,
            'difficulty': difficulty,
            'meal_type': meal_type
        }
        save_user_preferences(st.session_state.user_id, preferences)
        st.success("🎉 Preferences saved successfully!")
    
    st.markdown("---")
    
    # App info with beautiful styling
    st.markdown("### ℹ️ About This App")
    
    st.markdown("""
    <div class="info-box">
        <h4>🍳 What's In My Fridge v1.0</h4>
        <p>An intelligent recipe discovery app powered by AI and machine learning.</p>
        
        <h5>✨ Features:</h5>
        <ul>
            <li>🧠 Natural language ingredient processing</li>
            <li>🤖 Machine learning recipe ranking</li>
            <li>⚡ Smart caching for faster results</li>
            <li>❤️ Personalized recommendations</li>
            <li>🔍 Real-time recipe search</li>
        </ul>
        
        <p><strong>🚀 Built with:</strong> Streamlit, spaCy, scikit-learn, and Spoonacular API</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
