import pandas as pd

def get_unique_top_level_cuisines(csv_path: str):
    """
    Reads a CSV file and returns a list of unique top-level cuisine categories
    extracted from the 'cuisine_path' column.
    
    Example:
        /Desserts/Fruit Desserts/Apple Dessert Recipes/ → 'Desserts'
    """
    # Read CSV
    df = pd.read_csv(csv_path)
    
    # Identify the correct column
    if "cuisine_path" in df.columns:
        col = "cuisine_path"
    else:
        possible_cols = [c for c in df.columns if "cuisine" in c.lower()]
        if not possible_cols:
            raise ValueError("No 'cuisine_path' or similar column found.")
        col = possible_cols[0]
    
    # Extract top-level cuisines
    df["top_level_cuisine"] = df[col].astype(str).apply(
        lambda x: x.strip("/").split("/")[0] if isinstance(x, str) and "/" in x else x
    )
    
    # Return unique categories as a list
    return df["top_level_cuisine"].dropna().unique().tolist()


def categorize_cuisines(cuisine_list):
    """
    Categorizes a list of cuisine categories into:
    - Appetizers
    - Main Dishes
    - Desserts
    
    Returns a dictionary with these three categories.
    """
    # Define simple keyword-based classification rules
    appetizers_keywords = ["Appetizer", "Snack", "Salad", "Side", "Bread", "Soup"]
    main_dish_keywords = ["Main", "Meat", "Poultry", "Seafood", "BBQ", "Grilling", "Cuisine", "Everyday"]
    dessert_keywords = ["Dessert", "Pie", "Cake", "Cookie", "Sweet"]
    
    categorized = {"Appetizers": [], "Main Dish": [], "Dessert": []}
    
    for item in cuisine_list:
        if any(k.lower() in item.lower() for k in dessert_keywords):
            categorized["Dessert"].append(item)
        elif any(k.lower() in item.lower() for k in main_dish_keywords):
            categorized["Main Dish"].append(item)
        elif any(k.lower() in item.lower() for k in appetizers_keywords):
            categorized["Appetizers"].append(item)
        else:
            # Default to main dish if uncertain
            categorized["Main Dish"].append(item)

    return categorized

import pandas as pd

def categorize_dietary_labels(csv_path: str):
    """
    Reads a recipe CSV and categorizes each recipe as:
    Vegetarian, Vegan, Pescatarian, Dairy-Free, Nut-Free, Egg-Free
    based on ingredient keywords (and optionally title/cuisine fields).
    
    Returns a DataFrame with one boolean column per dietary category.
    """
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.lower()
    
    # Identify useful columns
    text_cols = [c for c in df.columns if any(k in c for k in ["ingredient", "title", "cuisine"])]
    if not text_cols:
        raise ValueError("No ingredient/title/cuisine column found for dietary inference.")
    
    # Combine all text columns into one lowercase text field
    df["combined_text"] = df[text_cols].astype(str).agg(" ".join, axis=1).str.lower()
    
    # Define keyword patterns for dietary detection
    meat_keywords = ["chicken", "beef", "pork", "bacon", "lamb", "turkey", "duck"]
    seafood_keywords = ["fish", "salmon", "shrimp", "tuna", "crab", "lobster"]
    dairy_keywords = ["milk", "cheese", "butter", "cream", "yogurt"]
    egg_keywords = ["egg", "eggs"]
    nut_keywords = ["almond", "walnut", "cashew", "peanut", "pecan", "pistachio", "hazelnut"]

    def has_any(text, keywords):
        return any(k in text for k in keywords)
    
    # Vegetarian: no meat, but can include dairy/eggs
    df["Vegetarian"] = ~df["combined_text"].apply(lambda x: has_any(x, meat_keywords))
    
    # Vegan: no meat, dairy, or eggs
    df["Vegan"] = ~df["combined_text"].apply(lambda x: has_any(x, meat_keywords + dairy_keywords + egg_keywords))
    
    # Pescatarian: allows seafood but excludes other meat
    df["Pescatarian"] = df["combined_text"].apply(
        lambda x: (has_any(x, seafood_keywords) and not has_any(x, meat_keywords))
    )
    
    # Dairy-Free: no dairy
    df["Dairy_Free"] = ~df["combined_text"].apply(lambda x: has_any(x, dairy_keywords))
    
    # Nut-Free: no nuts
    df["Nut_Free"] = ~df["combined_text"].apply(lambda x: has_any(x, nut_keywords))
    
    # Egg-Free: no eggs
    df["Egg_Free"] = ~df["combined_text"].apply(lambda x: has_any(x, egg_keywords))
    
    # Return the new DataFrame with the flags
    return df[["Vegetarian", "Vegan", "Pescatarian", "Dairy_Free", "Nut_Free", "Egg_Free"]]


lst = get_unique_top_level_cuisines("/Users/darenliu/Documents/UIUC_Classes/CS598/Project/archive-2/recipes.csv")
print(lst)


categorized = categorize_cuisines(lst)
print(categorized)

new_df = categorize_dietary_labels("/Users/darenliu/Documents/UIUC_Classes/CS598/Project/archive-2/recipes.csv")
print(new_df)