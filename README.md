# CS598 Nutrition Dataset Processing
This repository includes the python scripts for processing, input data, and output data

## Project Structure

```
CS598_Nutrition_dataset/
├── input_data/              # Raw input CSV files
│   ├── recipes.csv          # Main recipe dataset
│   └── test_recipes.csv     # Test dataset
├── output_data/             # Processed output CSV files
│   ├── cleaned_recipes.csv
│   └── cleaned_test_recipes.csv
├── processing_scripts/      # Processing modules
│   ├── category.py          # Recipe category classification (appetizer/main/dessert)
│   ├── cuisine_type.py      # Cuisine type detection (Italian, Chinese, etc.)
│   ├── data_cleaning.py     # Time standardization (convert to minutes)
│   ├── dietary_labels.py    # Dietary restriction detection (vegetarian, vegan, etc.)
│   └── difficulty.py        # Recipe difficulty calculation
└── processing.py            # Main orchestration script
```

## Features

### Data Cleaning (`data_cleaning.py`)
- Standardizes time columns (Prep Time, Cook Time, Total Time) to minutes
- Fills missing time values with 0
- Handles various time formats (e.g., "20 mins", "1 hrs", "PT1H30M")

### Category Classification (`category.py`)
- Classifies recipes into courses: appetizer, main dish, or dessert
- Based on top-level cuisine path

### Cuisine Type Detection (`cuisine_type.py`)
- Identifies cuisine types from cuisine path
- Supported cuisines: American, Chinese, Japanese, Korean, Thai, Vietnamese, Indian, Middle Eastern, Mediterranean, Italian, French, Spanish, Mexican, Latin American, African, Caribbean, British, German, Nordic
- Returns "N/A" if no match found

### Dietary Labels (`dietary_labels.py`)
- Detects dietary restrictions based on ingredients
- Flags: Vegetarian, Vegan, Pescatarian, Dairy-Free, Nut-Free, Egg-Free
- Returns combined dietary restrictions as comma-separated string

### Difficulty Scoring (`difficulty.py`)
- Calculates difficulty score based on total_time × number_of_directions
- Difficulty buckets:
  - Easy: < 200
  - Medium: < 600
  - Hard: ≥ 600
  - N/A: if score is 0 or total_time column is missing

## Usage

### Basic Usage

```bash
python processing.py <input.csv> <output.csv>
```

### Example

```bash
python processing.py input_data/test_recipes.csv output_data/cleaned_test_recipes.csv
```

### What the Pipeline Does

1. **Data Cleaning**: Standardizes all time columns to minutes
2. **Category Classification**: Adds `course` column (appetizer/main/dessert)
3. **Cuisine Detection**: Adds `cuisine_type` column
4. **Dietary Analysis**: Adds `dietary_restrictions` column
5. **Difficulty Calculation**: Adds `difficulty_score` and `difficulty` columns

## Output Columns

The processed CSV includes:
- All original columns
- `top_level_cuisine`: Extracted cuisine category
- `course`: Recipe course (appetizer, main, dessert)
- `cuisine_type`: Detected cuisine type or "N/A"
- `dietary_restrictions`: Detected dietary labels or "None"
- `difficulty_score`: Calculated difficulty score
- `difficulty`: Difficulty level (easy, medium, hard, or "N/A")

## Requirements

- Python 3.x
- pandas
- numpy

## Notes

- Missing or invalid data defaults to "N/A" for relevant fields
- Processing automatically overwrites output files
- All time values are standardized to minutes (integers)
