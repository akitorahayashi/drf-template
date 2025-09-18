"""
End-to-end test configuration.

Spins up the entire application stack using testcontainers.
"""

import os
import time
from pathlib import Path

import pytest
import requests
from dotenv import load_dotenv
from testcontainers.compose import DockerCompose


def _is_service_ready(url: str, expected_status: int = 200) -> bool:
    """Check if HTTP service is ready by making a request."""
    try:
        response = requests.get(url, timeout=5)
        return response.status_code == expected_status
    except Exception:
        return False


def _wait_for_service(url: str, timeout: int = 120, interval: int = 5) -> None:
    """Wait for HTTP service to be ready with timeout."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if _is_service_ready(url):
            return
        time.sleep(interval)
    raise TimeoutError(
        f"Service at {url} did not become ready within {timeout} seconds"
    )


@pytest.fixture(scope="session")
def app_container() -> DockerCompose:
    """
    Provides a fully running application stack via Docker Compose.
    """
    load_dotenv(".env")
    compose_files = [
        "docker-compose.dev.yml",
        "docker-compose.test.override.yml",
    ]

    # Find the project root by looking for a known file, e.g., pyproject.toml
    project_root = Path(__file__).parent.parent.parent

    with DockerCompose(
        context=str(project_root),
        compose_file_name=compose_files,
        build=True,
    ) as compose:
        # Get the test port from environment variable
        host_port = os.getenv("TEST_PORT", "8002")
        # Verify that api service is running
        api_container = compose.get_container("api")
        assert api_container is not None, "api container could not be found."

        # Construct the health check URL
        health_check_url = f"http://localhost:{host_port}/health/"

        # Wait for the service to be healthy
        _wait_for_service(health_check_url, timeout=120, interval=5)

        # Add the host port to the container object for access in other fixtures
        compose.host_port = host_port
        yield compose


@pytest.fixture(scope="session")
def page_url(app_container: DockerCompose) -> str:
    """
    Returns the base URL of the running application.
    """
    host_port = app_container.host_port
    return f"http://localhost:{host_port}/"
