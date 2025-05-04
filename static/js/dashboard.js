// Toggle profile panel
function toggleProfile(event) {
  event.stopPropagation();  // Prevent unintended closing
  const panel = document.getElementById('profilePanel');
  panel.classList.toggle('show');
}

// Close profile panel when clicking outside
document.addEventListener('click', function(event) {
  const panel = document.getElementById('profilePanel');
  const profileIcon = document.querySelector('.profile-icon');

  if (panel && !panel.contains(event.target) && !profileIcon.contains(event.target)) {
      panel.classList.remove('show');
  }
});

// Make first nav button active by default
document.addEventListener('DOMContentLoaded', function() {
  const navButtons = document.querySelectorAll('.nav-btn');
  if (navButtons.length > 0) {
      navButtons[0].classList.add('active');
  }

  // Add active state to clicked nav button
  navButtons.forEach(button => {
      button.addEventListener('click', function() {
          navButtons.forEach(btn => btn.classList.remove('active'));
          this.classList.add('active');
      });
  });

  // Add mobile menu toggle for responsive design
  const topBar = document.querySelector('.top-bar');
  if (topBar) {
      const toggleSidebarBtn = document.createElement('button');
      toggleSidebarBtn.classList.add('toggle-sidebar');
      toggleSidebarBtn.innerHTML = '<span></span><span></span><span></span>';
      toggleSidebarBtn.style.cssText = `
          background: none;
          border: none;
          display: none;
          flex-direction: column;
          justify-content: space-between;
          height: 20px;
          width: 26px;
          cursor: pointer;
          margin-right: 15px;
      `;

      toggleSidebarBtn.querySelectorAll('span').forEach(span => {
          span.style.cssText = `
              height: 2px;
              background-color: var(--text);
              width: 100%;
              border-radius: 2px;
              transition: all 0.3s ease;
          `;
      });

      topBar.prepend(toggleSidebarBtn);

      // Show toggle button on mobile
      const mediaQuery = window.matchMedia('(max-width: 768px)');
      function handleMobileChange(e) {
          toggleSidebarBtn.style.display = e.matches ? 'flex' : 'none';
      }
      handleMobileChange(mediaQuery);
      mediaQuery.addEventListener('change', handleMobileChange);

      // Toggle sidebar on mobile
      toggleSidebarBtn.addEventListener('click', function() {
          document.querySelector('.sidebar').classList.toggle('show');
      });
  }

  // Enable "Enter" key functionality for search
  let searchInput = document.getElementById("dashboard-search-input");
  if (searchInput) {
      searchInput.addEventListener("keypress", function(event) {
          if (event.key === "Enter") {
              event.preventDefault();
              searchBook("dashboard-search-input");
          }
      });
  }
});

// Function to show book suggestions
function showSuggestions(inputId, suggestionsBoxId) {
  let input = document.getElementById(inputId).value;
  let suggestionsBox = document.getElementById(suggestionsBoxId);

  if (input.length < 2) {
      suggestionsBox.innerHTML = "";
      return;
  }

  fetch(`/search_suggestions?q=${input}`)
      .then(response => response.json())
      .then(data => {
          suggestionsBox.innerHTML = "";
          data.forEach(book => {
              let suggestion = document.createElement("div");
              suggestion.classList.add("suggestion-item");
              suggestion.textContent = book.title;
              suggestion.onclick = function () {
                  document.getElementById(inputId).value = book.title;
                  suggestionsBox.innerHTML = "";
              };
              suggestionsBox.appendChild(suggestion);
          });
      });

  // Close suggestions when clicking outside
  document.addEventListener("click", function (event) {
      if (!document.getElementById(inputId).contains(event.target) && 
          !suggestionsBox.contains(event.target)) {
          suggestionsBox.innerHTML = "";
      }
  });
}

// Function to handle search and redirect
function searchBook(inputId) {
  let query = document.getElementById(inputId).value;
  if (query.trim() !== "") {
      window.location.href = `/search_results?q=${encodeURIComponent(query)}`;
  }
}

// Settings button functionality
document.getElementById('settings-btn')?.addEventListener('click', function() {
  console.log('Settings clicked');
  // Implement settings functionality here
});

document.addEventListener('DOMContentLoaded', function () {
    // Existing code...
  
    let searchInput = document.getElementById("dashboard-search-input");
    if (searchInput) {
      searchInput.addEventListener("input", function () {
        showSuggestions("dashboard-search-input", "suggestions-box");
      });
  
      searchInput.addEventListener("keypress", function (event) {
        if (event.key === "Enter") {
          event.preventDefault();
          searchBook("dashboard-search-input");
        }
      });
    }
  });
  

  function showSuggestions(inputId, suggestionsBoxId) {
    let input = document.getElementById(inputId).value;
    let suggestionsBox = document.getElementById(suggestionsBoxId);
  
    if (input.length < 2) {
      suggestionsBox.innerHTML = "";
      suggestionsBox.classList.remove("active");
      return;
    }
  
    fetch(`/search_suggestions?q=${input}`)
      .then(response => response.json())
      .then(data => {
        suggestionsBox.innerHTML = "";
        if (data.length === 0) {
          suggestionsBox.classList.remove("active");
          return;
        }
  
        data.forEach(book => {
          let suggestion = document.createElement("div");
          suggestion.classList.add("suggestion-item");
          suggestion.textContent = book.title;
          suggestion.onclick = function () {
            document.getElementById(inputId).value = book.title;
            suggestionsBox.innerHTML = "";
            suggestionsBox.classList.remove("active");
          };
          suggestionsBox.appendChild(suggestion);
        });
  
        suggestionsBox.classList.add("active");
      });
  
    document.addEventListener("click", function (event) {
      if (
        !document.getElementById(inputId).contains(event.target) &&
        !suggestionsBox.contains(event.target)
      ) {
        suggestionsBox.innerHTML = "";
        suggestionsBox.classList.remove("active");
      }
    });
  }
  