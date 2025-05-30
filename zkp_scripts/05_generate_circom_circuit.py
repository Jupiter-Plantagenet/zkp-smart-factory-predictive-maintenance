import joblib
import numpy as np
from sklearn.tree import _tree # For accessing tree internals
import os

# --- Configuration ---
current_script_dir = os.path.dirname(__file__) # 1. Determine the path to the directory containing *this* script (zkp_scripts)
BASE_DIR = os.path.abspath(os.path.join(current_script_dir, '..')) # 2. Go up one level to reach the project root ('your_root_directory')

# 3. Construct the full path to the model file relative to BASE_DIR
MODEL_PATH = os.path.join(BASE_DIR, "artifacts", "model", "decision_tree_model.joblib" )
FEATURE_NAMES_PATH = os.path.join(BASE_DIR, "artifacts", "model", "feature_names.joblib" )
CIRCOM_OUTPUT_FILE = os.path.join(BASE_DIR, "artifacts", "circuit", "decision_tree.circom" )

FIXED_POINT_MULTIPLIER = 10000
COMPARATOR_N_BITS = 32 

def generate_circom_code(model, feature_names):
    tree_ = model.tree_
    num_features = len(feature_names)
    circom_lines = []

    # --- START DEBUG PRINT ---
    print(f"[DEBUGGER] generate_circom_code: Initial check for root node (0).")
    if tree_ is not None and hasattr(tree_, 'children_left') and hasattr(tree_, 'children_right'):
        print(f"[DEBUGGER] Root Node (0) children_left: {tree_.children_left[0]}, children_right: {tree_.children_right[0]}")
        is_root_split_node = tree_.children_left[0] != tree_.children_right[0]
        print(f"[DEBUGGER] Root Node (0) is considered a split node: {is_root_split_node}")
        if is_root_split_node:
            print(f"[DEBUGGER] Root Node (0) feature index: {tree_.feature[0]}, threshold: {tree_.threshold[0]}")
            if tree_.feature[0] < len(feature_names):
                 print(f"[DEBUGGER] Root Node (0) feature name: {feature_names[tree_.feature[0]]}")
            else:
                 print(f"[DEBUGGER] Root Node (0) feature index {tree_.feature[0]} is out of bounds for feature_names (len {len(feature_names)})")
    else:
        print("[DEBUGGER] tree_ object is problematic or missing children attributes.")
    # --- END DEBUG PRINT ---

    circom_lines.append(f"pragma circom 2.1.5;\n")
    circom_lines.append(f"// Decision tree circuit generated programmatically")
    circom_lines.append(f"// Model used: {MODEL_PATH}\n")
    circom_lines.append(f"include \"../../node_modules/circomlib/circuits/comparators.circom\";\n")
    
    circom_lines.append(f"template DecisionTree(numFeatures) {{")
    circom_lines.append(f"    // --- Inputs ---")
    circom_lines.append(f"    // Expected order: {', '.join(feature_names)}")
    circom_lines.append(f"    // Values should be scaled and multiplied by {FIXED_POINT_MULTIPLIER}")
    circom_lines.append(f"    signal input features[numFeatures];\n")
    circom_lines.append(f"    // --- Output ---")
    circom_lines.append(f"    // 0 for No Failure, 1 for Failure")
    circom_lines.append(f"    signal output out_prediction;\n")

    node_comparator_outputs = {}

    def generate_node_comparators_recursive(node_index):
        if tree_.children_left[node_index] != tree_.children_right[node_index]: # If not a leaf
            feature_idx = tree_.feature[node_index]
            feature_name_for_node = feature_names[feature_idx] # Get the actual name of the feature
            original_sklearn_threshold = tree_.threshold[node_index] # The threshold from the scikit-learn tree

            # --- START DEBUG PRINT FOR THIS FUNCTION ---
        print(f"[DEBUGGER] generate_node_comparators_recursive: Entered for node {node_index}.")
        # --- END DEBUG PRINT ---
        if tree_.children_left[node_index] != tree_.children_right[node_index]: # If not a leaf
            feature_idx = tree_.feature[node_index]
            feature_name_for_node = feature_names[feature_idx] 
            original_sklearn_threshold = tree_.threshold[node_index]
            
            # --- START DEBUG PRINT FOR SPLIT NODE PROCESSING ---
            print(f"[DEBUGGER] Node {node_index} is SPLIT. Feature: {feature_name_for_node} (idx {feature_idx}), Threshold: {original_sklearn_threshold}")
            # --- END DEBUG PRINT ---

            # --- START OF THE PROPOSED LOGICAL CHANGE ---
            if feature_name_for_node in ['Type_H', 'Type_L', 'Type_M'] and \
               abs(original_sklearn_threshold - 0.5) < 1e-6: # Check if it's a Type_X feature and original threshold is 0.5
                
                # For binary (0/1) features where scikit-learn uses a 0.5 threshold,
                # the rule 'feature <= 0.5' effectively means 'feature == 0'.
                # To implement 'feature == 0' using 'LessEqThan(A, B)' where A is the feature (0 or 1),
                # B (the threshold for Circom) should be 0.
                # So, A <= 0 will be true (1) if A is 0, and false (0) if A is 1.
                threshold_fixed_point = 0 
                comment_threshold_explanation = f"(Original Threshold: {original_sklearn_threshold:.4f} for binary {feature_name_for_node}, Effective Fixed Threshold for '==0' logic: {threshold_fixed_point})"
            else:
                # For all other features or different thresholds, use the standard fixed-point conversion
                threshold_fixed_point = int(round(original_sklearn_threshold * FIXED_POINT_MULTIPLIER))
                comment_threshold_explanation = f"(Original Threshold: {original_sklearn_threshold:.4f}, Fixed: {threshold_fixed_point})"
            # --- END OF THE PROPOSED LOGICAL CHANGE ---
            
            comp_signal_name = f"comp_node{node_index}_out"
            node_comparator_outputs[node_index] = comp_signal_name
            # --- START DEBUG PRINT ---
            print(f"[DEBUGGER] Node {node_index}: Added '{comp_signal_name}' to node_comparator_outputs. Current keys: {list(node_comparator_outputs.keys())}")
            # --- END DEBUG PRINT ---

            circom_lines.append(f"    // Node {node_index}: If {feature_name_for_node} (features[{feature_idx}]) <= ... {comment_threshold_explanation}")
            circom_lines.append(f"    component comp_node{node_index} = LessEqThan({COMPARATOR_N_BITS});")
            circom_lines.append(f"    comp_node{node_index}.in[0] <== features[{feature_idx}];")
            circom_lines.append(f"    comp_node{node_index}.in[1] <== {threshold_fixed_point};") # Use the potentially adjusted threshold_fixed_point
            circom_lines.append(f"    signal {comp_signal_name} <== comp_node{node_index}.out; // 1 if true (left), 0 if false (right)\n")
            
            generate_node_comparators_recursive(tree_.children_left[node_index])
            generate_node_comparators_recursive(tree_.children_right[node_index])
        else:
            # --- START DEBUG PRINT FOR LEAF ---
            print(f"[DEBUGGER] Node {node_index} is a LEAF (in generate_node_comparators_recursive). Not added to node_comparator_outputs.")
            # --- END DEBUG PRINT ---
            pass


    circom_lines.append(f"    // --- Comparators for Split Nodes ---")
    generate_node_comparators_recursive(0) # Call that populates

    # --- START DEBUG PRINT ---
    print(f"[DEBUGGER] After generate_node_comparators_recursive(0), node_comparator_outputs keys: {list(node_comparator_outputs.keys())}")
    # --- END DEBUG PRINT ---

    circom_lines.append(f"    // --- Path Conditions and Leaf Value Aggregation ---")
    leaf_processing_details = []

    def build_leaf_paths_info(node_index, current_path_term_list):
        # --- START DEBUG PRINT FOR THIS FUNCTION ---
        print(f"[DEBUGGER] build_leaf_paths_info: Entered for node {node_index}.")
        # --- END DEBUG PRINT ---
        # current_path_term_list is a list of strings, e.g., ["comp_node0_out", "(1 - comp_node2_out)"]
        if tree_.children_left[node_index] == tree_.children_right[node_index]: # Is a Leaf
            leaf_value_counts = tree_.value[node_index][0]
            prediction = int(np.argmax(leaf_value_counts))
            leaf_processing_details.append( (node_index, current_path_term_list, prediction) )
            # --- START DEBUG PRINT ---
            print(f"[DEBUGGER] Node {node_index} is LEAF (in build_leaf_paths_info). Path terms: {current_path_term_list}, Prediction: {prediction}")
            # --- END DEBUG PRINT ---
        else: # Is a Split Node
            # --- START DEBUG PRINT ---
            print(f"[DEBUGGER] Node {node_index} is SPLIT (in build_leaf_paths_info). Attempting to access node_comparator_outputs for key {node_index}.")
            if node_index not in node_comparator_outputs:
                print(f"[DEBUGGER] CRITICAL: Key {node_index} NOT FOUND in node_comparator_outputs before access!")
            # --- END DEBUG PRINT ---
            comp_out_signal = node_comparator_outputs[node_index]
            
            left_path_terms = current_path_term_list + [f"{comp_out_signal}"]
            build_leaf_paths_info(tree_.children_left[node_index], left_path_terms)
            
            right_path_terms = current_path_term_list + [f"(1 - {comp_out_signal})"]
            build_leaf_paths_info(tree_.children_right[node_index], right_path_terms)

    build_leaf_paths_info(0, [])

    # --- Generating path condition signals and Summing up leaf contributions ---
    if not leaf_processing_details:
        circom_lines.append(f"    out_prediction <== 0; // Should not happen for a valid tree")
    else:
        sum_terms_for_final_prediction = [] # List of signal names that will be summed for out_prediction

        for i, (leaf_node_idx, path_terms_list, leaf_pred_value) in enumerate(leaf_processing_details):
            # path_terms_list contains individual factors like "comp_node0_out", "(1 - comp_node1_out)"
            
            # Step 1: Calculate the combined path condition signal for this leaf using sequential multiplication
            leaf_combined_path_condition_signal = f"path_leaf{leaf_node_idx}_active"

            if not path_terms_list: # Should be "1" if root is leaf (no conditions)
                circom_lines.append(f"    signal {leaf_combined_path_condition_signal} <== 1;")
            elif len(path_terms_list) == 1: # Only one condition/term in the path
                circom_lines.append(f"    signal {leaf_combined_path_condition_signal} <== {path_terms_list[0]};")
            else: # Multiple conditions, requires sequential multiplication
                current_product_signal = path_terms_list[0]
                # If the first term is an expression like (1-X), ensure it's assignable or assign to temp if needed.
                # However, Circom allows `signal s <== (1-X)*Y;` if (1-X) is not too complex.
                # Our terms are simple: "signal_name" or "(1 - signal_name)" which are fine on RHS.

                for j in range(1, len(path_terms_list)):
                    intermediate_product_signal_name = f"leaf{leaf_node_idx}_pathprod_step{j-1}"
                    circom_lines.append(f"    signal {intermediate_product_signal_name} <== {current_product_signal} * {path_terms_list[j]};")
                    current_product_signal = intermediate_product_signal_name
                # The final product for this path is now in current_product_signal
                circom_lines.append(f"    signal {leaf_combined_path_condition_signal} <== {current_product_signal};")
            
            circom_lines.append(f"    // Leaf {leaf_node_idx}: Prediction={leaf_pred_value}, PathSignal: {leaf_combined_path_condition_signal}")

            # Step 2: Calculate the contribution of this leaf to the final prediction
            leaf_contribution_signal = f"leaf{leaf_node_idx}_contribution"
            circom_lines.append(f"    signal {leaf_contribution_signal} <== {leaf_combined_path_condition_signal} * {leaf_pred_value};")
            sum_terms_for_final_prediction.append(leaf_contribution_signal)
        
        # Step 3: Sum up all leaf_X_contribution signals
        if not sum_terms_for_final_prediction:
             circom_lines.append(f"    out_prediction <== 0;") # Should not be reached if leaf_processing_details was populated
        elif len(sum_terms_for_final_prediction) == 1:
             circom_lines.append(f"    out_prediction <== {sum_terms_for_final_prediction[0]};\n")
        else:
            # Iteratively sum: S0=T0, S1=S0+T1, S2=S1+T2 ... SN=S(N-1)+TN
            current_total_sum_signal = sum_terms_for_final_prediction[0]
            for k in range(1, len(sum_terms_for_final_prediction)):
                # prev_total_sum_signal is current_total_sum_signal before update in this iteration
                next_partial_sum_signal = f"prediction_partial_sum_{k-1}" # Generate unique names for these intermediate sums
                circom_lines.append(f"    signal {next_partial_sum_signal} <== {current_total_sum_signal} + {sum_terms_for_final_prediction[k]};")
                current_total_sum_signal = next_partial_sum_signal # Update for the next iteration
            circom_lines.append(f"    out_prediction <== {current_total_sum_signal};\n")


    circom_lines.append(f"}}\n")
    circom_lines.append(f"// To use this, instantiate it in a main component")
    circom_lines.append(f"// component main {{public [features]}} = DecisionTree({num_features});")
    return "\n".join(circom_lines)

