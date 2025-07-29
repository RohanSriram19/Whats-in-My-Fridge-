<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# What's In My Fridge - Copilot Instructions

This is an intelligent Python web application that helps users find recipes based on ingredients they have at home using natural language processing and machine learning.

## Project Architecture

### Core Components:
- **app.py**: Main Streamlit web application interface
- **api.py**: External API integration (Spoonacular)
- **nlp.py**: Natural language processing for ingredient normalization using spaCy
- **cache.py**: Intelligent caching system using joblib
- **ranker.py**: ML-based recipe ranking using scikit-learn
- **db.py**: Local database management using TinyDB
- **utils.py**: Shared utility functions
- **config.py**: Application configuration and constants

### Key Technologies:
- **Frontend**: Streamlit for web UI
- **NLP**: spaCy for ingredient text processing and normalization
- **APIs**: Spoonacular for recipe data
- **Caching**: joblib for performance optimization
- **ML**: scikit-learn for personalized recipe ranking
- **Database**: TinyDB for local data storage

### Code Style Guidelines:
- Use type hints for all functions
- Include comprehensive docstrings
- Handle errors gracefully with user-friendly messages
- Prioritize user experience and performance
- Use caching to minimize API calls
- Implement proper error fallbacks (mock data when APIs fail)

### Feature Development Priorities:
1. User-friendly natural language ingredient input
2. Fast and accurate ingredient normalization
3. Intelligent recipe ranking based on user preferences
4. Efficient caching to reduce API costs
5. Personalization through machine learning
6. Clean and responsive Streamlit interface

### When adding new features:
- Consider impact on API rate limits
- Implement caching for any new API calls
- Add proper error handling and fallbacks
- Update the database schema if needed
- Maintain backwards compatibility
- Test with various ingredient input formats

### Common Patterns:
- All user-facing functions should handle empty/invalid inputs gracefully
- Use the utils module for common formatting and validation
- Cache expensive operations (API calls, ML model predictions)
- Store user interactions for ML model training
- Provide meaningful feedback to users about system status
