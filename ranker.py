from typing import List, Dict, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.metrics.pairwise import cosine_similarity
import joblib
import os
from db import get_user_feedback, get_user_preferences

class RecipeRanker:
    """Machine learning-based recipe ranking system"""
    
    def __init__(self, model_dir: str = "models"):
        self.model_dir = model_dir
        self.vectorizer = None
        self.classifier = None
        self.model_file = os.path.join(model_dir, "recipe_ranker.pkl")
        
        # Create model directory if it doesn't exist
        os.makedirs(model_dir, exist_ok=True)
        
        # Initialize or load models
        self._load_models()
    
    def _load_models(self):
        """Load existing models or create new ones"""
        try:
            if os.path.exists(self.model_file):
                models = joblib.load(self.model_file)
                self.vectorizer = models.get('vectorizer')
                self.classifier = models.get('classifier')
            else:
                self._initialize_models()
        except Exception as e:
            print(f"Error loading models: {e}")
            self._initialize_models()
    
    def _initialize_models(self):
        """Initialize new ML models"""
        # TF-IDF vectorizer for recipe text features
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            lowercase=True
        )
        
        # SGD Classifier for learning user preferences
        self.classifier = SGDClassifier(
            loss='log_loss',  # For probability estimates
            random_state=42,
            alpha=0.001
        )
    
    def _save_models(self):
        """Save trained models to disk"""
        try:
            models = {
                'vectorizer': self.vectorizer,
                'classifier': self.classifier
            }
            joblib.dump(models, self.model_file)
        except Exception as e:
            print(f"Error saving models: {e}")
    
    def _extract_recipe_features(self, recipe: Dict) -> str:
        """Extract text features from a recipe for ML processing"""
        features = []
        
        # Recipe title
        if recipe.get('title'):
            features.append(recipe['title'])
        
        # Used ingredients
        if recipe.get('usedIngredients'):
            used_ingredients = [ing.get('name', '') for ing in recipe['usedIngredients']]
            features.extend(used_ingredients)
        
        # Recipe summary/description
        if recipe.get('summary'):
            # Remove HTML tags from summary
            import re
            clean_summary = re.sub('<.*?>', '', recipe['summary'])
            features.append(clean_summary)
        
        # Cuisine type
        if recipe.get('cuisine'):
            features.append(recipe['cuisine'])
        
        # Dish types
        if recipe.get('dishTypes'):
            features.extend(recipe['dishTypes'])
        
        # Diet categories
        if recipe.get('diets'):
            features.extend(recipe['diets'])
        
        return ' '.join(features).lower()
    
    def _calculate_base_score(self, recipe: Dict, user_ingredients: List[str]) -> float:
        """Calculate base score based on ingredient matching"""
        if not recipe.get('usedIngredients'):
            return 0.0
        
        used_ingredients = [ing.get('name', '').lower() for ing in recipe['usedIngredients']]
        missed_ingredients = [ing.get('name', '').lower() for ing in recipe.get('missedIngredients', [])]
        
        # Score based on ingredient matching
        ingredient_score = len(used_ingredients) / max(len(user_ingredients), 1)
        
        # Penalty for missing ingredients
        missing_penalty = len(missed_ingredients) * 0.1
        
        # Bonus for health score
        health_bonus = recipe.get('healthScore', 50) / 100.0 * 0.2
        
        # Bonus for quick recipes
        time_bonus = 0.0
        ready_time = recipe.get('readyInMinutes', 60)
        if ready_time <= 30:
            time_bonus = 0.2
        elif ready_time <= 45:
            time_bonus = 0.1
        
        base_score = ingredient_score - missing_penalty + health_bonus + time_bonus
        return max(0.0, min(1.0, base_score))
    
    def rank_recipes(self, recipes: List[Dict], user_id: str, 
                    user_ingredients: List[str] = None) -> List[Dict]:
        """
        Rank recipes based on user preferences and ML model
        
        Args:
            recipes: List of recipe dictionaries
            user_id: User identifier for personalization
            user_ingredients: List of user's ingredients
            
        Returns:
            List of ranked recipes
        """
        if not recipes:
            return recipes
        
        user_ingredients = user_ingredients or []
        
        # Calculate base scores for all recipes
        for recipe in recipes:
            recipe['base_score'] = self._calculate_base_score(recipe, user_ingredients)
        
        # Try to apply ML ranking if we have user data
        try:
            ml_ranked = self._apply_ml_ranking(recipes, user_id)
            if ml_ranked:
                return ml_ranked
        except Exception as e:
            print(f"ML ranking failed, using base ranking: {e}")
        
        # Fallback to rule-based ranking
        return self._apply_rule_based_ranking(recipes, user_id)
    
    def _apply_ml_ranking(self, recipes: List[Dict], user_id: str) -> Optional[List[Dict]]:
        """Apply ML-based ranking using trained model"""
        # Get user feedback data
        feedback_data = get_user_feedback(user_id)
        
        if len(feedback_data) < 5:  # Need minimum feedback for ML
            return None
        
        # Extract features for current recipes
        recipe_features = []
        for recipe in recipes:
            features = self._extract_recipe_features(recipe)
            recipe_features.append(features)
        
        if not recipe_features:
            return None
        
        # Transform features using vectorizer
        try:
            if hasattr(self.vectorizer, 'vocabulary_'):
                # Vectorizer is already fitted
                X = self.vectorizer.transform(recipe_features)
            else:
                # Need to fit vectorizer first (shouldn't happen in normal flow)
                return None
            
            # Get ML scores
            if hasattr(self.classifier, 'coef_'):
                ml_scores = self.classifier.predict_proba(X)[:, 1]  # Probability of positive class
            else:
                return None
            
            # Combine ML scores with base scores
            for i, recipe in enumerate(recipes):
                ml_score = ml_scores[i] if i < len(ml_scores) else 0.5
                base_score = recipe.get('base_score', 0.5)
                
                # Weighted combination
                recipe['ml_score'] = ml_score
                recipe['final_score'] = 0.6 * base_score + 0.4 * ml_score
            
            # Sort by final score
            return sorted(recipes, key=lambda r: r.get('final_score', 0), reverse=True)
            
        except Exception as e:
            print(f"Error in ML ranking: {e}")
            return None
    
    def _apply_rule_based_ranking(self, recipes: List[Dict], user_id: str) -> List[Dict]:
        """Apply rule-based ranking using user preferences"""
        # Get user preferences
        preferences = get_user_preferences(user_id)
        
        # Apply preference-based adjustments
        for recipe in recipes:
            score = recipe.get('base_score', 0.5)
            
            # Dietary preferences
            if preferences.get('vegetarian') and self._is_vegetarian(recipe):
                score += 0.1
            if preferences.get('vegan') and self._is_vegan(recipe):
                score += 0.1
            if preferences.get('gluten_free') and self._is_gluten_free(recipe):
                score += 0.1
            
            # Time preferences
            max_time = preferences.get('max_prep_time', 60)
            recipe_time = recipe.get('readyInMinutes', 60)
            if recipe_time <= max_time:
                score += 0.05
            
            # Cuisine preferences
            preferred_cuisines = preferences.get('preferred_cuisines', [])
            recipe_cuisines = recipe.get('cuisines', [])
            if any(cuisine in preferred_cuisines for cuisine in recipe_cuisines):
                score += 0.1
            
            recipe['final_score'] = min(1.0, score)
        
        # Sort by final score
        return sorted(recipes, key=lambda r: r.get('final_score', 0), reverse=True)
    
    def _is_vegetarian(self, recipe: Dict) -> bool:
        """Check if recipe is vegetarian"""
        diets = [d.lower() for d in recipe.get('diets', [])]
        return 'vegetarian' in diets or 'vegan' in diets
    
    def _is_vegan(self, recipe: Dict) -> bool:
        """Check if recipe is vegan"""
        diets = [d.lower() for d in recipe.get('diets', [])]
        return 'vegan' in diets
    
    def _is_gluten_free(self, recipe: Dict) -> bool:
        """Check if recipe is gluten-free"""
        diets = [d.lower() for d in recipe.get('diets', [])]
        return 'gluten free' in diets or 'gluten-free' in diets
    
    def train_on_feedback(self, user_id: str):
        """Train the ML model based on user feedback"""
        try:
            feedback_data = get_user_feedback(user_id)
            
            if len(feedback_data) < 10:  # Need minimum data for training
                return False
            
            # Prepare training data
            X_text = []
            y = []
            
            for feedback in feedback_data:
                recipe_features = self._extract_recipe_features(feedback['recipe'])
                X_text.append(recipe_features)
                
                # Convert feedback to binary target
                rating = feedback.get('rating', 'neutral')
                y.append(1 if rating in ['like', 'love', 'tried'] else 0)
            
            # Fit vectorizer and transform text
            X = self.vectorizer.fit_transform(X_text)
            
            # Train classifier
            self.classifier.fit(X, y)
            
            # Save trained models
            self._save_models()
            
            return True
            
        except Exception as e:
            print(f"Error training model: {e}")
            return False

# Global ranker instance
ranker_instance = RecipeRanker()

def rank_recipes(recipes: List[Dict], user_id: str, 
                user_ingredients: List[str] = None) -> List[Dict]:
    """
    Main function to rank recipes for a user
    
    Args:
        recipes: List of recipe dictionaries
        user_id: User identifier
        user_ingredients: List of user's ingredients
        
    Returns:
        List of ranked recipes
    """
    return ranker_instance.rank_recipes(recipes, user_id, user_ingredients)

def train_user_model(user_id: str) -> bool:
    """
    Train personalized model for a user
    
    Args:
        user_id: User identifier
        
    Returns:
        True if training successful, False otherwise
    """
    return ranker_instance.train_on_feedback(user_id)