# --- Main execution ---
if __name__ == "__main__":
    try:
        model = joblib.load(MODEL_PATH)
        if not hasattr(model, 'tree_'):
            raise ValueError("Loaded model is not a scikit-learn Decision Tree or has no 'tree_' attribute.")
        
        feature_names_loaded = joblib.load(FEATURE_NAMES_PATH)
        
        print(f"Loaded model from {MODEL_PATH}")
        print(f"Feature names: {feature_names_loaded}")
        print(f"Fixed-point multiplier: {FIXED_POINT_MULTIPLIER}")
        print(f"Comparator n_bits: {COMPARATOR_N_BITS}\n")
        
        print("Generating Circom code...")
        circom_code_str = generate_circom_code(model, feature_names_loaded)
        
        with open(CIRCOM_OUTPUT_FILE, "w") as f:
            f.write(circom_code_str)
        
        print(f"\nCircom code successfully written to {CIRCOM_OUTPUT_FILE}")
        print("\n--- Next Steps ---")
        print(f"1. Review '{CIRCOM_OUTPUT_FILE}'.")
        print(f"2. Create a main component if needed (example provided at the end of the file).")
        print(f"3. Compile the Circom circuit: circom {CIRCOM_OUTPUT_FILE} --r1cs --wasm --sym -o ./circuit_build")
        # ... (rest of print statements)

    except Exception as e: # Changed to catch all exceptions for better debugging here
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()