#!/usr/bin/env python3
# simple_difficulty.py
# Usage: python simple_difficulty.py input.csv output.csv
# Assumes columns: total_time (minutes), directions (list OR text)

import sys
import ast
import csv

def count_steps(val):
    if val is None:
        return 0
    # If it's a Python-list string like '["step1","step2"]', parse it
    s = str(val).strip()
    try:
        maybe = ast.literal_eval(s)
        if isinstance(maybe, list):
            return sum(1 for x in maybe if str(x).strip())
    except Exception:
        pass
    # Fallback: split plain text on newlines; if too few, split on periods
    steps = [x.strip() for x in s.split("\n") if x.strip()]
    if len(steps) <= 1:
        steps = [x.strip() for x in s.split(".") if x.strip()]
    return len(steps)

def to_minutes(x):
    try:
        return max(float(x), 0.0)
    except Exception:
        return 0.0

def bucket(score):
    # Ultra-simple buckets you can tweak later if you want
    if score < 200:
        return "easy"
    elif score < 600:
        return "medium"
    else:
        return "hard"

def main():
    if len(sys.argv) != 3:
        print("Usage: python simple_difficulty.py input.csv output.csv")
        sys.exit(1)

    infile, outfile = sys.argv[1], sys.argv[2]

    with open(infile, newline="", encoding="utf-8") as f_in:
        reader = csv.DictReader(f_in)
        rows = list(reader)
        fieldnames = reader.fieldnames or []

    # Ensure output columns
    extra_cols = ["difficulty_score", "difficulty"]
    out_fields = fieldnames + [c for c in extra_cols if c not in fieldnames]

    for r in rows:
        total_time = to_minutes(r.get("total_time"))
        steps = count_steps(r.get("directions"))
        score = total_time * steps
        r["difficulty_score"] = f"{score:.2f}"
        r["difficulty"] = bucket(score)

    with open(outfile, "w", newline="", encoding="utf-8") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Done. Wrote {outfile}")

if __name__ == "__main__":
    main()
