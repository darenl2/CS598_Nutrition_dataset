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