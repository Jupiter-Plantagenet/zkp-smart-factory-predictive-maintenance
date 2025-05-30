import pandas as pd
import numpy as np
import json
import joblib # To load the scaler and model
import subprocess # To run external commands
import os
import shutil # For managing directories if needed
from dotenv import load_dotenv

load_dotenv() # Load variables from .env file


# --- Configuration ---
current_script_dir = os.path.dirname(__file__) # 1. Determine the path to the directory containing *this* script 
BASE_DIR = os.path.abspath(os.path.join(current_script_dir, '..')) # 2. Go up one level to reach the project root ('your_root_directory')

DATASET_PATH = os.path.join(BASE_DIR, "data", "ai4i2020.csv")
SCALER_PATH = os.path.join(BASE_DIR, "artifacts", "model", "standard_scaler.joblib")
MODEL_PATH = os.path.join(BASE_DIR, "artifacts", "model", "decision_tree_model.joblib")

# Circuit related paths
CIRCUIT_BUILD_DIR = os.path.join(BASE_DIR, "artifacts", "circuit", "circuit_build")
WASM_FILE_PATH = os.path.join(CIRCUIT_BUILD_DIR, "decision_tree_js", "decision_tree.wasm")
WITNESS_GEN_SCRIPT_PATH = os.path.join(CIRCUIT_BUILD_DIR, "decision_tree_js", "generate_witness.js")
R1CS_FILE_PATH = os.path.join(CIRCUIT_BUILD_DIR, "decision_tree.r1cs") # Not directly used by prove/verify but good to list

PROVING_KEY_PATH = os.path.join(BASE_DIR, "artifacts", "zkp_keys", "decision_tree_0001.zkey")
VERIFICATION_KEY_PATH = os.path.join(BASE_DIR, "artifacts", "zkp_keys", "verification_key.json")

# Temporary/Output file paths (can be in project root or a dedicated output folder)
INPUT_JSON_PATH = os.path.join(BASE_DIR, "runtime_outputs", "input.json")
WITNESS_FILE_PATH = os.path.join(CIRCUIT_BUILD_DIR, "decision_tree_js", "witness.wtns") # generate_witness.js creates it here
PROOF_JSON_PATH = os.path.join(BASE_DIR, "runtime_outputs", "proof.json")
PUBLIC_JSON_PATH = os.path.join(BASE_DIR, "runtime_outputs", "public.json")

#SNARKJS_CMD_PATH = r"C:\Users\NSL\AppData\Roaming\npm\snarkjs.cmd" # Use raw string for paths
SNARKJS_CMD_PATH_FROM_ENV = os.getenv("SNARKJS_CMD_PATH")
DEFAULT_WINDOWS_SNARKJS_PATH = r"C:\Users\NSL\AppData\Roaming\npm\snarkjs.cmd" # Your specific path

if SNARKJS_CMD_PATH_FROM_ENV:
    SNARKJS_CMD_PATH = SNARKJS_CMD_PATH_FROM_ENV
    print(f"Using SNARKJS_CMD_PATH from .env: {SNARKJS_CMD_PATH}")
elif os.name == 'nt' and os.path.exists(DEFAULT_WINDOWS_SNARKJS_PATH): # Check if on Windows and your default path exists
    SNARKJS_CMD_PATH = DEFAULT_WINDOWS_SNARKJS_PATH
    print(f"Using default Windows SNARKJS_CMD_PATH: {SNARKJS_CMD_PATH}")
else:
    SNARKJS_CMD_PATH = "snarkjs" # Fallback, assumes snarkjs is in system PATH
    print(f"SNARKJS_CMD_PATH not found in .env or default Windows path. Assuming 'snarkjs' is in system PATH.")



# Feature and model parameters (should match previous scripts)
FEATURE_NAMES_ORDER = ['Air temperature [K]', 'Process temperature [K]', 'Rotational speed [rpm]', 'Torque [Nm]', 'Tool wear [min]', 'Type_H', 'Type_L', 'Type_M']
NUMERICAL_FEATURES_FOR_SCALING = ['Air temperature [K]', 'Process temperature [K]', 'Rotational speed [rpm]', 'Torque [Nm]', 'Tool wear [min]']
FIXED_POINT_MULTIPLIER = 10000
SAMPLE_INDEX = 49 # UDI 50, an OSF failure case in dataset, but label is 0 (No Failure)

