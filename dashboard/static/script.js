// dashboard/static/script.js
document.addEventListener('DOMContentLoaded', function() {
    const predictionsTableBody = document.getElementById('predictionsTable').getElementsByTagName('tbody')[0];
    const refreshButton = document.getElementById('refreshData');
    const errorMessageElement = document.getElementById('error-message'); // Ensure you have <p id="error-message"></p> in HTML
    const loadingMessageElement = document.createElement('p'); // For loading state
    const filterUDIInput = document.getElementById('filterUDI');
    loadingMessageElement.textContent = 'Loading data...';
    loadingMessageElement.className = 'loading-text';


    const sepoliaEtherscanBaseUrl = "https://sepolia.etherscan.io/tx/";

    function displayError(message) {
        errorMessageElement.textContent = message;
        predictionsTableBody.innerHTML = ''; // Clear table on error
        const parent = predictionsTableBody.parentNode.parentNode; // Get .table-container
        if (parent.contains(loadingMessageElement)) {
            parent.removeChild(loadingMessageElement);
        }
    }

    function populateTable(data) {
        predictionsTableBody.innerHTML = ''; 
        errorMessageElement.textContent = ''; 

        if (!data || data.length === 0) {
            const row = predictionsTableBody.insertRow();
            const cell = row.insertCell();
            cell.colSpan = 10; 
            cell.textContent = 'No prediction data found on the blockchain yet, or an issue occurred fetching it.';
            cell.style.textAlign = 'center';
            return;
        }

        let filteredData = data;
        const filterUDIText = filterUDIInput.value.trim().toLowerCase();

        if (filterUDIText) {
            filteredData = data.filter(record => {
            return record.sample_udi && record.sample_udi.toString().toLowerCase().includes(filterUDIText);
            });
        }

        // Add event listener for the filter input
        if(filterUDIInput) {
            filterUDIInput.addEventListener('keyup', () => {
            // This will re-fetch and re-populate, which implicitly applies the filter.
            // A more optimized way would be to filter the already fetched data,
            // but for simplicity with the current fetchData structure:
                fetchData(); 
            });
        }

        filteredData.forEach(record => {
            const row = predictionsTableBody.insertRow();
            
            // Improved Date/Time Formatting
            let formattedTimestamp = 'N/A';
            if (record.run_timestamp_utc) {
                try {
                    formattedTimestamp = new Date(record.run_timestamp_utc).toLocaleString();
                } catch (e) {
                    console.warn("Could not parse timestamp:", record.run_timestamp_utc);
                    formattedTimestamp = record.run_timestamp_utc; // fallback
                }
            }
            row.insertCell().textContent = formattedTimestamp;

            row.insertCell().textContent = record.sample_udi || 'N/A';
            
            // Actual Label - often N/A when reading from chain, handle gracefully
            const actualLabelCell = row.insertCell();
            actualLabelCell.textContent = record.actual_label !== null && record.actual_label !== undefined ? 
                                          (record.actual_label == 1 ? 'Failure (1)' : 'No Failure (0)') : 'N/A (On-Chain)';
            
            // ML Prediction - often N/A when reading from chain
            const mlPredictionCell = row.insertCell();
            mlPredictionCell.textContent = record.ml_prediction !== null && record.ml_prediction !== undefined ? 
                                           (record.ml_prediction == 1 ? 'Failure (1)' : 'No Failure (0)') : 'N/A (On-Chain)';

            // Circuit Prediction
            const circuitPredictionCell = row.insertCell();
            if (record.circuit_prediction !== null && record.circuit_prediction !== undefined) {
                circuitPredictionCell.textContent = record.circuit_prediction == 1 ? 'Failure (1)' : 'No Failure (0)';
                circuitPredictionCell.classList.add(record.circuit_prediction == 1 ? 'failure-predicted' : 'no-failure-predicted');
            } else {
                circuitPredictionCell.textContent = 'N/A';
            }
            
            const zkpCell = row.insertCell();
            zkpCell.textContent = record.local_zkp_verified === true ? '✅ Verified' : (record.local_zkp_verified === false ? '❌ Not Verified' : 'N/A (On-Chain)');
            zkpCell.style.color = record.local_zk_p_verified === true ? 'green' : (record.local_zkp_verified === false ? 'red': 'inherit');


            const txHashCell = row.insertCell();
            if (record.blockchain_tx_hash && record.blockchain_tx_hash !== "None" && record.blockchain_tx_hash !== null && !record.blockchain_tx_hash.startsWith("Record ID:")) {
                const link = document.createElement('a');
                link.href = `${sepoliaEtherscanBaseUrl}0x${record.blockchain_tx_hash}`; 
                link.textContent = record.blockchain_tx_hash.substring(0, 10) + '...';
                link.target = '_blank';
                txHashCell.appendChild(link);
            } else {
                txHashCell.textContent = record.blockchain_tx_hash || 'N/A'; // Show "Record ID: X" or N/A
            }
            
            row.insertCell().textContent = record.gas_used || 'N/A';
            row.insertCell().textContent = record.tx_status || 'N/A';
            
            const notesCell = row.insertCell();
            notesCell.textContent = record.notes || '';
            notesCell.title = record.notes || ''; // Show full notes on hover
        });
    }

    function fetchData() {
        const parent = predictionsTableBody.parentNode.parentNode; // Get .table-container
        parent.insertBefore(loadingMessageElement, predictionsTableBody.parentNode);
        errorMessageElement.textContent = ''; // Clear previous errors
        predictionsTableBody.innerHTML = ''; // Clear table before fetch

        fetch('/api/predictions')
            .then(response => {
                if (parent.contains(loadingMessageElement)) {
                    parent.removeChild(loadingMessageElement);
                }
                if (!response.ok) {
                    // Try to get error message from backend if it's JSON
                    return response.json().then(errData => {
                        throw new Error(`HTTP error! Status: ${response.status}. Message: ${errData.error || response.statusText}`);
                    }).catch(() => {
                        // If backend didn't send JSON error or other issue
                        throw new Error(`HTTP error! Status: ${response.status}. ${response.statusText}`);
                    });
                }
                return response.json();
            })
            .then(data => {
                if (data.error) { // Should be caught by !response.ok now, but as a fallback
                    console.error('Error fetching predictions (data.error):', data.error);
                    displayError(`Error: ${data.error}`);
                } else {
                    populateTable(data);
                }
            })
            .catch(error => {
                if (parent.contains(loadingMessageElement)) {
                    parent.removeChild(loadingMessageElement);
                }
                console.error('Error fetching predictions (catch):', error);
                displayError(`Failed to fetch data: ${error.message}. Is the Flask server running and connected to the blockchain?`);
            });
    }

    refreshButton.addEventListener('click', fetchData);
    fetchData(); // Initial data load
});

