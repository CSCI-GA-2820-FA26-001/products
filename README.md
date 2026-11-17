# NYU DevOps Product Team

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)
[![Build Status](https://github.com/CSCI-GA-2820-FA26-001/products/actions/workflows/ci.yml/badge.svg)](https://github.com/CSCI-GA-2820-FA26-001/products/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/CSCI-GA-2820-FA26-001/products/graph/badge.svg?branch=master)](https://codecov.io/gh/CSCI-GA-2820-FA26-001/products)

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-red.svg)](https://www.python.org/)
[![Open in Remote - Containers](https://img.shields.io/static/v1?label=Remote%20-%20Containers&message=Open&color=blue&logo=visualstudiocode)](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/CSCI-GA-2820-FA26-001/products)

A RESTful product catalog service developed for the NYU DevOps and Agile Methodologies course.

## Overview

The Products Service provides a browser-based administration page and a JSON API for creating, retrieving, updating, deleting, and listing products. Products are stored in PostgreSQL using Flask-SQLAlchemy.

Each product contains a database-generated ID, a name, a description, and a price. Prices use decimal values internally and are returned as strings in JSON responses to preserve precision.

The service currently supports:

- Creating products with validated data.
- Retrieving individual products by ID.
- Updating existing products.
- Deleting products with idempotent behavior.
- Listing all products.
- Filtering products by exact name and price range.
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

The container build installs the application and development dependencies with Pipenv. Once the container is ready, start the service:

```bash
make run
```

## Using the administration page

Open [http://localhost:8080/](http://localhost:8080/). The page loads the catalog automatically.

| To... | On the page |
| --- | --- |
| Create a product | Click **Create Product**, enter the name, description, and price, then click **Create**. The confirmation shows the generated ID and saved details. Close it to see the new row. |
| Read a product | Click its name to see its ID, description, and price. |
| Update a product | Click **Update** in its row, edit the prefilled fields, and save. The product keeps its ID. |
| Delete a product | Click **Delete** in its row. This permanently removes the product. |
| Search or list all | Enter an exact name, minimum price, maximum price, or a combination, then click **Search**. Both price limits are inclusive. Click **Reset filters** to show all products again. |
| Submit feedback | Click **Review** in the product row, enter a whole-number rating from 1 to 5 and a non-blank review, then click **Submit Review**. The feedback area shows the new rating and text alongside earlier reviews. |

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

Product endpoints use the `/api` prefix. Open [Swagger UI](http://localhost:8080/apidocs/) to see the request fields, query parameters, and response codes. To create a product there, expand `POST /api/products`, select **Try it out**, enter the JSON body, and click **Execute**. A successful request returns `201 Created`.

| Method | Endpoint | Description | Successful response |
| --- | --- | --- | --- |
| `GET` | `/` | Open the administration page (HTML) | `200 OK` |
| `POST` | `/api/products` | Create a product | `201 Created` |
| `GET` | `/api/products` | List all products | `200 OK` |
| `GET` | `/api/products?name=<name>` | List products with an exact matching name | `200 OK` |
| `GET` | `/api/products/<product_id>` | Read a product | `200 OK` |
| `PUT` | `/api/products/<product_id>` | Update a product | `200 OK` |
| `DELETE` | `/api/products/<product_id>` | Delete a product | `204 No Content` |
| `POST` | `/api/products/<product_id>/comments` | Submit product feedback | `200 OK` |

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
| Open the administration page | `GET` | `http://localhost:8080/` | None | `200 OK` | HTML page titled `Products Administration` |
| Create a product | `POST` | `http://localhost:8080/api/products` | **Body → raw → JSON:** `{"name":"Notebook","description":"A paper notebook","price":"19.99"}` | `201 Created` | `{"id":1,"name":"Notebook","description":"A paper notebook","price":"19.99"}` |
| Read a product | `GET` | `http://localhost:8080/api/products/<product_id>` | None | `200 OK` | `{"id":1,"name":"Notebook","description":"A paper notebook","price":"19.99"}` |
| List all products | `GET` | `http://localhost:8080/api/products` | None | `200 OK` | `[{"id":1,"name":"Notebook","description":"A paper notebook","price":"19.99"}]` |
| Filter products by name | `GET` | `http://localhost:8080/api/products` | **Params:** Key = `name`, Value = `Notebook` | `200 OK` | `[{"id":1,"name":"Notebook","description":"A paper notebook","price":"19.99"}]` |
| Update a product | `PUT` | `http://localhost:8080/api/products/<product_id>` | **Body → raw → JSON:** `{"name":"Notebook","description":"Updated notebook","price":"24.50"}` | `200 OK` | `{"id":1,"name":"Notebook","description":"Updated notebook","price":"24.50"}` |
| Delete a product | `DELETE` | `http://localhost:8080/api/products/<product_id>` | None | `204 No Content` | Empty response body |

The Create response also includes a `Location` header pointing to the new product, for example:

```http
Location: http://localhost:8080/api/products/1
```

Use this URL in a GET request to verify that the product was saved.

The List and Filter responses may contain additional products if matching records already exist in the database. Name filtering uses exact matching and returns all products with that name.

### Test Error and Empty Results

API errors return JSON with a `message` field. For example, requesting a missing product returns `404 Not Found`. The table shows representative messages; the exact wording can vary.

| Test case | Method | URL | Request body or parameters | Expected status | Example response body |
| --- | --- | --- | --- | --- | --- |
| Create with missing required fields | `POST` | `http://localhost:8080/api/products` | **Body → raw → JSON:** `{}` | `400 Bad Request` | `{"message":"Missing product field: name"}` |
| Create with a negative price | `POST` | `http://localhost:8080/api/products` | **Body → raw → JSON:** `{"name":"Notebook","price":"-1.00"}` | `400 Bad Request` | `{"message":"Product price must be finite and non-negative"}` |
| Create with an unsupported content type | `POST` | `http://localhost:8080/api/products` | **Body → raw → Text:** `hello`; set `Content-Type: text/plain` | `415 Unsupported Media Type` | `{"message":"415 Unsupported Media Type: Content-Type must be application/json"}` |
| Read the deleted product | `GET` | `http://localhost:8080/api/products/<product_id>` | None; run after deleting the product | `404 Not Found` | `{"message":"404 Not Found: Product with id '1' was not found."}` |
| Filter by a name that does not exist | `GET` | `http://localhost:8080/api/products` | **Params:** Key = `name`, Value = `NonexistentProduct`; ensure no product has this name | `200 OK` | `[]` |
| Delete the same product again | `DELETE` | `http://localhost:8080/api/products/<product_id>` | None; repeat the previous DELETE request | `204 No Content` | Empty response body |

POST and PUT requests require both `name` and `price`. The `description` field is optional and defaults to an empty string when omitted.

Prices are returned as JSON strings. A successful DELETE request returns no response body, including when the product does not exist.

## Querying Products

The `GET /api/products` endpoint supports the following optional filters:

| Parameter | Description |
| --- | --- |
| `name` | Exact product name |
| `min_price` | Minimum price, inclusive |
| `max_price` | Maximum price, inclusive |

Filters can be used independently or combined. Products must satisfy all supplied conditions.

```http
GET /api/products?min_price=10
GET /api/products?max_price=50
GET /api/products?name=Notebook&min_price=10&max_price=50
```

Without filters, the endpoint returns all products. If no products match, it returns `200 OK` with an empty JSON array.

Invalid, negative, or non-finite prices, and a minimum price greater than the maximum, return a JSON `400 Bad Request` response.

## Product Ratings and Reviews

Submit a rating and optional written review using:

```http
POST /api/products/<product_id>/comments
Content-Type: application/json
```

Example request:

```json
{
  "rating": 5,
  "text": "Good quality and worth the price."
}
```

A successful request returns `200 OK` with the updated product:

```json
{
  "id": 1,
  "name": "Notebook",
  "description": "A paper notebook",
  "price": "19.99",
  "reviews": [
    {
      "rating": 5,
      "text": "Good quality and worth the price."
    }
  ]
}
```

Validation and behavior:

- `rating` is required and must be an integer from 1 to 5, inclusive. Booleans, decimal numbers, and numeric strings are invalid.
- `text` is optional. Missing, `null`, or whitespace-only text is stored as an empty string.
- Leading and trailing whitespace is removed from review text.
- Other non-string text values are rejected.
- Each successful submission appends a review and preserves previous reviews.
- Reviews are persisted and included when products are created, retrieved, updated, listed, or filtered. New products have `"reviews": []`.
- Supplying `reviews` in a product creation or update request does not create or replace reviews.
- Deleting a product also deletes its associated reviews.

| Condition | Response |
| --- | --- |
| Review saved successfully | `200 OK` |
| Missing or invalid rating, invalid text, or a non-object JSON body | `400 Bad Request` |
| Product does not exist | `404 Not Found` |
| Missing or unsupported Content-Type | `415 Unsupported Media Type` |

## Health Check

The service provides a health endpoint for Kubernetes readiness and liveness probes:

```http
GET /health
```

Expected response: `200 OK`

```json
{
  "status": "OK"
}
```

This endpoint checks application responsiveness; it does not verify database connectivity.

## Local Kubernetes Deployment

Run the following commands inside the Dev Container with Docker running. Stop any development server using port `8080` before creating the cluster.

```bash
make cluster
make build
make push
make deploy
```

The deployment includes:

- A local K3D/K3S cluster named `nyu-devops`.
- A local container registry at `cluster-registry:5000`.
- The Products application running as a Deployment.
- PostgreSQL 15 running as a StatefulSet with a database named `products`.
- A 1 GiB persistent volume claim for PostgreSQL data.
- A Service and Traefik Ingress exposing the application at `http://localhost:8080`.

Verify the deployment:

```bash
kubectl get pods
kubectl get services
kubectl get ingress
kubectl get pvc

curl http://localhost:8080/health
curl http://localhost:8080/api/products
```

### Redeploying Code Changes

After changing application code, rebuild, push, and deploy the image:

```bash
make build
make push
make deploy
```

`make deploy` applies the selected image, restarts the application pods, and waits for the rollout to complete. The default rollout timeout is 180 seconds.

To use a different image tag, supply the same tag to all three commands:

```bash
make build IMAGE_TAG=2.0
make push IMAGE_TAG=2.0
make deploy IMAGE_TAG=2.0
```

## Automated Tests and Code Quality

Run the code quality checks inside the Dev Container:

```bash
make lint
```

This runs Flake8 and Pylint against the application and tests.

Before running unit tests, create a dedicated PostgreSQL database named `testdb`. Tests clear records in the connected database, so use a database reserved for testing.

```bash
DATABASE_URI=postgresql+psycopg://postgres:pgs3cr3t@postgres:5432/testdb make test
```

The test suite covers product persistence, CRUD operations, query filters, ratings and reviews, health checks, and error responses. The minimum required code coverage is 95%.

### Browser tests (Behave and Selenium)

Run these tests inside the Dev Container. Behave runs the scenarios in `features/`; their Python steps use Selenium to interact with the UI, including creating test products. These tests change the catalog of the service they visit.

In one terminal, start the service against the dedicated `testdb` described above. Stop any existing service on port 8080 first:

```bash
DATABASE_URI=postgresql+psycopg://postgres:pgs3cr3t@postgres:5432/testdb make run
```

In a second terminal, run a feature:

```bash
python -m behave features/create_product.feature
```

`BASE_URL` tells Selenium which running service to visit and defaults to `http://localhost:8080`. To run the available scenarios against a populated test catalog:

```bash
BASE_URL=http://localhost:8080 python -m behave --tags="not @empty_catalog"
```

Run `python -m behave --tags="@empty_catalog"` separately against an empty test catalog, before scenarios that create products.

## Continuous Integration

GitHub Actions runs automatically on pull requests targeting `master` and pushes to `master`. The workflow also supports manual execution.

The workflow:

- Starts a PostgreSQL 15 service with a dedicated test database.
- Installs application and development dependencies.
- Runs Flake8 and Pylint.
- Runs unit tests and enforces at least 95% code coverage.
- Uploads the coverage report to Codecov.

The build fails if lint checks or tests fail, coverage falls below 95%, or the Codecov upload fails. The CI and Codecov badges at the top of this README link to the corresponding results.

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
├── workflows/              - Pull request CI configuration
└── ISSUE_TEMPLATE/         - User story and bug report templates

.vscode/                    - Workspace editor settings

config/
├── insecure-registry.json  - Local Docker registry configuration
└── registries.yaml         - Local K3D registry configuration

features/                   - Behave scenarios for the administration UI
├── environment.py          - Browser setup and BASE_URL configuration
└── steps/                  - Selenium step definitions

k8s/                        - Local Kubernetes deployment manifests

service/
├── __init__.py             - Flask application factory and initialization
├── config.py               - Application and database configuration
├── models.py               - Product model, validation, and persistence
├── routes.py               - REST API endpoints
├── static/                 - Administration page, stylesheets, and JavaScript
└── common/
    ├── cli_commands.py     - Database recreation command
    ├── error_handlers.py   - JSON error responses
    ├── log_handlers.py     - Logging configuration
    └── status.py           - HTTP status constants

tests/                     - test cases package
├── js/                    - JavaScript tests for the UI
├── __init__.py            - package initializer
├── factories.py           - Factory for testing with fake objects
├── test_cli_commands.py   - test suite for the CLI
├── test_models.py         - test suite for business models
└── test_routes.py         - test suite for service routes

.gitignore          - this will ignore vagrant and other metadata files
.flaskenv           - Environment variables to configure Flask
.gitattributes      - File to gix Windows CRLF issues
dot-env-example     - copy to .env to use environment variables
Pipfile             - Application and development dependencies
Pipfile.lock        - Locked dependency versions
```

## License

Copyright (c) 2016, 2025 [John Rofrano](https://www.linkedin.com/in/JohnRofrano/). All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the New York University (NYU) masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by [John Rofrano](https://cs.nyu.edu/~rofrano/), Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.
