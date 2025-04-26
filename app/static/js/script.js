const uploadBtn = document.getElementById('uploadBtn');
const formatBtn = document.getElementById('formatBtn');
const downloadBtn = document.getElementById('downloadBtn');
const jsonPreview = document.getElementById('jsonPreview');
const formattedPreview = document.getElementById('formattedPreview');

let jsonData = null; // Holds the uploaded JSON

uploadBtn.addEventListener('click', () => {
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = '.json';
    fileInput.click();

    fileInput.onchange = (e) => {
        const file = e.target.files[0];
        const reader = new FileReader();
        
        reader.onload = () => {
            jsonData = JSON.parse(reader.result);
            jsonPreview.textContent = JSON.stringify(jsonData, null, 2); // Preview the uploaded JSON
        };
        
        reader.readAsText(file);
    };
});

formatBtn.addEventListener('click', () => {
    if (!jsonData) {
        alert('Please upload a JSON file first.');
        return;
    }

    // Call the Flask backend to format the JSON
    fetch('/format-json', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ json: jsonData })
    })
    .then(response => response.json())
    .then(data => {
        formattedPreview.textContent = JSON.stringify(data, null, 2); // Preview the formatted JSON
    })
    .catch(error => {
        alert('Error formatting JSON');
        console.error(error);
    });
});

downloadBtn.addEventListener('click', () => {
    if (!formattedPreview.textContent) {
        alert('No formatted JSON to download.');
        return;
    }

    const blob = new Blob([formattedPreview.textContent], { type: 'application/json' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'formatted_output.json';  // The filename for the download
    link.click();
});
