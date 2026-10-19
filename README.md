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
