import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib
import os
import sys

# Add project root to sys.path to allow importing config_loader
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)
import config_loader as cfg # Import your configuration

# --- Configuration ---
DATASET_PATH = cfg.DATASET_PATH # Make sure this path is correct
# For one-hot encoding, we can specify a prefix to make new column names clearer
TYPE_COLUMN_PREFIX = "Type"
TARGET_COLUMN = 'Machine failure'
# Columns to drop as they are identifiers or too specific for general failure prediction initially
# We will also drop the specific failure types for now, focusing on the main 'Machine failure' target
COLUMNS_TO_DROP = ['UDI', 'Product ID', 'TWF', 'HDF', 'PWF', 'OSF', 'RNF']
# Features to scale
NUMERICAL_FEATURES = ['Air temperature [K]', 'Process temperature [K]', 'Rotational speed [rpm]', 'Torque [Nm]', 'Tool wear [min]']

TEST_SIZE = 0.2 # 20% of data for testing
RANDOM_STATE = 42 # For reproducibility

def load_data(path):
    """Loads the dataset from a CSV file."""
    try:
        df = pd.read_csv(path)
        print("Dataset loaded successfully for preprocessing.")
        return df
    except FileNotFoundError:
        print(f"Error: The file {path} was not found.")
        return None
    except Exception as e:
        print(f"An error occurred while loading the data: {e}")
        return None

def preprocess_data(df):
    """Performs preprocessing steps."""
    if df is None:
        return None, None, None, None

    # Drop unnecessary columns
    df_processed = df.drop(columns=COLUMNS_TO_DROP)
    print(f"Dropped columns: {', '.join(COLUMNS_TO_DROP)}")

    # One-hot encode the 'Type' column
    # drop_first=True helps to avoid multicollinearity if we were using linear models,
    # and reduces dimensionality slightly. For tree models, it's less critical but good practice.
    df_processed = pd.get_dummies(df_processed, columns=['Type'], prefix=TYPE_COLUMN_PREFIX, dtype=int)
    print("One-hot encoded 'Type' column.")
    print("Columns after one-hot encoding:", df_processed.columns.tolist())


    # Define features (X) and target (y)
    X = df_processed.drop(columns=[TARGET_COLUMN])
    y = df_processed[TARGET_COLUMN]
    print(f"Target variable: {TARGET_COLUMN}")
    print(f"Features: {X.columns.tolist()}")

    # Split data into training and testing sets
    # We use stratify=y because of the class imbalance in the target variable.
    # This ensures both train and test sets have a similar proportion of failures.
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )
    print(f"Data split into training and testing sets: {len(X_train)} train, {len(X_test)} test.")
    print(f"Training target distribution:\n{y_train.value_counts(normalize=True)}")
    print(f"Testing target distribution:\n{y_test.value_counts(normalize=True)}")

    # Feature Scaling (StandardScaler) for numerical features
    # Decision trees are not sensitive to feature scaling, but many other algorithms are.
    # It's generally good practice, and vital if we later compare with models that need it.
    # For zk-SNARKs, having features in a controlled range might also simplify circuit design later.
    scaler = StandardScaler()
    X_train[NUMERICAL_FEATURES] = scaler.fit_transform(X_train[NUMERICAL_FEATURES])
    X_test[NUMERICAL_FEATURES] = scaler.transform(X_test[NUMERICAL_FEATURES])
    print("Numerical features scaled using StandardScaler.")

    # --- save the scaler ---
    print(f"Saving standard scaler to: {cfg.SCALER_PATH}")
    joblib.dump(scaler, cfg.SCALER_PATH)
    # --- End of addition ---

    print("First 5 rows of scaled X_train:")
    print(X_train.head())


    return X_train, X_test, y_train, y_test, X.columns.tolist() # also return feature names

# --- Main execution ---
if __name__ == "__main__":
    dataset = load_data(DATASET_PATH)
    if dataset is not None:
        X_train, X_test, y_train, y_test, feature_names = preprocess_data(dataset)
        if X_train is not None:
            print("\nPreprocessing complete.")
           # --- Save the processed data and feature names ---
            X_train.to_csv(cfg.X_TRAIN_CSV_PATH, index=False)
            X_test.to_csv(cfg.X_TEST_CSV_PATH, index=False)
            y_train.to_csv(cfg.Y_TRAIN_CSV_PATH, index=False, header=['Machine failure']) # Save with header
            y_test.to_csv(cfg.Y_TEST_CSV_PATH, index=False, header=['Machine failure'])   # Save with header
            print(f"Saving feature names to: {cfg.FEATURE_NAMES_PATH}")
            joblib.dump(feature_names, cfg.FEATURE_NAMES_PATH)

            print(f"\nShape of X_train: {X_train.shape}")
            print(f"Shape of X_test: {X_test.shape}")
            print(f"Shape of y_train: {y_train.shape}")
            print(f"Shape of y_test: {y_test.shape}")
            print(f"Feature names: {feature_names}")
            print("Processed data (X_train, X_test, y_train, y_test) and feature_names saved to files.") 