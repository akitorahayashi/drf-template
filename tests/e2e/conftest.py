import os
import subprocess
import time
from pathlib import Path

import pytest
import requests
from dotenv import load_dotenv


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
def app_container():
    """
    Provides a fully running application stack via Docker Compose subprocess.
    """
    load_dotenv(".env")
    compose_files = [
        "docker-compose.dev.yml",
        "docker-compose.test.override.yml",
    ]

    # Find the project root by looking for a known file, e.g., pyproject.toml
    project_root = Path(__file__).parent.parent.parent

    # Build command
    cmd = [
        "docker",
        "compose",
        "-f",
        compose_files[0],
        "-f",
        compose_files[1],
        "up",
        "--build",
        "--wait",
    ]

    # Start the services
    print(f"Starting Docker Compose with command: {' '.join(cmd)}")
    process = subprocess.Popen(
        cmd,
        cwd=str(project_root),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True,
    )

    # Stream output in real-time
    while True:
        output = process.stdout.readline()
        if output == "" and process.poll() is not None:
            break
        if output:
            print(output.strip())

    # Check if the process succeeded
    if process.returncode != 0:
        raise RuntimeError(
            f"Docker Compose failed with return code {process.returncode}"
        )

    try:
        # Get the test port from environment variable
        host_port = os.getenv("TEST_PORT", "8002")

        # Construct the health check URL
        health_check_url = f"http://localhost:{host_port}/health/"

        # Wait for the service to be healthy
        _wait_for_service(health_check_url, timeout=120, interval=5)

        # Create a simple object to hold the host port
        class ComposeManager:
            def __init__(self, host_port):
                self.host_port = host_port

        compose_manager = ComposeManager(host_port)
        yield compose_manager

    finally:
        # Clean up - stop the services
        cleanup_cmd = [
            "docker",
            "compose",
            "-f",
            compose_files[0],
            "-f",
            compose_files[1],
            "down",
        ]
        print(f"Cleaning up with command: {' '.join(cleanup_cmd)}")
        subprocess.run(cleanup_cmd, cwd=str(project_root), check=True)


@pytest.fixture(scope="session")
def page_url(app_container) -> str:
    """
    Returns the base URL of the running application.
    """
    host_port = app_container.host_port
    return f"http://localhost:{host_port}/"
