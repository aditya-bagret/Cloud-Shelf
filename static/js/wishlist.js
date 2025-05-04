document.addEventListener("DOMContentLoaded", function () {
    const wishlistHeart = document.getElementById("wishlist-heart");
    if (!wishlistHeart) return;

    wishlistHeart.addEventListener("click", function () {
        if (this.classList.contains("disabled")) return;
        this.classList.add("disabled");
        const isAdded = this.classList.contains("added");

        if (isAdded) {
            removeFromWishlist().finally(() => this.classList.remove("disabled"));
        } else {
            addToWishlist().finally(() => this.classList.remove("disabled"));
        }
    });

    function showToast(message) {
        let toast = document.querySelector(".toast");
        if (!toast) {
            toast = document.createElement("div");
            toast.className = "toast";
            document.body.appendChild(toast);
        }
        toast.textContent = message;
        toast.classList.add("show");
        setTimeout(() => {
            toast.classList.remove("show");
        }, 2000);
    }

    function addToWishlist() {
        const bookId = wishlistHeart.getAttribute("data-book-id");
        return fetch(`/wishlist/add/${bookId}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            }
        })
            .then(response => {
                if (!response.ok) throw new Error("Network response was not ok");
                return response.json();
            })
            .then(data => {
                wishlistHeart.classList.add("added");
                wishlistHeart.querySelector("i").classList.replace("fa-regular", "fa-solid");
                showToast("Added to wishlist");
            })
            .catch(error => {
                showToast("Error adding to wishlist");
                console.error("Error:", error);
            });
    }

    function removeFromWishlist() {
        const bookId = wishlistHeart.getAttribute("data-book-id");
        return fetch(`/wishlist/remove/${bookId}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            }
        })
            .then(response => {
                if (!response.ok) throw new Error("Network response was not ok");
                return response.json();
            })
            .then(data => {
                wishlistHeart.classList.remove("added");
                wishlistHeart.querySelector("i").classList.replace("fa-solid", "fa-regular");
                showToast("Removed from wishlist");
            })
            .catch(error => {
                showToast("Error removing from wishlist");
                console.error("Error:", error);
            });
    }
});