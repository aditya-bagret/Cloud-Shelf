document.getElementById("search-input").addEventListener("input", function () {
    let input = this.value.trim();
    let suggestionsBox = document.getElementById("suggestions-box");

    if (input.length === 0) {
        suggestionsBox.style.display = "none";
        return;
    }

    // Fetch search suggestions
    fetch(`/search_suggestions?q=${encodeURIComponent(input)}`)
        .then(response => response.json())
        .then(data => {
            if (data.length > 0) {
                suggestionsBox.innerHTML = "<ul>" +
                    data.map(book => `<li onclick="selectSuggestion('${book.title}')">${book.title}</li>`).join('') +
                    "</ul>";
                suggestionsBox.style.display = "block"; // Show suggestions
            } else {
                suggestionsBox.style.display = "none"; // Hide if no match
            }
        })
        .catch(error => console.error("Error fetching suggestions:", error));
});

function selectSuggestion(book) {
    document.getElementById("search-input").value = book;
    document.getElementById("suggestions-box").style.display = "none"; // Hide suggestions
}

document.addEventListener("click", function (event) {
    let suggestionsBox = document.getElementById("suggestions-box");
    let searchInput = document.getElementById("search-input");

    if (event.target !== searchInput && event.target !== suggestionsBox) {
        suggestionsBox.style.display = "none";
    }
});


document.addEventListener("DOMContentLoaded", function () {
    const searchInput = document.getElementById("search-input");

    // ✅ Make searchBook globally accessible
    window.searchBook = function () {
        const query = searchInput.value.trim();
        if (query) {
            window.location.href = `/search_results?q=${encodeURIComponent(query)}`;
        }
    };
});
