(function () {
    "use strict";

    const ui = window.ProductsUI;
    const byId = (id) => document.getElementById(id);
    const REQUEST_TIMEOUT_MS = 20000;

    let requestNumber = 0;
    let activeController = null;

    function clearDetails() {
        byId("product_details").hidden = true;

        ["id", "name", "description", "price"].forEach((field) => {
            byId("detail_product_" + field).textContent = "";
        });
    }

    function showReadError(message) {
        const dialog = byId("retrieve-product-dialog");

        clearDetails();
        dialog.dataset.state = "error";
        dialog.setAttribute("aria-busy", "false");

        ui.showMessage(message, "error");
    }

    function cancelRequest() {
        requestNumber += 1;

        if (activeController) {
            activeController.abort();
            activeController = null;
        }

        const dialog = byId("retrieve-product-dialog");

        dialog.setAttribute("aria-busy", "false");
        dialog.dataset.state = "idle";
    }

    async function readProduct(productId) {
        const currentRequest = ++requestNumber;

        if (activeController) {
            activeController.abort();
            activeController = null;
        }

        ui.openDialog("retrieve-product-dialog");
        clearDetails();

        const dialog = byId("retrieve-product-dialog");
        const id = String(productId ?? "");

        if (
            !/^[1-9]\d*$/.test(id)
            || !Number.isSafeInteger(Number(id))
        ) {
            showReadError("Please select a valid product.");
            return;
        }

        const controller = new AbortController();
        activeController = controller;

        dialog.dataset.state = "loading";
        dialog.setAttribute("aria-busy", "true");
        ui.showMessage("Loading product...", "info");

        const timeout = window.setTimeout(() => {
            controller.abort();
        }, REQUEST_TIMEOUT_MS);

        try {
            const response = await fetch(
                ui.API_BASE_URL + "/" + encodeURIComponent(id),
                {
                    method: "GET",
                    headers: {
                        Accept: "application/json"
                    },
                    cache: "no-store",
                    signal: controller.signal
                }
            );

            if (currentRequest !== requestNumber || !dialog.open) {
                return;
            }

            if (response.status === 404) {
                throw new Error("Product not found.");
            }

            if (!response.ok) {
                throw new Error(
                    "Unable to load product (HTTP "
                    + response.status
                    + ")."
                );
            }

            const product = await response.json();

            if (currentRequest !== requestNumber || !dialog.open) {
                return;
            }

            if (
                !product
                || Array.isArray(product)
                || String(product.id) !== id
                || typeof product.name !== "string"
                || typeof product.description !== "string"
                || !["string", "number"].includes(typeof product.price)
            ) {
                throw new Error(
                    "The server returned invalid product details."
                );
            }

            ui.showProductDetails(product);
        } catch (error) {
            if (currentRequest !== requestNumber || !dialog.open) {
                return;
            }

            showReadError(
                error.name === "AbortError"
                    ? "Loading product timed out. Please try again."
                    : error.message || "Unable to load product. Please try again."
            );
        } finally {
            window.clearTimeout(timeout);

            if (currentRequest === requestNumber) {
                activeController = null;
                dialog.setAttribute("aria-busy", "false");
            }
        }
    }

    function initialize() {
        const body = byId("products_body");

        body.addEventListener("click", (event) => {
            const button = event.target.closest(
                "button[data-action='retrieve']"
            );

            if (
                !button
                || !body.contains(button)
                || button.disabled
            ) {
                return;
            }

            readProduct(button.dataset.productId);
        });

        byId("retrieve-product-dialog").addEventListener(
            "close",
            cancelRequest
        );
    }

    window.ProductsRead = Object.freeze({
        readProduct
    });

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initialize);
    } else {
        initialize();
    }
})();