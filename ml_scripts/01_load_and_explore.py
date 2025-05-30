import pandas as pd
import os

# --- Configuration ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATASET_PATH = os.path.join(BASE_DIR, 'data', 'manufacturing_6G_dataset.csv') # Make sure this path is correct

def load_data(path):
    """Loads the dataset from a CSV file."""
    try:
        df = pd.read_csv(path)
        print("Dataset loaded successfully!")
        return df
    except FileNotFoundError:
        print(f"Error: The file {path} was not found.")
        print("Please make sure the dataset is in the correct directory.")
        return None
    except Exception as e:
        print(f"An error occurred while loading the data: {e}")
        return None

def explore_data(df):
    """Performs initial exploration of the dataframe."""
    if df is None:
        return

    print("\n--- First 5 Rows ---")
    print(df.head())

    print("\n--- Dataset Info ---")
    df.info()

    print("\n--- Descriptive Statistics ---")
    print(df.describe())

    print("\n--- Value Counts for 'Type' ---")
    print(df['Type'].value_counts())

    print("\n--- Value Counts for 'Machine failure' (Target Variable) ---")
    print(df['Machine failure'].value_counts())

    # Identify potential specific failure columns if they exist
    failure_columns = [col for col in df.columns if 'failure' in col.lower() and col != 'Machine failure']
    if failure_columns:
        print("\n--- Value Counts for Specific Failure Types ---")
        for col in failure_columns:
            print(f"\n--- {col} ---")
            print(df[col].value_counts())


# --- Main execution ---
if __name__ == "__main__":
    dataset = load_data(DATASET_PATH)
    if dataset is not None:
        explore_data(dataset)
        print("\nScript finished.")