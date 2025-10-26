#!/usr/bin/env python3

import re
import pandas as pd
import numpy as np


def fill_missing_times_with_zero_df(input_csv, prep_col="prep_time", cook_col="cook_time", total_col="total_time"):
    """
    input_csv: path to CSV file
    """
    df = pd.read_csv(input_csv)

    for col in [prep_col, cook_col, total_col]:
        if col not in df.columns:
            df[col] = np.nan

    def clean_value(x):
        if pd.isna(x) or str(x).strip().lower() in {"", "none", "nan", "null"}:
            return 0
        try:
            return int(float(x))
        except ValueError:
            return 0

    df[prep_col] = df[prep_col].apply(clean_value)
    df[cook_col] = df[cook_col].apply(clean_value)
    df[total_col] = df[total_col].apply(clean_value)

    # Ensure integer dtype
    df[prep_col] = df[prep_col].astype(int)
    df[cook_col] = df[cook_col].astype(int)
    df[total_col] = df[total_col].astype(int)

    return df


def standardize_time_columns_df(input_csv, prep_col="prep_time", cook_col="cook_time", total_col="total_time"):
    """
    input_csv: Path to the CSV file.
    """
    df = pd.read_csv(input_csv)

    def parse_time_to_minutes(value):
        if pd.isna(value):
            return 0
        if isinstance(value, (int, float)):
            return int(round(value))

        text = str(value).lower().strip()

        iso = re.match(r"pt(?:(\d+(?:\.\d+)?)h)?(?:(\d+(?:\.\d+)?)m)?", text)
        if iso:
            h = float(iso.group(1) or 0)
            m = float(iso.group(2) or 0)
            return int(round(h * 60 + m))

        hours = re.findall(r"(\d+(?:\.\d+)?)\s*(?:h|hr|hour|hours)", text)
        minutes = re.findall(r"(\d+(?:\.\d+)?)\s*(?:m|min|mins|minute|minutes)", text)

        h = float(hours[0]) if hours else 0.0
        m = float(minutes[0]) if minutes else 0.0

        if not hours and not minutes:
            nums = re.findall(r"\d+(?:\.\d+)?", text)
            if nums:
                m = float(nums[0])

        return int(round(h * 60 + m))

    df["prep_time_minutes"] = (
        df[prep_col].apply(parse_time_to_minutes) if prep_col in df.columns else 0
    )
    df["cook_time_minutes"] = (
        df[cook_col].apply(parse_time_to_minutes) if cook_col in df.columns else 0
    )

    if total_col in df.columns:
        df["total_time_minutes"] = df[total_col].apply(parse_time_to_minutes)
    else:
        df["total_time_minutes"] = (
            df["prep_time_minutes"] + df["cook_time_minutes"]
        )

    df["prep_time_minutes"] = df["prep_time_minutes"].astype(int)
    df["cook_time_minutes"] = df["cook_time_minutes"].astype(int)
    df["total_time_minutes"] = df["total_time_minutes"].astype(int)

    return df
