# cuisine_type_utils.py
# Usage (DataFrame-in/out):
#   df = add_cuisine_type(df, path_col="cuisine_path")
#
# Usage (CSV wrapper, returns only cuisine_type column):
#   out = categorize_cuisine_type("input.csv", path_col="cuisine_path")
#
# Behavior:
#   - Parses the cuisine_path column only (no ML, no broad keyword mapping)
#   - Matches against a controlled list:
#       american, chinese, japanese, korean, thai, vietnamese, indian,
#       middle_eastern, mediterranean, italian, french, spanish, mexican,
#       latin_american, african, caribbean, british, german, nordic
#   - If no match, sets "N/A"

from __future__ import annotations
import re
import pandas as pd
from typing import Dict

# Controlled output tokens (snake_case)
CONTROLLED_CUISINES = [
    "american", "chinese", "japanese", "korean", "thai", "vietnamese",
    "indian", "middle_eastern", "mediterranean", "italian", "french",
    "spanish", "mexican", "latin_american", "african", "caribbean",
    "british", "german", "nordic",
]

# Patterns to look for in the path (lowercase, with spaces) → output token
# (single-word cuisines map to themselves; multi-word need explicit patterns)
PATTERN_TO_TOKEN: Dict[str, str] = {
    "american": "american",
    "chinese": "chinese",
    "japanese": "japanese",
    "korean": "korean",
    "thai": "thai",
    "vietnamese": "vietnamese",
    "indian": "indian",
    "middle eastern": "middle_eastern",
    "mediterranean": "mediterranean",
    "italian": "italian",
    "french": "french",
    "spanish": "spanish",
    "mexican": "mexican",
    "latin american": "latin_american",
    "african": "african",
    "caribbean": "caribbean",
    "british": "british",
    "german": "german",
    "nordic": "nordic",
}

def _norm_text(s: str) -> str:
    """lowercase, trim, collapse whitespace, normalize separators to '/'."""
    s = (s or "").lower().strip()
    s = re.sub(r"[>\|]", "/", s)              # accept '>' or '|' as separators too
    s = re.sub(r"\s+", " ", s)
    return s

def _extract_cuisine_from_path(path_value: str) -> str:
    """Return a controlled cuisine token if found in path; else 'N/A'."""
    if not isinstance(path_value, str) or not path_value.strip():
        return "N/A"
    text = _norm_text(path_value)
    # Check each pattern; first match wins
    for pattern, token in PATTERN_TO_TOKEN.items():
        if pattern in text:
            return token
    return "N/A"

def add_cuisine_type(df: pd.DataFrame, *, path_col: str = "cuisine_path") -> pd.DataFrame:
    """
    DataFrame → DataFrame. Adds:
      - cuisine_type (one of CONTROLLED_CUISINES or 'N/A')
    Does not write to disk.
    """
    df = df.copy()
    # find the cuisine_path-like column if needed
    if path_col not in df.columns:
        alt = next((c for c in df.columns if "cuisine" in c.lower() and "path" in c.lower()), None)
        if not alt:
            df["cuisine_type"] = "N/A"
            return df
        path_col = alt

    df["cuisine_type"] = df[path_col].apply(_extract_cuisine_from_path)
    return df

def categorize_cuisine_type(csv_path: str, *, path_col: str = "cuisine_path") -> pd.DataFrame:
    """
    CSV wrapper (parity with your other helpers).
    Reads CSV, derives cuisine_type, and returns only that column.
    Does not save to CSV.
    """
    df = pd.read_csv(csv_path)
    df2 = add_cuisine_type(df, path_col=path_col)
    return df2[["cuisine_type"]]
