document.addEventListener("DOMContentLoaded", function () {
    const searchInput = document.getElementById("search-input");
    const suggestionsBox = document.getElementById("suggestions-box");

    // Function to display search suggestions
    async function showSuggestions() {
        const query = searchInput.value.trim();
        if (query.length === 0) {
            suggestionsBox.innerHTML = "";
            return;
        }

        try {
            const response = await fetch(`/search_suggestions?q=${encodeURIComponent(query)}`);
            const results = await response.json();

            suggestionsBox.innerHTML = ""; // Clear previous suggestions

            if (results.length > 0) {
                results.forEach(book => {
                    const suggestionItem = document.createElement("div");
                    suggestionItem.classList.add("suggestion-item");
                    suggestionItem.textContent = book.title; // Assuming 'title' field in the database
                    suggestionItem.addEventListener("click", function () {
                        searchInput.value = book.title;
                        suggestionsBox.innerHTML = ""; // Hide suggestions after selection
                    });
                    suggestionsBox.appendChild(suggestionItem);
                });
                suggestionsBox.style.display = "block";
            } else {
                suggestionsBox.innerHTML = "<p>No results found</p>";
            }
        } catch (error) {
            console.error("Error fetching search suggestions:", error);
        }
    }

    // Attach function to input event
    searchInput.addEventListener("input", showSuggestions);

    // ✅ Make searchBook globally accessible
    window.searchBook = function () {
        const query = searchInput.value.trim();
        if (query) {
            window.location.href = `/search_results?q=${encodeURIComponent(query)}`;
        }
    };
});