def run_command(command_parts, working_dir=None, shell_cmd=False):
    """Runs an external command using subprocess and prints its output."""
    print(f"\nExecuting command: {' '.join(command_parts)}")
    if working_dir:
        print(f"Working directory: {working_dir}")
    try:
        # On Windows, shell=True might sometimes be needed if commands aren't found directly,
        # but it's generally safer to use shell=False and provide full paths if necessary.
        # For `node` and `snarkjs` (if installed globally or in PATH), shell=False should work.
        process = subprocess.run(command_parts, cwd=working_dir, capture_output=True, text=True, check=True, shell=shell_cmd)
        print("Command STDOUT:")
        print(process.stdout)
        if process.stderr:
            print("Command STDERR:")
            print(process.stderr)
        print("Command executed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print("Error executing command.")
        print("Return code:", e.returncode)
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False
    except FileNotFoundError:
        print(f"Error: Command or executable not found: {command_parts[0]}")
        print("Ensure Node.js and snarkjs are installed and in your system PATH.")
        return False


def prepare_input_for_circuit(original_df, sample_idx, scaler, feature_names_order, numerical_features_to_scale, multiplier, output_json_path):
    """Prepares a single sample for the Circom circuit and saves to input.json."""
    sample_original_row = original_df.iloc[[sample_idx]]
    print(f"\nOriginal sample data (row index {sample_idx}):")
    print(sample_original_row)
    actual_failure_status = sample_original_row['Machine failure'].iloc[0]
    print(f"Actual failure status for sample {sample_idx} (from dataset): {actual_failure_status}")

    type_val = sample_original_row['Type'].iloc[0]
    type_h_val = 1 if type_val == 'H' else 0
    type_l_val = 1 if type_val == 'L' else 0
    type_m_val = 1 if type_val == 'M' else 0
    
    numerical_data_for_scaling = sample_original_row[numerical_features_to_scale]
    scaled_numerical_data = scaler.transform(numerical_data_for_scaling)
    fixed_point_numerical = [int(round(val * multiplier)) for val in scaled_numerical_data[0]]

    input_features_map = {}
    for i, name in enumerate(numerical_features_to_scale):
        input_features_map[name] = fixed_point_numerical[i]
    input_features_map['Type_H'] = type_h_val
    input_features_map['Type_L'] = type_l_val
    input_features_map['Type_M'] = type_m_val
    
    circuit_input_array = [input_features_map[name] for name in feature_names_order]
    
    print(f"Prepared circuit input features (Order: {feature_names_order}):")
    print(circuit_input_array)
    
    input_json_data = {"features": circuit_input_array}
    with open(output_json_path, 'w') as f:
        json.dump(input_json_data, f, indent=2)
    print(f"Circuit input data written to {output_json_path}")
    return actual_failure_status, circuit_input_array


# --- Main Automation Logic ---
if __name__ == "__main__":
    print("--- Starting Automated Proof Generation ---")

    # 1. Load data, scaler, and ML model
    try:
        df_original = pd.read_csv(DATASET_PATH)
        scaler = joblib.load(SCALER_PATH)
        ml_model = joblib.load(MODEL_PATH)
        print("Dataset, scaler, and ML model loaded successfully.")
    except Exception as e:
        print(f"Error loading initial files: {e}")
        exit()

    # 2. Prepare input.json for the chosen sample
    print(f"\n--- Preparing input for sample index: {SAMPLE_INDEX} ---")
    actual_label, prepared_circuit_inputs = prepare_input_for_circuit(
        df_original, SAMPLE_INDEX, scaler, FEATURE_NAMES_ORDER,
        NUMERICAL_FEATURES_FOR_SCALING, FIXED_POINT_MULTIPLIER, INPUT_JSON_PATH
    )

    # 3. (Optional) Get prediction from scikit-learn model for comparison
    #    Need to prepare data for scikit-learn model similarly (scaled, but not fixed-point, and as DataFrame)
    sample_for_sklearn = pd.DataFrame([prepared_circuit_inputs], columns=FEATURE_NAMES_ORDER)
    # Re-transform OHE back to original scale (0 or 1) if they were part of scaling for circuit inputs.
    # However, our current prepared_circuit_inputs has fixed-point for numerical and 0/1 for OHE.
    # For scikit-learn, we need scaled numerical and 0/1 OHE.
    # The scaler was only fit on NUMERICAL_FEATURES_FOR_SCALING.
    
    # Let's re-prepare the scikit-learn input correctly from the sample:
    sklearn_input_data_dict = {}
    sample_original_row = df_original.iloc[[SAMPLE_INDEX]]
    numerical_original_values = sample_original_row[NUMERICAL_FEATURES_FOR_SCALING]
    numerical_scaled_values = scaler.transform(numerical_original_values) # This is what the model was trained on

    for i, name in enumerate(NUMERICAL_FEATURES_FOR_SCALING):
        sklearn_input_data_dict[name] = numerical_scaled_values[0][i]
    
    type_val = sample_original_row['Type'].iloc[0]
    sklearn_input_data_dict['Type_H'] = 1 if type_val == 'H' else 0
    sklearn_input_data_dict['Type_L'] = 1 if type_val == 'L' else 0
    sklearn_input_data_dict['Type_M'] = 1 if type_val == 'M' else 0
    
    sklearn_input_df = pd.DataFrame([sklearn_input_data_dict])[FEATURE_NAMES_ORDER] # Ensure correct column order
    
    ml_prediction = ml_model.predict(sklearn_input_df)[0]
    print(f"\nScikit-learn model prediction for sample {SAMPLE_INDEX}: {ml_prediction} ({'Failure' if ml_prediction == 1 else 'No Failure'})")
    print(f"Actual label from dataset for sample {SAMPLE_INDEX}: {actual_label} ({'Failure' if actual_label == 1 else 'No Failure'})")

    # 4. Generate Witness
    print("\n--- Generating Witness ---")
    witness_gen_command = [
        "node",
        os.path.relpath(WITNESS_GEN_SCRIPT_PATH, os.path.join(CIRCUIT_BUILD_DIR, "decision_tree_js")), # generate_witness.js
        os.path.relpath(WASM_FILE_PATH, os.path.join(CIRCUIT_BUILD_DIR, "decision_tree_js")),            # decision_tree.wasm
        os.path.relpath(INPUT_JSON_PATH, os.path.join(CIRCUIT_BUILD_DIR, "decision_tree_js")),          # ../../input.json
        os.path.relpath(WITNESS_FILE_PATH, os.path.join(CIRCUIT_BUILD_DIR, "decision_tree_js"))         # witness.wtns
    ]
    if not run_command(witness_gen_command, working_dir=os.path.join(CIRCUIT_BUILD_DIR, "decision_tree_js")):
        print("Witness generation failed. Exiting.")
        exit()

    # 5. Generate Proof
    print("\n--- Generating Proof ---")
    prove_command = [
        #"snarkjs", "groth16", "prove",
        SNARKJS_CMD_PATH, "groth16", "prove", # Changed "snarkjs" to SNARKJS_CMD_PATH
        PROVING_KEY_PATH,
        WITNESS_FILE_PATH, # Path from project root
        PROOF_JSON_PATH,
        PUBLIC_JSON_PATH
    ]
    if not run_command(prove_command, working_dir=BASE_DIR): # Run snarkjs from project root
        print("Proof generation failed. Exiting.")
        exit()

    # 6. Verify Proof
    print("\n--- Verifying Proof ---")
    verify_command = [
        #"snarkjs", "groth16", "verify",
        SNARKJS_CMD_PATH, "groth16", "verify", # Changed "snarkjs" to SNARKJS_CMD_PATH
        VERIFICATION_KEY_PATH,
        PUBLIC_JSON_PATH,
        PROOF_JSON_PATH
    ]
    if not run_command(verify_command, working_dir=BASE_DIR): # Run snarkjs from project root
        print("Proof verification failed.")
    else:
        print("Proof verified successfully!")
        try:
            with open(PUBLIC_JSON_PATH, 'r') as f:
                public_signals = json.load(f)
            # Assuming the output is the first element if features are also public,
            # or the last if only inputs are listed first.
            # snarkjs usually puts public inputs first then public outputs.
            # Our circuit: public [features], output out_prediction.
            # So, 8 inputs, then 1 output. Output is at index 8 (9th element).
            # Or, if snarkjs separates them, it might be simpler.
            # Let's check the specific format of public.json produced.
            # If it's [out, in1, in2,...] then output is public_signals[0]
            # If it's [in1, in2,..., out] then output is public_signals[-1]
            # Based on your previous public.json, it was [out, in1, in2...]
            circuit_prediction = int(public_signals[0]) # First element is the output
            print(f"Circuit prediction (from public.json output): {circuit_prediction} ({'Failure' if circuit_prediction == 1 else 'No Failure'})")
            if circuit_prediction == ml_prediction:
                print("Circuit prediction matches scikit-learn model prediction.")
            else:
                print("WARNING: Circuit prediction MISMATCHES scikit-learn model prediction!")
            if circuit_prediction == actual_label:
                print("Circuit prediction matches actual label from dataset.")
            else:
                print("WARNING: Circuit prediction MISMATCHES actual label from dataset!")

        except Exception as e:
            print(f"Error reading/interpreting public.json: {e}")

    print("\n--- Automated Proof Generation Finished ---")