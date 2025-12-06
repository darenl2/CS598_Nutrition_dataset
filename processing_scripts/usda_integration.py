# processing_scripts/usda_integration.py

import re
import ast
import json
from pathlib import Path

import pandas as pd
import requests


# Put your USDA FoodData Central API key here directly
USDA_API_KEY = "WAhcbpuNqcWedcRtDpbTTfrXwEiHTrDVxnAA3u8g"

BASE_URL = "https://api.nal.usda.gov/fdc/v1"
CACHE_PATH = Path("usda_cache.json")


def _load_cache():
    if CACHE_PATH.exists():
        try:
            return json.loads(CACHE_PATH.read_text())
        except Exception:
            return {}
    return {}


def _save_cache(cache):
    CACHE_PATH.write_text(json.dumps(cache, indent=2))


def clean_ingredient(raw: str) -> str:
    if not isinstance(raw, str):
        return ""

    ing = raw.lower()

    ing = re.sub(r"\([^)]*\)", "", ing)  # remove parentheses
    ing = re.sub(r"\d+\/\d+|\d+", "", ing)  # remove numbers

    units = [
        "cup", "cups", "tbsp", "tablespoon", "tsp", "teaspoon",
        "oz", "ounce", "ounces", "gram", "grams",
        "ml", "kg", "pinch", "clove", "cloves", "slice", "slices",
        "can", "cans", "package", "packages",
    ]
    for u in units:
        ing = re.sub(rf"\b{u}\b", " ", ing)

    ing = re.sub(r"[,\.:-]", " ", ing)
    ing = re.sub(r"\s+", " ", ing)
    ing = ing.strip()

    parts = ing.split()
    if len(parts) >= 2:
        return " ".join(parts[-2:])
    elif len(parts) == 1:
        return parts[0]
    return ""


def parse_ingredients_field(value):
    """
    Robust parser for a variety of ingredient formats:
    - Python list of dicts
    - String representing a list of dicts
    - String of comma/semicolon separated ingredients
    """
    # Case 1: Already a Python list (most ideal)
    if isinstance(value, list):
        cleaned = []
        for item in value:
            if isinstance(item, dict) and "name" in item:
                cleaned.append(item["name"])
            else:
                cleaned.append(str(item))
        return cleaned

    # Case 2: String that *looks* like a list
    if isinstance(value, str):
        s = value.strip()

        # Try to parse as Python literal
        if s.startswith("[") and s.endswith("]"):
            try:
                parsed = ast.literal_eval(s)
                if isinstance(parsed, list):
                    cleaned = []
                    for item in parsed:
                        if isinstance(item, dict) and "name" in item:
                            cleaned.append(item["name"])
                        else:
                            cleaned.append(str(item))
                    return cleaned
            except Exception:
                pass

        # Fallback: naive splitting
        return [p.strip() for p in re.split(r"[;,]", s) if p.strip()]

    return []



def usda_search(ingredient_name: str):
    if not USDA_API_KEY or not ingredient_name:
        return None

    params = {
        "api_key": USDA_API_KEY,
        "query": ingredient_name,
        "pageSize": 1,
        "dataType": ["Survey (FNDDS)", "SR Legacy"],
    }

    try:
        resp = requests.get(f"{BASE_URL}/foods/search", params=params, timeout=10)
    except Exception:
        return None

    if resp.status_code != 200:
        return None

    data = resp.json()
    foods = data.get("foods", [])
    if not foods:
        return None

    nutrients = foods[0].get("foodNutrients", [])
    for n in nutrients:
        if n.get("nutrientId") == 1008:  # Energy kcal
            return n.get("value")

    return None


def query_usda_calories(cleaned_ing: str, cache: dict):
    if cleaned_ing in cache:
        return cache[cleaned_ing]

    kcal = usda_search(cleaned_ing)
    cache[cleaned_ing] = kcal
    return kcal


def compute_total_calories_for_row(ingredients_value, cache: dict, max_ingredients: int = 3) -> float:
    ingredient_list = parse_ingredients_field(ingredients_value)
    total = 0.0

    for raw in ingredient_list[:max_ingredients]:
        cleaned = clean_ingredient(raw)
        kcal = query_usda_calories(cleaned, cache)
        if kcal:
            total += float(kcal)

    return total


def add_usda_calories(df: pd.DataFrame, ingredients_col: str = "ingredients", max_rows: int | None = None) -> pd.DataFrame:
    if ingredients_col not in df.columns:
        print(f"⚠ ingredients column '{ingredients_col}' not found, skipping USDA calories")
        df["total_calories_usda"] = None
        return df

    cache = _load_cache()
    df = df.copy()

    total_rows = len(df)
    limit = max_rows if max_rows is not None else total_rows

    calories = []
    for i, val in enumerate(df[ingredients_col]):
        if i >= limit:
            calories.append(None)
            continue

        if i % 100 == 0:
            print(f"USDA calories: processing row {i}/{limit}")

        total = compute_total_calories_for_row(val, cache)
        calories.append(total)

    df["total_calories_usda"] = calories
    _save_cache(cache)
    return df
