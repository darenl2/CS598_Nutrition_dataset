# difficulty_utils.py
# Usage (DataFrame-in/out):
#   df = add_difficulty(df, time_col="total_time", directions_col="directions")
#
# Usage (CSV wrapper, returns only difficulty columns):
#   out = categorize_difficulty("input.csv", time_col="total_time", directions_col="directions")

import ast
import pandas as pd

def _count_steps(val) -> int:
    """
    Robust step counter:
      - if directions is a JSON/Python list string → count non-empty items
      - else split text by newline, fallback to periods
    """
    if val is None:
        return 0
    s = str(val).strip()
    if not s:
        return 0
    # Try list-like first
    try:
        maybe = ast.literal_eval(s)
        if isinstance(maybe, list):
            return sum(1 for x in maybe if str(x).strip())
    except Exception:
        pass
    # Fallback: text splits
    parts = [x.strip() for x in s.split("\n") if x.strip()]
    if len(parts) <= 1:
        parts = [x.strip() for x in s.split(".") if x.strip()]
    return len(parts)

def _to_minutes(x) -> float:
    try:
        return max(float(x), 0.0)
    except Exception:
        return 0.0

def _bucket(score: float) -> str:
    # Ultra-simple buckets you can tweak later
    if score < 200:
        return "easy"
    elif score < 600:
        return "medium"
    else:
        return "hard"

def add_difficulty(df: pd.DataFrame, *, time_col: str = "total_time", directions_col: str = "directions") -> pd.DataFrame:
    """
    DataFrame → DataFrame. Adds:
      - difficulty_score = total_time * number_of_directions
      - difficulty ∈ {easy, medium, hard}
    Does not write to disk.
    """
    df = df.copy()

    # Ensure columns exist (graceful defaults if missing)
    if time_col not in df.columns:
        df["_tmp_time_"] = 0.0
        time_col = "_tmp_time_"
    if directions_col not in df.columns:
        df["_tmp_dir_"] = ""
        directions_col = "_tmp_dir_"

    steps = df[directions_col].apply(_count_steps)
    mins = df[time_col].apply(_to_minutes)
    df["difficulty_score"] = (mins * steps).round(2)
    df["difficulty"] = df["difficulty_score"].apply(_bucket)

    # Drop temps if we created them
    for c in ["_tmp_time_", "_tmp_dir_"]:
        if c in df.columns:
            df.drop(columns=[c], inplace=True)
    return df

def categorize_difficulty(csv_path: str, *, time_col: str = "total_time", directions_col: str = "directions") -> pd.DataFrame:
    """
    Convenience wrapper mirroring your other CSV-path helpers.
    Reads CSV, computes difficulty, and returns only the new columns.
    Does not save to CSV (keeps parity with your dietary/cuisine helpers).
    """
    df = pd.read_csv(csv_path)
    df2 = add_difficulty(df, time_col=time_col, directions_col=directions_col)
    return df2[["difficulty_score", "difficulty"]]
