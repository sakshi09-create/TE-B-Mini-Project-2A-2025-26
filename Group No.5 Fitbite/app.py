# app.py
# Enhanced backend server for FitBite with improved error handling,
# logging, and additional features for better user experience

import json
import logging
import bcrypt
import pandas as pd
import joblib
from flask import Flask, request, jsonify
from flask_cors import CORS
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import ast
import os
from datetime import datetime, timedelta
import traceback
import random
import shutil

# --- AI API Implementation Imports (Switched to Google GenAI) ---
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# IMPORTANT: Ensure 'google-genai' is installed (pip install google-genai)
# AND your API Key is set as an environment variable (GEMINI_API_KEY).
from google import genai
from google.genai.errors import APIError
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# --- END AI API Implementation Imports ---

# --- Flask App Initialization ---
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# --- Enhanced Logging Configuration (FIXED SPAMMING) ---
# Configure logger to output only INFO and above, but we remove the repetitive user load log in load_users
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fitbite.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Suppress werkzeug logs for cleaner output
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# --- Configuration ---
USERS_FILE = 'users.json'
RECIPES_FILE = 'recipes_upd.csv'
VECTORIZER_FILE = 'tfidf_vectorizer.joblib'

# --- Global Variables ---
df = None
tfidf_vectorizer = None
tfidf_matrix = None
gemini_client = None # Global client for Gemini

# --- Data Loading Functions ---
def safe_literal_eval(val):
    """Safely evaluate string representations of lists"""
    if pd.isna(val) or val == '':
        return []
    try:
        if isinstance(val, str):
            return ast.literal_eval(val)
        return val if isinstance(val, list) else []
    except (ValueError, SyntaxError):
        return []

def load_recipe_data():
    """Load recipe data and TF-IDF model with enhanced error handling"""
    global df, tfidf_vectorizer, tfidf_matrix
    
    logger.info("Loading recipe data and model...")
    
    try:
        # Check if files exist
        if not os.path.exists(RECIPES_FILE):
            logger.error(f"Recipe file not found: {RECIPES_FILE}")
            return False
            
        if not os.path.exists(VECTORIZER_FILE):
            logger.error(f"Vectorizer file not found: {VECTORIZER_FILE}")
            return False
        
        # Load recipe data
        df = pd.read_csv(RECIPES_FILE)
        logger.info(f"Loaded {len(df)} recipes")

        # *** CRITICAL FIX FOR NUTRI-PLANNER ***
        # The 'nutrition' column must be converted from a string to a list of numbers.
        if 'nutrition' in df.columns:
            df['nutrition'] = df['nutrition'].apply(safe_literal_eval)
        else:
            logger.error("FATAL: 'nutrition' column not found. NutriPlanner will not work.")
            return False
        # *** END OF FIX ***
        
        # Process tags column
        if 'tags' in df.columns:
            df['tags'] = df['tags'].apply(safe_literal_eval)
        else:
            logger.warning("No 'tags' column found in recipe data")
            df['tags'] = [[] for _ in range(len(df))]
        
        # Load TF-IDF vectorizer and create matrix
        tfidf_vectorizer = joblib.load(VECTORIZER_FILE)
        
        # Handle missing ingredients column
        if 'ingredients' not in df.columns:
            logger.error("No 'ingredients' column found in recipe data")
            return False
            
        tfidf_matrix = tfidf_vectorizer.transform(df['ingredients'])
        
        logger.info("Data and model loaded successfully.")
        return True
        
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        logger.error(traceback.format_exc())
        return False

# --- Helper Functions ---
def load_users():
    """Load user database with enhanced error handling"""
    try:
        if not os.path.exists(USERS_FILE):
            logger.info(f"Creating new user file: {USERS_FILE}")
            with open(USERS_FILE, 'w') as f:
                json.dump({}, f)
            return {}
            
        with open(USERS_FILE, 'r') as f:
            users = json.load(f)
            # logger.info(f"Loaded {len(users)} users") # REMOVED REPETITIVE LOGGING
            return users
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.warning(f"Error loading users file: {str(e)}, creating a new one.")
        return {}

def save_users(users_data):
    """
    Safely save user database using a temporary file to prevent corruption.
    This is an atomic operation to avoid the backup file issue.
    """
    temp_file = f"{USERS_FILE}.tmp"
    try:
        with open(temp_file, 'w') as f:
            json.dump(users_data, f, indent=4)
        # If write is successful, replace the original file
        shutil.move(temp_file, USERS_FILE)
        # logger.info(f"Saved {len(users_data)} users to database") # REMOVED REPETITIVE LOGGING
    except Exception as e:
        logger.error(f"Error saving users: {str(e)}")
        # Clean up temp file if it exists
        if os.path.exists(temp_file):
            os.remove(temp_file)
        raise

