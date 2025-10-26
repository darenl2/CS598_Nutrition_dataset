
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