import pandas as pd

def analyze_calories(file_path):
    """
    Analyzes the 'total_calories_usda' column of a CSV file.

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        dict: A dictionary containing the mean, median, 25th percentile,
              75th percentile, minimum, and maximum calories, along with
              the recipe names and row indices for the min, median, and max calories.
    """
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        return {"error": f"File not found at {file_path}"}

    if 'total_calories_usda' not in df.columns:
        return {"error": "'total_calories_usda' column not found in the CSV."}

    calories = df['total_calories_usda'].dropna()

    if calories.empty:
        return {"error": "No valid calorie data found in 'total_calories_usda' column."}

    mean_calories = calories.mean()
    median_calories = calories.median()
    percentile_25 = calories.quantile(0.25)
    percentile_75 = calories.quantile(0.75)
    min_calories = calories.min()
    max_calories = calories.max()

    # Get the index of the min, median, and max calorie values
    min_calorie_row = df.loc[calories.idxmin()]
    max_calorie_row = df.loc[calories.idxmax()]
    median_calorie_row = df.loc[(df['total_calories_usda'] - median_calories).abs().argsort()[:1].values[0]]


    return {
        "mean_calories": mean_calories,
        "median_calories": median_calories,
        "25th_percentile_calories": percentile_25,
        "75th_percentile_calories": percentile_75,
        "min_calories": min_calories,
        "min_calorie_recipe_name": min_calorie_row['recipe_name'] if 'recipe_name' in df.columns else "N/A",
        "min_calorie_row_index": int(min_calorie_row.name),
        "max_calories": max_calories,
        "max_calorie_recipe_name": max_calorie_row['recipe_name'] if 'recipe_name' in df.columns else "N/A",
        "max_calorie_row_index": int(max_calorie_row.name),
        "median_calorie_recipe_name": median_calorie_row['recipe_name'] if 'recipe_name' in df.columns else "N/A",
        "median_calorie_row_index": int(median_calorie_row.name)
    }

def analyze_difficulty(file_path):
    """
    Analyzes the 'difficulty' column of a CSV file to count recipes by difficulty.

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        dict: A dictionary containing the counts for each difficulty level.
    """
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        return {"error": f"File not found at {file_path}"}

    if 'difficulty' not in df.columns:
        return {"error": "'difficulty' column not found in the CSV."}

    difficulty_counts = df['difficulty'].value_counts().to_dict()

    return {"difficulty_counts": difficulty_counts}

def analyze_difficulty_scores(file_path):
    """
    Analyzes the 'difficulty' column of a CSV file for numerical scores.

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        dict: A dictionary containing the min, median, mean, and max difficulty scores,
              along with recipe names and row indices for these scores.
    """
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        return {"error": f"File not found at {file_path}"}

    if 'difficulty_score' not in df.columns:
        return {"error": "'difficulty_score' column not found in the CSV."}

    scores = df['difficulty_score'].dropna()

    if scores.empty:
        return {"error": "No valid difficulty score data found."}

    min_score = scores.min()
    median_score = scores.median()
    mean_score = scores.mean()
    max_score = scores.max()

    # Get the row for min, median (closest), and max scores
    min_score_row = df.loc[scores.idxmin()]
    max_score_row = df.loc[scores.idxmax()]
    median_score_row_index = (df['difficulty_score'] - median_score).abs().idxmin()
    median_score_row = df.loc[median_score_row_index]

    return {
        "min_difficulty_score": min_score,
        "min_difficulty_recipe_name": min_score_row['recipe_name'] if 'recipe_name' in df.columns else "N/A",
        "min_difficulty_row_index": int(min_score_row.name),
        "median_difficulty_score": median_score,
        "median_difficulty_recipe_name": median_score_row['recipe_name'] if 'recipe_name' in df.columns else "N/A",
        "median_difficulty_row_index": int(median_score_row.name),
        "mean_difficulty_score": mean_score,
        "max_difficulty_score": max_score,
        "max_difficulty_recipe_name": max_score_row['recipe_name'] if 'recipe_name' in df.columns else "N/A",
        "max_difficulty_row_index": int(max_score_row.name),
    }

