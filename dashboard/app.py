# dashboard/app.py
from flask import Flask, render_template, jsonify
import pandas as pd
import os
import traceback
from web3 import Web3, HTTPProvider
from web3.middleware import ExtraDataToPOAMiddleware
from datetime import datetime, timezone
import json
import numpy as np # Add numpy import for isinstance checks


import sys
PROJECT_ROOT_FOR_CONFIG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT_FOR_CONFIG)
import config_loader as cfg

app = Flask(__name__)

# --- Web3 Setup --- (as before)
# ... (w3, contract, blockchain_enabled setup) ...
w3 = None
contract = None
blockchain_enabled = False

if cfg.SEPOLIA_RPC_URL and cfg.CONTRACT_ADDRESS and cfg.CONTRACT_ABI:
    try:
        w3 = Web3(HTTPProvider(cfg.SEPOLIA_RPC_URL))
        w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
        if w3.is_connected():
            print("Successfully connected to Sepolia for dashboard.")
            contract = w3.eth.contract(address=cfg.CONTRACT_ADDRESS, abi=cfg.CONTRACT_ABI)
            blockchain_enabled = True
            print(f"Smart contract loaded at address: {cfg.CONTRACT_ADDRESS}")
        else:
            print("ERROR: Failed to connect to Sepolia RPC for dashboard.")
    except Exception as e:
        print(f"ERROR: Could not initialize Web3 or load contract for dashboard: {e}")
        # traceback.print_exc() # Already printed in the main script
else:
    print("WARNING: Blockchain configuration missing. Live data will be unavailable.")


# --- Path to CSV ---
CSV_FILE_PATH = cfg.RESULTS_CSV_PATH # From config_loader

@app.route('/')
def index():
    return render_template('index.html')

def convert_to_native_python_type(value):
    """Converts common numpy types to native Python types for JSON serialization."""
    if isinstance(value, np.integer):
        return int(value)
    elif isinstance(value, np.floating):
        return float(value)
    elif isinstance(value, np.bool_):
        return bool(value)
    elif pd.isna(value) or value is None: # Handle Pandas NaT/NaN and Python None
        return None # Or an empty string "" if preferred for display
    return value

def format_record_for_dashboard(event_log, record_struct_data, csv_lookup_data):
    tx_hash_hex = event_log.transactionHash.hex()
    record_udi = event_log.args.udi

    csv_row_dict = {} # To store extracted and type-converted CSV data
    if csv_lookup_data is not None:
        matching_rows = csv_lookup_data[csv_lookup_data['blockchain_tx_hash'] == tx_hash_hex]
        if not matching_rows.empty:
            csv_row = matching_rows.iloc[0]
            # Convert relevant CSV fields to native Python types
            csv_row_dict['actual_label'] = convert_to_native_python_type(csv_row.get('actual_label'))
            csv_row_dict['ml_prediction'] = convert_to_native_python_type(csv_row.get('ml_prediction'))
            csv_row_dict['zkp_time_seconds'] = convert_to_native_python_type(csv_row.get('zkp_time_seconds'))
            csv_row_dict['local_zkp_verified'] = convert_to_native_python_type(csv_row.get('local_zkp_verified'))
            csv_row_dict['gas_used'] = convert_to_native_python_type(csv_row.get('gas_used'))
            csv_row_dict['tx_status'] = convert_to_native_python_type(csv_row.get('tx_status'))
        else: # Fallback if no tx_hash match
            matching_udi_rows = csv_lookup_data[csv_lookup_data['sample_udi'] == record_udi]
            if not matching_udi_rows.empty:
                csv_row = matching_udi_rows.iloc[0]
                csv_row_dict['actual_label'] = convert_to_native_python_type(csv_row.get('actual_label'))
                # ... convert other fields similarly for UDI match ...
                print(f"Note: Found CSV data for UDI {record_udi} by UDI match, not TxHash.")


    public_inputs_formatted = [str(val) for val in record_struct_data[3]]

    # Ensure all values being returned are JSON serializable native Python types
    return {
        'run_timestamp_utc': str(datetime.fromtimestamp(event_log.args.timestamp, tz=timezone.utc).isoformat()),
        'sample_udi': int(event_log.args.udi), # from blockchain
        'sample_index': f"N/A (ID: {int(event_log.args.recordId)})",
        'actual_label': csv_row_dict.get('actual_label', "N/A (CSV Miss)"),
        'ml_prediction': csv_row_dict.get('ml_prediction', "N/A (CSV Miss)"),
        'circuit_prediction': int(event_log.args.predictedClass), # from blockchain
        'inputs_for_circuit': json.dumps(public_inputs_formatted),
        'zkp_time_seconds': csv_row_dict.get('zkp_time_seconds'),
        'local_zkp_verified': csv_row_dict.get('local_zkp_verified', True), # Default to True if on-chain & no CSV data
        'blockchain_tx_hash': tx_hash_hex,
        'gas_used': csv_row_dict.get('gas_used'),
        'tx_status': csv_row_dict.get('tx_status', 'Success (On-chain)'),
        'notes': str(record_struct_data[5]) # notes from getRecord
    }

@app.route('/api/predictions')
def get_predictions_combined():
    if not blockchain_enabled or not contract:
        return jsonify({"error": "Blockchain connection not available. Check server logs."}), 503

    # Load CSV data
    csv_data_df = None
    try:
        if os.path.exists(CSV_FILE_PATH):
            csv_data_df = pd.read_csv(CSV_FILE_PATH)
            # Convert blockchain_tx_hash in CSV to lowercase for case-insensitive matching if needed,
            # though tx hashes are typically case-sensitive in exact form.
            # We'll assume direct string match.
        else:
            print(f"Warning: CSV file not found at {CSV_FILE_PATH}. Some fields will be N/A.")
    except Exception as e:
        print(f"Warning: Could not load or parse CSV data: {e}")


    predictions = []
    try:
        print("Accessing /api/predictions (blockchain events + CSV enrichment mode)")
        event_filter = contract.events.PredictionLogged.create_filter(from_block='earliest', to_block='latest')
        logs = event_filter.get_all_entries()
        print(f"Found {len(logs)} PredictionLogged events.")

        recent_logs_to_process = sorted(logs, key=lambda x: x.blockNumber, reverse=True)[:20]

        for event_log in recent_logs_to_process:
            record_id = event_log.args.recordId
            print(f"Processing event for Record ID: {record_id}, TxHash: {event_log.transactionHash.hex()}")
            
            record_struct_data = contract.functions.getRecord(record_id).call()
            
            formatted_record = format_record_for_dashboard(event_log, record_struct_data, csv_data_df)
            predictions.append(formatted_record)
        
        print(f"Formatted {len(predictions)} records for dashboard.")
        return jsonify(predictions)

    except Exception as e:
        print(f"!!! Error in get_predictions_combined !!!")
        print(f"Error type: {type(e)}")
        print(f"Error message: {e}")
        traceback.print_exc()
        return jsonify({"error": "An internal server error occurred. Check Flask console."}), 500

if __name__ == '__main__':
    if not cfg.SEPOLIA_RPC_URL or not cfg.CONTRACT_ADDRESS or not cfg.CONTRACT_ABI:
        print("CRITICAL: Essential configuration from config_loader.py is missing!")
    app.run(debug=True, port=5001)