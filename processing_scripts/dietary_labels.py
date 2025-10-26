import pandas as pd

def categorize_dietary_labels(csv_path: str):
    """
    Reads a recipe CSV and creates a single column 'dietary_restrictions'
    listing all applicable dietary labels (e.g. 'Vegetarian, Nut-Free').
    """
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.lower()

    # Identify useful columns
    text_cols = [c for c in df.columns if any(k in c for k in ["ingredient", "title", "cuisine"])]
    if not text_cols:
        raise ValueError("No ingredient/title/cuisine column found for dietary inference.")

    # Combine text fields for keyword searching
    df["combined_text"] = df[text_cols].astype(str).agg(" ".join, axis=1).str.lower()

    # Define keyword sets
    meat_keywords = ["chicken", "beef", "pork", "bacon", "lamb", "turkey", "duck"]
    seafood_keywords = ["fish", "salmon", "shrimp", "tuna", "crab", "lobster"]
    dairy_keywords = ["milk", "cheese", "butter", "cream", "yogurt"]
    egg_keywords = ["egg", "eggs"]
    nut_keywords = ["almond", "walnut", "cashew", "peanut", "pecan", "pistachio", "hazelnut"]

    def has_any(text, keywords):
        return any(k in text for k in keywords)

    # Compute flags
    df["Vegetarian"]  = ~df["combined_text"].apply(lambda x: has_any(x, meat_keywords))
    df["Vegan"]       = ~df["combined_text"].apply(lambda x: has_any(x, meat_keywords + dairy_keywords + egg_keywords))
    df["Pescatarian"] =  df["combined_text"].apply(lambda x: (has_any(x, seafood_keywords) and not has_any(x, meat_keywords)))
    df["Dairy_Free"]  = ~df["combined_text"].apply(lambda x: has_any(x, dairy_keywords))
    df["Nut_Free"]    = ~df["combined_text"].apply(lambda x: has_any(x, nut_keywords))
    df["Egg_Free"]    = ~df["combined_text"].apply(lambda x: has_any(x, egg_keywords))

    # Combine all True flags into a comma-separated string
    dietary_cols = ["Vegetarian", "Vegan", "Pescatarian", "Dairy_Free", "Nut_Free", "Egg_Free"]

    def combine_restrictions(row):
        restrictions = [col for col in dietary_cols if row[col]]
        return ", ".join(restrictions) if restrictions else "None"

    df["dietary_restrictions"] = df.apply(combine_restrictions, axis=1)

    # Clean up temporary columns if you don’t need them
    df.drop(columns=["combined_text"] + dietary_cols, inplace=True)

    return df
