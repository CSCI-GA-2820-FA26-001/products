(function () {
    "use strict";

    const ui = window.ProductsUI;
    const byId = (id) => document.getElementById(id);
    const REQUEST_TIMEOUT_MS = 20000;

    const PRICE_FIELDS = [
        {
            id: "search_min_price",
            key: "min_price",
            label: "Minimum price"
        },
        {
            id: "search_max_price",
            key: "max_price",
            label: "Maximum price"
        }
    ];

    const DECIMAL_PATTERN =
        /^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$/;

    let requestNumber = 0;
    let activeController = null;

    function cancelActiveRequest() {
        requestNumber += 1;

        if (activeController) {
            activeController.abort();
            activeController = null;
        }

        return requestNumber;
    }

    function clearValidation() {
        PRICE_FIELDS.forEach((field) => {
            byId(field.id).setAttribute("aria-invalid", "false");
            byId(field.id + "_error").textContent = "";
        });
    }

    function setStatus(state, message) {
        const status = byId("results_status");
        const isError = state === "invalid" || state === "error";

        status.dataset.state = state;
        status.className = isError ? "alert alert-danger" : "";
        status.setAttribute("role", isError ? "alert" : "status");
        status.textContent = message;
    }

    function readFilters() {
        const filters = {};
        const errors = [];
        const name = byId("search_name").value.trim();

        if (name !== "") {
            filters.name = name;
        }

        PRICE_FIELDS.forEach((field) => {
            const value = byId(field.id).value.trim();

            if (value === "") {
                return;
            }

            const amount = Number(value);

            if (
                !DECIMAL_PATTERN.test(value)
                || !Number.isFinite(amount)
                || amount < 0
            ) {
                errors.push({
                    id: field.id,
                    message:
                        field.label
                        + " must be a finite, non-negative number."
                });
                return;
            }

            // Preserve the entered decimal string in the request.
            filters[field.key] = value;
        });

        if (
            filters.min_price !== undefined
            && filters.max_price !== undefined
            && Number(filters.min_price) > Number(filters.max_price)
        ) {
            errors.push({
                id: "search_max_price",
                message:
                    "Maximum price must be greater than or equal to minimum price."
            });
        }

        return { filters, errors };
    }

    function showValidationErrors(errors) {
        cancelActiveRequest();

        byId("products_body").replaceChildren();
        byId("search_results").setAttribute("aria-busy", "false");

        setStatus("invalid", "Please correct the search filters.");

        errors.forEach((error) => {
            byId(error.id).setAttribute("aria-invalid", "true");
            byId(error.id + "_error").textContent = error.message;
        });

        byId(errors[0].id).focus();
    }

    async function loadProducts(filters = {}) {
        const currentRequest = cancelActiveRequest();
        const controller = new AbortController();

        activeController = controller;
        clearValidation();

        const results = byId("search_results");
        const body = byId("products_body");
        const query = new URLSearchParams(filters).toString();
        const url = ui.API_BASE_URL + (query ? "?" + query : "");

        results.setAttribute("aria-busy", "true");
        body.replaceChildren();

        setStatus(
            "loading",
            query ? "Searching products..." : "Loading products..."
        );

        const timeout = window.setTimeout(() => {
            controller.abort();
        }, REQUEST_TIMEOUT_MS);

        try {
            const response = await fetch(url, {
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

            let payload;

            try {
                payload = await response.json();
            } catch (_) {
                throw new Error(
                    "The server returned an unreadable response."
                );
            }

            if (currentRequest !== requestNumber) {
                return;
            }

            if (!response.ok) {
                const message =
                    payload && typeof payload.message === "string"
                        ? payload.message
                        : "Unable to load products. Please try again.";

                if (response.status === 400) {
                    setStatus("invalid", message);
                    return;
                }

                throw new Error(message);
            }

            if (!Array.isArray(payload)) {
                throw new Error(
                    "The server returned an invalid product list."
                );
            }

            ui.renderProducts(payload);
        } catch (error) {
            if (currentRequest !== requestNumber) {
                return;
            }

            body.replaceChildren();

            setStatus(
                "error",
                error.name === "AbortError"
                    ? "Loading products timed out. Please try again."
                    : "Unable to load products. Please try again."
            );
        } finally {
            window.clearTimeout(timeout);

            if (currentRequest === requestNumber) {
                activeController = null;
                results.setAttribute("aria-busy", "false");
            }
        }
    }

    function submitSearch(event) {
        event.preventDefault();

        ui.clearMessage();
        clearValidation();

        const { filters, errors } = readFilters();

        if (errors.length) {
            showValidationErrors(errors);
            return;
        }

        loadProducts(filters);
    }

    function initialize() {
        const form = byId("search_form");

        form.noValidate = true;
        byId("search-btn").disabled = false;

        form.addEventListener("submit", submitSearch);

        PRICE_FIELDS.forEach((field) => {
            byId(field.id).addEventListener("input", () => {
                byId(field.id).setAttribute("aria-invalid", "false");
                byId(field.id + "_error").textContent = "";
            });
        });

        // rest_api.js resets the form before this listener runs.
        byId("reset-search-btn").addEventListener("click", () => {
            loadProducts();
        });

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