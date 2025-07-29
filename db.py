from tinydb import TinyDB, Query
from typing import Dict, List, Optional
import os
import time
import uuid

class DatabaseManager:
    """Simple database manager using TinyDB for local storage"""
    
    def __init__(self, db_path: str = "data/app_database.json"):
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.db = TinyDB(db_path)
        
        # Create tables
        self.users = self.db.table('users')
        self.feedback = self.db.table('feedback')
        self.favorites = self.db.table('favorites')
        self.search_history = self.db.table('search_history')
        self.preferences = self.db.table('preferences')
    
    def save_user_feedback(self, user_id: str, recipe_id: int, rating: str, 
                          recipe_data: Optional[Dict] = None):
        """
        Save user feedback for a recipe
        
        Args:
            user_id: User identifier
            recipe_id: Recipe ID
            rating: Rating ('like', 'dislike', 'love', 'tried', etc.)
            recipe_data: Optional full recipe data
        """
        feedback_entry = {
            'user_id': user_id,
            'recipe_id': recipe_id,
            'rating': rating,
            'timestamp': time.time(),
            'recipe': recipe_data
        }
        
        # Check if feedback already exists for this user/recipe combo
        Feedback = Query()
        existing = self.feedback.search(
            (Feedback.user_id == user_id) & (Feedback.recipe_id == recipe_id)
        )
        
        if existing:
            # Update existing feedback
            self.feedback.update(
                {'rating': rating, 'timestamp': time.time()},
                (Feedback.user_id == user_id) & (Feedback.recipe_id == recipe_id)
            )
        else:
            # Insert new feedback
            self.feedback.insert(feedback_entry)
    
    def get_user_feedback(self, user_id: str) -> List[Dict]:
        """
        Get all feedback for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            List of feedback entries
        """
        Feedback = Query()
        return self.feedback.search(Feedback.user_id == user_id)
    
    def save_recipe_to_favorites(self, user_id: str, recipe: Dict):
        """
        Save a recipe to user's favorites
        
        Args:
            user_id: User identifier
            recipe: Recipe dictionary
        """
        favorite_entry = {
            'user_id': user_id,
            'recipe_id': recipe.get('id'),
            'recipe': recipe,
            'timestamp': time.time()
        }
        
        # Check if already in favorites
        Favorite = Query()
        existing = self.favorites.search(
            (Favorite.user_id == user_id) & (Favorite.recipe_id == recipe.get('id'))
        )
        
        if not existing:
            self.favorites.insert(favorite_entry)
    
    def get_user_favorites(self, user_id: str) -> List[Dict]:
        """
        Get user's favorite recipes
        
        Args:
            user_id: User identifier
            
        Returns:
            List of favorite recipes
        """
        Favorite = Query()
        favorites = self.favorites.search(Favorite.user_id == user_id)
        return [fav['recipe'] for fav in favorites]
    
    def remove_from_favorites(self, user_id: str, recipe_id: int):
        """
        Remove a recipe from user's favorites
        
        Args:
            user_id: User identifier
            recipe_id: Recipe ID to remove
        """
        Favorite = Query()
        self.favorites.remove(
            (Favorite.user_id == user_id) & (Favorite.recipe_id == recipe_id)
        )
    
    def save_search_history(self, user_id: str, ingredients: List[str], 
                           recipes_found: int, search_params: Optional[Dict] = None):
        """
        Save a search to user's history
        
        Args:
            user_id: User identifier
            ingredients: List of ingredients searched
            recipes_found: Number of recipes found
            search_params: Optional search parameters
        """
        history_entry = {
            'user_id': user_id,
            'ingredients': ingredients,
            'recipe_count': recipes_found,
            'timestamp': time.time(),
            'search_params': search_params or {}
        }
        
        self.search_history.insert(history_entry)
    
    def get_user_history(self, user_id: str, limit: int = 50) -> List[Dict]:
        """
        Get user's search history
        
        Args:
            user_id: User identifier
            limit: Maximum number of entries to return
            
        Returns:
            List of search history entries
        """
        History = Query()
        history = self.search_history.search(History.user_id == user_id)
        
        # Sort by timestamp (newest first) and limit
        sorted_history = sorted(history, key=lambda x: x.get('timestamp', 0), reverse=True)
        return sorted_history[:limit]
    
    def save_user_preferences(self, user_id: str, preferences: Dict):
        """
        Save user preferences
        
        Args:
            user_id: User identifier
            preferences: Dictionary of user preferences
        """
        pref_entry = {
            'user_id': user_id,
            'preferences': preferences,
            'timestamp': time.time()
        }
        
        # Check if preferences already exist
        Pref = Query()
        existing = self.preferences.search(Pref.user_id == user_id)
        
        if existing:
            # Update existing preferences
            self.preferences.update(
                {'preferences': preferences, 'timestamp': time.time()},
                Pref.user_id == user_id
            )
        else:
            # Insert new preferences
            self.preferences.insert(pref_entry)
    
    def get_user_preferences(self, user_id: str) -> Dict:
        """
        Get user preferences
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary of user preferences
        """
        Pref = Query()
        prefs = self.preferences.search(Pref.user_id == user_id)
        
        if prefs:
            return prefs[0].get('preferences', {})
        else:
            # Return default preferences
            return {
                'vegetarian': False,
                'vegan': False,
                'gluten_free': False,
                'dairy_free': False,
                'max_prep_time': 60,
                'preferred_cuisines': [],
                'difficulty_level': 'any'
            }
    
    def get_user_stats(self, user_id: str) -> Dict:
        """
        Get user statistics
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary of user statistics
        """
        # Count searches
        History = Query()
        search_count = len(self.search_history.search(History.user_id == user_id))
        
        # Count favorites
        Favorite = Query()
        favorite_count = len(self.favorites.search(Favorite.user_id == user_id))
        
        # Count feedback
        Feedback = Query()
        feedback_entries = self.feedback.search(Feedback.user_id == user_id)
        feedback_count = len(feedback_entries)
        
        # Count likes vs dislikes
        likes = sum(1 for f in feedback_entries if f.get('rating') in ['like', 'love'])
        dislikes = sum(1 for f in feedback_entries if f.get('rating') == 'dislike')
        
        # Most recent activity
        last_search = 0
        if search_count > 0:
            recent_searches = self.search_history.search(History.user_id == user_id)
            if recent_searches:
                last_search = max(s.get('timestamp', 0) for s in recent_searches)
        
        return {
            'search_count': search_count,
            'favorite_count': favorite_count,
            'feedback_count': feedback_count,
            'likes': likes,
            'dislikes': dislikes,
            'last_activity': last_search
        }
    
    def cleanup_old_data(self, days_old: int = 90):
        """
        Clean up old data to keep database size manageable
        
        Args:
            days_old: Remove data older than this many days
        """
        cutoff_time = time.time() - (days_old * 24 * 60 * 60)
        
        # Remove old search history
        History = Query()
        self.search_history.remove(History.timestamp < cutoff_time)
        
        # Remove old feedback (keep favorites and preferences)
        Feedback = Query()
        self.feedback.remove(Feedback.timestamp < cutoff_time)

