function showSection(section) {
    // Hide all sections
    document.querySelectorAll('.dashboard-section, .history-section, .account-section, .plan-section').forEach(sec => {
        sec.classList.remove('show');
    });
    // Show the selected section
    document.getElementById(section).classList.add('show');
}

async function callApi(input) {
    const file = input.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('YOUR_API_ENDPOINT_HERE', {
            method: 'POST',
            body: formData
        });
        if (!response.ok) throw new Error('Network response was not ok');
        const data = await response.json();
        displayResults(data);
    } catch (error) {
        console.error('Error:', error);
        alert("Failed to call API. Please try again.");
    }
}

function displayResults(data) {
    const resultsList = document.getElementById('apiResultsList');

    // Clear previous results
    resultsList.innerHTML = '';

    // Assuming data is an array of results
    data.forEach(item => {
        const listItem = document.createElement('li');
        listItem.textContent = item.name; // Change according to your data structure
        resultsList.appendChild(listItem);
    });
}