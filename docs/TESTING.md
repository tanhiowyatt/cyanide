# Testing Cyanide

This document outlines the testing infrastructure, strategies, and procedures for the Cyanide Honeypot.

## 1. Prerequisites

Before running tests, ensure you have installed the testing dependencies:

```bash
pip install -r tests/requirements.txt
```

Key dependencies include:
- `pytest`: Main testing framework.
- `pytest-asyncio`: For testing asynchronous code.
- `pytest-cov`: For coverage reporting.
- `pytest-mock`: For mocking objects and functions.

## 2. Test Structure

- **Unit Tests (`tests/`)**: Test individual components in isolation (e.g., `ShellEmulator`, `FakeFilesystem`).
- **Integration Tests (`tests/integration/`)**: Test interactions between multiple components.
- **Smoke Tests (`tests/smoke_test.py`)**: Verify that the application starts and basic services (SSH, Telnet, Metrics) are reachable in a live container.

## 3. Running Tests

### Standard Test Run
To run all unit tests with terminal-only coverage reporting:

```bash
pytest -c tests/pytest.ini
```

### Running Specific Tests
To run a specific test file:

```bash
pytest -c tests/pytest.ini tests/test_shell_emulator.py
```

### Running Smoke Tests
Smoke tests are designed to run against a running container. They verify port availability and health endpoints.

```bash
# In one terminal, start the honeypot
python3 src/cyanide/main.py

# In another terminal, run the smoke test
python3 tests/smoke_test.py
```

## 4. Coverage Reporting

Coverage is configured to output directly to the terminal for fast feedback.

- **Missing Lines**: The report shows specific line numbers that are not covered.
- **Skip Covered**: Files with 100% coverage are hidden from the summary to reduce noise.
- **Threshold**: The project aims for high coverage on core logic.

Configuration is located in `tests/.coveragerc`.

## 5. CI/CD Integration

Tests are automatically executed on every push and pull request via GitHub Actions:
- **`smoke_test.yml`**: Builds the Docker image, runs the container, and executes `smoke_test.py`.
- **`security_scan.yml`**: Scans the Docker image for vulnerabilities using Trivy.

## 6. Writing New Tests

- **Fixtures**: Shared fixtures (like `mock_fs` and `shell`) are defined in `tests/conftest.py`.
- **Async**: Use `@pytest.mark.asyncio` for tests involving `async/await`.
- **Mocking**: Use the `mocker` fixture provided by `pytest-mock` for internal component mocking.
