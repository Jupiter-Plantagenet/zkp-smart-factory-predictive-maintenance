# config_loader.py
import os
from dotenv import load_dotenv
import json
from web3 import Web3 # Import Web3 here for to_checksum_address

load_dotenv() # Load variables from .env file

# Blockchain and Account Configuration
SEPOLIA_RPC_URL = os.getenv("SEPOLIA_RPC_URL")
DEPLOYER_PRIVATE_KEY = os.getenv("DEPLOYER_PRIVATE_KEY")
_raw_contract_address = os.getenv("PREDICTION_LOGGER_CONTRACT_ADDRESS") # Load raw address


# --- START MODIFICATION ---
CONTRACT_ADDRESS = None
if _raw_contract_address:
    try:
        CONTRACT_ADDRESS = Web3.to_checksum_address(_raw_contract_address)
        print(f"Contract address loaded and checksummed: {CONTRACT_ADDRESS}")
    except ValueError as e: # Catches if the address is fundamentally invalid
        print(f"Error: PREDICTION_LOGGER_CONTRACT_ADDRESS '{_raw_contract_address}' is not a valid Ethereum address. {e}")
else:
    print("Error: PREDICTION_LOGGER_CONTRACT_ADDRESS is not set in .env file.")
# --- END MODIFICATION ---

# Contract ABI (Paste the ABI JSON string here or load from a file)
# To get ABI from Remix: Compile tab -> ABI button (copy to clipboard)
# Option 1: Paste as a multi-line string
CONTRACT_ABI_STRING = """
[
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_udi",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "_predictedClass",
				"type": "uint256"
			},
			{
				"internalType": "uint256[8]",
				"name": "_publicInputs",
				"type": "uint256[8]"
			},
			{
				"internalType": "uint256[2]",
				"name": "_pi_a",
				"type": "uint256[2]"
			},
			{
				"internalType": "uint256[2][2]",
				"name": "_pi_b",
				"type": "uint256[2][2]"
			},
			{
				"internalType": "uint256[2]",
				"name": "_pi_c",
				"type": "uint256[2]"
			},
			{
				"internalType": "string",
				"name": "_notes",
				"type": "string"
			}
		],
		"name": "logPrediction",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "recordId",
				"type": "uint256"
			}
		],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "newOwner",
				"type": "address"
			}
		],
		"name": "transferOwnership",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"stateMutability": "nonpayable",
		"type": "constructor"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "uint256",
				"name": "recordId",
				"type": "uint256"
			},
			{
				"indexed": true,
				"internalType": "uint256",
				"name": "udi",
				"type": "uint256"
			},
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "timestamp",
				"type": "uint256"
			},
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "predictedClass",
				"type": "uint256"
			},
			{
				"indexed": true,
				"internalType": "address",
				"name": "submittedBy",
				"type": "address"
			}
		],
		"name": "PredictionLogged",
		"type": "event"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_recordId",
				"type": "uint256"
			}
		],
		"name": "getRecord",
		"outputs": [
			{
				"components": [
					{
						"internalType": "uint256",
						"name": "udi",
						"type": "uint256"
					},
					{
						"internalType": "uint256",
						"name": "timestamp",
						"type": "uint256"
					},
					{
						"internalType": "uint256",
						"name": "predictedClass",
						"type": "uint256"
					},
					{
						"internalType": "uint256[8]",
						"name": "publicInputs",
						"type": "uint256[8]"
					},
					{
						"components": [
							{
								"internalType": "uint256[2]",
								"name": "pi_a",
								"type": "uint256[2]"
							},
							{
								"internalType": "uint256[2][2]",
								"name": "pi_b",
								"type": "uint256[2][2]"
							},
							{
								"internalType": "uint256[2]",
								"name": "pi_c",
								"type": "uint256[2]"
							}
						],
						"internalType": "struct PredictionLogger.PredictionProof",
						"name": "proof",
						"type": "tuple"
					},
					{
						"internalType": "string",
						"name": "notes",
						"type": "string"
					}
				],
				"internalType": "struct PredictionLogger.PredictionRecord",
				"name": "",
				"type": "tuple"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "owner",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "recordCount",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"name": "records",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "udi",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "timestamp",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "predictedClass",
				"type": "uint256"
			},
			{
				"components": [
					{
						"internalType": "uint256[2]",
						"name": "pi_a",
						"type": "uint256[2]"
					},
					{
						"internalType": "uint256[2][2]",
						"name": "pi_b",
						"type": "uint256[2][2]"
					},
					{
						"internalType": "uint256[2]",
						"name": "pi_c",
						"type": "uint256[2]"
					}
				],
				"internalType": "struct PredictionLogger.PredictionProof",
				"name": "proof",
				"type": "tuple"
			},
			{
				"internalType": "string",
				"name": "notes",
				"type": "string"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
]
"""
try:
    CONTRACT_ABI = json.loads(CONTRACT_ABI_STRING)
    print(f"Loaded ABI type: {type(CONTRACT_ABI)}")
    print(f"Loaded ABI (Complete): {CONTRACT_ABI[:] if CONTRACT_ABI else 'None'}")
