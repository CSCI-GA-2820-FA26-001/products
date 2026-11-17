(function () {
    "use strict";

    const ui = window.ProductsUI;
    const byId = (id) => document.getElementById(id);
    let saving = false;

    function enableReviewButtons() {
        byId("products_body")
            .querySelectorAll('button[data-action="review"]')
            .forEach((button) => {
                button.disabled = false;
                button.title = "View and add reviews";
            });
    }

    async function openReviews(id) {
        ui.clearMessage();
        try {
            // Load the product again so the dialog shows its latest reviews.
            const response = await fetch(ui.API_BASE_URL + "/" + id, {cache: "no-store"});
            if (response.status === 404) {
                throw new Error("Product was not found.");
            }
            if (!response.ok) {
                throw new Error("Unable to load the product's reviews.");
            }
            ui.openReviewDialog(await response.json());
        } catch (error) {
            ui.showMessage(error.message, "error");
        }
    }

    function initialize() {
        const body = byId("products_body");
        const form = byId("review-product-form");
        const button = byId("submit-feedback-btn");
        const dialog = byId("review-product-dialog");

        // Rows are re-rendered on every load, so enable Review each time.
        new MutationObserver(enableReviewButtons).observe(body, {childList: true});
        enableReviewButtons();

        body.addEventListener("click", (event) => {
            const review = event.target.closest('button[data-action="review"]');
            if (review) openReviews(review.dataset.productId);
        });

        form.noValidate = true;
        button.disabled = false;

        form.addEventListener("submit", async (event) => {
            event.preventDefault();
            if (saving) return;
            ui.clearMessage();
            const rating = byId("product_rating").value.trim();
            const text = byId("product_review_text").value;
            if (!/^[1-5]$/.test(rating)) {
                ui.showMessage("Rating must be a whole number from 1 to 5.", "error");
                return;
            }
            if (!text.trim()) {
                ui.showMessage("Review text must not be blank.", "error");
                return;
            }
            saving = true;
            button.disabled = true;
            try {
                const response = await fetch(
                    ui.API_BASE_URL + "/" + dialog.dataset.productId + "/comments",
                    {
                        method: "POST",
                        headers: {"Content-Type": "application/json"},
                        body: JSON.stringify({rating: Number(rating), text: text.trim()})
                    }
                );
                if (response.status === 404) {
                    throw new Error("Product was not found.");
                }
                if (!response.ok) {
                    const error = await response.json().catch(() => ({}));
                    throw new Error(error.message || "Unable to save the review.");
                }
                // Reload the product so the table shows every saved review.
                const refreshed = await fetch(
                    ui.API_BASE_URL + "/" + dialog.dataset.productId,
                    {cache: "no-store"}
                );
                if (!refreshed.ok) {
                    throw new Error("Product was not found.");
                }
                ui.renderFeedback((await refreshed.json()).reviews || []);
                form.reset();
                ui.showMessage("Review submitted successfully.", "success");
            } catch (error) {
                ui.showMessage(error.message, "error");
            } finally {
                saving = false;
                button.disabled = false;
            }
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initialize);
    } else {
        initialize();
    }
})();