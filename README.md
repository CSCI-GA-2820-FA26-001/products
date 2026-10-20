# NYU DevOps Product Team

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-red.svg)](https://www.python.org/)
[![Open in Remote - Containers](https://img.shields.io/static/v1?label=Remote%20-%20Containers&message=Open&color=blue&logo=visualstudiocode)](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/CSCI-GA-2820-FA26-001/products)

A RESTful product catalog service developed for the NYU DevOps and Agile Methodologies course.

## Overview

The Products Service provides a JSON API for creating, retrieving, updating, deleting, and listing products. Products are stored in PostgreSQL using Flask-SQLAlchemy.

Each product contains a database-generated ID, a name, a description, and a price. Prices use decimal values internally and are returned as strings in JSON responses to preserve precision.

The service currently supports:

- Creating products with validated data.
- Retrieving individual products by ID.
- Updating existing products.
- Deleting products with idempotent behavior.
- Listing all products.
- Filtering products by exact name.
- Returning structured JSON error responses.

## Automatic Setup

The repository includes a VS Code Dev Container configuration with a Python development environment and PostgreSQL 15.

### Prerequisites

- Git
- Docker Desktop or a compatible Docker environment
- Visual Studio Code
- The VS Code Dev Containers extension

### Start the Development Environment

1. Clone the repository:

   ```bash
   git clone https://github.com/CSCI-GA-2820-FA26-001/products.git
   cd products
   ```

2. Open the repository in VS Code.

3. Run **Dev Containers: Reopen in Container** from the Command Palette.

Once the container is ready, start the service:

```bash
make run
```

## Product model

| Field | JSON type | Required in POST and PUT | Description |
| --- | --- | --- | --- |
| `id` | Integer | No | Database-generated identifier; request-body IDs are ignored |
| `name` | String | Yes | Non-blank product name, up to 63 characters |
| `description` | String | No | Product description; defaults to an empty string when omitted |
| `price` | String or number in requests; string in responses | Yes | Finite, non-negative decimal amount |

Example product:

```json
{
  "id": 1,
  "name": "Notebook",
  "description": "A paper notebook",
  "price": "19.99"
}
```

Validation rules:

- `name` must be a string containing at least one non-whitespace character.
- `name` must not exceed 63 characters.
- `description` must be a string when supplied; `null` is invalid.
- `price` accepts decimal strings and JSON numbers.
- Zero is a valid price.
- Negative prices, booleans, `null`, invalid numeric strings, `NaN`, and infinity are rejected.
- Decimal strings are recommended when submitting prices to preserve the intended decimal value.
- Prices are not restricted to two decimal places.
- Product names do not have to be unique.

## REST API

All paths below are relative to the service base URL, such as `http://localhost:8080`.

| Method | Endpoint | Description | Successful response |
| --- | --- | --- | --- |
| `GET` | `/` | Read service information | `200 OK` |
| `POST` | `/products` | Create a product | `201 Created` |
| `GET` | `/products` | List all products | `200 OK` |
| `GET` | `/products?name=<name>` | List products with an exact matching name | `200 OK` |
| `GET` | `/products/<product_id>` | Read a product | `200 OK` |
| `PUT` | `/products/<product_id>` | Update a product | `200 OK` |
| `DELETE` | `/products/<product_id>` | Delete a product | `204 No Content` |

## Testing the Service

### Start the Service

Run the following command inside the Dev Container:

```bash
make run
```

Keep the service running and ensure port `8080` is forwarded to your local machine.

### Test with Postman

Open Postman and create HTTP requests using the base URL:

```text
http://localhost:8080
```

For POST and PUT requests:

1. Select **Body → raw → JSON**.
2. Enter the JSON request body shown below.
3. Ensure the request header is exactly `Content-Type: application/json`.
4. Click **Send** and compare the response with the expected result.

Run the following operations in order. Replace `<product_id>` with the ID returned by the Create request. The response examples assume the generated ID is `1`.

| Operation | Method | URL | Request body or parameters | Expected status | Example response body |
| --- | --- | --- | --- | --- | --- |
| Read service information | `GET` | `http://localhost:8080/` | None | `200 OK` | `{"name":"Products Service","version":"1.0.0","products_url":"/products"}` |
| Create a product | `POST` | `http://localhost:8080/products` | **Body → raw → JSON:** `{"name":"Notebook","description":"A paper notebook","price":"19.99"}` | `201 Created` | `{"id":1,"name":"Notebook","description":"A paper notebook","price":"19.99"}` |
| Read a product | `GET` | `http://localhost:8080/products/<product_id>` | None | `200 OK` | `{"id":1,"name":"Notebook","description":"A paper notebook","price":"19.99"}` |
| List all products | `GET` | `http://localhost:8080/products` | None | `200 OK` | `[{"id":1,"name":"Notebook","description":"A paper notebook","price":"19.99"}]` |
| Filter products by name | `GET` | `http://localhost:8080/products` | **Params:** Key = `name`, Value = `Notebook` | `200 OK` | `[{"id":1,"name":"Notebook","description":"A paper notebook","price":"19.99"}]` |
| Update a product | `PUT` | `http://localhost:8080/products/<product_id>` | **Body → raw → JSON:** `{"name":"Notebook","description":"Updated notebook","price":"24.50"}` | `200 OK` | `{"id":1,"name":"Notebook","description":"Updated notebook","price":"24.50"}` |
| Delete a product | `DELETE` | `http://localhost:8080/products/<product_id>` | None | `204 No Content` | Empty response body |

The Create response also includes a `Location` header pointing to the new product, for example:

```http
Location: http://localhost:8080/products/1
```

Use this URL in a GET request to verify that the product was saved.

The List and Filter responses may contain additional products if matching records already exist in the database. Name filtering uses exact matching and returns all products with that name.

### Test Error and Empty Results

Use the following requests to verify validation, missing resources, and repeated deletion.

| Test case | Method | URL | Request body or parameters | Expected status | Example response body |
| --- | --- | --- | --- | --- | --- |
| Create with missing required fields | `POST` | `http://localhost:8080/products` | **Body → raw → JSON:** `{}` | `400 Bad Request` | `{"status":400,"error":"Bad Request","message":"Missing product field: name"}` |
| Create with a negative price | `POST` | `http://localhost:8080/products` | **Body → raw → JSON:** `{"name":"Notebook","price":"-1.00"}` | `400 Bad Request` | `{"status":400,"error":"Bad Request","message":"Product price must be finite and non-negative"}` |
| Create with an unsupported content type | `POST` | `http://localhost:8080/products` | **Body → raw → Text:** `hello`; set `Content-Type: text/plain` | `415 Unsupported Media Type` | `{"status":415,"error":"Unsupported media type","message":"415 Unsupported Media Type: Content-Type must be application/json"}` |
| Read the deleted product | `GET` | `http://localhost:8080/products/<product_id>` | None; run after deleting the product | `404 Not Found` | `{"status":404,"error":"Not Found","message":"404 Not Found: Product with id '1' was not found."}` |
| Filter by a name that does not exist | `GET` | `http://localhost:8080/products` | **Params:** Key = `name`, Value = `NonexistentProduct`; ensure no product has this name | `200 OK` | `[]` |
| Delete the same product again | `DELETE` | `http://localhost:8080/products/<product_id>` | None; repeat the previous DELETE request | `204 No Content` | Empty response body |

POST and PUT requests require both `name` and `price`. The `description` field is optional and defaults to an empty string when omitted.

Prices are returned as JSON strings. A successful DELETE request returns no response body, including when the product does not exist.

## Contents

The project contains the following:

```text
.devcontainer/               - VS Code development container configuration
├── Dockerfile              - Development environment image
├── devcontainer.json       - VS Code configuration and port forwarding
├── docker-compose.yml      - Application and PostgreSQL services
├── devcontainer-lock.json  - Locked development container features
└── scripts/                - Development tools and setup scripts

.github/
└── ISSUE_TEMPLATE/         - User story and bug report templates

.vscode/                    - Workspace editor settings

config/
├── insecure-registry.json  - Local Docker registry configuration
└── registries.yaml         - Local K3D registry configuration

service/
├── __init__.py             - Flask application factory and initialization
├── config.py               - Application and database configuration
├── models.py               - Product model, validation, and persistence
├── routes.py               - REST API endpoints
└── common/
    ├── cli_commands.py     - Database recreation command
    ├── error_handlers.py   - JSON error responses
    ├── log_handlers.py     - Logging configuration
    └── status.py           - HTTP status constants

tests/                     - test cases package
├── __init__.py            - package initializer
├── factories.py           - Factory for testing with fake objects
├── test_cli_commands.py   - test suite for the CLI
├── test_models.py         - test suite for business models
└── test_routes.py         - test suite for service routes

.gitignore          - this will ignore vagrant and other metadata files
.flaskenv           - Environment variables to configure Flask
.gitattributes      - File to gix Windows CRLF issues
dot-env-example     - copy to .env to use environment variables
pyproject.toml      - Poetry list of Python libraries required by your code
```

## License

Copyright (c) 2016, 2025 [John Rofrano](https://www.linkedin.com/in/JohnRofrano/). All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the New York University (NYU) masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by [John Rofrano](https://cs.nyu.edu/~rofrano/), Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.
