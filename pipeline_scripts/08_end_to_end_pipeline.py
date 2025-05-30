# 08_end_to_end_pipeline.py
import pandas as pd
import numpy as np
import json
import joblib
import subprocess
import os
import time
from datetime import datetime, timezone # Ensure timezone is imported
import csv
import traceback # For detailed error printing

import config_loader as cfg # Your configuration file
from web3 import Web3, HTTPProvider
from web3.middleware import ExtraDataToPOAMiddleware

# --- Helper Functions ---
def run_command(command_parts, working_dir=None, shell_cmd=False):
    """Runs an external command using subprocess and prints its output."""
    print(f"\nExecuting command: {' '.join(command_parts)}")
    if working_dir:
        print(f"Working directory: {working_dir}")
    try:
        process = subprocess.run(command_parts, cwd=working_dir, capture_output=True, text=True, check=True, shell=shell_cmd)
        # print("Command STDOUT:", process.stdout) # Verbose, uncomment if needed
        if process.stderr:
            print(f"Command STDERR for '{' '.join(command_parts)}': {process.stderr}")
        print(f"Command {' '.join(command_parts)} executed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {' '.join(command_parts)}")
        print("Return code:", e.returncode)
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False
    except FileNotFoundError:
        print(f"Error: Command or executable not found: {command_parts[0]}")
        return False

def prepare_input_for_circuit(original_df, sample_idx, scaler, feature_names_order, numerical_features_to_scale, multiplier, output_json_path):
    """Prepares a single sample for the Circom circuit and saves to input.json."""
    sample_original_row = original_df.iloc[[sample_idx]]
    udi = sample_original_row['UDI'].iloc[0]
    actual_failure_status = sample_original_row['Machine failure'].iloc[0]
    print(f"\nProcessing UDI {udi} (Dataset Index {sample_idx}). Actual Failure from Dataset: {actual_failure_status}")

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
    
    input_json_data = {"features": circuit_input_array}
    with open(output_json_path, 'w') as f:
        json.dump(input_json_data, f, indent=2)
    # print(f"Circuit input data for UDI {udi} written to {output_json_path}")
    return udi, actual_failure_status, circuit_input_array

def format_proof_for_contract(proof_json_path):
    """Parses proof.json and formats A, B, C components for Solidity, ensuring Python ints from decimal strings."""
    with open(proof_json_path, 'r') as f:
        proof_data = json.load(f) # proof_data values are decimal strings
    
    pi_a = [int(x) for x in proof_data['pi_a'][:2]] 
    
    pi_b = [
        [int(x) for x in proof_data['pi_b'][0][:2]],
        [int(x) for x in proof_data['pi_b'][1][:2]]
    ]
    pi_c = [int(x) for x in proof_data['pi_c'][:2]]
    
    return pi_a, pi_b, pi_c

def get_public_signals_for_contract(public_json_path):
    """Parses public.json to get circuit output and public inputs (as a list) for the contract."""
    with open(public_json_path, 'r') as f:
        public_signals_str = json.load(f)
    
    public_signals_int = [int(s) for s in public_signals_str] # Convert decimal strings to int
    
    circuit_output_predicted_class = public_signals_int[0]
    circuit_public_inputs = list(public_signals_int[1:1+8]) # Ensure LIST of 8 ints
    
    if len(circuit_public_inputs) != 8:
        raise ValueError(f"Expected 8 public inputs from public.json, got {len(circuit_public_inputs)}")

    return circuit_output_predicted_class, circuit_public_inputs

