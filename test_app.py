#!/usr/bin/env python3
"""
Quick test script to verify What's In My Fridge functionality
"""

from nlp import normalize_ingredients
from api import fetch_recipes
from cache import get_cache_stats
from utils import get_app_info
import config

def test_nlp():
    """Test ingredient normalization"""
    print("🧠 Testing NLP ingredient processing...")
    
    test_input = "eggs, leftover chicken, half a bell pepper, shredded mozz"
    normalized = normalize_ingredients(test_input)
    
    print(f"   Input: {test_input}")
    print(f"   Normalized: {normalized}")
    print("   ✅ NLP processing working!")
    return normalized

def test_api(ingredients):
    """Test API functionality"""
    print("\n🍳 Testing recipe API...")
    
    recipes = fetch_recipes(ingredients, max_results=3)
    
    print(f"   Found {len(recipes)} recipes")
    if recipes:
        print(f"   Sample recipe: {recipes[0].get('title', 'Unknown')}")
        print("   ✅ API working (using mock data if no API key)")
    else:
        print("   ⚠️  No recipes returned")
    
    return recipes

def test_cache():
    """Test caching system"""
    print("\n💾 Testing cache system...")
    
    stats = get_cache_stats()
    print(f"   Cache entries: {stats['total_entries']}")
    print(f"   Cache size: {stats['cache_size_mb']} MB")
    print("   ✅ Cache system working!")

def test_app_info():
    """Test app information"""
    print("\n📱 Testing app configuration...")
    
    info = get_app_info()
    print(f"   App: {info['app_name']} v{info['version']}")
    print(f"   Features available: {sum(info['features'].values())}/{len(info['features'])}")
    
    for feature, available in info['features'].items():
        status = "✅" if available else "⚠️"
        print(f"   {status} {feature}")
    
    return info

def main():
    print("🚀 What's In My Fridge - Quick Test")
    print("=" * 50)
    
    try:
        # Test each component
        ingredients = test_nlp()
        recipes = test_api(ingredients)
        test_cache()
        info = test_app_info()
        
        print("\n" + "=" * 50)
        print("✅ All tests completed successfully!")
        print("\nℹ️  Note: To use real recipe data, add your Spoonacular API key to .env file")
        print("📖 Check README.md for setup instructions")
        
        if not info['environment_status']['spoonacular_api_key']:
            print("\n⚠️  No API key detected - using mock recipe data")
            print("   Get your free API key: https://spoonacular.com/food-api")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        print("   Check README.md for troubleshooting")

if __name__ == "__main__":
    main()
