import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
import joblib # For loading feature names and later the model
import matplotlib.pyplot as plt # For plotting tree (optional, needs graphviz for visualization)
from sklearn.tree import plot_tree # For plotting tree
import os

# --- Configuration ---
current_script_dir = os.path.dirname(__file__) # 1. Determine the path to the directory containing *this* script 
BASE_DIR = os.path.abspath(os.path.join(current_script_dir, '..')) # 2. Go up one level to reach the project root ('your_root_directory')

DATA_SPLITS_DIR = os.path.join(BASE_DIR, "artifacts", "data_splits")
X_TRAIN_PATH = os.path.join(DATA_SPLITS_DIR, "X_train.csv")
Y_TRAIN_PATH = os.path.join(DATA_SPLITS_DIR, "y_train.csv")
X_TEST_PATH = os.path.join(DATA_SPLITS_DIR, "X_test.csv")
Y_TEST_PATH = os.path.join(DATA_SPLITS_DIR, "y_test.csv")

FEATURE_NAMES_PATH = os.path.join(BASE_DIR, "artifacts", "model", "feature_names.joblib")
MODEL_SAVE_PATH =  os.path.join(BASE_DIR, "artifacts", "model", "decision_tree_model.joblib") # Where to save the trained model

# Decision Tree Parameters (can be tuned later)
DT_MAX_DEPTH = 5 # Limiting depth to prevent overfitting and for easier visualization/zk-SNARK conversion
DT_MIN_SAMPLES_LEAF = 10
DT_RANDOM_STATE = 42

def load_processed_data():
    """Loads the preprocessed training and testing data."""
    try:
        X_train = pd.read_csv(X_TRAIN_PATH)
        y_train = pd.read_csv(Y_TRAIN_PATH).squeeze() # .squeeze() to convert single column DataFrame to Series
        X_test = pd.read_csv(X_TEST_PATH)
        y_test = pd.read_csv(Y_TEST_PATH).squeeze()
        feature_names = joblib.load(FEATURE_NAMES_PATH)
        print("Processed data loaded successfully.")
        return X_train, y_train, X_test, y_test, feature_names
    except FileNotFoundError as e:
        print(f"Error: A data file was not found. {e}")
        print("Please ensure '02_preprocess_data.py' was run successfully and data files exist.")
        return None, None, None, None, None
    except Exception as e:
        print(f"An error occurred while loading processed data: {e}")
        return None, None, None, None, None

def train_decision_tree(X_train, y_train):
    """Trains a Decision Tree classifier."""
    print(f"\nTraining Decision Tree model (max_depth={DT_MAX_DEPTH}, min_samples_leaf={DT_MIN_SAMPLES_LEAF})...")
    # Initialize Decision Tree Classifier
    # We can add class_weight='balanced' to handle imbalance if initial results are poor on the minority class
    model = DecisionTreeClassifier(
        max_depth=DT_MAX_DEPTH,
        min_samples_leaf=DT_MIN_SAMPLES_LEAF,
        random_state=DT_RANDOM_STATE,
        class_weight='balanced' # Option to consider
    )

    model.fit(X_train, y_train)
    print("Model training complete.")
    return model

def evaluate_model(model, X_test, y_test, feature_names):
    """Evaluates the model and prints classification report and confusion matrix."""
    print("\n--- Model Evaluation ---")
    y_pred = model.predict(X_test)

    print("\nAccuracy:", accuracy_score(y_test, y_pred))
    # For imbalanced classes, precision, recall, and F1 are more informative for the positive class (failure=1)
    print("Precision (Failure=1):", precision_score(y_test, y_pred, pos_label=1, zero_division=0))
    print("Recall (Failure=1):", recall_score(y_test, y_pred, pos_label=1, zero_division=0))
    print("F1-score (Failure=1):", f1_score(y_test, y_pred, pos_label=1, zero_division=0))

    print("\nConfusion Matrix:")
    # Rows are actual, Columns are predicted.
    # TN FP
    # FN TP
    cm = confusion_matrix(y_test, y_pred)
    print(cm)
    # For better readability of CM:
    print(f"True Negatives (TN): {cm[0,0]} (Correctly predicted 'No Failure')")
    print(f"False Positives (FP): {cm[0,1]} (Incorrectly predicted 'Failure') - Type I Error")
    print(f"False Negatives (FN): {cm[1,0]} (Incorrectly predicted 'No Failure') - Type II Error, critical for us!")
    print(f"True Positives (TP): {cm[1,1]} (Correctly predicted 'Failure')")


    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['No Failure (0)', 'Failure (1)'], zero_division=0))

    # Optional: Plot the tree (can be very large if max_depth is high)
    # To make this work, you might need to install graphviz (both the Python library `pip install graphviz`
    # and the Graphviz software itself: https://graphviz.org/download/ and add it to PATH)
    # If graphviz is a hassle, we can skip this for now or export to text.
    try:
        plt.figure(figsize=(20,10)) # Adjust size as needed
        plot_tree(model, filled=True, feature_names=feature_names, class_names=['No Failure', 'Failure'], rounded=True, proportion=False, precision=2, fontsize=10)
        plt.title(f"Decision Tree (Max Depth: {DT_MAX_DEPTH})")
        plt.savefig("decision_tree_visualization.png")
        print("\nDecision tree visualization saved to decision_tree_visualization.png")
        # plt.show() # Uncomment to display if running in an environment that supports it
    except Exception as e:
        print(f"\nCould not plot tree. Error: {e}")
        print("Ensure graphviz is installed and in PATH if you want to visualize the tree image.")
        print("You can also export tree rules to text if visualization fails.")

# --- Main execution ---
if __name__ == "__main__":
    X_train, y_train, X_test, y_test, feature_names = load_processed_data()

    if X_train is not None:
        model = train_decision_tree(X_train, y_train)

        evaluate_model(model, X_test, y_test, feature_names)

        # Save the trained model
        joblib.dump(model, MODEL_SAVE_PATH)
        print(f"\nTrained model saved to {MODEL_SAVE_PATH}")

        print("\nScript finished.")