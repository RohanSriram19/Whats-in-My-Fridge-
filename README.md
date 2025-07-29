# What's In My Fridge 🍳

**Turn your random ingredients into delicious meals!**

What's In My Fridge is an intelligent Python web application that helps you discover recipes using ingredients you already have at home. Simply type what's in your kitchen using natural language, and get personalized recipe suggestions powered by AI.

![App Screenshot](https://images.unsplash.com/photo-1556909114-9b5b93d8d8b8?w=800&h=400&fit=crop)

## ✨ Features

### 🧠 **Smart Ingredient Processing**
- **Natural Language Input**: Type ingredients however you want - "half a bell pepper, some shredded mozz, leftover chicken"
- **AI-Powered Normalization**: Uses spaCy NLP to understand synonyms, slang, and variations
- **Fuzzy Matching**: Handles typos and alternative ingredient names

### 🍽️ **Intelligent Recipe Discovery**
- **Real Recipe Data**: Powered by Spoonacular API with thousands of recipes
- **Smart Matching**: Finds recipes that maximize use of your available ingredients
- **Multiple Cuisines**: Filter by cuisine type (Italian, Mexican, Asian, etc.)

### 🚀 **Performance & Personalization**
- **Lightning Fast**: Intelligent caching reduces API calls and speeds up results
- **Machine Learning**: Learns your preferences to rank recipes better over time
- **User Feedback**: Like/dislike system improves future recommendations

### 📱 **User-Friendly Interface**
- **Clean Streamlit UI**: Easy-to-use web interface with no login required
- **Recipe Details**: Photos, prep time, servings, and ingredient lists
- **Favorites System**: Save recipes you want to try later
- **Search History**: Track your past ingredient searches

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd whats-in-my-fridge
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Download spaCy language model**
   ```bash
   python -m spacy download en_core_web_sm
   ```

4. **Set up API key**
   - Get a free API key from [Spoonacular](https://spoonacular.com/food-api)
   - Copy `.env.example` to `.env`
   - Add your API key to the `.env` file:
     ```
     SPOONACULAR_API_KEY=your_api_key_here
     ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

6. **Open your browser**
   - Navigate to `http://localhost:8501`
   - Start finding recipes!

## 🏗️ Project Structure

```
whats-in-my-fridge/
│
├── app.py               # Main Streamlit application
├── api.py               # Spoonacular API integration
├── nlp.py               # Natural language processing
├── cache.py             # Intelligent caching system
├── db.py                # Local database management
├── ranker.py            # ML-based recipe ranking
├── utils.py             # Shared utility functions
├── config.py            # Configuration settings
│
├── requirements.txt     # Python dependencies
├── .env.example        # Environment variables template
├── .github/
│   └── copilot-instructions.md
└── README.md           # This file
```

## 🎯 How It Works

1. **Input Processing**: You enter ingredients in natural language
2. **NLP Normalization**: spaCy processes and normalizes ingredient names
3. **Recipe Fetching**: Spoonacular API finds matching recipes
4. **Intelligent Ranking**: ML model ranks recipes based on your preferences
5. **Caching**: Results are cached for faster future searches
6. **User Feedback**: Your likes/dislikes improve future recommendations

## 🔧 Configuration

### API Keys
- **Spoonacular**: Required for recipe data (150 free requests/day)
- Get your key at: https://spoonacular.com/food-api

### Environment Variables
Copy `.env.example` to `.env` and configure:
```bash
SPOONACULAR_API_KEY=your_api_key_here
CACHE_DURATION_HOURS=24
MAX_CACHE_ENTRIES=1000
```

## 🤖 Machine Learning Features

### Personalized Ranking
- Learns from your feedback (likes, dislikes, saves)
- Considers dietary preferences and cooking time preferences
- Improves recommendations over time

### Ingredient Processing
- Handles ingredient synonyms ("mozz" → "mozzarella cheese")
- Normalizes quantities and descriptors
- Extracts meaningful ingredient names from natural language

## 📊 Usage Examples

### Example Inputs:
```
"eggs, leftover chicken, half a bell pepper, shredded mozzarella"
"some pasta, cherry tomatoes, garlic, parmesan cheese"
"ground beef, onions, canned beans, rice, cheese"
"spinach, feta, eggs, phyllo dough"
```

### What the App Does:
1. **Normalizes** → `["eggs", "chicken", "bell pepper", "mozzarella cheese"]`
2. **Searches** → Finds recipes using Spoonacular API
3. **Ranks** → Orders by ingredient match and your preferences
4. **Displays** → Shows recipes with photos, times, and details

## 🔍 Features in Detail

### Smart Ingredient Understanding
- **Synonyms**: "mozz" → "mozzarella", "parm" → "parmesan"
- **Variations**: "cherry tomatoes" → "tomatoes"
- **Quantities**: Removes "1 cup", "2 tbsp", etc.
- **Descriptors**: Ignores "fresh", "chopped", "organic"

### Recipe Information
- High-quality photos
- Prep and cook times
- Serving sizes
- Ingredient lists with what you have vs. what you need
- Links to full recipes
- Nutrition information (when available)

### User Data
- Search history
- Favorite recipes
- Feedback tracking
- Dietary preferences
- All stored locally (no account required)

## 🛠️ Development

### Adding New Features
1. Update relevant modules (api.py, nlp.py, etc.)
2. Add configuration to config.py
3. Update the UI in app.py
4. Test with various ingredient combinations
5. Update documentation

### Testing Different Ingredients
Try the app with:
- Common pantry items
- International ingredients
- Ingredient misspellings
- Various input formats
- Different cuisine preferences

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🙋‍♀️ Support

### Troubleshooting
- **No recipes found**: Check your API key and internet connection
- **Slow loading**: Clear cache using the settings page
- **spaCy errors**: Ensure language model is installed: `python -m spacy download en_core_web_sm`

### Get Help
- Check the troubleshooting section above
- Review your `.env` file configuration
- Ensure all dependencies are installed

## 🎉 Acknowledgments

- **Spoonacular API** for recipe data
- **spaCy** for natural language processing
- **Streamlit** for the amazing web framework
- **scikit-learn** for machine learning capabilities

---

**Ready to transform your cooking?** Install the app and turn your random ingredients into amazing meals! 🍳✨
