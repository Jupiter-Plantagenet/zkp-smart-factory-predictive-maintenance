# ZK-Verified Predictive Maintenance and Auditable Manufacturing Log

This project implements an end-to-end system for predictive maintenance in a smart factory. It uses a Machine Learning model to predict equipment failures, Zero-Knowledge Proofs (zk-SNARKs) to verify the prediction computation, and logs these verifiable events to the Sepolia Ethereum testnet for an immutable audit trail. A web dashboard visualizes these on-chain records.

## Table of Contents
1.  [Project Overview](#project-overview)
2.  [System Architecture](#system-architecture)
3.  [Features](#features)
4.  [Prerequisites](#prerequisites)
5.  [Project Setup](#project-setup)
6.  [Step-by-Step Execution Guide](#step-by-step-execution-guide)
    * [A. Data Preprocessing & ML Model Training](#a-data-preprocessing--ml-model-training)
    * [B. ZK-SNARK Circuit Generation & Setup](#b-zk-snark-circuit-generation--setup)
    * [C. Smart Contract Deployment](#c-smart-contract-deployment)
    * [D. Configure Environment for Pipeline](#d-configure-environment-for-pipeline)
    * [E. Run the End-to-End Pipeline](#e-run-the-end-to-end-pipeline)
    * [F. Run the Web Dashboard](#f-run-the-web-dashboard)
7.  [Folder Structure (Recommended)](#folder-structure-recommended)
8.  [Troubleshooting](#troubleshooting)

## 1. Project Overview
This system demonstrates how zk-SNARKs can enhance trust and privacy in predictive maintenance by allowing for verifiable computations without revealing underlying sensitive data. Predictions from a Decision Tree model are proven correct using Groth16 zk-SNARKs (with Circom and snarkjs), and these verified events are logged on the Sepolia blockchain via a Solidity smart contract. A Flask-based web dashboard provides a view into these on-chain records.

## 2. System Architecture
The system comprises:
* **Data Preprocessing Module:** Cleans and prepares sensor data.
* **Machine Learning Module:** Trains a Decision Tree for failure prediction.
* **ZK-SNARK Circuit Generation Module:** Translates the trained Decision Tree into a Circom arithmetic circuit.
* **ZKP Proving System:** Uses `snarkjs` for trusted setup, witness generation, and proof creation/verification (Groth16).
* **Orchestration Pipeline:** Python scripts automate the flow from data input to blockchain logging.
* **Blockchain Module:** A Solidity smart contract (`PredictionLogger.sol`) on Sepolia for storing verifiable prediction records.
* **Web Dashboard:** A Flask and HTML/JS/CSS application to display on-chain data.

## 3. Features
* Predictive maintenance using a Decision Tree model.
* Generation of zk-SNARK proofs for prediction integrity.
* Logging of verifiable predictions to the Sepolia Ethereum testnet.
* Automated end-to-end pipeline for processing data samples.
* Web dashboard to visualize on-chain prediction logs with Etherscan links.
* Local ZKP verification before blockchain submission.

## 4. Prerequisites
Ensure you have the following installed:
* **Python:** 3.10+ (Anaconda/Miniconda recommended for environment management).
* **Node.js and npm:** Node.js v18+ LTS recommended.
* **Rust and Cargo:** For compiling Circom. Follow official Rust installation guide.
* **Circom Compiler:** Install from source ([https://github.com/iden3/circom#installation](https://github.com/iden3/circom#installation)) and ensure `circom` is in your system PATH.
* **snarkjs:** Install globally: `npm install -g snarkjs`
* **Solidity Compiler (`solc`):** If compiling/deploying contract locally (e.g., via Hardhat/Truffle). For this guide, we'll assume Remix IDE for deployment.
* **MetaMask Browser Extension:** (Or similar EVM wallet) for deploying the smart contract and interacting with the Sepolia testnet. Ensure it's funded with Sepolia ETH from a faucet (e.g., [sepoliafaucet.com](https://sepoliafaucet.com/), [infura.io/faucet/sepolia](https://infura.io/faucet/sepolia)).

## 5. Project Setup

1.  **Clone the Repository:**
    ```bash
    git clone <your-repo-url>
    cd <your-repo-name> # e.g., smart_factory_zkp_project
    ```

2.  **Create and Activate Conda Environment:**
    ```bash
    conda create --name smart_factory_env python=3.11 -y 
    conda activate smart_factory_env
    ```

3.  **Install Python Dependencies:**
    (Ensure `requirements.txt` is in your project root)
    ```bash
    pip install -r requirements.txt
    ```

4.  **Install Node.js Dependencies (for `circomlib`):**
    (Ensure `package.json` exists or run `npm init -y` first, then install)
    In the project root directory:
    ```bash
    npm install circomlib
    ```
    This creates `node_modules/circomlib` which the generated Circom circuit will reference.

5.  **Prepare Dataset:**
    * Download the "AI4I 2020 Predictive Maintenance Dataset" (typically `ai4i2020.csv`).
    * Create a `data/` folder in your project root and place `ai4i2020.csv` inside it.
    * Update `DATASET_PATH` in `config_loader.py` if needed (it should default to `data/ai4i2020.csv` if `config_loader.py` is in the root and uses the suggested `os.path.join` structure).

6.  **Prepare Powers of Tau File (Phase 1 ZKP Setup - Generic):**
    This is a one-time setup for a given constraint size. These files can be large.
    * Run the following commands in your project root (the `12` means it supports circuits up to 2^12 = 4096 constraints; our circuit is smaller):
        ```bash
        snarkjs powersoftau new bn128 12 pot12_0000.ptau -v
        snarkjs powersoftau contribute pot12_0000.ptau pot12_0001.ptau --name="My Initial Tau Contribution" -v -e="random string 1"
        # For a real ceremony, many contributions are needed. For development, one is okay.
        snarkjs powersoftau prepare phase2 pot12_0001.ptau pot12_final.ptau -v
        ```
    * This will create `pot12_final.ptau` in your project root. This file is generic and can be reused. (Ensure `.ptau` files are in your `.gitignore` if you don't want to commit them due to size).

## 6. Step-by-Step Execution Guide

Make sure all paths in `config_loader.py` are correctly set up to point to your organized script/artifact locations. The paths below assume you've organized scripts into `ml_scripts/`, `zkp_scripts/`, etc., and artifacts into `artifacts/`.

**A. Data Preprocessing & ML Model Training**
These scripts generate the ML model, scaler, and feature names list.

1.  **Run Preprocessing:**
    ```bash
    python ml_scripts/02_preprocess_data.py
    ```
    *Outputs:* `standard_scaler.joblib`, `feature_names.joblib` (e.g., in `artifacts/model/`) and data splits (e.g., in `artifacts/data_splits/`).

2.  **Train ML Model:**
    ```bash
    python ml_scripts/03_train_evaluate_model.py
    ```
    *Outputs:* `decision_tree_model.joblib` (e.g., in `artifacts/model/`).

**B. ZK-SNARK Circuit Generation & Setup**

1.  **Generate Circom Circuit from Trained Model:**
    ```bash
    python zkp_scripts/05_generate_circom_circuit.py
    ```
    *Outputs:* `decision_tree.circom` (e.g., in `artifacts/circuit/`). Ensure the `include` path for `circomlib` inside this generated file is correct relative to its location and the root `node_modules` (e.g., `../../node_modules/...`).

2.  **Compile Circom Circuit:**
    * Navigate to where `decision_tree.circom` was saved (e.g., `cd artifacts/circuit/`).
    * Uncomment the `component main {public [features]} = DecisionTree(8);` line at the end of `decision_tree.circom`.
    * Create an output directory for compiled artifacts: `mkdir circuit_build`
    * Compile:
        ```bash
        circom decision_tree.circom --r1cs --wasm --sym -o ./circuit_build
        ```
    *Outputs:* `.r1cs`, `.wasm`, `.sym` files in `circuit_build/`.
    * Navigate back to the project root: `cd ../..` (adjust as per your structure).

3.  **Perform Groth16 Trusted Setup (Circuit-Specific Phase 2):**
    Run these commands from the project root. Adjust paths to your `.r1cs` file (now in `artifacts/circuit/circuit_build/`) and desired output locations for keys (e.g., `artifacts/zkp_keys/`).
    ```bash
    snarkjs groth16 setup ./artifacts/circuit/circuit_build/decision_tree.r1cs pot12_final.ptau ./artifacts/zkp_keys/decision_tree_0000.zkey -v
    snarkjs zkey contribute ./artifacts/zkp_keys/decision_tree_0000.zkey ./artifacts/zkp_keys/decision_tree_0001.zkey --name="Primary User Contribution" -v -e="some unique random string"
    snarkjs zkey export verificationkey ./artifacts/zkp_keys/decision_tree_0001.zkey ./artifacts/zkp_keys/verification_key.json -v
    ```
    *Outputs:* `decision_tree_0001.zkey` (proving key) and `verification_key.json` in (e.g.) `artifacts/zkp_keys/`.

**C. Smart Contract Deployment (`contracts/PredictionLogger.sol`)**

1.  Open Remix IDE ([https://remix.ethereum.org/](https://remix.ethereum.org/)).
his step is for information if users want to understand the contract or deploy their own instance. For running the project against the primary deployed instance, this step can be skipped by users.
2.  The Solidity smart contract contracts/PredictionLogger.sol is used to log verifiable predictions.
3.  A primary instance of this contract has already been deployed to the Sepolia Test Network at address: YOUR_DEPLOYED_CONTRACT_ADDRESS (the one you will put in .env.example and that users will copy to their .env).
4.  The ABI for this contract is included in config_loader.py.
5.  (Optional) If users wish to deploy their own instance, they can use Remix IDE or other Solidity development tools, then update PREDICTION_LOGGER_CONTRACT_ADDRESS in their local .env file and the ABI in config_loader.py if they modify the contract

**D. Configure Environment for Pipeline**

1.  Copy `.env.example` to `.env` in the project root.
2.  Edit `.env` and fill in:
    * `SEPOLIA_RPC_URL`
    * `DEPLOYER_PRIVATE_KEY` (for the account used to deploy the contract and send transactions)
    * `PREDICTION_LOGGER_CONTRACT_ADDRESS` (the address you just copied, if deploying own instance)
3.  Open `config_loader.py` and paste the full **ABI JSON string** into the `CONTRACT_ABI_STRING` variable, if deploying own instance.
4.  Also in `config_loader.py`, ensure all paths to models, scalers, circuit files, ZKP keys, and output directories reflect your chosen organized structure (e.g., within `artifacts/`).

**E. Run the End-to-End Pipeline**
This script processes samples, generates ZK proofs, and logs to the blockchain.
* Ensure your `.env` and `config_loader.py` are correctly set up.
* Modify `sample_indices_to_process` in `pipeline_scripts/08_end_to_end_pipeline.py` to select the samples you want to run.
* It's recommended to delete any old `end_to_end_results.csv` (e.g., in `artifacts/runtime_outputs/`) before a new batch run.
    ```bash
    python pipeline_scripts/08_end_to_end_pipeline.py
    ```
*Outputs:* Populates `end_to_end_results.csv`, sends transactions to Sepolia.

**F. Run the Web Dashboard**
    ```bash
    cd dashboard
    python app.py
    ```
    Open your browser to `http://127.0.0.1:5001/`. The dashboard will fetch and display records from the `PredictionLogger` smart contract on Sepolia.

## 7. Folder Structure (Recommended)

```

<your_project_root>/
|-- .env.example
|-- .gitignore
|-- README.md
|-- requirements.txt
|-- config_loader.py
|-- package.json
|-- package-lock.json
|-- pot12_final.ptau  (generate yours)
|
|-- data/
|   |-- ai4i2020.csv
|
|-- ml_scripts/
|   |-- 02_preprocess_data.py
|   |-- 03_train_evaluate_model.py
|
|-- zkp_scripts/
|   |-- 05_generate_circom_circuit.py
|
|-- pipeline_scripts/
|   |-- 08_end_to_end_pipeline.py
|
|-- contracts/
|   |-- PredictionLogger.sol #this has already been deployed, the address is in .env.example in this project
|
|-- dashboard/
|   |-- app.py
|   |-- templates/index.html
|   |-- static/style.css, script.js
|
|-- artifacts/  <-- Directory for files generated by the scripts
|   |-- model/            <-- ML model, scaler, feature_names
|   |-- circuit/          <-- decision_tree.circom
|   |   |-- circuit_build/  <-- .r1cs, .wasm, .sym (gitignore this subdir)
|   |-- zkp_keys/         <-- .zkey, verification_key.json (gitignore these files)
|   |-- runtime_outputs/  <-- end_to_end_results.csv, input.json, proof.json, etc. (gitignore these)
|
|-- node_modules/         <-- (gitignore this)

```

*Adjust paths in `config_loader.py` and scripts to match this structure.*

## 8. Troubleshooting
* **PATH Issues (`circom`, `snarkjs`, `node` not found):** Ensure these tools are installed correctly and their executable locations are in your system's PATH environment variable.
* **Python `ModuleNotFoundError`:** Make sure you have activated the Conda environment (`conda activate smart_factory_env`) and run `pip install -r requirements.txt`.
* **`web3.py` Errors:**
    * `InvalidAddress` (Checksum): Ensure contract address in `.env` (and thus `config_loader.py`) is checksummed. `config_loader.py` now handles this.
    * `MismatchedABI`: Double-check the ABI in `config_loader.py` is exact and complete for the deployed contract. Verify Python data types being passed to contract functions.
    * Connection Errors: Verify your `SEPOLIA_RPC_URL` is correct and active.
* **Blockchain Transaction Failures:**
    * `Insufficient funds`: Add more Sepolia test ETH to your deployer account.
    * `Nonce too low`: The pipeline script now fetches nonce per transaction, which should be robust. If it persists, check for other wallets/scripts using the same account and nonce, or transactions stuck in the mempool.
    * `Gas estimation failed` / `Out of gas`: Increase the `gas` limit in `tx_params` within `08_end_to_end_pipeline.py`.
* **ZK-SNARK Errors (`snarkjs` or circuit compilation):** These can be complex. Refer to Circom and snarkjs documentation. Ensure circuit logic is correct and constraints are quadratic. The provided scripts should handle this for the decision tree.
* **CSV Parsing Errors (Dashboard):** Ensure `end_to_end_results.csv` is deleted before the pipeline generates a new one, especially if you change the columns being logged. The dashboard now reads live from blockchain, but this was a past issue.

---