def analyze_by_dietary_restriction(file_path):
    """
    Analyzes calorie and difficulty scores for each unique dietary restriction.

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        dict: A nested dictionary with analysis for each dietary restriction.
    """
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        return {"error": f"File not found at {file_path}"}

    if 'dietary_restrictions' not in df.columns:
        return {"error": "'dietary_restrictions' column not found in the CSV."}
    if 'total_calories_usda' not in df.columns:
        return {"error": "'total_calories_usda' column not found in the CSV."}
    if 'difficulty_score' not in df.columns:
        return {"error": "'difficulty_score' column not found in the CSV."}

    all_restrictions = set()
    # Ensure we handle NaN values in dietary_restrictions gracefully
    for restrictions_str in df['dietary_restrictions'].dropna():
        if restrictions_str.strip() != "N/A": # Ignore 'N/A' as a restriction
            for res in restrictions_str.split(', '):
                all_restrictions.add(res.strip())
    
    analysis_results = {}
    for restriction in sorted(list(all_restrictions)): # Sort for consistent output
        # Filter DataFrame for recipes containing the current restriction
        filtered_df = df[df['dietary_restrictions'].dropna().apply(lambda x: restriction in x and restriction != "N/A")]

        if filtered_df.empty:
            analysis_results[restriction] = {"error": f"No recipes found for restriction: {restriction}"}
            continue

        # Calorie analysis
        calories = filtered_df['total_calories_usda'].dropna()
        if calories.empty:
            calorie_analysis = {"error": "No valid calorie data for this restriction."}
        else:
            min_cal = calories.min()
            median_cal = calories.median()
            max_cal = calories.max()
            
            min_cal_row = filtered_df.loc[calories.idxmin()]
            max_cal_row = filtered_df.loc[calories.idxmax()]
            median_cal_row_index = (calories - median_cal).abs().idxmin()
            median_cal_row = filtered_df.loc[median_cal_row_index]

            calorie_analysis = {
                "min_calories": min_cal,
                "min_calorie_recipe_name": min_cal_row['recipe_name'] if 'recipe_name' in df.columns else "N/A",
                "min_calorie_row_index": int(min_cal_row.name),
                "median_calories": median_cal,
                "median_calorie_recipe_name": median_cal_row['recipe_name'] if 'recipe_name' in df.columns else "N/A",
                "median_calorie_row_index": int(median_cal_row.name),
                "max_calories": max_cal,
                "max_calorie_recipe_name": max_cal_row['recipe_name'] if 'recipe_name' in df.columns else "N/A",
                "max_calorie_row_index": int(max_cal_row.name),
            }
        
        # Difficulty score analysis
        scores = filtered_df['difficulty_score'].dropna()
        if scores.empty:
            difficulty_analysis = {"error": "No valid difficulty score data for this restriction."}
        else:
            min_score = scores.min()
            median_score = scores.median()
            max_score = scores.max()

            min_score_row = filtered_df.loc[scores.idxmin()]
            max_score_row = filtered_df.loc[scores.idxmax()]
            median_score_row_index = (scores - median_score).abs().idxmin()
            median_score_row = filtered_df.loc[median_score_row_index]

            difficulty_analysis = {
                "min_difficulty_score": min_score,
                "min_difficulty_recipe_name": min_score_row['recipe_name'] if 'recipe_name' in df.columns else "N/A",
                "min_difficulty_row_index": int(min_score_row.name),
                "median_difficulty_score": median_score,
                "median_difficulty_recipe_name": median_score_row['recipe_name'] if 'recipe_name' in df.columns else "N/A",
                "median_difficulty_row_index": int(median_score_row.name),
                "max_difficulty_score": max_score,
                "max_difficulty_recipe_name": max_score_row['recipe_name'] if 'recipe_name' in df.columns else "N/A",
                "max_difficulty_row_index": int(max_score_row.name),
            }
        
        analysis_results[restriction] = {
            "calorie_analysis": calorie_analysis,
            "difficulty_analysis": difficulty_analysis
        }
    
    return analysis_results

if __name__ == "__main__":
    file_path = "/Users/darenliu/Documents/UIUC_Classes/CS598/CS598_Nutrition_dataset/output_data/cleaned_recipes.csv"
    analysis_results = analyze_calories(file_path)

    if "error" in analysis_results:
        print(f"Error: {analysis_results['error']}")
    else:
        print("Calorie Analysis Results:")
        for key, value in analysis_results.items():
            if isinstance(value, (float, int)) and not isinstance(value, bool):
                print(f"- {key.replace('_', ' ').title()}: {value:.2f}")
            else:
                print(f"- {key.replace('_', ' ').title()}: {value}")
    
    print("\n" + "-" * 30 + "\n") # Separator

    difficulty_results = analyze_difficulty(file_path)

    if "error" in difficulty_results:
        print(f"Error: {difficulty_results['error']}")
    else:
        print("Difficulty Analysis Results:")
        for difficulty, count in difficulty_results["difficulty_counts"].items():
            print(f"- {difficulty.title()}: {count}")

    print("\n" + "-" * 30 + "\n") # Separator

    difficulty_score_results = analyze_difficulty_scores(file_path)

    if "error" in difficulty_score_results:
        print(f"Error: {difficulty_score_results['error']}")
    else:
        print("Difficulty Score Analysis Results:")
        for key, value in difficulty_score_results.items():
            if isinstance(value, (float, int)) and not isinstance(value, bool):
                print(f"- {key.replace('_', ' ').title()}: {value:.2f}")
            else:
                print(f"- {key.replace('_', ' ').title()}: {value}")
    
    print("\n" + "-" * 30 + "\n") # Separator

    dietary_restriction_results = analyze_by_dietary_restriction(file_path)

    if "error" in dietary_restriction_results:
        print(f"Error: {dietary_restriction_results['error']}")
    else:
        print("Dietary Restriction Analysis Results:")
        for restriction, results in dietary_restriction_results.items():
            print(f"\n--- {restriction.replace('_', ' ').title()} ---")
            if "error" in results:
                print(f"  Error: {results['error']}")
            else:
                print("  Calorie Analysis:")
                for key, value in results["calorie_analysis"].items():
                    if isinstance(value, (float, int)) and not isinstance(value, bool):
                        print(f"    - {key.replace('_', ' ').title()}: {value:.2f}")
                    else:
                        print(f"    - {key.replace('_', ' ').title()}: {value}")
                print("  Difficulty Analysis:")
                for key, value in results["difficulty_analysis"].items():
                    if isinstance(value, (float, int)) and not isinstance(value, bool):
                        print(f"    - {key.replace('_', ' ').title()}: {value:.2f}")
                    else:
                        print(f"    - {key.replace('_', ' ').title()}: {value}")
