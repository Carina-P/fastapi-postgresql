# FastAPI + PostgreSQL — Backend Learning Project

[![Python CI](https://github.com/Carina-P/fastapi-postgresql/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/Carina-P/fastapi-postgresql/actions/workflows/ci.yml)

A hands-on backend project demonstrating a REST API built with **Python 3.13, FastAPI, PostgreSQL, Psycopg 3 and Docker**. It provides endpoints for products, customers and orders, with SQL-based data access, request validation, transactional writes and automated tests.

The repository also demonstrates **GitHub Actions CI/CD**, including database-backed tests and multi-platform container images published to GitHub Container Registry (GHCR).

> **Scope:** This repository contains one FastAPI application backed by PostgreSQL. Microservice communication, HTTPX retries and idempotency were explored in separate exercises and are not part of this repository's documented implementation.

## Features

- **Product management:** Create, retrieve, list, partially update and delete products; filter by activity, category and price range.
- **Customer management:** Create and retrieve customers; retrieve a customer's orders, optionally filtered by status.
- **Order management:** Create orders with multiple items, retrieve orders and filter the order list by status.
- **PostgreSQL integration:** SQL queries with Psycopg 3 and parameter binding.
- **Validation and error handling:** Pydantic models, database constraints and HTTP errors such as 404 and 409.
- **Transactional order creation:** Order and order-item operations handled together in the database layer.
- **Automated tests:** pytest tests run against a dedicated PostgreSQL test database in CI.
- **CI/CD:** Test, build and publish Docker images for `linux/amd64` and `linux/arm64`.

## Tech stack

| Component | Technology |
| --- | --- |
| Language | Python 3.13 |
| Web framework | FastAPI |
| Validation | Pydantic |
| Database | PostgreSQL 18 |
| Driver | Psycopg 3 |
| Containers | Docker, Docker Compose |
| Tests | pytest, HTTPX / FastAPI TestClient |
| CI/CD | GitHub Actions, Docker Buildx, GHCR |

## Project structure

```text
.
├── .github/workflows/ci.yml   # Tests and Docker image publishing
├── app/
│   ├── main.py                # FastAPI app, routers and /health
│   ├── routers/               # Product, customer and order routes
│   ├── models.py              # Request and response models
│   └── database.py            # Psycopg database operations
├── db/
│   ├── schema.sql             # Database schema
│   ├── seed.sql               # Sample data
│   └── init_db.py             # Test-database initialization only
├── tests/                     # Automated API/database tests
├── Dockerfile
├── compose.yaml
└── requirements.txt
```

## API endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/health` | Basic application health endpoint |
| GET | `/products` | List products; filter using `active`, `category`, `min_price`, `max_price` |
| GET | `/products/{product_id}` | Retrieve one product |
| POST | `/products` | Create a product |
| PATCH | `/products/{product_id}` | Update selected product fields |
| DELETE | `/products/{product_id}` | Delete a product |
| GET | `/customers` | List customers |
| GET | `/customers/{customer_id}` | Retrieve one customer |
| POST | `/customers` | Create a customer |
| GET | `/customers/{customer_id}/orders` | List one customer's orders; optional `status` filter |
| GET | `/orders` | List orders; optional `status` filter |
| GET | `/orders/{order_id}` | Retrieve one order, including its total |
| POST | `/orders` | Create an order |

FastAPI provides interactive API documentation at **http://localhost:8000/docs** after startup.

## Run locally with Docker Compose

**Prerequisites:** Docker with Compose and Git.

```bash
git clone https://github.com/Carina-P/fastapi-postgresql.git
cd fastapi-postgresql
docker compose up -d
```

The checked-in `compose.yaml` **pulls** `ghcr.io/carina-p/fastapi-postgresql:latest`; it does not build the application locally. It starts:

- FastAPI on **http://localhost:8000**
- PostgreSQL on host port **5433** (container port 5432)

### Initialize the local database

For a new PostgreSQL volume, apply the schema and sample data from the repository:

```bash
docker compose exec -T db psql -U postgres -d learning < db/schema.sql
docker compose exec -T db psql -U postgres -d learning < db/seed.sql
```

Run these initialization commands **once on a fresh database**. The SQL scripts are not presented as repeatable migrations. The `db/init_db.py` script is intentionally restricted to the `learning_test_db` test database, so it should **not** be used to initialize the normal `learning` database.

Check the API:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/products
```

Stop the services with `docker compose down`. The named PostgreSQL volume preserves your data; `docker compose down -v` deletes that volume.

**Note:** The database credentials in `compose.yaml` are development-only example values. Change them and use appropriate secret handling for any non-local deployment.

### Build locally instead of pulling GHCR

You can build a local image using the included Dockerfile:

```bash
docker build -t fastapi-postgresql:local .
```

To use that image with Compose, change the `app.image` value in `compose.yaml` to `fastapi-postgresql:local`, or supply an equivalent local Compose override.

## Testing

The repository uses pytest and a separate test database. The CI workflow automatically starts PostgreSQL 18, sets `DB_NAME=learning_test_db`, initializes it using `db/init_db.py`, and runs:

```bash
python -m pytest tests/
```

For local test execution, install `requirements.txt`, configure the database environment variables (`DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`), and ensure a reachable **dedicated test database** named `learning_test_db` exists. Then run the initialization command and pytest. **Do not point the test setup at a database containing data you want to keep.**

## CI/CD

The workflow in `.github/workflows/ci.yml`:

1. Runs on pushes to `main`, version tags beginning with `v`, and pull requests.
2. Runs tests against a PostgreSQL 18 service, after initializing the test schema and seed data.
3. Builds Docker images for **AMD64 and ARM64** after successful tests.
4. Publishes images to GHCR on pushes to `main` or version tags; pull requests are built without publishing.

Images are tagged `latest` and with the commit SHA on `main`; version-tag pushes publish a corresponding version tag (for example, `v1.0.0`).

[View GitHub Actions](https://github.com/Carina-P/fastapi-postgresql/actions) · [View package](https://github.com/Carina-P?tab=packages)

## What this project demonstrates

- Designing and documenting REST APIs with FastAPI and Pydantic.
- Writing safe, parameterized SQL with Psycopg.
- Handling relational data, joins, aggregate queries and database constraints.
- Using transactions for operations that write related records.
- Returning meaningful HTTP errors for missing or conflicting resources.
- Structuring a backend into routers, models and database operations.
- Running reproducible tests in CI and shipping multi-platform container images.

## Project purpose

This is a **learning and demonstration project**, not a production-ready service. It is intended to make backend design decisions and implementation details visible in code.
