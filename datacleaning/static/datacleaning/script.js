// Select DOM elements
const fileInput = document.getElementById('fileInput');
const fileDataContainer = document.getElementById('fileDataContainer');
const validateButton = document.getElementById('validateButton');
const validationResults = document.getElementById('validationResults');
const missingDataForm = document.getElementById('missingDataForm');
const applyMissingDataButton = document.getElementById('applyMissingData');

let parsedCSVData = []; // To hold the parsed CSV data
let displayedRows = 0;
const rowsPerLoad = 50; // Number of rows to display per load

// Event listener for the file input to handle file selection and CSV parsing
fileInput.addEventListener('change', function(event) {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function(e) {
        const contents = e.target.result;
        parsedCSVData = parseCSV(contents); // Parse CSV data
        
        displayedRows = 0; // Reset displayed rows counter
        displayFileData(parsedCSVData); // Display parsed CSV data
         // Log the file data container content
        validateButton.style.display = 'inline-block'; // Show validation button
    };
    reader.readAsText(file); // Read the file as text
});



// Function to parse CSV data into an array of arrays (rows and columns)
function parseCSV(data) {
    data = data.replace(/\r/g, ''); // Remove carriage returns
    const rows = data.split('\n').map(row => row.trim());
    const parsedData = rows.map(row => {
        const cells = row.split(/,(?=(?:(?:[^"]*"){2})*[^"]*$)/); // Handles quoted cells correctly
        return cells.map(cell => cell.replace(/(^"|"$)/g, '').trim()); // Remove surrounding quotes
    });
    return parsedData.filter(row => row.some(cell => cell.trim() !== '')); // Filter out fully empty rows
}

// Function to display parsed CSV data in a table format
function displayFileData(data) {
    fileDataContainer.innerHTML = ''; // Clear any existing content
    const table = document.createElement('table');
    const tableBody = document.createElement('tbody');
    table.appendChild(tableBody);
    fileDataContainer.appendChild(table);
    renderRows(data, 0, rowsPerLoad); // Render the first batch of rows
}

// Function to render a subset of rows (for pagination) in the table
function renderRows(data, startIndex, rowsPerLoad, tableBody = document.querySelector('table tbody')) {
    tableBody.innerHTML = ''; // Clear previous rows
    
    const rowsToRender = data.slice(startIndex, startIndex + rowsPerLoad);
    rowsToRender.forEach(row => {
        const tr = document.createElement('tr');
        row.forEach(value => {
            const td = document.createElement('td');
            td.textContent = value;
            tr.appendChild(td);
        });
        tableBody.appendChild(tr); // Append the row to the table body
    });
}


// Event listener for the Validate Data button to check for issues in the data
validateButton.addEventListener('click', function() {
    const results = {
        missingValues: [],
        invalidData: [],
        duplicates: []
    };
    const numRows = parsedCSVData.length - 1; // Total number of rows
    const numColumns = parsedCSVData[0].length; // Total number of columns
    let totalDataSizeBytes = 0;

    // Calculate total data size in bytes
    parsedCSVData.forEach(row => {
        totalDataSizeBytes += new Blob([row.join(',')]).size;
    });
    const totalDataSizeKB = (totalDataSizeBytes / 1024).toFixed(2); // Convert to KB

    const headers = parsedCSVData[0];
    const columnTypes = {}; // Object to track column data types
    const seen = new Set(); // Set to track duplicate rows

    // Iterate through data to check for missing values, invalid data, and duplicates
    for (let i = 1; i < parsedCSVData.length; i++) {
        const row = parsedCSVData[i];
        headers.forEach((header, colIndex) => {
            const value = row[colIndex];
            if (value === null || value === undefined || value === '') {
                results.missingValues.push(`Row ${i + 1}: Missing value in '${header}'`);
            }
            if (!isNaN(Number(value))) {
                columnTypes[header] = 'number'; // Mark column as numeric if a number is found
            } else if (value !== '' && typeof value !== 'number' && typeof value !== 'string') {
                results.invalidData.push(`Row ${i + 1}: Invalid value in '${header}'`);
            }
        });

        const rowString = JSON.stringify(row.map(cell => cell.trim()));
        if (seen.has(rowString)) {
            results.duplicates.push(`Duplicate at Row ${i + 1}`); // Track duplicate rows
        } else {
            seen.add(rowString);
        }
    }

    // Display validation results
    validationResults.style.visibility = 'visible';
    validationResults.innerHTML = ''; // Clear previous results
    validationResults.innerHTML += `<p><strong>Data Size:</strong> ${totalDataSizeKB} KB</p>`;
    validationResults.innerHTML += `<p><strong>Rows:</strong> ${numRows}</p>`;
    validationResults.innerHTML += `<p><strong>Columns:</strong> ${numColumns}</p>`;

    if (results.missingValues.length > 0 || results.invalidData.length > 0 || results.duplicates.length > 0) {
        if (results.missingValues.length > 0) {
            validationResults.innerHTML += `<h3>Missing Values</h3><ul><li>${results.missingValues.join('</li><li>')}</li></ul>`;
        }
        if (results.invalidData.length > 0) {
            validationResults.innerHTML += `<h3>Invalid Data</h3><ul><li>${results.invalidData.join('</li><li>')}</li></ul>`;
        }
        if (results.duplicates.length > 0) {
            validationResults.innerHTML += `<h3>Duplicate Rows</h3><ul><li>${results.duplicates.join('</li><li>')}</li></ul>`;
        }
        missingDataForm.style.display = 'block'; // Show the missing data form after validation results are displayed
    } else {
        validationResults.innerHTML = `<p>Validation successful. No issues found.</p>`;
    }

    window.scrollTo(0, 0);
});

// Wait until the DOM is fully loaded
// Wait until the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function () {
    const removeDuplicatesBtn = document.getElementById('removeDuplicatesBtn');
    // Get form elements
    const strategySelect = document.getElementById('strategy');
    const customValueInputDiv = document.getElementById('custom-value-input');
    const applyButton = document.getElementById('applyMissingData');
    const customValueInputContainer = document.getElementById('custom-value-input'); // Container for dynamic inputs
    const customValueInput = document.querySelector('#custom_value_input');
    const customValueInputs = document.querySelectorAll('.custom_value_input');
    let currentOperation = "";

    if (!customValueInput) {
        console.error('custom_value_input element not found');
        return; // Exit if the input field is not found
    }

    // Listen for changes in strategy selection
    function handleStrategyChange() {
        const selectedStrategy = strategySelect.value;
        if (selectedStrategy === "fill_custom") {
            customValueInputContainer.style.display = 'block'; 
            generateCustomValueInputs(); 
        } else {
            customValueInputContainer.style.display = 'none'; 
        }
    }
    

    strategySelect.addEventListener('change', handleStrategyChange);

    // Initialize the input visibility based on the current selection
    handleStrategyChange();

    // Apply button click event
    
    
    

    /**
     * Function to collect custom values entered by the user for each column
     */
    
    function displayCustomValueInputs(missingColumns) {
        const customValueInputsContainer = document.getElementById('customValueInputsContainer'); // Your container
        customValueInputsContainer.innerHTML = ''; // Clear previous inputs
        
        // Create input fields for each missing column
        missingColumns.forEach((column, index) => {
            const label = document.createElement('label');
            label.innerText = `Enter value for ${column}: `;
    
            const inputField = document.createElement('input');
            inputField.setAttribute('type', 'text');
            inputField.setAttribute('id', `custom-value-${index}`); // Unique id for each input
            inputField.setAttribute('data-column-index', index); // Store the column index as data attribute
            
            customValueInputsContainer.appendChild(label);
            customValueInputsContainer.appendChild(inputField);
            customValueInputsContainer.appendChild(document.createElement('br')); // Line break for better layout
        });
    
        console.log('Custom input fields:', document.querySelectorAll('input[type="text"]')); // Debug: Check if inputs exist
    }
    function collectCustomValues() {
        const inputs = document.querySelectorAll('#custom-value-input input'); // Select inputs by container ID
        const customValues = {};
        
        inputs.forEach(input => {
            const columnName = input.id.replace('custom_value_', ''); // Extract column name
            customValues[columnName] = input.value.trim() || ''; 
        });

        console.log('Collected custom values:', customValues); // Debugging log
        return customValues;
    }
    
    applyButton.addEventListener('click', function() {
        const selectedStrategy = strategySelect.value; 
        const customValues = collectCustomValues(); 
     
        if (selectedStrategy === 'fill_custom' && Object.values(customValues).some(value => value === '')) {
            alert('Please enter valid custom values.');
            return;
        }
     
        console.log('Custom Values:', customValues); 
     
        handleMissingValues(selectedStrategy, customValues);
        currentOperation = "Handling Missing Data"; // Ensure this is set when the operation starts
        renderUpdatedData(parsedCSVData);
    });
    

    /**
     * Function to generate dynamic input fields for each column with missing values
     */
    function generateCustomValueInputs() {
        customValueInputContainer.innerHTML = ''; // Clear previous inputs
        const missingColumns = findMissingColumns(parsedCSVData); // Identify missing columns
        
        if (missingColumns.length > 0) {
            missingColumns.forEach((colName) => {
                const inputWrapper = document.createElement('div');
                const label = document.createElement('label');
                label.textContent = `Enter custom value for "${colName}":`;
                const input = document.createElement('input');
                input.type = 'text';
                input.id = `custom_value_${colName}`; // Use clear and identifiable ID
                input.classList.add('custom_value_input');
                inputWrapper.appendChild(label);
                inputWrapper.appendChild(input);
                customValueInputContainer.appendChild(inputWrapper);
            });
        }
    }
    

    /**
     * Function to find columns with missing values
     * (You should implement this to return an array of column names that contain missing data)
     */
    function findMissingColumns(data) {
        const missingColumns = new Set();
        const headerRow = data[0]; // First row contains column names

        for (let i = 1; i < data.length; i++) {
            const row = data[i];
            row.forEach((value, index) => {
                if (value === null || value === undefined || value === '') {
                    missingColumns.add(headerRow[index]);
                }
            });
        }

        return Array.from(missingColumns); // Return as an array of column names
    }
    function removeDuplicates(arr) {
        if (!arr || arr.length === 0) {
            console.error("Array is undefined or empty");
            return [];
        }
        
        console.log('Before removing duplicates:', arr);  // Log the data before duplicates removal
        
        const uniqueData = arr.filter((value, index, self) => 
            self.findIndex((row) => JSON.stringify(row) === JSON.stringify(value)) === index
        );
        
        console.log('After removing duplicates:', uniqueData);  // Log the data after duplicates removal
        parsedCSVData = uniqueData;
        return uniqueData;

    }
    
    /**
     * Function to handle missing values based on the selected strategy
     * @param {string} strategy - The selected strategy (fill_custom, drop_rows)
     * @param {Array} customValues - Custom values entered for each column (if applicable)
     */
    function handleMissingValues(strategy, customValues) {
        // Remove the re-declaration of 'strategy'
        if (!strategy || strategy === "invalid") {
            console.error("Invalid strategy selected.");
            return; // Exit early if the strategy is invalid
        }
        switch (strategy) {
            case 'fill_custom':
                console.log('Filling missing values with Custom Values...');
                fillMissingValuesWithCustom(parsedCSVData, customValues);  // Pass custom values for each column
                break;
            case 'drop_rows':
                console.log('Dropping rows with missing values...');
                dropRowsWithMissingValues(parsedCSVData);
                break;
            default:
                console.error('Invalid strategy selected.');
        }
    
        // After handling missing values, proceed to remove duplicates
        
        
    
        renderUpdatedData(parsedCSVData,'updatedDataMissing');
        document.getElementById("removeDuplicatesOptions").style.display = "block";
    }
    
    // Function to fill missing values with custom values provided by the user
    function fillMissingValuesWithCustom(data, customValues) {
        for (let i = 1; i < data.length; i++) { 
            const row = data[i];
            row.forEach((value, colIndex) => {
                const columnName = data[0][colIndex]; 
                if ((value === '' || value === null) && customValues[columnName]) { 
                    row[colIndex] = customValues[columnName]; 
                }
            });
        }
        renderUpdatedData(data); 
    }
    
    
    
    
    
    // Function to drop rows that contain any missing values
    function dropRowsWithMissingValues(data) {
        console.log('Before drop:', data);
        const updatedData = [data[0]]; // Keep the headers
        for (let i = 1; i < data.length; i++) {
            const row = data[i];
            if (!row.includes('') && !row.includes(null)) {
                updatedData.push(row);
            }
        }
        parsedCSVData = updatedData; // Update the global parsed CSV data
        console.log('After drop:', parsedCSVData);
        renderUpdatedData(parsedCSVData);
    }

    // Function to render updated data (to be used after applying any missing data handling)
    

    // Render rows for updated data
    

// Function to render updated data (re-render the table after changes)
function renderUpdatedData(data, containerId) {
    console.log("Container ID:", containerId);  // Debugging step to check if it's valid
    const updatedDataContainer = document.getElementById(containerId);
    if (!updatedDataContainer) {
        console.error(`Element with ID '${containerId}' not found.`);
        return;
    }
    updatedDataContainer.innerHTML = '';
    const table = document.createElement('table');
    const tableBody = document.createElement('tbody');
    table.appendChild(tableBody);
    updatedDataContainer.appendChild(table);
    renderRows(data, 0, data.length, tableBody);
}



// Function to render rows into a table
function renderRows(data, startIndex, endIndex, tableBody) {
    const rows = data.slice(startIndex, endIndex);
    rows.forEach((row) => {
        const tr = document.createElement('tr');
        row.forEach((cell) => {
            const td = document.createElement('td');
            td.textContent = cell;
            tr.appendChild(td);
        });
        tableBody.appendChild(tr);
    });
}

removeDuplicatesBtn.addEventListener('click', function() {
    const data = parsedCSVData;
    const uniqueData = removeDuplicates(data);
    renderUpdatedData(uniqueData, 'updatedDataDuplicates');
    currentOperation = "Removing Duplicates";  // Ensure the currentOperation is updated before render
});
downloadCSVButton.addEventListener('click', function() {
    if (parsedCSVData.length === 0) {
        alert('No data to download.');
        return;
    }

    const csvContent = generateCSV(parsedCSVData);
    const filename = `Updated Data (After ${currentOperation}).csv`;

    console.log("Current operation:", currentOperation);  // Debug: Check if currentOperation is set
    console.log("CSV Content:", csvContent);  // Debug: Check generated CSV content

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.setAttribute('href', URL.createObjectURL(blob));
    link.setAttribute('download', filename); // Use dynamic filename
    link.click(); // Trigger the download
});


function generateCSV(data) {
    return data.map(row => {
        return row.map(cell => {
            if (cell && (cell.includes(',') || cell.includes('"') || cell.includes('\n'))) {
                return `"${cell.replace(/"/g, '""')}"`;
            }
            return cell;
        }).join(',');
    }).join('\n');
}


});

// document.getElementById('downloadCSVButton').addEventListener('click', function() {
//     if (parsedCSVData.length === 0) {
//         alert('No data to download.');
//         return;
//     }
    
//     const csvContent = generateCSV(parsedCSVData);

//     // Determine the filename dynamically based on the operation being performed
//     const operation = "Handling Missing Data";  // Change this based on your operation
//     const filename = `Updated Data (After ${operation}).csv`;

//     const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
//     const link = document.createElement('a');
//     link.setAttribute('href', URL.createObjectURL(blob));
//     link.setAttribute('download', filename); // Use dynamic filename
//     link.click(); // Trigger the download
// });

// function generateCSV(data) {
//     return data.map(row => {
//         return row.map(cell => {
//             if (cell && (cell.includes(',') || cell.includes('"') || cell.includes('\n'))) {
//                 return `"${cell.replace(/"/g, '""')}"`;
//             }
//             return cell;
//         }).join(',');
//     }).join('\n');
// }

