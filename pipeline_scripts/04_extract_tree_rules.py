import joblib
import os
from sklearn.tree import _tree # For accessing tree internals

# --- Configuration ---
current_script_dir = os.path.dirname(__file__) # 1. Determine the path to the directory containing *this* script 
BASE_DIR = os.path.abspath(os.path.join(current_script_dir, '..')) # 2. Go up one level to reach the project root ('your_root_directory')

MODEL_PATH = os.path.join(BASE_DIR, "artifacts", "model", "decision_tree_model.joblib" ) # From the run with class_weight='balanced'
FEATURE_NAMES_PATH = os.path.join(BASE_DIR, "artifacts", "model", "feature_names.joblib" )

def get_tree_rules(tree_model, feature_names, node_index=0, depth=0, current_rule=""):
    """
    Recursively extracts rules from a decision tree.
    Returns a list of rules, where each rule is a string leading to a classification.
    """
    rules_list = []

    # Check if the node is a leaf node
    is_leaf = tree_model.tree_.children_left[node_index] == tree_model.tree_.children_right[node_index]

    # Indentation for readability
    indent = "  " * depth

    if is_leaf:
        # Get the class prediction for this leaf
        # tree_.value[node_index] gives an array like [[num_samples_class_0, num_samples_class_1]]
        class_counts = tree_model.tree_.value[node_index][0]
        predicted_class = class_counts.argmax() # 0 for 'No Failure', 1 for 'Failure'
        class_name = "Failure" if predicted_class == 1 else "No Failure"

        # Purity of the leaf
        purity = class_counts[predicted_class] / class_counts.sum()

        rule_str = f"{current_rule} THEN Class: {class_name} (Samples: {class_counts.sum()}, Purity: {purity:.2f}, Values: {class_counts})"
        rules_list.append(rule_str)
        # For printing directly:
        print(f"{indent}LEAF: Predict {class_name} (Samples: {int(class_counts.sum())}, Values: {class_counts.astype(int)})")

    else:
        # It's a split node
        feature_index = tree_model.tree_.feature[node_index]
        feature_name = feature_names[feature_index]
        threshold = tree_model.tree_.threshold[node_index]

        # For printing directly:
        print(f"{indent}NODE {node_index}: If {feature_name} <= {threshold:.4f}")

        # Recurse for the 'True' condition (left child)
        left_child_index = tree_model.tree_.children_left[node_index]
        rule_true_condition = f"{current_rule}IF ({feature_name} <= {threshold:.4f}) AND " if current_rule else f"IF ({feature_name} <= {threshold:.4f}) AND "
        # For printing directly:
        get_tree_rules(tree_model, feature_names, left_child_index, depth + 1, rule_true_condition)

        # For printing directly:
        print(f"{indent}NODE {node_index}: Else (If {feature_name} > {threshold:.4f})")

        # Recurse for the 'False' condition (right child)
        right_child_index = tree_model.tree_.children_right[node_index]
        rule_false_condition = f"{current_rule}IF ({feature_name} > {threshold:.4f}) AND " if current_rule else f"IF ({feature_name} > {threshold:.4f}) AND "
        # For printing directly:
        get_tree_rules(tree_model, feature_names, right_child_index, depth + 1, rule_false_condition)

    return rules_list # Though for this script, we are mostly using print statements

# --- Main execution ---
if __name__ == "__main__":
    try:
        model = joblib.load(MODEL_PATH)
        feature_names = joblib.load(FEATURE_NAMES_PATH)
        print(f"Loaded model from {MODEL_PATH}")
        print(f"Loaded feature names: {feature_names}")
        print("\n--- Decision Tree Rules ---")

        # The get_tree_rules function as written above prints rules directly.
        # If you wanted to collect them into a list:
        # collected_rules = get_tree_rules(model, feature_names)
        # for rule in collected_rules:
        #    print(rule)
        # For now, direct printing during recursion is fine for inspection.
        get_tree_rules(model, feature_names)

        print("\nScript finished.")

    except FileNotFoundError as e:
        print(f"Error: A model or feature file was not found. {e}")
        print(f"Please ensure '{MODEL_PATH}' and '{FEATURE_NAMES_PATH}' exist from the previous script run.")
    except Exception as e:
        print(f"An error occurred: {e}")