except json.JSONDecodeError as e:
    print(f"Error: Could not parse CONTRACT_ABI_STRING. Please ensure it's a valid JSON. Error: {e}")
    print("ABI String causing error was:\n", CONTRACT_ABI_STRING)
    CONTRACT_ABI = None # Set to None if parsing fails

# You can verify if variables are loaded
if not all([SEPOLIA_RPC_URL, DEPLOYER_PRIVATE_KEY, CONTRACT_ADDRESS, CONTRACT_ABI]):
    print("Error: One or more environment variables or the ABI is missing or invalid.")
    print(f"SEPOLIA_RPC_URL: {'Loaded' if SEPOLIA_RPC_URL else 'MISSING'}")
    print(f"DEPLOYER_PRIVATE_KEY: {'Loaded' if DEPLOYER_PRIVATE_KEY else 'MISSING'}")
    print(f"CONTRACT_ADDRESS: {'Loaded' if CONTRACT_ADDRESS else 'MISSING'}")
    print(f"CONTRACT_ABI: {'Loaded' if CONTRACT_ABI else 'MISSING or INVALID JSON'}")
    # exit() # Optionally exit if config is incomplete

# Paths (copied and adapted from 07_automate_proof_generation.py)
BASE_DIR = os.path.dirname(os.path.abspath(os.path.join(os.getcwd(), __file__)))  # Assuming config_loader.py is in project root

DATASET_PATH = os.path.join(BASE_DIR, "data", "ai4i2020.csv")
SCALER_PATH = os.path.join(BASE_DIR, "artifacts", "model", "standard_scaler.joblib")
MODEL_PATH = os.path.join(BASE_DIR, "artifacts", "model", "decision_tree_model.joblib")

CIRCUIT_BUILD_DIR = os.path.join(BASE_DIR, "artifacts", "circuit", "circuit_build")
WASM_FILE_PATH = os.path.join(CIRCUIT_BUILD_DIR, "decision_tree_js", "decision_tree.wasm")
WITNESS_GEN_SCRIPT_PATH = os.path.join(CIRCUIT_BUILD_DIR, "decision_tree_js", "generate_witness.js")

PROVING_KEY_PATH = os.path.join(BASE_DIR, "artifacts", "zkp_keys", "decision_tree_0001.zkey")
VERIFICATION_KEY_PATH = os.path.join(BASE_DIR, "artifacts", "zkp_keys", "verification_key.json")

INPUT_JSON_PATH = os.path.join(BASE_DIR, "runtime_outputs", "input.json")
WITNESS_FILE_PATH = os.path.join(CIRCUIT_BUILD_DIR, "decision_tree_js", "witness.wtns")
PROOF_JSON_PATH = os.path.join(BASE_DIR, "runtime_outputs", "proof.json")
PUBLIC_JSON_PATH = os.path.join(BASE_DIR, "runtime_outputs", "public.json")
RESULTS_CSV_PATH = os.path.join(BASE_DIR, "runtime_outputs", "end_to_end_results.csv")

DATA_SPLITS_DIR = os.path.join(BASE_DIR, "artifacts", "data_splits")
X_TRAIN_CSV_PATH = os.path.join(DATA_SPLITS_DIR, "X_train.csv")
X_TEST_CSV_PATH = os.path.join(DATA_SPLITS_DIR, "X_test.csv")
Y_TRAIN_CSV_PATH = os.path.join(DATA_SPLITS_DIR, "y_train.csv")
Y_TEST_CSV_PATH = os.path.join(DATA_SPLITS_DIR, "y_test.csv")



# Feature and model parameters
FEATURE_NAMES_ORDER = ['Air temperature [K]', 'Process temperature [K]', 'Rotational speed [rpm]', 'Torque [Nm]', 'Tool wear [min]', 'Type_H', 'Type_L', 'Type_M']
NUMERICAL_FEATURES_FOR_SCALING = ['Air temperature [K]', 'Process temperature [K]', 'Rotational speed [rpm]', 'Torque [Nm]', 'Tool wear [min]']
FIXED_POINT_MULTIPLIER = 10000
SAMPLE_INDEX = 49 # UDI 50

# Path to snarkjs.cmd
#SNARKJS_CMD_PATH = r"C:\Users\NSL\AppData\Roaming\npm\snarkjs.cmd" # Update if your path is different
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
