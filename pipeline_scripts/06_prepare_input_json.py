import pandas as pd
import numpy as np
import json
import os
import joblib # To load the scaler

# --- Configuration ---
current_script_dir = os.path.dirname(__file__) # 1. Determine the path to the directory containing *this* script 
BASE_DIR = os.path.abspath(os.path.join(current_script_dir, '..')) # 2. Go up one level to reach the project root ('your_root_directory')

DATASET_PATH = os.path.join(BASE_DIR, "data", "ai4i2020.csv")
SCALER_PATH = os.path.join(BASE_DIR, "artifacts", "model", "standard_scaler.joblib") # Saved from 02_preprocess_data.py
FEATURE_NAMES_ORDER = ['Air temperature [K]', 'Process temperature [K]', 'Rotational speed [rpm]', 'Torque [Nm]', 'Tool wear [min]', 'Type_H', 'Type_L', 'Type_M'] # Must match circuit's expected order
NUMERICAL_FEATURES_FOR_SCALING = ['Air temperature [K]', 'Process temperature [K]', 'Rotational speed [rpm]', 'Torque [Nm]', 'Tool wear [min]']
FIXED_POINT_MULTIPLIER = 10000
OUTPUT_JSON_PATH = os.path.join(BASE_DIR, "runtime_outputs", "input.json")
SAMPLE_INDEX = 7000 # Pick a sample index from the original dataset (0 to 9999)
                    # Let's pick one that should result in a failure with the class_weight='balanced' model
                    # From 03_train_evaluate_model.py, we saw many False Positives. Let's try to find an actual TP or FN.
                    # Or just pick any, e.g., one of the failure instances from the original dataset.
                    # Row 75 in ai4i2020.csv is a TWF failure. Let's use index 74.
                    # Row 130 in ai4i2020.csv is a HDF failure. Index 129.
                    # Row 50 in ai4i2020.csv is an OSF failure. Index 49.
SAMPLE_INDEX = 49 # This is actually UDI 50, which is an OSF failure.

