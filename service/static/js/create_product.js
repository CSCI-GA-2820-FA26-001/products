(function () {
    "use strict";

    const ui = window.ProductsUI;
    const byId = (id) => document.getElementById(id);
    let saving = false;

    function initialize() {
        const form = byId("create-product-form");
        const button = byId("create-btn");
        form.noValidate = true;
        button.disabled = false;

        form.addEventListener("submit", async (event) => {
            event.preventDefault();
            if (saving) return;
            ui.clearMessage();
            const name = byId("create_product_name").value.trim();
            const price = byId("create_product_price").value.trim();
            if (!name || name.length > 63) {
                ui.showMessage("Name must contain 1 to 63 characters.", "error");
                return;
            }
            if (!price || !Number.isFinite(Number(price)) || Number(price) < 0) {
                ui.showMessage("Price must be a finite, non-negative number.", "error");
                return;
            }
            saving = true;
            button.disabled = true;
            try {
                const response = await fetch(ui.API_BASE_URL, {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({
                        name,
                        description: byId("create_product_description").value,
                        // Keep decimal precision in the request.
                        price
                    })
                });
                let product;
                try {
                    product = await response.json();
                } catch (_) {
                    throw new Error("The server returned an unreadable response.");
                }
                if (response.status !== 201) {
                    throw new Error(product.message || "Unable to create the product.");
                }
                ui.showProductDetails(product);
                ui.showMessage("Product created successfully.", "success");
                await window.ProductsList.loadProducts();
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
