# 🧪 Testing and Quality Assurance

The Cyanide project maintains a comprehensive, multi-layer verification suite. We strive for a minimum of **70% unit test coverage** and full end-to-end integration coverage for our core emulation engines.

## 📄 Overview
We treat security as a first-class citizen, and our test suite ensures that no logic changes break existing emulated commands or detection signatures. The suite includes low-level unit tests, cross-protocol integration tests, and performance load tests.

## 🛠️ How it Works
1.  **Unit Tests**: Focused on individual components (`pytest tests/unit/`).
2.  **Integration Tests**: Multi-component flows, like the **Malware Flow** (`test_malware_flow.py`).
3.  **CI Pipeline**: Every pull request must pass `black`, `isort`, `ruff`, and reach the coverage target.

## ⚙️ Configuration
Test configurations are typically handled via `pytest` fixtures in `tests/conftest.py`. You can also configure coverage reports and async settings via `pyproject.toml`.

## 📑 Detailed Documents

*   **[Core Unit Tests](../../tests/unit/)**: Structural verification of the VFS, detection engine, and configuration parser.
*   **[Integration Logic](../../tests/integration/)**: Multi-service tests that simulate attacker sessions across SSH and Telnet including MiTM scenarios.
*   **[Smoke Tests](../../tests/integration/smoke_test.py)**: Quick-start verification to ensure the Docker stack is healthy post-deployment.
*   **[Coverage Reports](index.md#coverage-metrics)**: Tracking the project's health via `pytest-cov`.

## 🔗 See Also
*   🏗️ **[Core Engine Architecture](../core/architecture.md)**: Design principles that inform the testing strategy.
*   🔧 **[Operational Testing](../tooling/index.md)**: Using real-world data to drift-test the ML engine.

---
*Last updated: 2026-03-10*
