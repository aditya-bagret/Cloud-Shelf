// Initialize global variables
let currentPage = 1;
let totalPages = 0;
let pdfDoc = null;

function initializePDF() {
    const iframe = document.getElementById('pdfFrame');
    const pdfUrl = iframe.src;

    // Attempt to use PDF.js to get page count (optional, as iframe viewers handle this)
    pdfjsLib.getDocument(pdfUrl).promise.then(function (pdf) {
        pdfDoc = pdf;
        totalPages = pdf.numPages;
        updatePageNumber();
        iframe.contentWindow.postMessage({ type: 'setPage', pageNumber: currentPage }, '*'); // Attempt to set page
    }).catch(function (error) {
        console.error("Error loading PDF with PDF.js:", error);
        // Fallback: Rely on iframe's native viewer
        totalPages = 1; // Default if PDF.js fails
        updatePageNumber();
    });

    // Add loading state
    const pdfViewer = document.querySelector('.pdf-viewer');
    pdfViewer.classList.add('loading');

    iframe.addEventListener('load', function () {
        pdfViewer.classList.remove('loading');
        // Optional: Try to control page via iframe (browser-dependent)
        try {
            iframe.contentWindow.postMessage({ type: 'setPage', pageNumber: currentPage }, '*');
        } catch (e) {
            console.warn("Page control via iframe not supported:", e);
        }
    });
}

// Function to go to the next page
function nextPage() {
    if (currentPage < totalPages) {
        currentPage++;
        updatePageNumber();
        const iframe = document.getElementById('pdfFrame');
        iframe.contentWindow.postMessage({ type: 'setPage', pageNumber: currentPage }, '*');
    }
}

// Function to go to the previous page
function prevPage() {
    if (currentPage > 1) {
        currentPage--;
        updatePageNumber();
        const iframe = document.getElementById('pdfFrame');
        iframe.contentWindow.postMessage({ type: 'setPage', pageNumber: currentPage }, '*');
    }
}

// Function to update the page number displayed on the screen
function updatePageNumber() {
    const pageNumberElement = document.getElementById('pageNumber');
    const prevButton = document.getElementById('prevPageBtn');
    const nextButton = document.getElementById('nextPageBtn');

    pageNumberElement.innerText = Page ${currentPage} of ${totalPages};
    prevButton.disabled = currentPage === 1;
    nextButton.disabled = currentPage === totalPages;
}

// Call the initializePDF function once the page is loaded
document.addEventListener('DOMContentLoaded', function () {
    initializePDF();
});

// Optional: Add wheel event listener for navigation
document.getElementById('pdfFrame').addEventListener('wheel', function (event) {
    const pdfViewer = document.querySelector('.pdf-viewer');
    if (event.deltaY > 0 && !pdfViewer.classList.contains('loading')) {
        nextPage();
    } else if (event.deltaY < 0 && !pdfViewer.classList.contains('loading')) {
        prevPage();
    }
});