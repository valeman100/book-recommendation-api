function showSection(section) {
    // Hide all sections
    document.querySelectorAll('.dashboard-section, .history-section, .account-section, .plan-section, .logout-section').forEach(sec => {
        sec.classList.remove('show');
    });
    // Show the selected section
    document.getElementById(section).classList.add('show');
}

async function recommendation(input, user_id) {
    const file = input.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function (e) {
        const uploadedImage = document.getElementById("uploadedImage");
        uploadedImage.src = e.target.result;
        uploadedImage.style.display = "block";
        uploadedImage.style.margin = "auto";
        uploadedImage.style.maxWidth = "100%"; // Ensure image does not exceed the width of its container
        uploadedImage.style.maxHeight = "100vw"; // Ensure image does not exceed the height of the viewport
        uploadedImage.style.objectFit = "contain"; // Maintain aspect ratio
    };
    reader.readAsDataURL(file);

    // Create FormData for the request
    const formData = new FormData();
    formData.append('image', file);  // The form field is 'image' based on your curl example

    try {
        const response = await fetch(`http://localhost:3000/my-bookshelf/get-recommendation/${user_id}`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`Network response was not ok: ${response.statusText}`);
        }

        const data = await response.json();
        displayResults(data);

    } catch (error) {
        console.error('Error:', error);
        alert("Failed to call API. Please try again.");
    }
}

function displayResults(data) {
    const apiResultText = document.getElementById("apiResultText");
    const recommendedBooks = document.getElementById("recommendedBooks");

    // Clear previous results
    recommendedBooks.innerHTML = "";

    // Handle case where no recommendations are found
    if (!data.recommended_books || data.recommended_books.length === 0) {
        apiResultText.innerHTML = "No recommendations found.";
        return;
    }

    // Set header text for recommendations bold big text
    apiResultText.innerHTML = "Recommended Books:";
    apiResultText.style.fontWeight = "bold";
    apiResultText.style.fontSize = "1.5rem";
    apiResultText.style.marginBottom = "10px";

    // Iterate over each recommended book and create its display card
    data.recommended_books.forEach((book) => {
        const bookDiv = document.createElement("div");
        bookDiv.classList.add("book-card");
        bookDiv.style.border = "1px solid #ddd";
        bookDiv.style.borderRadius = "8px";
        bookDiv.style.padding = "10px";
        bookDiv.style.margin = "10px 0";
        bookDiv.style.textAlign = "left";
        bookDiv.style.boxShadow = "0 2px 4px rgba(0, 0, 0, 0.1)";

        // Create book title
        const title = document.createElement("h3");
        title.textContent = book.title;
        title.style.marginBottom = "5px";

        // Create author text
        const author = document.createElement("p");
        author.innerHTML = `<strong>Author:</strong> ${book.author}`;
        author.style.marginBottom = "5px";

        // Create description text
        const description = document.createElement("p");
        description.innerHTML = `<strong>Description:</strong> ${book.description}`;

        // Append title, author, and description to the book card
        bookDiv.appendChild(title);
        bookDiv.appendChild(author);
        bookDiv.appendChild(description);

        // Append book card to the container
        recommendedBooks.appendChild(bookDiv);
    });

    // Ensure the section is visible
    showSection("dashboard");

}