def calculate_ratings(recipe_id, all_users):
    """Calculate average rating and rating count for a recipe"""
    try:
        ratings = []
        recipe_id_str = str(recipe_id)
        
        for user in all_users.values():
            if 'ratings' in user and recipe_id_str in user['ratings']:
                rating = user['ratings'][recipe_id_str]
                if isinstance(rating, (int, float)) and 1 <= rating <= 5:
                    ratings.append(rating)
        
        if not ratings:
            return 0.0, 0
            
        avg_rating = sum(ratings) / len(ratings)
        return round(avg_rating, 1), len(ratings)
        
    except Exception as e:
        logger.error(f"Error calculating ratings for recipe {recipe_id}: {str(e)}")
        return 0.0, 0

def safe_list_parse(val):
    """Safely converts string representation of lists/arrays into a list."""
    if isinstance(val, list):
        return val
    if not isinstance(val, str) or pd.isna(val) or val.strip() == '':
        return []
    try:
        # Use json.loads after replacing single quotes with double quotes
        # as the array syntax often comes from Python's list representation.
        return json.loads(val.replace("'", '"'))
    except (json.JSONDecodeError, ValueError, TypeError):
        # Fallback to ast.literal_eval if json.loads fails
        try:
            return ast.literal_eval(val)
        except (ValueError, SyntaxError):
            # Final fallback, try splitting by comma, cleaning up brackets
            if val.strip().startswith('[') and val.strip().endswith(']'):
                val = val.strip()[1:-1]
            return [item.strip() for item in val.split(',') if item.strip()]


def validate_recipe_data(recipe):
    """Validate and clean recipe data before sending to client"""
    try:
        # Ensure required fields exist
        recipe_data = {
            'id': int(recipe.get('id', 0)),
            'name': str(recipe.get('name', 'Unknown Recipe')),
            'prep_time': int(recipe.get('minutes', 0)),
            'description': str(recipe.get('description', '')),
        }
        
        # *** FIX: Use the new robust parser for ingredients and steps ***
        recipe_data['ingredients'] = safe_list_parse(recipe.get('ingredients', []))
        recipe_data['steps'] = safe_list_parse(recipe.get('steps', []))
        # *** END FIX ***
        
        # Process nutrition (already handled by safe_literal_eval on load, ensure structure)
        nutrition = recipe.get('nutrition', [])
        recipe_data['nutrition'] = nutrition if isinstance(nutrition, list) else []
        
        # Process tags (already handled by safe_literal_eval on load, ensure structure)
        tags = recipe.get('tags', [])
        recipe_data['tags'] = tags if isinstance(tags, list) else []
        
        return recipe_data
        
    except Exception as e:
        logger.error(f"Error validating recipe data: {str(e)}")
        return None

# --- API Routes ---
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "recipes_loaded": df is not None,
        "total_recipes": len(df) if df is not None else 0
    })

@app.route('/login', methods=['POST'])
def login():
    """Handle user login with enhanced validation"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "No data provided."}), 400
            
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({"success": False, "message": "Username and password are required."}), 400
        
        users = load_users()
        
        if username not in users:
            logger.warning(f"Login attempt with non-existent username: {username}")
            return jsonify({"success": False, "message": "Invalid username or password."}), 401
            
        stored_password = users[username].get('password', '')
        if not stored_password:
            return jsonify({"success": False, "message": "Invalid account data."}), 401
            
        if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
            logger.info(f"Successful login for user: {username}")
            
            # Update last login time
            users[username]['last_login'] = datetime.now().isoformat()
            save_users(users)
            
            return jsonify({
                "success": True, 
                "message": f"Welcome back, {username}!",
                "user_data": {
                    "username": username,
                    "total_ratings": len(users[username].get('ratings', {})),
                    "favorite_count": len(users[username].get('favorites', [])),
                    "search_history": users[username].get('search_history', [])
                }
            })
        else:
            logger.warning(f"Failed login attempt for user: {username}")
            return jsonify({"success": False, "message": "Invalid username or password."}), 401
            
    except Exception as e:
        logger.error(f"Error in login: {str(e)}")
        return jsonify({"success": False, "message": "An error occurred during login."}), 500

@app.route('/signup', methods=['POST'])
def signup():
    """Handle user registration with enhanced validation"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "No data provided."}), 400
            
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        # Enhanced validation
        if not username: return jsonify({"success": False, "message": "Username is required."}), 400
        if len(username) < 3: return jsonify({"success": False, "message": "Username must be at least 3 characters long."}), 400
        if len(username) > 50: return jsonify({"success": False, "message": "Username must be less than 50 characters."}), 400
        if not password: return jsonify({"success": False, "message": "Password is required."}), 400
        if len(password) < 6: return jsonify({"success": False, "message": "Password must be at least 6 characters long."}), 400
        if len(password) > 128: return jsonify({"success": False, "message": "Password must be less than 128 characters."}), 400
        
        users = load_users()
        
        if username.lower() in [u.lower() for u in users.keys()]:
            return jsonify({"success": False, "message": "Username already exists."}), 409

        # Create new user
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        users[username] = {
            "password": hashed_password.decode('utf-8'),
            "ratings": {}, "favorites": [], "search_history": [],
            "meal_plans": [], 
            # --- FIX: Add NutriPlanner history tracking ---
            "nutri_plan_history": [], 
            # --- END FIX ---
            "created_at": datetime.now().isoformat(),
            "last_login": None
        }
        
        save_users(users)
        logger.info(f"New user registered: {username}")
        
        return jsonify({"success": True, "message": "Account created successfully! You can now log in."}), 201
        
    except Exception as e:
        logger.error(f"Error in signup: {str(e)}")
        return jsonify({"success": False, "message": "An error occurred during registration."}), 500

