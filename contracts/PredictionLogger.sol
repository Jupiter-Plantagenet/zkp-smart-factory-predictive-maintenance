// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title PredictionLogger
 * @dev Stores predictive maintenance records with associated ZK proofs.
 * The logPrediction function is public to allow any address with gas to log data.
 * Ownership is maintained for potential future administrative functions.
 */
contract PredictionLogger {
    struct PredictionProof {
        uint256[2] pi_a;
        uint256[2][2] pi_b; // Solidity expects fixed-size arrays for calldata structs
        uint256[2] pi_c;
    }

    struct PredictionRecord {
        uint256 udi;            // Unique Device Identifier or sample ID
        uint256 timestamp;      // Blockchain timestamp of logging
        uint256 predictedClass; // 0 for No Failure, 1 for Failure (output of the ZK circuit)
        uint256[8] publicInputs; // Public inputs to the ZK proof (the 8 features)
        PredictionProof proof;  // The Groth16 proof components
        string notes;           // e.g., "Local ZKP verification successful"
    }

    uint256 public recordCount;
    mapping(uint256 => PredictionRecord) public records; // Maps a recordId to a PredictionRecord

    address public owner;

    event PredictionLogged(
        uint256 indexed recordId,
        uint256 indexed udi,
        uint256 timestamp,
        uint256 predictedClass,
        address indexed submittedBy // The address that called logPrediction
    );

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function.");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    /**
     * @dev Logs a new prediction record. Publicly callable.
     * @param _udi Unique Device Identifier or sample ID.
     * @param _predictedClass The prediction output from the ZK circuit (0 or 1).
     * @param _publicInputs The 8 public input features used for the ZK proof.
     * @param _pi_a Proof component A.
     * @param _pi_b Proof component B.
     * @param _pi_c Proof component C.
     * @param _notes Additional notes for the record.
     * @return recordId The ID of the newly created record.
     */
    function logPrediction(
        uint256 _udi,
        uint256 _predictedClass,
        uint256[8] calldata _publicInputs,
        uint256[2] calldata _pi_a,
        uint256[2][2] calldata _pi_b,
        uint256[2] calldata _pi_c,
        string calldata _notes
    ) public returns (uint256 recordId) { // MODIFICATION: 'onlyOwner' modifier removed
        
        recordId = recordCount;
        records[recordId] = PredictionRecord({
            udi: _udi,
            timestamp: block.timestamp,
            predictedClass: _predictedClass,
            publicInputs: _publicInputs,
            proof: PredictionProof(_pi_a, _pi_b, _pi_c),
            notes: _notes
        });

        recordCount++;
        emit PredictionLogged(recordId, _udi, block.timestamp, _predictedClass, msg.sender);
        return recordId;
    }

    /**
     * @dev Retrieves a stored prediction record by its ID.
     * @param _recordId The ID of the record to retrieve.
     * @return The PredictionRecord struct.
     */
    function getRecord(uint256 _recordId) public view returns (PredictionRecord memory) {
        require(_recordId < recordCount, "Record ID out of bounds.");
        return records[_recordId];
    }

    /**
     * @dev Allows the current owner to transfer control of the contract to a newOwner.
     * @param newOwner The address to transfer ownership to.
     */
    function transferOwnership(address newOwner) public onlyOwner { // This function remains owner-restricted
        require(newOwner != address(0), "Invalid new owner address.");
        owner = newOwner;
    }
}