# Global database instance
db_manager = DatabaseManager()

# Convenience functions
def save_user_feedback(user_id: str, recipe_id: int, rating: str, 
                      recipe_data: Optional[Dict] = None):
    """Save user feedback for a recipe"""
    db_manager.save_user_feedback(user_id, recipe_id, rating, recipe_data)

def get_user_feedback(user_id: str) -> List[Dict]:
    """Get all feedback for a user"""
    return db_manager.get_user_feedback(user_id)

def save_recipe_to_favorites(user_id: str, recipe: Dict):
    """Save a recipe to user's favorites"""
    db_manager.save_recipe_to_favorites(user_id, recipe)

def get_user_favorites(user_id: str) -> List[Dict]:
    """Get user's favorite recipes"""
    return db_manager.get_user_favorites(user_id)

def remove_from_favorites(user_id: str, recipe_id: int):
    """Remove a recipe from favorites"""
    db_manager.remove_from_favorites(user_id, recipe_id)

def save_search_history(user_id: str, ingredients: List[str], 
                       recipes_found: int, search_params: Optional[Dict] = None):
    """Save search to history"""
    db_manager.save_search_history(user_id, ingredients, recipes_found, search_params)

def get_user_history(user_id: str, limit: int = 50) -> List[Dict]:
    """Get user's search history"""
    return db_manager.get_user_history(user_id, limit)

def save_user_preferences(user_id: str, preferences: Dict):
    """Save user preferences"""
    db_manager.save_user_preferences(user_id, preferences)

def get_user_preferences(user_id: str) -> Dict:
    """Get user preferences"""
    return db_manager.get_user_preferences(user_id)

def get_user_stats(user_id: str) -> Dict:
    """Get user statistics"""
    return db_manager.get_user_stats(user_id)