@app.route('/rate_recipe', methods=['POST'])
def rate_recipe():
    """Save user's recipe rating with validation"""
    try:
        data = request.get_json()
        if not data: return jsonify({"success": False, "message": "No data provided."}), 400
            
        username = data.get('username', '').strip()
        recipe_id = data.get('recipe_id')
        rating = data.get('rating')
        
        # Validation
        if not username: return jsonify({"success": False, "message": "Username is required."}), 400
        if recipe_id is None: return jsonify({"success": False, "message": "Recipe ID is required."}), 400
        if not isinstance(rating, (int, float)) or not (1 <= rating <= 5):
            return jsonify({"success": False, "message": "Rating must be between 1 and 5."}), 400
        
        users = load_users()
        if username not in users: return jsonify({"success": False, "message": "User not found."}), 404
            
        # Check if recipe exists
        if df is not None and int(recipe_id) not in df['id'].values:
            return jsonify({"success": False, "message": "Recipe not found."}), 404
        
        # Save rating
        if 'ratings' not in users[username]: users[username]['ratings'] = {}
        users[username]['ratings'][str(recipe_id)] = int(rating)
        save_users(users)
        
        logger.info(f"User {username} rated recipe {recipe_id} with {rating} stars")
        
        return jsonify({"success": True, "message": "Rating saved successfully!", "rating": rating})
        
    except Exception as e:
        logger.error(f"Error in rate_recipe: {str(e)}")
        return jsonify({"success": False, "message": "An error occurred while saving the rating."}), 500

@app.route('/favorite_recipe', methods=['POST'])
def favorite_recipe():
    """Add/remove recipe from user's favorites"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        recipe_id = str(data.get('recipe_id'))
        action = data.get('action', 'toggle')  # 'add', 'remove', or 'toggle'
        
        if not username or not recipe_id:
            return jsonify({"success": False, "message": "Username and recipe ID are required."}), 400
        
        users = load_users()
        if username not in users: return jsonify({"success": False, "message": "User not found."}), 404
            
        if 'favorites' not in users[username]: users[username]['favorites'] = []
            
        favorites = users[username]['favorites']
        is_favorited = recipe_id in favorites
        
        if action == 'add' or (action == 'toggle' and not is_favorited):
            if not is_favorited: favorites.append(recipe_id)
            is_favorited = True
        elif action == 'remove' or (action == 'toggle' and is_favorited):
            if is_favorited: favorites.remove(recipe_id)
            is_favorited = False
            
        save_users(users)
        
        return jsonify({"success": True, "is_favorited": is_favorited, "total_favorites": len(favorites)})
        
    except Exception as e:
        logger.error(f"Error in favorite_recipe: {str(e)}")
        return jsonify({"success": False, "message": "An error occurred."}), 500

@app.route('/get_favorites', methods=['POST'])
def get_favorites():
    """Get user's favorite recipes"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        
        if not username: return jsonify({"success": False, "message": "Username is required."}), 400
        
        users = load_users()
        if username not in users: return jsonify({"success": False, "message": "User not found."}), 404
            
        favorite_ids = users[username].get('favorites', [])
        
        favorites = []
        if df is not None and favorite_ids:
            # Need to convert list of string IDs back to integers for DataFrame filtering
            int_favorite_ids = []
            for i in favorite_ids:
                try:
                    int_favorite_ids.append(int(i))
                except ValueError:
                    logger.warning(f"Invalid recipe ID in favorites: {i}")

            favorite_recipes_df = df[df['id'].isin(int_favorite_ids)]
            for _, recipe_row in favorite_recipes_df.iterrows():
                recipe_data = validate_recipe_data(recipe_row)
                if recipe_data:
                    avg_rating, num_ratings = calculate_ratings(recipe_data["id"], users)
                    recipe_data.update({
                        "avg_rating": f"{avg_rating:.1f}", "num_ratings": num_ratings, "is_favorited": True
                    })
                    favorites.append(recipe_data)
        
        return jsonify({"success": True, "favorites": favorites})
        
    except Exception as e:
        logger.error(f"Error in get_favorites: {str(e)}")
        return jsonify({"success": False, "message": "An error occurred."}), 500

