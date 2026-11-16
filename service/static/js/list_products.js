(function () {
    "use strict";

    const ui = window.ProductsUI;
    const byId = (id) => document.getElementById(id);
    const REQUEST_TIMEOUT_MS = 20000;

    let requestNumber = 0;
    let activeController = null;

    async function loadProducts() {
        const currentRequest = ++requestNumber;

        if (activeController) {
            activeController.abort();
        }

        const controller = new AbortController();
        activeController = controller;

        const results = byId("search_results");
        const status = byId("results_status");
        const body = byId("products_body");

        results.setAttribute("aria-busy", "true");

        status.dataset.state = "loading";
        status.className = "";
        status.setAttribute("role", "status");
        status.textContent = "Loading products...";

        // An old result must not appear to be this request's result.
        body.replaceChildren();

        const timeout = window.setTimeout(() => {
            controller.abort();
        }, REQUEST_TIMEOUT_MS);

        try {
            // No query parameters: the API returns the complete catalog.
            const response = await fetch(ui.API_BASE_URL, {
                method: "GET",
                headers: {
                    Accept: "application/json"
                },
                cache: "no-store",
                signal: controller.signal
            });

            if (currentRequest !== requestNumber) {
                return;
            }

            if (!response.ok) {
                throw new Error(
                    "The server returned HTTP " + response.status + "."
                );
            }

            const products = await response.json();

            if (currentRequest !== requestNumber) {
                return;
            }

            if (!Array.isArray(products)) {
                throw new Error(
                    "The server returned an invalid product list."
                );
            }

            // The shared renderer replaces rows and handles empty arrays.
            ui.renderProducts(products);
        } catch (error) {
            // A newer request owns the UI after a reset or refresh.
            if (currentRequest !== requestNumber) {
                return;
            }

            body.replaceChildren();

            status.dataset.state = "error";
            status.className = "alert alert-danger";
            status.setAttribute("role", "alert");

            status.textContent = error.name === "AbortError"
                ? "Loading products timed out. Use Reset filters to try again."
                : "Unable to load products. Use Reset filters to try again.";
        } finally {
            window.clearTimeout(timeout);

            if (currentRequest === requestNumber) {
                results.setAttribute("aria-busy", "false");
                activeController = null;
            }
        }
    }

    function initialize() {
        // rest_api.js already resets the form and clears messages.
        byId("reset-search-btn").addEventListener(
            "click",
            loadProducts
        );

        // Show the complete catalog without requiring a search.
        loadProducts();
    }

    window.ProductsList = Object.freeze({
        loadProducts
    });

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initialize);
    } else {
        initialize();
    }
})();