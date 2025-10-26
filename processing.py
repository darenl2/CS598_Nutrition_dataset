import sys
import re
import ast
import pandas as pd

from processing_scripts import cuisines as cuisines_mod
from processing_scripts import dietary_labels as dietary_mod
from processing_scripts import difficulty as difficulty_mod
from processing_scripts import data_cleaning as data_cleaning_mod  


def add_course_from_cuisine_path(df: pd.DataFrame, path_col: str = "cuisine_path") -> pd.DataFrame:
    """Derive top_level_cuisine and a simple course label using cuisines.py utilities."""
    # find cuisine_path-like column
    col = path_col if path_col in df.columns else next((c for c in df.columns if "cuisine" in c.lower()), None)

    def top_level(x: str):
        if not isinstance(x, str) or not x.strip():
            return None
        s = x.strip().strip("/")
        s = re.sub(r"\s*>\s*|\s*\|\s*", "/", s)
        return s.split("/")[0] if "/" in s else s

    df = df.copy()
    df["top_level_cuisine"] = df[col].astype(str).apply(top_level) if col else None

    # use your cuisines.py categorize_cuisines() to map top-levels into buckets, then to canonical course
    uniques = sorted(set([t for t in df["top_level_cuisine"].dropna().tolist()]))
    buckets = cuisines_mod.categorize_cuisines(uniques)  # {"Appetizers":[...], "Main Dish":[...], "Dessert":[...]}

    rev = {}
    for bucket, items in buckets.items():
        for it in items:
            rev[it] = bucket

    def to_course(tlc):
        b = rev.get(tlc, "Main Dish")
        return {"Appetizers": "appetizer", "Main Dish": "main", "Dessert": "dessert"}.get(b, "main")

    df["course"] = df["top_level_cuisine"].apply(to_course)
    return df


def add_dietary_flags(df: pd.DataFrame, in_csv_path: str) -> pd.DataFrame:
    """Use your dietary_labels.py which returns a DF of booleans from a CSV path; align and merge."""
    flags = dietary_mod.categorize_dietary_labels(in_csv_path)
    flags = flags.reset_index(drop=True)
    df = df.reset_index(drop=True)
    return pd.concat([df, flags], axis=1)


def add_difficulty_simple(df: pd.DataFrame) -> pd.DataFrame:
    """
    Keep difficulty identical to your simple version:
      score = total_time * number_of_directions
      buckets: <200 easy, <600 medium, else hard
    We don't call a CLI; we inline the same logic so the orchestrator stays file-in/file-out.
    """
    # detect columns
    time_col = next((c for c in df.columns if c.lower() in ["total_time", "total time"]), None)
    dir_col = next((c for c in df.columns if any(k in c.lower() for k in ["direction","instruction","step"])), None)

    def count_steps(val):
        if val is None:
            return 0
        s = str(val).strip()
        try:
            maybe = ast.literal_eval(s)
            if isinstance(maybe, list):
                return sum(1 for x in maybe if str(x).strip())
        except Exception:
            pass
        parts = [x.strip() for x in s.split("\n") if x.strip()]
        if len(parts) <= 1:
            parts = [x.strip() for x in s.split(".") if x.strip()]
        return len(parts)

    def to_minutes(x):
        try:
            return max(float(x), 0.0)
        except Exception:
            return 0.0

    steps = df[dir_col].apply(count_steps) if dir_col else 0
    mins = df[time_col].apply(to_minutes) if time_col else 0.0
    score = (mins * steps).round(2) if isinstance(steps, pd.Series) else 0.0

    df = df.copy()
    df["difficulty_score"] = score

    def bucket(s):
        if s < 200:
            return "easy"
        elif s < 600:
            return "medium"
        return "hard"

    df["difficulty"] = df["difficulty_score"].apply(bucket) if isinstance(score, pd.Series) else "easy"
    return df

# ---------- main ----------

def main():
    if len(sys.argv) != 3:
        print("Usage: python build_cleaned_dataset.py <input.csv> <output.csv>")
        sys.exit(1)

    in_csv, out_csv = sys.argv[1], sys.argv[2]
    
    # Apply data cleaning: standardize time columns (replaces original columns)
    # Check what column names exist and map appropriately
    temp_df = pd.read_csv(in_csv, nrows=1)
    
    # Map based on what columns exist
    prep_col = "prep_time" if "prep_time" in temp_df.columns else ("Prep Time" if "Prep Time" in temp_df.columns else None)
    cook_col = "cook_time" if "cook_time" in temp_df.columns else ("Cook Time" if "Cook Time" in temp_df.columns else None)
    total_col = "total_time" if "total_time" in temp_df.columns else ("Total Time" if "Total Time" in temp_df.columns else None)
    
    df = data_cleaning_mod.standardize_time_columns_df(in_csv, prep_col=prep_col, cook_col=cook_col, total_col=total_col)

    # Continue with other transformations
    df = add_course_from_cuisine_path(df)
    df = add_dietary_flags(df, in_csv)
    df = add_difficulty_simple(df)

    # Write to CSV, overwriting any existing file
    df.to_csv(out_csv, index=False, mode='w')
    print(f"✅ cleaned dataset written: {out_csv}")

if __name__ == "__main__":
    main()