@app.route('/save_search_history', methods=['POST'])
def save_search_history():
    """Save user's search history for meal planning"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        ingredients = data.get('ingredients', '').strip()
        
        if not username or not ingredients: return jsonify({"success": False, "message": "Username and ingredients are required."}), 400
        
        users = load_users()
        if username not in users: return jsonify({"success": False, "message": "User not found."}), 404
            
        if 'search_history' not in users[username]: users[username]['search_history'] = []
            
        search_entry = {"ingredients": ingredients, "timestamp": datetime.now().isoformat(), "date": datetime.now().strftime("%Y-%m-%d")}
        
        history = users[username]['search_history']
        history.insert(0, search_entry)
        users[username]['search_history'] = history[:50] # Keep last 50
        
        save_users(users)
        return jsonify({"success": True})
        
    except Exception as e:
        logger.error(f"Error in save_search_history: {str(e)}")
        return jsonify({"success": False, "message": "An error occurred."}), 500

@app.route('/generate_meal_plan', methods=['POST'])
def generate_meal_plan():
    """Generate meal plan based on user's search history and preferences"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        days = int(data.get('days', 7))
        
        if not username: return jsonify({"success": False, "message": "Username is required."}), 400
        
        users = load_users()
        if username not in users: return jsonify({"success": False, "message": "User not found."}), 404
            
        search_history = users[username].get('search_history', [])
        
        popular_ingredients = []
        if search_history:
            common_ingredients = [ing.strip().lower() for search in search_history[:10] for ing in search.get('ingredients', '').split(',') if ing.strip()]
            from collections import Counter
            ingredient_counts = Counter(common_ingredients)
            popular_ingredients = [ing for ing, count in ingredient_counts.most_common(10)]
        
        meal_plan = []
        if df is None or df.empty: return jsonify({"success": False, "message": "Recipe data is not available."}), 500

        for day in range(days):
            day_plan = {"day": day + 1, "date": (datetime.now() + timedelta(days=day)).strftime("%Y-%m-%d"), "meals": {}}
            
            for meal_type in ['breakfast', 'lunch', 'dinner']:
                meal_recipes_df = pd.DataFrame()
                
                if meal_type == 'breakfast': meal_keywords = ['breakfast', 'morning']
                elif meal_type == 'lunch': meal_keywords = ['lunch', 'salad', 'sandwich']
                else: meal_keywords = ['dinner', 'main', 'entree']

                mask = df['tags'].apply(lambda tags: any(keyword in str(tag).lower() for tag in tags for keyword in meal_keywords))
                meal_recipes_df = df[mask]

                if len(meal_recipes_df) < 10 and popular_ingredients:
                    for ingredient in popular_ingredients:
                        ing_mask = df['ingredients'].str.lower().str.contains(ingredient, na=False)
                        meal_recipes_df = pd.concat([meal_recipes_df, df[ing_mask]]).drop_duplicates(subset=['id'])
                        if len(meal_recipes_df) > 20: break
                
                if meal_recipes_df.empty:
                    meal_recipes_df = df.sample(min(10, len(df)))

                if not meal_recipes_df.empty:
                    selected_recipe = meal_recipes_df.sample(1).iloc[0]
                    recipe_data = validate_recipe_data(selected_recipe)
                    if recipe_data:
                        avg_rating, num_ratings = calculate_ratings(recipe_data["id"], users)
                        recipe_data.update({"avg_rating": f"{avg_rating:.1f}", "num_ratings": num_ratings})
                        day_plan["meals"][meal_type] = recipe_data
            
            meal_plan.append(day_plan)
        
        if 'meal_plans' not in users[username]: users[username]['meal_plans'] = []
        plan_entry = {"created_at": datetime.now().isoformat(), "days": days, "plan": meal_plan}
        users[username]['meal_plans'].insert(0, plan_entry)
        users[username]['meal_plans'] = users[username]['meal_plans'][:5] # Keep last 5
        save_users(users)
        
        return jsonify({"success": True, "meal_plan": meal_plan, "based_on_ingredients": popular_ingredients[:5]})
        
    except Exception as e:
        logger.error(f"Error in generate_meal_plan: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"success": False, "message": "An error occurred while generating meal plan."}), 500

@app.route('/recommend', methods=['POST'])
def recommend():
    """Generate recipe recommendations with enhanced filtering and error handling"""
    try:
        if df is None or tfidf_vectorizer is None or tfidf_matrix is None:
            return jsonify({"error": "Recipe data not loaded. Please restart the server."}), 500
            
        data = request.get_json()
        if not data: return jsonify({"error": "No data provided."}), 400
            
        user_ingredients = data.get('ingredients', '').strip()
        prep_time, dietary_pref, cuisine, meal_type, taste_profile, username = \
            data.get('prep_time'), data.get('dietary_preference'), data.get('cuisine'), \
            data.get('meal_type'), data.get('taste_profile'), data.get('username')

        if not user_ingredients: return jsonify({"error": "Ingredients are required."}), 400

        logger.info(f"Recommendation request: ingredients='{user_ingredients}', prep_time={prep_time}, diet={dietary_pref}, cuisine={cuisine}")

        if username:
            try:
                users = load_users()
                if username in users:
                    if 'search_history' not in users[username]: users[username]['search_history'] = []
                    search_entry = {
                        "ingredients": user_ingredients, "timestamp": datetime.now().isoformat(),
                        "filters": {"prep_time": prep_time, "dietary_preference": dietary_pref, "cuisine": cuisine, "meal_type": meal_type}
                    }
                    users[username]['search_history'].insert(0, search_entry)
                    users[username]['search_history'] = users[username]['search_history'][:50]
                    save_users(users)
            except Exception as e:
                logger.warning(f"Could not save search history: {e}")

        user_tfidf = tfidf_vectorizer.transform([user_ingredients])
        similarities = cosine_similarity(user_tfidf, tfidf_matrix).flatten()
        top_indices = similarities.argsort()[-500:][::-1]
        
        filtered_df = df.iloc[top_indices].copy()
        filtered_df['similarity_score'] = similarities[top_indices]

        if prep_time:
            try:
                if int(prep_time) > 0: filtered_df = filtered_df[filtered_df['minutes'] <= int(prep_time)]
            except (ValueError, TypeError): logger.warning(f"Invalid prep_time value: {prep_time}")

        for key, col_val in [('dietary_preference', dietary_pref), ('cuisine', cuisine), ('meal_type', meal_type)]:
            if col_val and col_val != 'Any':
                val_lower = col_val.lower()
                filtered_df = filtered_df[filtered_df['tags'].apply(lambda tags: any(val_lower in str(tag).lower() for tag in tags if tag))]

        final_recommendations = filtered_df.head(20)
        recommendations = []
        all_users = load_users()
        user_favorites = all_users.get(username, {}).get('favorites', [])
        
        for index, recipe in final_recommendations.iterrows():
            recipe_data = validate_recipe_data(recipe)
            if recipe_data:
                avg_rating, num_ratings = calculate_ratings(recipe_data["id"], all_users)
                recipe_data.update({
                    "avg_rating": f"{avg_rating:.1f}", "num_ratings": num_ratings,
                    "similarity_score": round(recipe.get('similarity_score', 0), 3),
                    "is_favorited": str(recipe_data["id"]) in user_favorites
                })
                recommendations.append(recipe_data)

        logger.info(f"Returning {len(recommendations)} recipe recommendations")
        
        return jsonify({
            "recommendations": recommendations, "total_found": len(filtered_df),
            "search_params": {
                "ingredients": user_ingredients, "prep_time": prep_time, "dietary_preference": dietary_pref,
                "cuisine": cuisine, "meal_type": meal_type, "taste_profile": taste_profile
            }
        })
        
    except Exception as e:
        logger.error(f"Error in recommend: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"error": "An error occurred while generating recommendations."}), 500

@app.route('/user_stats', methods=['POST'])
def get_user_stats():
    """Get user statistics and rating history"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        
        if not username: return jsonify({"error": "Username is required."}), 400
            
        users = load_users()
        if username not in users: return jsonify({"error": "User not found."}), 404
            
        user_data = users[username]
        ratings = user_data.get('ratings', {})
        total_ratings = len(ratings)
        avg_rating_given = sum(ratings.values()) / total_ratings if total_ratings > 0 else 0
        
        rating_distribution = {str(i): 0 for i in range(1, 6)}
        for rating in ratings.values():
            if str(int(rating)) in rating_distribution: rating_distribution[str(int(rating))] += 1
            
        all_ingredients = [ing.strip().lower() for search in user_data.get('search_history', []) for ing in search.get('ingredients', '').split(',') if ing.strip()]
        from collections import Counter
        top_ingredients = [ing for ing, count in Counter(all_ingredients).most_common(10)]
        
        # --- FIX: Calculate NutriPlanner Statistics ---
        nutri_plans = user_data.get('nutri_plan_history', [])
        total_plans = len(nutri_plans)
        
        total_calories = 0
        for plan in nutri_plans:
            total_calories += plan.get('target_calories', 0)
            
        avg_cal_goal = round(total_calories / total_plans, 0) if total_plans > 0 else 'N/A'
        # --- END FIX ---
            
        return jsonify({
            "success": True,
            "stats": {
                "total_ratings": total_ratings, "total_favorites": len(user_data.get('favorites', [])),
                "total_searches": len(user_data.get('search_history', [])), "average_rating_given": round(avg_rating_given, 1),
                "rating_distribution": rating_distribution, "top_ingredients": top_ingredients,
                "member_since": user_data.get('created_at'), "last_login": user_data.get('last_login'),
                # --- FIX: Add NutriPlanner stats to response ---
                "total_meal_plans_generated": total_plans,
                "average_target_calories": avg_cal_goal
                # --- END FIX ---
            }
        })
        
    except Exception as e:
        logger.error(f"Error in get_user_stats: {str(e)}")
        return jsonify({"error": "An error occurred while fetching user statistics."}), 500

@app.route('/popular_recipes', methods=['GET'])
def get_popular_recipes():
    """Get most popular recipes based on ratings"""
    try:
        if df is None: return jsonify({"error": "Recipe data not loaded."}), 500
            
        users = load_users()
        recipe_scores = {
            recipe_id: {
                'avg_rating': (ratings := calculate_ratings(recipe_id, users))[0],
                'num_ratings': ratings[1],
                'popularity_score': ratings[0] * (ratings[1] + 1)
            } for recipe_id in df['id']
        }
        
        sorted_recipes = sorted(recipe_scores.items(), key=lambda x: x[1]['popularity_score'], reverse=True)
        top_recipe_ids = [recipe_id for recipe_id, _ in sorted_recipes[:10]]
        
        popular_recipes = []
        for recipe_id in top_recipe_ids:
            recipe_row = df[df['id'] == recipe_id].iloc[0]
            recipe_data = validate_recipe_data(recipe_row)
            if recipe_data:
                score_data = recipe_scores[recipe_id]
                recipe_data.update({"avg_rating": f"{score_data['avg_rating']:.1f}", "num_ratings": score_data['num_ratings']})
                popular_recipes.append(recipe_data)
        
        return jsonify({"success": True, "popular_recipes": popular_recipes})
        
    except Exception as e:
        logger.error(f"Error in get_popular_recipes: {str(e)}")
        return jsonify({"error": "An error occurred while fetching popular recipes."}), 500

@app.route('/recipe/<int:recipe_id>', methods=['GET'])
def get_recipe_details(recipe_id):
    """Get detailed information about a specific recipe"""
    try:
        if df is None: return jsonify({"error": "Recipe data not loaded."}), 500
            
        recipe_rows = df[df['id'] == recipe_id]
        if recipe_rows.empty: return jsonify({"error": "Recipe not found."}), 404
            
        recipe_data = validate_recipe_data(recipe_rows.iloc[0])
        if recipe_data is None: return jsonify({"error": "Invalid recipe data."}), 500
            
        avg_rating, num_ratings = calculate_ratings(recipe_id, load_users())
        recipe_data.update({"avg_rating": f"{avg_rating:.1f}", "num_ratings": num_ratings})
        
        return jsonify({"success": True, "recipe": recipe_data})
        
    except Exception as e:
        logger.error(f"Error in get_recipe_details: {str(e)}")
        return jsonify({"error": "An error occurred while fetching recipe details."}), 500

@app.route('/search', methods=['POST'])
def search_recipes():
    """Search recipes by name or description"""
    try:
        if df is None: return jsonify({"error": "Recipe data not loaded."}), 500
            
        data = request.get_json()
        query = data.get('query', '').strip().lower()
        limit = min(int(data.get('limit', 10)), 50)
        username = data.get('username')
        
        if not query: return jsonify({"error": "Search query is required."}), 400
            
        matching_recipes = df[df['name'].str.lower().str.contains(query, na=False) | df['description'].str.lower().str.contains(query, na=False)].head(limit)
        
        results = []
        users = load_users()
        user_favorites = users.get(username, {}).get('favorites', [])
        
        for _, recipe in matching_recipes.iterrows():
            recipe_data = validate_recipe_data(recipe)
            if recipe_data:
                avg_rating, num_ratings = calculate_ratings(recipe_data["id"], users)
                recipe_data.update({
                    "avg_rating": f"{avg_rating:.1f}", "num_ratings": num_ratings,
                    "is_favorited": str(recipe_data["id"]) in user_favorites
                })
                results.append(recipe_data)
        
        return jsonify({"success": True, "results": results, "total_found": len(results), "query": query})
        
    except Exception as e:
        logger.error(f"Error in search_recipes: {str(e)}")
        return jsonify({"error": "An error occurred while searching recipes."}), 500

# --- NutriPlanner Functions ---
def calculate_bmr(gender, weight, height, age):
    """Calculate Basal Metabolic Rate (BMR) using Mifflin-St Jeor equation"""
    if gender.lower() == 'male':
        return 10 * float(weight) + 6.25 * float(height) - 5 * int(age) + 5
    else: # female
        return 10 * float(weight) + 6.25 * float(height) - 5 * int(age) - 161

def calculate_calories(bmr, activity_level):
    """Calculate daily caloric needs based on activity level"""
    activity_multipliers = {'sedentary': 1.2, 'lightly active': 1.375, 'moderately active': 1.55, 'very active': 1.725, 'extra active': 1.9}
    return bmr * activity_multipliers.get(activity_level.lower(), 1.2)

def adjust_calories_for_goal(daily_calories, goal):
    """Adjust caloric intake based on user's goal"""
    if goal.lower() == 'lose weight':
        return daily_calories - 500
    elif goal.lower() == 'gain muscle':
        return daily_calories + 500
    else: # maintain weight
        return daily_calories

@app.route('/nutriplanner', methods=['POST'])
def nutriplanner():
    """Endpoint for NutriPlanner to get recipe recommendations"""
    try:
        data = request.get_json()
        if not data: return jsonify({"success": False, "message": "No data provided."}), 400

        height, weight, age, gender, activity_level, goal, username = \
            data.get('height'), data.get('weight'), data.get('age'), data.get('gender'), \
            data.get('activity_level'), data.get('goal'), data.get('username')

        if not all([height, weight, age, gender, activity_level, goal]):
            return jsonify({"success": False, "message": "All fields are required."}), 400
            
        # Ensure numerical data is correctly typed
        try:
            height, weight, age = float(height), float(weight), int(age)
        except ValueError:
            return jsonify({"success": False, "message": "Height, weight, and age must be valid numbers."}), 400

        bmr = calculate_bmr(gender, weight, height, age)
        daily_calories = calculate_calories(bmr, activity_level)
        target_calories = adjust_calories_for_goal(daily_calories, goal)
        target_calories = max(1200, target_calories) # Safety minimum
        
        # Meal distribution based on the target
        # Narrowed range to ensure meals fit well within target calories
        # Breakfast: 20-30%, Lunch: 30-40%, Dinner: 30-40%
        breakfast_calories_range = (target_calories * 0.20, target_calories * 0.30)
        lunch_calories_range = (target_calories * 0.30, target_calories * 0.40)
        dinner_calories_range = (target_calories * 0.30, target_calories * 0.40)
        
        # --- CONSTANT FOR MULTIPLE MEAL PLANS ---
        NUM_RECIPES_PER_MEAL = 3 
        # --- END CONSTANT ---

        def get_recipes_in_range(calorie_range):
            return df[df['nutrition'].apply(lambda x: isinstance(x, list) and len(x) > 0 and calorie_range[0] <= x[0] <= calorie_range[1])]

        breakfast_recipes = get_recipes_in_range(breakfast_calories_range)
        lunch_recipes = get_recipes_in_range(lunch_calories_range)
        dinner_recipes = get_recipes_in_range(dinner_calories_range)
        
        # Select multiple recipes for each meal
        breakfast_plan = breakfast_recipes.sample(min(NUM_RECIPES_PER_MEAL, len(breakfast_recipes))).to_dict('records')
        lunch_plan = lunch_recipes.sample(min(NUM_RECIPES_PER_MEAL, len(lunch_recipes))).to_dict('records')
        dinner_plan = dinner_recipes.sample(min(NUM_RECIPES_PER_MEAL, len(dinner_recipes))).to_dict('records')
        
        # Validate data structure and format before sending back
        final_plan = {}
        users = load_users()
        
        for meal, plans in [("breakfast", breakfast_plan), ("lunch", lunch_plan), ("dinner", dinner_plan)]:
            validated_plans = []
            for recipe_row in plans:
                validated_recipe = validate_recipe_data(recipe_row)
                if validated_recipe:
                    # Re-calculate ratings for fresh data display
                    avg_rating, num_ratings = calculate_ratings(validated_recipe["id"], users)
                    validated_recipe.update({"avg_rating": f"{avg_rating:.1f}", "num_ratings": num_ratings})
                    validated_plans.append(validated_recipe)
            final_plan[meal] = validated_plans
                    
        # --- FIX: Save NutriPlanner generation history (for statistics) ---
        if username and username in users:
            plan_summary = {
                "user_data": data,
                "target_calories": round(target_calories, 0),
                "timestamp": datetime.now().isoformat()
            }
            if 'nutri_plan_history' not in users[username]: users[username]['nutri_plan_history'] = []
            users[username]['nutri_plan_history'].insert(0, plan_summary)
            save_users(users)
        # --- END FIX ---


        return jsonify({"success": True, "plan": final_plan, "target_calories": round(target_calories, 0)})

    except Exception as e:
        logger.error(f"Error in NutriPlanner: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"success": False, "message": "An internal error occurred."}), 500


# --- NEW CHATBOT API ROUTE (SWITCHED TO GEMINI) ---
@app.route('/fitbite_ai_chat', methods=['POST'])
def fitbite_ai_chat():
    """
    Handles chat requests using the Google Gemini model.
    """
    global gemini_client
    
    if gemini_client is None:
        logger.error("Gemini Client not initialized. API Key likely missing.")
        return jsonify({"success": False, "response": "AI service not configured. Please set GEMINI_API_KEY on the server."}), 500
        
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        username = data.get('username', 'Guest')

        if not user_message:
            return jsonify({"success": False, "response": "Message cannot be empty."}), 400

        logger.info(f"Chat request from {username}: {user_message}")

        # 1. Prepare Recipe Data Summary for RAG-like Context (Limited)
        recipe_context = "FitBite Recipe Data Summary: "
        if df is not None and not df.empty:
            recipe_scores = {
                recipe_id: {
                    'avg_rating': (ratings := calculate_ratings(recipe_id, load_users()))[0],
                    'num_ratings': ratings[1],
                    'popularity_score': ratings[0] * (ratings[1] + 1)
                } for recipe_id in df['id']
            }
            sorted_recipes = sorted(recipe_scores.items(), key=lambda x: x[1]['popularity_score'], reverse=True)
            top_recipe_ids = [recipe_id for recipe_id, _ in sorted_recipes[:5]]
            
            top_recipes_df = df[df['id'].isin(top_recipe_ids)]
            for _, row in top_recipes_df.iterrows():
                # Including tags in the context to make the AI more specific
                recipe_context += f"Recipe: {row['name']} (Tags: {', '.join(row['tags'])}), "
        
        # 2. Define System Prompt for Gemini
        system_prompt = f"""
        You are the **FitBite AI Assistant**, a friendly, expert nutritional and recipe guide.
        Your primary role is to answer user questions about food, nutrition, cooking techniques, and meal planning.
        The user's name is {username}.
        
        **Instructions:**
        1.  **Be Accurate:** Provide accurate, helpful, and concise information based on general nutrition science.
        2.  **Refer to App Features:** If the user asks about searching recipes, generating meal plans, or calorie goals, **ALWAYS** politely guide them to use the following app features, as you cannot execute searches yourself:
            -   **Recipe Search/Ingredients:** "🔍 Find Recipes" 
            -   **Calorie/Macro Goals:** "📊 NutriPlanner" 
            -   **Weekly Planning:** "📅 Meal Planner"
        3.  **Use Context:** Use the following summary of the most popular recipes in the FitBite database to inform your recipe suggestions. Do not list the summary itself, but integrate the knowledge naturally.

        **FitBite Context (Popular Recipes):** {recipe_context.strip()}
        """
        
        # 3. Call Gemini API
        try:
            config = {
                "system_instruction": system_prompt
            }

            response = gemini_client.models.generate_content(
                model='gemini-2.5-flash', 
                contents=[user_message],
                config=config
            )
            
            ai_response = response.text
            return jsonify({"success": True, "response": ai_response})
        
        except APIError as e:
            logger.error(f"Gemini API Error: {e}")
            # Gemini may return quota errors, authorization errors, etc. Handle as 429 for quotas or 401 for auth.
            if "quota" in str(e).lower() or "rate" in str(e).lower():
                 return jsonify({"success": False, "response": "I'm experiencing high traffic right now (Quota/Rate Limit). Please check your server's Gemini usage or try again in a moment!"}), 429
            elif "auth" in str(e).lower() or "api key" in str(e).lower():
                 return jsonify({"success": False, "response": "Authentication failed. Please check your GEMINI_API_KEY."}), 401
            else:
                 return jsonify({"success": False, "response": f"A network or service error occurred: {str(e)}"}), 500
        
        except Exception as e:
            logger.error(f"General AI Call Error: {str(e)}")
            return jsonify({"success": False, "response": "An unexpected server error occurred while connecting to the AI service."}), 500

    except Exception as e:
        logger.error(f"Error in fitbite_ai_chat: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"success": False, "response": "An unhandled server error occurred."}), 500
# --- END NEW CHATBOT API ROUTE ---


# --- Error Handlers ---
@app.errorhandler(404)
def not_found(error): return jsonify({"error": "Endpoint not found."}), 404
@app.errorhandler(405)
def method_not_allowed(error): return jsonify({"error": "Method not allowed."}), 405
@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({"error": "Internal server error."}), 500

# --- Application Startup ---
def initialize_app():
    """Initialize the application with proper error handling"""
    global gemini_client
    logger.info("=== FitBite Backend Server Starting ===")
    
    if not load_recipe_data():
        logger.error("Failed to load recipe data. Server cannot start.")
        return False
    
    # Initialize Gemini Client
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        try:
            # Use the environment variable key for initialization
            gemini_client = genai.Client()
            logger.info("Gemini Client initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            logger.error("Please ensure the 'google-genai' library is installed and the GEMINI_API_KEY is set correctly.")
            return False
    else:
        logger.warning("GEMINI_API_KEY not found. Chatbot functionality will be disabled or fail.")
    
    users = load_users()
    logger.info(f"User database initialized with {len(users)} users")
    return True

if __name__ == '__main__':
    if initialize_app():
        logger.info("Starting FitBite server at http://127.0.0.1:5000")
        app.run(host='0.0.0.0', port=5000, debug=False)
    else:
        logger.error("Server initialization failed. Exiting.")
        exit(1)