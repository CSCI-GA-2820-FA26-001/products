(function () {
    "use strict";

    // Shared configuration for the future UI feature stories.
    // Defining this value does not make a request.
    const API_BASE_URL = "/products";

    const byId = (id) => document.getElementById(id);

    const CREATE_FIELDS = [
        "create_product_name",
        "create_product_description",
        "create_product_price"
    ];

    function showMessage(message, kind = "info") {
        const classes = {
            info: "alert-info",
            success: "alert-success",
            error: "alert-danger",
            warning: "alert-warning"
        };

        const targets = [byId("flash_message")];
        const dialog = document.querySelector("dialog[open]");
        const local = dialog && dialog.querySelector("[data-message]");

        if (local) {
            targets.push(local);
        }

        targets.forEach((target) => {
            target.textContent = message;
            target.className = message
                ? "message alert " + (classes[kind] || classes.info)
                : "message";
        });
    }

    function clearMessage() {
        document.querySelectorAll(".message").forEach((target) => {
            target.textContent = "";
            target.className = "message";
        });
    }

    function openDialog(id) {
        clearMessage();

        const dialog = byId(id);

        document.querySelectorAll("dialog[open]").forEach((opened) => {
            if (opened !== dialog) {
                opened.close();
            }
        });

        if (!dialog.open) {
            dialog.showModal();
        }
    }

    function clearCreateForm() {
        CREATE_FIELDS.forEach((id) => {
            byId(id).value = "";
        });

        clearMessage();
        byId("create_product_name").focus();
    }

    function appendCell(row, value, className = "") {
        const cell = document.createElement("td");

        cell.textContent = value == null ? "" : String(value);
        cell.className = className;

        row.appendChild(cell);

        return cell;
    }

    function productButton(product, action, label, style) {
        const button = document.createElement("button");

        button.type = "button";
        button.id = action + "-" + product.id;
        button.dataset.action = action;
        button.dataset.productId = String(product.id);
        button.className = "btn " + style;
        button.textContent = label;

        button.disabled = action !== "update";
        button.title = action === "update" ? "Update this product" : "This action is unavailable.";

        button.setAttribute(
            "aria-label",
            label + " — product " + product.id
        );

        if (action !== "delete") {
            button.setAttribute("aria-haspopup", "dialog");
        }

        return button;
    }

    function renderProducts(products) {
        const body = byId("products_body");

        body.replaceChildren();

        products.forEach((product) => {
            const row = document.createElement("tr");

            row.id = "product-" + product.id;
            row.dataset.productId = String(product.id);

            appendCell(row, product.id);

            const name = appendCell(row, "");

            name.appendChild(
                productButton(
                    product,
                    "retrieve",
                    product.name,
                    "btn-link product-link"
                )
            );

            appendCell(
                row,
                product.description,
                "description-cell"
            );

            appendCell(row, product.price);

            const actions = appendCell(row, "");
            const group = document.createElement("div");

            group.className = "row-actions";

            group.append(
                productButton(
                    product,
                    "update",
                    "Update",
                    "btn-warning btn-sm"
                ),
                productButton(
                    product,
                    "delete",
                    "Delete",
                    "btn-danger btn-sm"
                ),
                productButton(
                    product,
                    "review",
                    "Review",
                    "btn-primary btn-sm"
                )
            );

            actions.appendChild(group);
            body.appendChild(row);
        });

        byId("search_results").setAttribute("aria-busy", "false");
        byId("results_status").dataset.state = "ready";

        byId("results_status").textContent = products.length
            ? products.length + " product(s)."
            : "No products found.";
    }

    function renderFeedback(reviews) {
        const body = byId("feedback_body");

        body.replaceChildren();

        reviews.forEach((review) => {
            const row = document.createElement("tr");

            appendCell(row, review.rating);
            appendCell(row, review.text, "review-text");

            body.appendChild(row);
        });

        byId("reviews_status").textContent = reviews.length
            ? reviews.length + " saved review(s)."
            : "No reviews yet.";
    }

    function updateForm(product) {
        byId("product_id").value = product.id;
        byId("product_name").value = product.name;
        byId("product_description").value = product.description ?? "";
        byId("product_price").value = product.price;
    }

    function showProductDetails(product) {
        ["id", "name", "description", "price"].forEach((field) => {
            byId("detail_product_" + field).textContent =
                String(product[field] ?? "");
        });

        openDialog("retrieve-product-dialog");
    }

    function openUpdateDialog(product) {
        updateForm(product);
        byId("update-product-dialog").dataset.productId = String(product.id);
        openDialog("update-product-dialog");
    }

    function openReviewDialog(product) {
        const dialog = byId("review-product-dialog");

        dialog.dataset.productId = String(product.id);

        byId("review-product-form").reset();

        byId("review_product_label").textContent =
            product.name + " (ID: " + product.id + ")";

        renderFeedback(product.reviews || []);
        openDialog("review-product-dialog");
    }

    function initialize() {
        // Block default navigation, including submitting with Enter.
        // Feature stories can add their own submit handlers later.
        document.querySelectorAll("form").forEach((form) => {
            form.addEventListener("submit", (event) => {
                event.preventDefault();
            });
        });

        document.querySelectorAll("[data-close]").forEach((button) => {
            button.addEventListener("click", () => {
                button.closest("dialog").close();
            });
        });

        byId("open-create-btn").addEventListener("click", () => {
            byId("create-product-form").reset();
            openDialog("create-product-dialog");
        });

        byId("clear-btn").addEventListener(
            "click",
            clearCreateForm
        );

        byId("reset-search-btn").addEventListener("click", () => {
            byId("search_form").reset();
            clearMessage();
            byId("search_name").focus();
        });

        // No initial product request, mock catalog, or business action handlers.
        // List, Query, Create, Read, Update, Delete and Action are separate stories.
    }

    window.ProductsUI = Object.freeze({
        API_BASE_URL,
        showMessage,
        clearMessage,
        clearCreateForm,
        renderProducts,
        renderFeedback,
        updateForm,
        showProductDetails,
        openUpdateDialog,
        openReviewDialog
    });

    if (document.readyState === "loading") {
        document.addEventListener(
            "DOMContentLoaded",
            initialize
        );
    } else {
        initialize();
    }
})();