def log_to_csv(data_dict):
    """Logs a dictionary of data to a CSV file."""
    file_exists = os.path.isfile(cfg.RESULTS_CSV_PATH)
    fieldnames = ['run_timestamp_utc', 'sample_udi', 'sample_index', 'actual_label', 
                  'ml_prediction', 'circuit_prediction', 'inputs_for_circuit',
                  'zkp_time_seconds', 'local_zkp_verified', 
                  'blockchain_tx_hash', 'gas_used', 'tx_status', 'notes']
    
    # Ensure all fields exist in data_dict, add placeholders if not, and convert numpy types
    for field in fieldnames:
        value = data_dict.get(field) # Use .get() to avoid KeyError if field is missing
        if isinstance(value, np.integer):
            data_dict[field] = int(value)
        elif isinstance(value, np.floating):
            data_dict[field] = float(value)
        elif isinstance(value, np.bool_):
            data_dict[field] = bool(value)
        elif value is None: # Explicitly set None for missing, rather than relying on setdefault
             data_dict[field] = None
        # Ensure no other problematic types are passed (e.g. by ensuring all are str, int, float, bool, or None)


    with open(cfg.RESULTS_CSV_PATH, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow({k: data_dict.get(k, '') for k in fieldnames}) # Write empty string for any Nones for CSV


# --- Main Pipeline ---
if __name__ == "__main__":
    print("--- Starting End-to-End Smart Factory Pipeline (Targeted Batch Processing) ---")
    
    # --- Load initial files (once) ---
    try:
        df_original = pd.read_csv(cfg.DATASET_PATH)
        if 'UDI' not in df_original.columns or 'Machine failure' not in df_original.columns or 'Type' not in df_original.columns:
            print("CRITICAL Error: Essential columns ('UDI', 'Machine failure', 'Type') not found in dataset.")
            exit()
        scaler = joblib.load(cfg.SCALER_PATH)
        ml_model = joblib.load(cfg.MODEL_PATH)
        print("Dataset, scaler, and ML model loaded.")
    except Exception as e:
        print(f"CRITICAL Error loading initial files: {e}. Exiting.")
        traceback.print_exc()
        exit()
    
    # --- Explicitly define sample indices to process for discrepancy analysis ---
    # These are 0-based dataset indices.
    # UDI 1   -> Index 0   (Actual Failure: 0 from dataset)
    # UDI 50  -> Index 49  (Actual Failure: 0 from dataset)
    # UDI 78  -> Index 77  (Actual Failure: 1 from dataset)
    # UDI 161 -> Index 160 (Actual Failure: 1 from dataset)
    # UDI 501 -> Index 500 (Actual Failure: 0 from dataset)
    sample_indices_to_process = [0, 49, 77, 160, 500] 
    print(f"Targeted sample indices for this run: {sample_indices_to_process}")

    if not sample_indices_to_process:
        print("No samples selected to process. Exiting.")
        exit()
    
    # --- Connect to blockchain (once) ---
    w3 = None
    contract = None
    account = None

    if all([cfg.SEPOLIA_RPC_URL, cfg.DEPLOYER_PRIVATE_KEY, cfg.CONTRACT_ADDRESS, cfg.CONTRACT_ABI]):
        try:
            w3 = Web3(HTTPProvider(cfg.SEPOLIA_RPC_URL))
            w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
            if not w3.is_connected():
                raise ConnectionError("Failed to connect to Sepolia RPC.")
            print(f"Connected to Sepolia. Chain ID: {w3.eth.chain_id}")
            account = w3.eth.account.from_key(cfg.DEPLOYER_PRIVATE_KEY)
            print(f"Using account: {account.address}")
            contract = w3.eth.contract(address=cfg.CONTRACT_ADDRESS, abi=cfg.CONTRACT_ABI)
        except Exception as e:
            print(f"CRITICAL Error connecting to blockchain or loading contract: {e}. Blockchain logging will be skipped.")
            traceback.print_exc()
            w3 = None 
    else:
        print("Blockchain configuration missing. Blockchain logging will be skipped.")

    # --- Loop through selected samples ---
    for sample_idx in sample_indices_to_process:
        print(f"\n================ PROCESSING SAMPLE AT DATASET INDEX: {sample_idx} ================")
        run_log = { 
            'run_timestamp_utc': datetime.now(timezone.utc).isoformat(),
            'sample_index': sample_idx,
            'sample_udi': None, 'actual_label': None, 'ml_prediction': None,
            'circuit_prediction': None, 'inputs_for_circuit': None,
            'zkp_time_seconds': None, 'local_zkp_verified': False, 
            'blockchain_tx_hash': None, 'gas_used': None, 'tx_status': None, 
            'notes': ''
        }

        try:
            # 1. Prepare input.json
            start_time_zkp = time.time() 
            udi, actual_label, circuit_input_array = prepare_input_for_circuit(
                df_original, sample_idx, scaler, cfg.FEATURE_NAMES_ORDER,
                cfg.NUMERICAL_FEATURES_FOR_SCALING, cfg.FIXED_POINT_MULTIPLIER, cfg.INPUT_JSON_PATH
            )
            run_log['sample_udi'] = int(udi)
            run_log['actual_label'] = int(actual_label)
            run_log['inputs_for_circuit'] = json.dumps(circuit_input_array)

            # 2. Get scikit-learn model prediction
            sample_original_row = df_original.iloc[[sample_idx]]
            numerical_original_values = sample_original_row[cfg.NUMERICAL_FEATURES_FOR_SCALING]
            numerical_scaled_values = scaler.transform(numerical_original_values)
            sklearn_input_data_dict = {}
            for i, name in enumerate(cfg.NUMERICAL_FEATURES_FOR_SCALING):
                sklearn_input_data_dict[name] = numerical_scaled_values[0][i]
            type_val = sample_original_row['Type'].iloc[0]
            sklearn_input_data_dict['Type_H'] = 1 if type_val == 'H' else 0
            sklearn_input_data_dict['Type_L'] = 1 if type_val == 'L' else 0
            sklearn_input_data_dict['Type_M'] = 1 if type_val == 'M' else 0
            sklearn_input_df = pd.DataFrame([sklearn_input_data_dict])[cfg.FEATURE_NAMES_ORDER]
            ml_pred = ml_model.predict(sklearn_input_df)[0]
            run_log['ml_prediction'] = int(ml_pred)
            print(f"Scikit-learn model prediction for UDI {udi}: {ml_pred} ({'Failure' if ml_pred == 1 else 'No Failure'})")
            
            # 3. Generate Witness, Proof
            print("\n--- Generating Witness ---")
            witness_gen_command = [ "node",
                os.path.relpath(cfg.WITNESS_GEN_SCRIPT_PATH, os.path.join(cfg.CIRCUIT_BUILD_DIR, "decision_tree_js")),
                os.path.relpath(cfg.WASM_FILE_PATH, os.path.join(cfg.CIRCUIT_BUILD_DIR, "decision_tree_js")),
                os.path.relpath(cfg.INPUT_JSON_PATH, os.path.join(cfg.CIRCUIT_BUILD_DIR, "decision_tree_js")),
                os.path.relpath(cfg.WITNESS_FILE_PATH, os.path.join(cfg.CIRCUIT_BUILD_DIR, "decision_tree_js"))]
            if not run_command(witness_gen_command, working_dir=os.path.join(cfg.CIRCUIT_BUILD_DIR, "decision_tree_js")):
                raise Exception("Witness generation failed.")

            print("\n--- Generating Proof ---")
            prove_command = [ cfg.SNARKJS_CMD_PATH, "groth16", "prove",
                cfg.PROVING_KEY_PATH, cfg.WITNESS_FILE_PATH,
                cfg.PROOF_JSON_PATH, cfg.PUBLIC_JSON_PATH]
            if not run_command(prove_command, working_dir=cfg.BASE_DIR):
                raise Exception("Proof generation failed.")
            
            run_log['zkp_time_seconds'] = round(time.time() - start_time_zkp, 2)

            # 4. Local ZKP Verification
            print("\n--- Local ZKP Verification ---")
            verify_command = [ cfg.SNARKJS_CMD_PATH, "groth16", "verify",
                cfg.VERIFICATION_KEY_PATH, cfg.PUBLIC_JSON_PATH, cfg.PROOF_JSON_PATH]
            # We need to capture stdout to check for "OK!"
            process_verify = subprocess.run(verify_command, cwd=cfg.BASE_DIR, capture_output=True, text=True, shell=False)
            if process_verify.returncode == 0 and "[INFO]  snarkJS: OK!" in process_verify.stdout:
                run_log['local_zkp_verified'] = True
                print("Local ZKP verification successful!")
            else:
                run_log['notes'] += "Local ZKP verification FAILED or command error. "
                print(f"Local ZKP verification FAILED. STDOUT: {process_verify.stdout} STDERR: {process_verify.stderr}")


            # 5. Prepare data for smart contract
            pi_a, pi_b, pi_c = format_proof_for_contract(cfg.PROOF_JSON_PATH)
            circuit_predicted_class, circuit_public_inputs_for_contract = get_public_signals_for_contract(cfg.PUBLIC_JSON_PATH)
            run_log['circuit_prediction'] = int(circuit_predicted_class)
            print(f"Circuit prediction (from public.json) for UDI {udi}: {circuit_predicted_class}")

            # 6. Log to Blockchain (if w3 is available)
            if w3 and contract and account: 
                print("\n--- Logging to Sepolia Blockchain ---")
                tx_notes_for_chain = f"ZKP Verified Prediction for UDI {udi}. LocalVerify: {run_log['local_zkp_verified']}"
                public_inputs_int_list_for_chain = [int(x) for x in circuit_public_inputs_for_contract]

                try:
                    current_tx_nonce = w3.eth.get_transaction_count(account.address)
                    print(f"Attempting to send transaction with nonce: {current_tx_nonce} for UDI {udi}")

                    tx_params = {
                        'from': account.address,
                        'nonce': current_tx_nonce, 
                        'gas': 2000000, # Increased gas limit slightly
                        'gasPrice': w3.to_wei('10', 'gwei') # Adjust if needed based on Sepolia conditions
                    }
                
                    tx = contract.functions.logPrediction(
                        int(udi), int(circuit_predicted_class),
                        public_inputs_int_list_for_chain, # list of 8 ints
                        pi_a, pi_b, pi_c,                   # list / list of lists for proof
                        tx_notes_for_chain
                    ).build_transaction(tx_params)

                    signed_tx = w3.eth.account.sign_transaction(tx, private_key=cfg.DEPLOYER_PRIVATE_KEY)
                    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction) 
                    print(f"Transaction sent for UDI {udi}. Tx Hash: {tx_hash.hex()}")
                    
                    print("Waiting for transaction receipt...")
                    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=360) # Increased timeout
                    
                    if tx_receipt.status == 1:
                        print(f"Transaction for UDI {udi} successful! Gas used: {tx_receipt.gasUsed}")
                        run_log['blockchain_tx_hash'] = tx_hash.hex()
                        run_log['gas_used'] = tx_receipt.gasUsed
                        run_log['tx_status'] = 'Success'
                        run_log['notes'] += " | Logged to blockchain."
                    else:
                        run_log['notes'] += f" | Blockchain transaction FAILED (Receipt Status 0). TxHash: {tx_hash.hex()}"
                        run_log['tx_status'] = 'Failed (On-Chain)'
                        print(f"Transaction for UDI {udi} FAILED. Receipt: {tx_receipt}")
                
                except Exception as blockchain_err:
                    print(f"Error during blockchain interaction for UDI {udi}: {blockchain_err}")
                    run_log['notes'] += f" | Blockchain interaction error: {type(blockchain_err).__name__} - {blockchain_err}"
                    run_log['tx_status'] = 'Error'
                    traceback.print_exc()
            else:
                run_log['notes'] += " | Skipped blockchain logging (config or connection issue)."

        except Exception as e:
            print(f"ERROR processing sample index {sample_idx} (UDI {run_log.get('sample_udi', 'N/A')}): {e}")
            run_log['notes'] += f" | Top-Level Processing Error: {type(e).__name__} - {e}"
            traceback.print_exc() 
        
        finally:
            log_to_csv(run_log)
            print(f"Finished processing sample index {sample_idx}. Results logged.")
            if w3: 
                time.sleep(10) # Increased delay for Sepolia between transactions

    print("\n--- End-to-End Batch Pipeline Finished ---")
    print(f"All results logged to {cfg.RESULTS_CSV_PATH}")