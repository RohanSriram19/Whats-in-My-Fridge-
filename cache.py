import joblib
import hashlib
import os
import time
from typing import Dict, List, Optional, Any
import json

class RecipeCache:
    """Intelligent caching system for recipe data"""
    
    def __init__(self, cache_dir: str = ".cache"):
        self.cache_dir = cache_dir
        self.cache_file = os.path.join(cache_dir, "recipe_cache.pkl")
        self.metadata_file = os.path.join(cache_dir, "cache_metadata.json")
        self.max_cache_size = 1000  # Maximum number of cached entries
        self.cache_duration = 24 * 60 * 60  # 24 hours in seconds
        
        # Create cache directory if it doesn't exist
        os.makedirs(cache_dir, exist_ok=True)
        
        # Initialize or load cache
        self.cache = self._load_cache()
        self.metadata = self._load_metadata()
    
    def _load_cache(self) -> Dict:
        """Load cache from disk"""
        try:
            if os.path.exists(self.cache_file):
                return joblib.load(self.cache_file)
            else:
                return {}
        except Exception as e:
            print(f"Error loading cache: {e}")
            return {}
    
    def _save_cache(self):
        """Save cache to disk"""
        try:
            joblib.dump(self.cache, self.cache_file)
        except Exception as e:
            print(f"Error saving cache: {e}")
    
    def _load_metadata(self) -> Dict:
        """Load cache metadata from disk"""
        try:
            if os.path.exists(self.metadata_file):
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            else:
                return {}
        except Exception as e:
            print(f"Error loading cache metadata: {e}")
            return {}
    
    def _save_metadata(self):
        """Save cache metadata to disk"""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            print(f"Error saving cache metadata: {e}")
    
    def _generate_cache_key(self, ingredients: List[str], **kwargs) -> str:
        """Generate a unique cache key for the given parameters"""
        # Sort ingredients to ensure consistent keys
        sorted_ingredients = sorted([ing.lower().strip() for ing in ingredients])
        
        # Include additional parameters in the key
        key_data = {
            'ingredients': sorted_ingredients,
            **kwargs
        }
        
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache entry is still valid"""
        if cache_key not in self.metadata:
            return False
        
        timestamp = self.metadata[cache_key].get('timestamp', 0)
        return (time.time() - timestamp) < self.cache_duration
    
    def _cleanup_cache(self):
        """Remove expired entries and enforce size limits"""
        current_time = time.time()
        
        # Remove expired entries
        expired_keys = []
        for key, meta in self.metadata.items():
            if (current_time - meta.get('timestamp', 0)) > self.cache_duration:
                expired_keys.append(key)
        
        for key in expired_keys:
            self.cache.pop(key, None)
            self.metadata.pop(key, None)
        
        # Enforce size limit by removing oldest entries
        if len(self.cache) > self.max_cache_size:
            # Sort by timestamp and remove oldest
            sorted_keys = sorted(
                self.metadata.keys(),
                key=lambda k: self.metadata[k].get('timestamp', 0)
            )
            
            keys_to_remove = sorted_keys[:-self.max_cache_size]
            for key in keys_to_remove:
                self.cache.pop(key, None)
                self.metadata.pop(key, None)
    
    def get_cached_recipes(self, cache_key: str) -> Optional[List[Dict]]:
        """
        Retrieve cached recipes if available and valid
        
        Args:
            cache_key: Cache key for the recipe search
            
        Returns:
            List of cached recipes or None if not found/expired
        """
        if cache_key in self.cache and self._is_cache_valid(cache_key):
            # Update access time
            self.metadata[cache_key]['last_accessed'] = time.time()
            self.metadata[cache_key]['access_count'] = self.metadata[cache_key].get('access_count', 0) + 1
            return self.cache[cache_key]
        
        return None
    
    def store_cached_recipes(self, cache_key: str, recipes: List[Dict]):
        """
        Store recipes in cache
        
        Args:
            cache_key: Cache key for the recipe search
            recipes: List of recipe dictionaries to cache
        """
        current_time = time.time()
        
        # Store the recipes
        self.cache[cache_key] = recipes
        
        # Store metadata
        self.metadata[cache_key] = {
            'timestamp': current_time,
            'last_accessed': current_time,
            'access_count': 1,
            'recipe_count': len(recipes)
        }
        
        # Cleanup if needed
        self._cleanup_cache()
        
        # Save to disk
        self._save_cache()
        self._save_metadata()
    
    def clear_cache(self):
        """Clear all cached data"""
        self.cache.clear()
        self.metadata.clear()
        self._save_cache()
        self._save_metadata()
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        total_entries = len(self.cache)
        total_recipes = sum(meta.get('recipe_count', 0) for meta in self.metadata.values())
        total_accesses = sum(meta.get('access_count', 0) for meta in self.metadata.values())
        
        if self.metadata:
            avg_age = (time.time() - sum(meta.get('timestamp', 0) for meta in self.metadata.values()) / len(self.metadata)) / 3600
        else:
            avg_age = 0
        
        return {
            'total_entries': total_entries,
            'total_recipes_cached': total_recipes,
            'total_cache_hits': total_accesses,
            'average_age_hours': round(avg_age, 2),
            'cache_size_mb': self._get_cache_size_mb()
        }
    
    def _get_cache_size_mb(self) -> float:
        """Get cache file size in MB"""
        try:
            if os.path.exists(self.cache_file):
                size_bytes = os.path.getsize(self.cache_file)
                return round(size_bytes / (1024 * 1024), 2)
        except:
            pass
        return 0.0

# Global cache instance
cache_instance = RecipeCache()

def get_cached_recipes(cache_key: str) -> Optional[List[Dict]]:
    """
    Get cached recipes using the provided cache key
    
    Args:
        cache_key: Unique cache key for the search
        
    Returns:
        List of cached recipes or None if not found
    """
    return cache_instance.get_cached_recipes(cache_key)

def store_cached_recipes(cache_key: str, recipes: List[Dict]):
    """
    Store recipes in cache using the provided cache key
    
    Args:
        cache_key: Unique cache key for the search
        recipes: List of recipe dictionaries to cache
    """
    cache_instance.store_cached_recipes(cache_key, recipes)

def get_cache_stats() -> Dict:
    """Get cache usage statistics"""
    return cache_instance.get_cache_stats()

def clear_cache():
    """Clear all cached data"""
    cache_instance.clear_cache()

# Convenience function for creating cache keys
def create_cache_key(ingredients: List[str], max_results: int = 10, 
                    cuisine: Optional[str] = None, **kwargs) -> str:
    """
    Create a cache key for recipe search parameters
    
    Args:
        ingredients: List of ingredient names
        max_results: Maximum number of results
        cuisine: Optional cuisine filter
        **kwargs: Additional parameters
        
    Returns:
        Unique cache key string
    """
    params = {
        'max_results': max_results,
        'cuisine': cuisine,
        **kwargs
    }
    return cache_instance._generate_cache_key(ingredients, **params)
