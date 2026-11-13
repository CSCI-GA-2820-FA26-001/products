(function () {
    "use strict";

    const ui = window.ProductsUI;
    const byId = (id) => document.getElementById(id);
    let loading = false;
    let saving = false;

    async function requestProduct(id, options) {
        const response = await fetch(ui.API_BASE_URL + "/" + encodeURIComponent(id), options);
        let data;
        try {
            data = await response.json();
        } catch (_) {
            throw new Error("The server returned an unreadable response. Please try again.");
        }
        if (!response.ok) {
            throw new Error(response.status === 404
                ? "Product not found. It may have been deleted."
                : (data.message || "Unable to update the product. Please try again."));
        }
        return data;
    }

    function initialize() {
        const form = byId("update-product-form");
        const dialog = byId("update-product-dialog");
        const save = byId("update-btn");
        // Show validation errors in the dialog.
        form.noValidate = true;
        save.disabled = false;

        byId("products_body").addEventListener("click", async (event) => {
            const button = event.target.closest('button[data-action="update"]');
            if (!button || button.disabled || loading || saving) return;
            loading = true;
            button.disabled = true;
            ui.clearMessage();
            try {
                const product = await requestProduct(button.dataset.productId);
                ui.openUpdateDialog(product);
            } catch (error) {
                ui.showMessage(error.message, "error");
            } finally {
                loading = false;
                button.disabled = false;
            }
        });

        form.addEventListener("submit", async (event) => {
            event.preventDefault();
            if (saving) return;
            ui.clearMessage();
            const id = dialog.dataset.productId;
            const name = byId("product_name").value.trim();
            const price = byId("product_price").value.trim();
            if (!id) {
                ui.showMessage("Select a product to update first.", "error");
                return;
            }
            if (!name || name.length > 63) {
                ui.showMessage("Name must contain 1 to 63 characters.", "error");
                return;
            }
            if (!price || !Number.isFinite(Number(price)) || Number(price) < 0) {
                ui.showMessage("Price must be a finite, non-negative number.", "error");
                return;
            }
            saving = true;
            save.disabled = true;
            try {
                const product = await requestProduct(id, {
                    method: "PUT",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({
                        name,
                        description: byId("product_description").value,
                        // Keep the price as a string to preserve precision.
                        price
                    })
                });
                ui.updateForm(product);
                const row = byId("product-" + id);
                if (row) {
                    row.querySelector('[data-action="retrieve"]').textContent = product.name;
                    row.cells[2].textContent = product.description;
                    row.cells[3].textContent = product.price;
                }
                ui.showMessage("Product updated successfully.", "success");
            } catch (error) {
                ui.showMessage(error.message, "error");
            } finally {
                saving = false;
                save.disabled = false;
            }
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initialize);
    } else {
        initialize();
    }
})();
