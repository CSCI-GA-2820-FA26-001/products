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

    function initialize() {
        const body = byId("products_body");

        // Rows are re-rendered on every load, so enable Delete each time.
        new MutationObserver(enableDeleteButtons).observe(body, {childList: true});
        enableDeleteButtons();

        body.addEventListener("click", async (event) => {
            const button = event.target.closest('button[data-action="delete"]');
            if (!button || deleting) return;
            ui.clearMessage();
            deleting = true;
            button.disabled = true;
            try {
                const response = await fetch(
                    ui.API_BASE_URL + "/" + button.dataset.productId,
                    {method: "DELETE"}
                );
                if (response.status !== 204) {
                    throw new Error("Unable to delete the product.");
                }
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