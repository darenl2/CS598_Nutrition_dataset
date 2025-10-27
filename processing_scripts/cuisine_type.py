from __future__ import annotations
import re
import pandas as pd

CONTROLLED_CUISINES = [
    "american", "chinese", "japanese", "korean", "thai", "vietnamese",
    "indian", "middle_eastern", "mediterranean", "italian", "french",
    "spanish", "mexican", "latin_american", "african", "caribbean",
    "british", "german", "nordic",
]

def _norm_text(s: str) -> str:
    s = (s or "").lower().strip()
    s = re.sub(r"[>\|]", "/", s)
    s = re.sub(r"\s+", " ", s)
    return s

def _extract_cuisine_from_path(path_value: str) -> str:
    """Return a controlled cuisine token if found in path; else 'N/A'."""
    if not isinstance(path_value, str) or not path_value.strip():
        return "N/A"
    text = _norm_text(path_value)
    
    for cuisine in CONTROLLED_CUISINES:
        pattern = cuisine.replace("_", " ")
        if pattern in text:
            return cuisine
    
    return "N/A"

def add_cuisine_type(df: pd.DataFrame, *, path_col: str = "cuisine_path") -> pd.DataFrame:

    df = df.copy()
    if path_col not in df.columns:
        alt = next((c for c in df.columns if "cuisine" in c.lower() and "path" in c.lower()), None)
        if not alt:
            df["cuisine_type"] = "N/A"
            return df
        path_col = alt

    df["cuisine_type"] = df[path_col].apply(_extract_cuisine_from_path)
    return df

def categorize_cuisine_type(csv_path: str, *, path_col: str = "cuisine_path") -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    df2 = add_cuisine_type(df, path_col=path_col)
    return df2[["cuisine_type"]]