// Function to sort the table
function sortTable(columnIndex, tableId) {
    const table = document.getElementById(tableId);
    const tbody = table.getElementsByTagName('tbody')[0];
    const rows = Array.from(tbody.getElementsByTagName('tr'));
    const headerCell = table.getElementsByTagName('th')[columnIndex];
    const isAscending = !(headerCell.classList.contains('sort-asc')); // Toggle direction

    // Reset other headers' sort indicators
    table.querySelectorAll('th').forEach(th => {
        th.classList.remove('sort-asc', 'sort-desc');
        th.innerHTML = th.innerHTML.replace(/ (↑|↓)$/, ""); // Remove old arrow
    });

    rows.sort((rowA, rowB) => {
        let cellA = rowA.getElementsByTagName('td')[columnIndex].textContent.trim().toLowerCase();
        let cellB = rowB.getElementsByTagName('td')[columnIndex].textContent.trim().toLowerCase();

        // Attempt to convert to number for numeric sort if possible
        let numA = parseFloat(cellA);
        let numB = parseFloat(cellB);

        if (!isNaN(numA) && !isNaN(numB)) {
            cellA = numA;
            cellB = numB;
        }
        
        // For ZKP Verified (Local) - treat '✅ Verified' as higher/true
        if (columnIndex === 5) { // Assuming ZKP Verified is the 6th column (index 5)
            cellA = cellA.startsWith('✅') ? 1 : 0;
            cellB = cellB.startsWith('✅') ? 1 : 0;
        }


        if (cellA < cellB) {
            return isAscending ? -1 : 1;
        }
        if (cellA > cellB) {
            return isAscending ? 1 : -1;
        }
        return 0;
    });

    // Re-append sorted rows
    rows.forEach(row => tbody.appendChild(row));

    // Update header with sort indicator
    if (isAscending) {
        headerCell.classList.add('sort-asc');
        headerCell.innerHTML += ' &uarr;'; // Up arrow
    } else {
        headerCell.classList.add('sort-desc');
        headerCell.innerHTML += ' &darr;'; // Down arrow
    }
}

// Add event listeners to table headers for sorting
document.addEventListener('DOMContentLoaded', function() {
    // ... (your existing DOMContentLoaded code for fetching data) ...

    const predictionsTable = document.getElementById('predictionsTable');
    if (predictionsTable) {
        const headers = predictionsTable.getElementsByTagName('th');
        for (let i = 0; i < headers.length; i++) {
            headers[i].style.cursor = 'pointer'; // Indicate clickable
            headers[i].addEventListener('click', () => sortTable(i, 'predictionsTable'));
        }
    }
});