def prepare_input_for_circuit(original_df, sample_idx, scaler, feature_names_order, numerical_features_to_scale, multiplier):
    """Prepares a single sample for the Circom circuit."""
    sample_original_row = original_df.iloc[[sample_idx]] # Keep it as a DataFrame row
    print(f"\nOriginal sample data (row index {sample_idx}):")
    print(sample_original_row)

    # 1. One-hot encode 'Type'
    type_val = sample_original_row['Type'].iloc[0]
    type_h_val = 1 if type_val == 'H' else 0
    type_l_val = 1 if type_val == 'L' else 0
    type_m_val = 1 if type_val == 'M' else 0

    # 2. Prepare numerical features for scaling
    numerical_data_for_scaling = sample_original_row[numerical_features_to_scale]

    # 3. Scale numerical features
    scaled_numerical_data = scaler.transform(numerical_data_for_scaling)

    # 4. Convert to fixed-point integers
    fixed_point_numerical = [int(round(val * multiplier)) for val in scaled_numerical_data[0]] # [0] because transform returns 2D array

    # 5. Assemble all features in the correct order for the circuit
    # Order: ['Air temperature [K]', 'Process temperature [K]', 'Rotational speed [rpm]', 'Torque [Nm]', 'Tool wear [min]', 'Type_H', 'Type_L', 'Type_M']

    # Create a dictionary to map feature names to their values
    # This makes it easier to ensure the correct order.
    input_features_map = {}

    # Add scaled and fixed-point numerical features
    for i, name in enumerate(numerical_features_to_scale):
        input_features_map[name] = fixed_point_numerical[i]

    # Add one-hot encoded 'Type' features (these are 0 or 1, not scaled usually, but circuit expects integer)
    # The decision tree thresholds for Type_H/L/M will be based on 0/1 values or their scaled equivalents if they were scaled
    # In our 02_preprocess_data.py, Type_X columns were NOT scaled by StandardScaler.
    # The tree would have learned thresholds like 0.5 for these if they are binary.
    # For circuit, we need to be consistent. The tree used 0/1 for Type_X.
    # Thresholds like 'Type_L <= 0.5000' in the rules confirm this.
    # So, use 0 or 1 directly, then multiply by multiplier if the circuit expects ALL inputs fixed-point.
    # However, for binary 0/1 features, multiplying by the fixed_point_multiplier is unusual unless all inputs must be in same scale.
    # The LessEqThan comparator will take integer inputs. 0.5 * 10000 = 5000. So Type_L (0 or 1) vs 5000.
    # Let's pass them as 0 * multiplier or 1 * multiplier if other features are scaled.
    # Or, more simply, since tree nodes for Type_L used threshold 0.5, its fixed point is 5000.
    # The input Type_L (0 or 1) should be compared to that.
    # The simplest is to just provide 0 or 1 for Type_X features, and ensure comparator thresholds for them are also simple (e.g. 0 or 1, or 0.5 * multiplier).
    # The current circuit generator uses the tree's float thresholds and converts them. So, for Type_L <= 0.5, it becomes Type_L_input vs 5000.
    # So, the Type_L_input should be 0 or 1 (not multiplied).
    # Let's verify this:
    #   If Type_L is 0, then 0 <= 5000 (true)
    #   If Type_L is 1, then 1 <= 5000 (true) -- this is not right for Type_L <= 0.5 meaning Type_L is 0.
    # The comparison `Type_L <= 0.5` should effectively be `Type_L == 0`.
    # The `LessEqThan` component checks `in[0] <= in[1]`.
    # If tree says `Type_L <= 0.5`, it means if Type_L is 0, go left. If Type_L is 1, go right.
    # Circuit: `comp.in[0] <== features["Type_L"]; comp.in[1] <== 5000;` (fixed point of 0.5)
    # If `features["Type_L"]` is 0 -> `0 <= 5000` -> true (left). Correct.
    # If `features["Type_L"]` is 1 -> `1 <= 5000` -> true (left). Incorrect!
    #
    # The issue is how scikit-learn handles splits on one-hot encoded features if they are not perfectly binary (0/1) due to some floating point noise,
    # or if it genuinely uses <= threshold. Our Type_X are definitely 0 or 1.
    # A split on `Type_L <= 0.5` means if `Type_L` is 0, it's true. If `Type_L` is 1, it's false.
    # So, if `comp_nodeX.out` is 1 (true path), then `Type_L` was 0.
    # The Circom LessEqThan(X,Y) outputs 1 if X <= Y.
    # So for `Type_L <= 0.5` (threshold_fixed = 5000):
    #   - Input Type_L = 0: `0 <= 5000` is TRUE. comp.out = 1. (Correct for left branch if Type_L=0)
    #   - Input Type_L = 1: `1 <= 5000` is TRUE. comp.out = 1. (Incorrect! Should be false for Type_L=1 to go right)
    #
    # This means the interpretation of tree rule `Type_L <= 0.5` needs to be handled carefully for binary features.
    # Scikit-learn's `tree_.threshold` for binary features (0/1) is often 0.5.
    # The `LessEqThan` comparator will work correctly if the input for `Type_L` is simply 0 or 1.
    # `comp_TypeL.in[0] <== Type_L_feature;` (0 or 1)
    # `comp_TypeL.in[1] <== 0;` (if threshold was 0.5, effectively comparing to 0 if we adjust logic)
    # Or, more simply, `Type_L_feature` (0 or 1) fed into `comp_TypeL.in[0]`, and `threshold_fixed_point` (e.g. 5000 for 0.5) fed into `comp_TypeL.in[1]`.
    # The problem is that `0 <= 5000` is true, and `1 <= 5000` is true. `LessEqThan` is not a perfect binary split at 0.5 this way.
    #
    # For binary features that are 0 or 1, a split `feature <= 0.5` means `feature == 0`.
    # We need to ensure our circuit reflects `feature == 0`.
    # `IsEqual` component could be used: `is_equal = IsEqual(); is_equal.in[0] <== feature; is_equal.in[1] <== 0; result <== is_equal.out;`
    # Or, if using `LessEqThan` with threshold 0.5 (fixed point 5000):
    #   If `Type_L` is 0, `0 <= 5000` -> out=1. (Correct: path taken if Type_L is 0)
    #   If `Type_L` is 1, `1 <= 5000` -> out=1. (Incorrect: path should not be taken if Type_L is 1)
    #
    # The Python circuit generator for `LessEqThan` assumes `X <= Y`.
    # If a tree node says "Type_L <= 0.5", it means if Type_L is 0, go left. If Type_L is 1, go right.
    # The comparator `comp_nodeX.out` is 1 if true (left), 0 if false (right).
    # If `Type_L` (input is 0 or 1) is the feature, and threshold is 0.5 (fixed 5000):
    #   `comp.in[0] <== Type_L_input`
    #   `comp.in[1] <== 5000` (fixed point of 0.5)
    #   `comp.out` is 1 if `Type_L_input <= 5000`.
    #   If `Type_L_input = 0`, `0 <= 5000` -> `comp.out = 1`. (Correct for "go left")
    #   If `Type_L_input = 1`, `1 <= 5000` -> `comp.out = 1`. (This is the error in interpretation for binary vars)
    #
    # The decision tree thresholds for OHE features are always 0.5 in scikit-learn.
    # The `LessEqThan(N)` component compares two N-bit numbers.
    # If our Type_L is 0 or 1. Threshold 0.5 (fixed 5000).
    # We need the comparison to be effectively `Type_L == 0`.
    #
    # The simplest way is that the input `features` for Type_H, Type_L, Type_M should simply be `0` or `1`.
    # The circuit's `LessEqThan` with `threshold_fixed_point = 5000` for these features *will behave like an `IsZero` check IF THE INPUT IS GUARANTEED TO BE 0 OR 1 for that feature index.*
    # No, this is still not right. `1 <= 5000` is true.
    #
    # The split `feature_X <= 0.5` for a binary (0/1) feature `feature_X` means:
    # - If `feature_X = 0`, condition is TRUE (left branch).
    # - If `feature_X = 1`, condition is FALSE (right branch).
    #
    # The `LessEqThan` component outputs 1 if `in[0] <= in[1]`.
    # Let `in[0]` be `feature_X` (0 or 1). Let `in[1]` be fixed point of 0.5 (e.g. 5000 if multiplier is 10000, or simply 0 if we adjust the logic).
    #
    # If `in[1]` is 0 (representing the threshold conceptually for `==0` logic):
    #   `feature_X = 0`: `0 <= 0` is TRUE. `comp.out = 1`. (Correct for left branch)
    #   `feature_X = 1`: `1 <= 0` is FALSE. `comp.out = 0`. (Correct for right branch)
    #
    # So, for binary (0/1) features where the tree split is effectively `feature == 0` (represented as `feature <= 0.5`),
    # the threshold used in the `LessEqThan` comparator in Circom should be `0`.
    #
    # The current Circom generator (`05_...py`) uses `threshold_fixed_point = int(round(tree_.threshold[node_index] * FIXED_POINT_MULTIPLIER))`.
    # If `tree_.threshold[node_index]` is 0.5 for a OHE feature, this becomes `5000`.
    # This is what's causing the conceptual mismatch for binary features.
    #
    # Quick fix for `05_generate_circom_circuit.py`:
    # If feature_name is one of 'Type_H', 'Type_L', 'Type_M', then threshold_fixed_point should be 0 if original threshold was 0.5.
    # This needs to be done carefully in the `generate_node_comparators_recursive` function of `05_...py`.
    #
    # Let's assume for now `05_...py` is correct and the tree build might have not used 0.5, or there's another interpretation.
    # The provided rules output: `NODE 7: If Type_L <= 0.5000`
    # If the circuit generator used `threshold_fixed_point = 5000` for this.
    # And inputs for Type_L are just 0 or 1.
    # The `comp_node7_out` signal would be 1 if `Type_L_input <= 5000`. This is ALWAYS 1 if Type_L_input is 0 or 1.
    # This means `comp_node7_out` would always be 1, and the tree would always take the left branch at Node 7. This is not right.
    #
    # This is a critical point. The circuit generator MUST correctly implement the logic for binary features.
    # The simplest way to fix in `05_generate_circom_circuit.py`:
    # Inside `generate_node_comparators_recursive`:
    #   `feature_name = feature_names[feature_idx]`
    #   `original_threshold = tree_.threshold[node_index]`
    #   `if feature_name in ['Type_H', 'Type_L', 'Type_M'] and original_threshold == 0.5:`
    #       `threshold_fixed_point = 0 # Effectively makes 'feature <= 0.5' behave as 'feature == 0'`
    #   `else:`
    #       `threshold_fixed_point = int(round(original_threshold * FIXED_POINT_MULTIPLIER))`
    # And the input for Type_H/L/M in `input.json` should be 0 or 1.

    # For NOW, for `06_prepare_input_json.py`, we will provide Type_H/L/M as 0 or 1.
    # The fix above for `05_generate_circom_circuit.py` would be required for correctness of the circuit.
    # I will assume this fix is made to `05_...py` before recompiling the circuit and doing the setup again.
    # If not, the circuit will behave incorrectly for splits on Type_X features.

    # For now, this `06_prepare_input_json.py` will proceed with inputs as 0/1 for Type_X.
    input_features_map['Type_H'] = type_h_val
    input_features_map['Type_L'] = type_l_val
    input_features_map['Type_M'] = type_m_val

    # Assemble final ordered list for json
    circuit_input_array = [input_features_map[name] for name in feature_names_order]

    print(f"Scaled & Fixed-Point Features (Order: {feature_names_order}):")
    print(circuit_input_array)

    # Create the JSON structure
    # The main component in Circom expects an object where the key is "features" and value is the array
    input_json_data = {"features": circuit_input_array}

    with open(OUTPUT_JSON_PATH, 'w') as f:
        json.dump(input_json_data, f, indent=2)
    print(f"\nInput data written to {OUTPUT_JSON_PATH}")

    # Also return the original failure status for comparison
    actual_failure_status = sample_original_row['Machine failure'].iloc[0]
    print(f"Actual failure status for sample {sample_idx}: {actual_failure_status}")
    return actual_failure_status


# --- Main execution ---
if __name__ == "__main__":
    try:
        df_original = pd.read_csv(DATASET_PATH)
        scaler_loaded = joblib.load(SCALER_PATH)

        print(f"Preparing input for sample index: {SAMPLE_INDEX}")
        prepare_input_for_circuit(
            df_original,
            SAMPLE_INDEX,
            scaler_loaded,
            FEATURE_NAMES_ORDER,
            NUMERICAL_FEATURES_FOR_SCALING,
            FIXED_POINT_MULTIPLIER
        )
    except FileNotFoundError as e:
        print(f"Error: A required file was not found. {e}")
        print("Please ensure dataset and scaler.joblib exist.")
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()