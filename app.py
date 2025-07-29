import streamlit as st
import time
from typing import List, Dict
from nlp import normalize_ingredients
from api import fetch_recipes
from cache import get_cached_recipes, store_cached_recipes
from ranker import rank_recipes
from db import save_user_feedback, get_user_history, save_recipe_to_favorites, save_user_preferences, get_user_favorites
import uuid
import hashlib

# Page configuration
st.set_page_config(
    page_title="What's In My Fridge",
    page_icon="🍳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced aesthetics
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    /* Global styling */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        font-family: 'Poppins', sans-serif;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(90deg, #ff6b6b, #4ecdc4);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    .main-header h1 {
        color: white;
        font-size: 3rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        color: rgba(255,255,255,0.9);
        font-size: 1.2rem;
        margin: 0.5rem 0 0 0;
        font-weight: 300;
    }
    
    /* Card styling */
    .recipe-card {
        background: white;
        border-radius: 20px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.2);
        backdrop-filter: blur(10px);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .recipe-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.15);
    }
    
    /* Input styling */
    .stTextArea textarea {
        background: rgba(255,255,255,0.9);
        border: 2px solid #e0e0e0;
        border-radius: 15px;
        padding: 1rem;
        font-size: 16px;
        font-family: 'Poppins', sans-serif;
        transition: border-color 0.3s ease;
    }
    
    .stTextArea textarea:focus {
        border-color: #4ecdc4;
        box-shadow: 0 0 20px rgba(78, 205, 196, 0.2);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-size: 16px;
        font-weight: 600;
        font-family: 'Poppins', sans-serif;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    .css-1d391kg .css-1v0mbdj {
        color: white;
    }
    
    /* Metric styling */
    .metric-container {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 1rem;
        border-radius: 15px;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    /* Info boxes */
    .info-box {
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border-left: 5px solid #4ecdc4;
    }
    
    /* Success messages */
    .success-message {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        padding: 1rem;
        border-radius: 15px;
        border-left: 5px solid #4ecdc4;
        margin: 1rem 0;
    }
    
    /* Recipe grid */
    .recipe-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 2rem;
        margin: 2rem 0;
    }
    
    /* Tags */
    .ingredient-tag {
        background: linear-gradient(45deg, #ff9a9e, #fecfef);
        color: #333;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
        margin: 0.2rem;
        display: inline-block;
    }
    
    .missing-tag {
        background: linear-gradient(45deg, #ffecd2, #fcb69f);
        color: #333;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
        margin: 0.2rem;
        display: inline-block;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #764ba2, #667eea);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'user_id' not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())
if 'current_recipes' not in st.session_state:
    st.session_state.current_recipes = []
if 'current_ingredients' not in st.session_state:
    st.session_state.current_ingredients = []

def main():
    # Modern Header with gradient background
    st.markdown("""
    <div class="main-header">
        <h1>🍳 What's In My Fridge</h1>
        <p>Transform your ingredients into culinary masterpieces with AI</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced Sidebar
    with st.sidebar:
        st.markdown("### 🧭 Navigation")
        page = st.selectbox(
            "",
            ["🏠 Find Recipes", "📖 Recipe History", "⭐ Favorites", "⚙️ Settings"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Quick stats in sidebar
        st.markdown("### 📊 Quick Stats")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("🔍", "Searches", len(st.session_state.get('search_history', [])))
        with col2:
            st.metric("❤️", "Favorites", len(st.session_state.get('favorites', [])))
    
    if page == "🏠 Find Recipes":
        show_recipe_finder()
    elif page == "📖 Recipe History":
        show_history()
    elif page == "⭐ Favorites":
        show_favorites()
    elif page == "⚙️ Settings":
        show_settings()

def show_recipe_finder():
    # Modern section header
    st.markdown("""
    <div style="background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%); 
                padding: 1.5rem; border-radius: 15px; margin: 2rem 0;">
        <h2 style="color: white; margin: 0; font-weight: 600;">🔍 Recipe Discovery</h2>
        <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0;">
            Tell us what ingredients you have, and we'll find amazing recipes for you!
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced instructions with better styling
    with st.expander("💡 How to get the best results", expanded=False):
        st.markdown("""
        <div class="info-box">
            <h4>🎯 Tips for Perfect Results</h4>
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
    st.markdown("### 🥘 What's in your kitchen?")
    
    ingredient_input = st.text_area(
        "",
        placeholder="e.g., eggs, leftover chicken, half a bell pepper, shredded mozzarella cheese, spinach...",
        height=120,
        help="💡 Type ingredients separated by commas. Be as natural as you like!",
        label_visibility="collapsed"
    )
    
    # Enhanced search options in columns
    st.markdown("### ⚙️ Customize Your Search")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        max_recipes = st.slider("🔢 Number of recipes:", 5, 20, 10)
    
    with col2:
        cuisine_filter = st.selectbox(
            "🌍 Cuisine:",
            ["Any", "Italian", "Mexican", "Asian", "American", "Mediterranean", "Indian"]
        )
    
    with col3:
        diet_filter = st.selectbox(
            "🥗 Diet:",
            ["Any", "Vegetarian", "Vegan", "Gluten-Free", "Keto"]
        )
    
    # Enhanced search button
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        search_clicked = st.button(
            "🔍 Discover Amazing Recipes", 
            type="primary", 
            use_container_width=True
        )
    
    if search_clicked:
        if ingredient_input.strip():
            search_recipes(ingredient_input, max_recipes, cuisine_filter, diet_filter)
        else:
            st.error("🥺 Please tell us what ingredients you have first!")
    
    # Display current recipes if any
    if st.session_state.current_recipes:
        display_recipes(st.session_state.current_recipes)

def search_recipes(ingredient_input: str, max_recipes: int, cuisine_filter: str, diet_filter: str = "Any"):
    """Search for recipes based on user input"""
    
    with st.spinner("🧠 Understanding your ingredients..."):
        # Normalize ingredients using NLP
        try:
            normalized_ingredients = normalize_ingredients(ingredient_input)
            st.session_state.current_ingredients = normalized_ingredients
            
            # Show processed ingredients with enhanced styling
            if normalized_ingredients:
                ingredient_tags = ""
                for ing in normalized_ingredients:
                    ingredient_tags += f'<span class="ingredient-tag">🥘 {ing}</span>'
                
                st.markdown(f"""
                <div class="success-message">
                    <h4>✨ We found these ingredients:</h4>
                    {ingredient_tags}
                </div>
                """, unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"😅 Oops! Error processing ingredients: {str(e)}")
            return
    
    with st.spinner("🍳 Finding amazing recipes just for you..."):
        try:
            # Create cache key
            cache_key = hashlib.md5(
                f"{','.join(sorted(normalized_ingredients))}_{max_recipes}_{cuisine_filter}_{diet_filter}".encode()
            ).hexdigest()
            
            # Try to get from cache first
            cached_recipes = get_cached_recipes(cache_key)
            
            if cached_recipes:
                st.success("⚡ Found cached results - lightning fast!")
                recipes = cached_recipes
            else:
                # Fetch from API
                recipes = fetch_recipes(
                    ingredients=normalized_ingredients,
                    max_results=max_recipes,
                    cuisine=cuisine_filter if cuisine_filter != "Any" else None
                )
                
                # Cache the results
                store_cached_recipes(cache_key, recipes)
            
            if recipes:
                # Rank recipes based on user preferences (if available)
                ranked_recipes = rank_recipes(recipes, st.session_state.user_id)
                st.session_state.current_recipes = ranked_recipes
                
                # Enhanced success message
                st.markdown(f"""
                <div class="success-message">
                    <h3>🎉 Found {len(ranked_recipes)} delicious recipes!</h3>
                    <p>Ranked by how well they match your ingredients and preferences</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("😔 No recipes found with those ingredients. Try different ingredients or check your API configuration.")
                
        except Exception as e:
            st.error(f"😰 Error fetching recipes: {str(e)}")

def display_recipes(recipes: List[Dict]):
    """Display recipe results in a beautiful grid"""
    
    st.markdown(f"""
    <div style="background: linear-gradient(90deg, #ff9a9e 0%, #fecfef 100%); 
                padding: 1.5rem; border-radius: 15px; margin: 2rem 0;">
        <h2 style="color: white; margin: 0; font-weight: 600;">
            🍽️ Recipe Suggestions ({len(recipes)} found)
        </h2>
        <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0;">
            Scroll through these delicious options crafted just for you! 
            <strong>Click the "📖 View Full Recipe" buttons to get complete instructions.</strong>
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
                <div style="font-size: 1.5rem;">⏱️</div>
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
        health_score = recipe.get('healthScore', 50)
        st.markdown(f"""
        <div class="metric-container">
            <div style="font-size: 1.5rem;">💚</div>
            <div style="font-size: 1.2rem; font-weight: 600;">{health_score}</div>
            <div style="font-size: 0.8rem;">health</div>
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
            <strong>🎯 Using your ingredients:</strong><br>
            {used_tags}
        </div>
        """, unsafe_allow_html=True)
    
    # Missing ingredients
    if recipe.get('missedIngredients'):
        missed = [ing.get('name', ing.get('original', '')) for ing in recipe['missedIngredients']]
        if missed:
            missed_tags = ""
            for ing in missed[:3]:  # Show max 3 missing ingredients
                missed_tags += f'<span class="missing-tag">🛒 {ing}</span>'
            
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
                📖 View Full Recipe & Instructions
            </a>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div></div>", unsafe_allow_html=True)

def show_history():
    """Show user's recipe history with enhanced styling"""
    st.markdown("""
    <div style="background: linear-gradient(90deg, #a8edea 0%, #fed6e3 100%); 
                padding: 1.5rem; border-radius: 15px; margin: 2rem 0;">
        <h2 style="color: #333; margin: 0; font-weight: 600;">📖 Your Recipe Journey</h2>
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
            st.markdown(f"⏱️ **{recipe['readyInMinutes']} min**")
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
            "📊 Difficulty level:", 
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
