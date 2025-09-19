# ==============================================================================
# justfile for Django Project Automation
#
# Provides a unified interface for common development tasks, abstracting away
# the underlying Docker Compose commands for a better Developer Experience (DX).
# ==============================================================================

# --- 変数定義 ---

# .env ファイルから変数をロード (justが自動的に実行)
# デフォルトのプロジェクト名を設定 (.envで上書き可能)
PROJECT_NAME := env("PROJECT_NAME", "drf-template")

# 環境ごとのプロジェクト名
DEV_PROJECT_NAME := PROJECT_NAME + "-dev"
PROD_PROJECT_NAME := PROJECT_NAME + "-prod"
TEST_PROJECT_NAME := PROJECT_NAME + "-test"

# Sudo設定
# 実行方法:
#   just up
#   just --set SUDO true up
#   SUDO=true just up
SUDO := default("false")
DOCKER_CMD := if SUDO == "true" { "sudo docker" } else { "docker" }

# --- Docker Compose コマンド定義 ---
DEV_COMPOSE  := DOCKER_CMD + " compose -f docker-compose.dev.yml --project-name " + DEV_PROJECT_NAME
PROD_COMPOSE := DOCKER_CMD + " compose -f docker-compose.dev.yml --project-name " + PROD_PROJECT_NAME
TEST_COMPOSE := DOCKER_CMD + " compose -f docker-compose.dev.yml -f docker-compose.test.override.yml --project-name " + TEST_PROJECT_NAME


# ==============================================================================
# HELP (デフォルトターゲット)
# ==============================================================================

# Show this help message
default:
    @just --list


# ==============================================================================
# Environment Setup
# ==============================================================================

# Initialize project: install dependencies, create .env file and pull required Docker images
@setup:
    @echo "Installing python dependencies with uv..."
    @uv sync
    @echo "Creating environment file..."
    @if [ ! -f .env ] && [ -f .env.example ]; then
        echo "Creating .env from .env.example..."
        cp .env.example .env
        echo "✅ Environment file created (.env)"
    else
        echo ".env already exists. Skipping creation."
    fi
    @echo "💡 You can customize .env for your specific needs:"
    @echo "   📝 Change database settings if needed"
    @echo "   📝 Adjust other settings as needed"
    @echo ""
    @echo "Pulling PostgreSQL image for development..."
    # justfileはレシピ全体を1つのシェルで実行するため、`\`での行連結は不要
    POSTGRES_IMAGE="postgres:16-alpine"
    if [ -f .env ] && grep -q "^POSTGRES_IMAGE=" .env; then
        POSTGRES_IMAGE=$$(sed -n 's/^POSTGRES_IMAGE=\(.*\)/\1/p' .env | head -n1 | tr -d '\r')
        [ -z "$$POSTGRES_IMAGE" ] && POSTGRES_IMAGE="postgres:16-alpine"
    fi
    echo "Using POSTGRES_IMAGE=$$POSTGRES_IMAGE"
    {{DOCKER_CMD}} pull "$$POSTGRES_IMAGE"
    @echo "✅ Setup complete. Dependencies are installed and .env file is ready."


# ==============================================================================
# Development Environment Commands
# ==============================================================================

# Build images and start dev containers
@up:
    @echo "Building images and starting DEV containers..."
    @{{DEV_COMPOSE}} up --build -d

# Stop dev containers
@down:
    @echo "Stopping DEV containers..."
    @{{DEV_COMPOSE}} down --remove-orphans

# Build images and start prod-like containers
@up-prod:
    @echo "Starting up PROD-like containers..."
    @{{PROD_COMPOSE}} up -d --build

# Stop prod-like containers
@down-prod:
    @echo "Shutting down PROD-like containers..."
    @{{PROD_COMPOSE}} down --remove-orphans

# Rebuild services, pulling base images, without cache, and restart
@rebuild:
    @echo "Rebuilding all DEV services with --no-cache and --pull..."
    @{{DEV_COMPOSE}} up -d --build --no-cache --pull always


# ==============================================================================
# CODE QUALITY
# ==============================================================================

# Format code with black and ruff --fix
@format:
    @echo "Formatting code with black and ruff..."
    @uv run black .
    @uv run ruff check . --fix

# Lint code with black check and ruff
@lint:
    @echo "Linting code with black check and ruff..."
    @uv run black --check .
    @uv run ruff check .


# ==============================================================================
# TESTING
# ==============================================================================

# Run complete test suite (local SQLite then docker PostgreSQL)
@test: local-test docker-test

# --- Local testing (lightweight, fast development) ---

# Run lightweight local test suite (unit + SQLite DB tests)
@local-test: unit-test sqlt-test

# Run unit tests locally
@unit-test:
    @echo "🚀 Running unit tests (local)..."
    @uv run pytest tests/unit -v -s

# Run database tests with SQLite (fast, lightweight, no docker)
@sqlt-test:
    @echo "🚀 Running database tests with SQLite..."
    @USE_SQLITE=true uv run pytest tests/db -v -s

# --- Docker testing (production-like, comprehensive) ---

# Run all Docker-based tests
@docker-test: build-test pstg-test e2e-test

# Build Docker image for testing without leaving artifacts
@build-test:
    @echo "Building Docker image for testing (clean build)..."
    TEMP_IMAGE_TAG=$$(date +%s)-build-test
    {{DOCKER_CMD}} build --target production --tag temp-build-test:$$TEMP_IMAGE_TAG . && \
    echo "Build successful. Cleaning up temporary image..." && \
    {{DOCKER_CMD}} rmi temp-build-test:$$TEMP_IMAGE_TAG || true

# Run database tests with PostgreSQL (robust, production-like)
@pstg-test:
    @echo "🚀 Starting TEST containers for PostgreSQL database test..."
    @{{TEST_COMPOSE}} up -d --build
    @echo "Running database tests inside api container (against PostgreSQL)..."
    
    # justはデフォルトで `set -e` のように動作するため、
    # テストが失敗しても `down` を実行するために `set +e` を使う
    @set +e
    {{TEST_COMPOSE}} exec api uv run pytest tests/db -v -s
    EXIT_CODE=$$? # テストの終了コードを取得
    @set -e
    
    @echo "🔴 Stopping TEST containers..."
    @{{TEST_COMPOSE}} down --remove-orphans
    @exit $$EXIT_CODE # テストの終了コードでjustプロセスを終了させる

# Run e2e tests against containerized application stack (runs from host)
@e2e-test:
    @echo "🚀 Running e2e tests (from host)..."
    @uv run pytest tests/e2e -v -s


# ==============================================================================
# CLEANUP
# ==============================================================================

# Remove __pycache__ and .venv to make project lightweight
@clean:
    @echo "🧹 Cleaning up project..."
    @find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    @rm -rf .venv
    @rm -rf .pytest_cache
    @rm -rf .ruff_cache
    @echo "✅ Cleanup completed"