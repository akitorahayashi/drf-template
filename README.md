## Overview

A template for building REST APIs with Django.

## Prerequisites

Before you begin, ensure you have the following tools installed:

- **Docker**: Latest version recommended
- **Docker Compose**: Included with Docker
- **just**: Command runner (install via `cargo install just` or package manager)
- **Python**: 3.12 (recommended, see `.python-version`)
- **uv**: Fast Python package manager (install via `curl -LsSf https://astral.sh/uv/install.sh | sh`)

## Getting Started

To start your new project, clone this repository. Then, to set up the local environment and install dependencies using uv, run:

```bash
just setup
```
This command will also create the necessary `.env` files from the example file.

## Building and Running with Docker

The application is designed to run inside Docker containers. To build and start the containers in the background, use:

```bash
just up
```

Once the containers are running, you can access the application at `http://localhost:8000`.

To stop and remove the containers, run:
```bash
just down
```

### Production-like Execution

To simulate a production environment, you can use a command that starts the containers without the development-specific overrides:

```bash
just up-prod
```

> **⚠️ Important**
> Before running `just up-prod`, you must run `just setup` and configure the production-specific environment variables. The `.env` file is ignored by Git.

To stop and remove the production-like containers:
```bash
just down-prod
```

## Testing and Code Quality

The project is equipped with tools to maintain code quality, including tests, a linter, and a formatter.

### Running Tests

```bash
just test
```
This runs all tests (local SQLite + Docker PostgreSQL).

For faster local testing only:
```bash
just local-test
```

### Code Formatting and Linting

We use `black` and `ruff` to automatically format the code.

To format your code:
```bash
just format
```

To check for linting and formatting issues (as the CI pipeline does):
```bash
just lint
```

### Available Commands

To see all available commands:
```bash
just help
```

## Project Structure

A key feature of this template is how Django apps are organized.

-   **`apps/` directory**: All Django applications reside within the `apps/` directory.
-   **Namespace Package**: The `apps/` directory is configured as a [PEP 420 namespace package](https://www.python.org/dev/peps/pep-0420/), meaning it does **not** contain an `__init__.py` file. This allows for better separation of concerns and makes it easier to add or remove apps.
-   **Packaging**: The `pyproject.toml` file is configured to include the `apps` and `config` directories in the distribution.

