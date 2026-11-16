(function () {
    "use strict";

    const ui = window.ProductsUI;
    const byId = (id) => document.getElementById(id);
    let deleting = false;

    function enableDeleteButtons() {
        byId("products_body")
            .querySelectorAll('button[data-action="delete"]')
            .forEach((button) => {
                button.disabled = false;
                button.title = "Delete this product";
            });
    }

    function clearStaleDetails(id) {
        if (byId("detail_product_id").textContent === id) {
            ["id", "name", "description", "price"].forEach((field) => {
                byId("detail_product_" + field).textContent = "";
            });
        }
        if (byId("product_id").value === id) {
            byId("update-product-form").reset();
        }
        const review = byId("review-product-dialog");
        if (review.dataset.productId === id) {
            delete review.dataset.productId;
            byId("review_product_label").textContent = "";
            byId("feedback_body").replaceChildren();
        }
    }

    function initialize() {
        const body = byId("products_body");

        // Rows are re-rendered on every load, so enable Delete each time.
        new MutationObserver(enableDeleteButtons).observe(body, {childList: true});
        enableDeleteButtons();

        body.addEventListener("click", async (event) => {
            const button = event.target.closest('button[data-action="delete"]');
            if (!button || deleting) return;
            ui.clearMessage();
            const id = button.dataset.productId || "";
            if (!/^[1-9]\d*$/.test(id)) {
                ui.showMessage("Product ID is missing or invalid.", "error");
                return;
            }
            deleting = true;
            button.disabled = true;
            try {
                const response = await fetch(ui.API_BASE_URL + "/" + id, {method: "DELETE"});
                // The API returns 204 for unknown or already deleted IDs too.
                if (response.status !== 204) {
                    throw new Error("Unable to delete the product.");
                }
                clearStaleDetails(id);
                await window.ProductsList.loadProducts();
                ui.showMessage("Product deleted successfully.", "success");
            } catch (error) {
                ui.showMessage(error.message, "error");
                button.disabled = false;
            } finally {
                deleting = false;
            }
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initialize);
    } else {
        initialize();
    }
})();