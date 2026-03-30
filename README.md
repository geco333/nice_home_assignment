# ParaBank Playwright Automation Framework

A production-ready automation framework that validates core banking workflows on [ParaBank](https://parabank.parasoft.com/parabank) using **Python Playwright** for UI testing and **requests** for backend API testing, with **Allure** for rich test reporting.

---

## Setup & Execution

### Prerequisites

- Python 3.11+
- `pip`
- `curl` (for the account-creation step that uses curl as required)

### Local Setup

```bash
# 1. Clone the repository
git clone <repo-url> && cd nice_home_assignment

# 2. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install Playwright browsers
python -m playwright install --with-deps chromium

# 5. Copy and optionally edit environment config
cp .env.example .env
```

### Running Tests

```bash
# Run all tests (sequential)
pytest

# Run only the E2E banking workflow
pytest tests/e2e/ -m e2e

# Run only negative tests
pytest tests/negative/ -m negative

# Run headed (visible browser)
HEADLESS=false pytest

# Run in all test suites in parallel
pytest -vs -n auto --dist loadfile
```

### Parallel Execution with pytest-xdist

The project includes `pytest-xdist` for parallel test execution. Use the `-n` flag to specify the number of workers:

```bash
# Auto-detect number of CPU cores
pytest -n auto

# Use a specific number of workers
pytest -n 4

# Distribute tests by file (recommended) — keeps tests within the same file
# on the same worker, preserving shared_context ordering for E2E flows
pytest -n auto --dist loadfile

# Parallel negative tests only (these are fully independent)
pytest tests/negative/ -n auto
```

> **Important:** The E2E tests in `test_banking_workflow.py` use a class-scoped `shared_context` to pass state between sequential steps (e.g., customer ID, account IDs). When running in parallel, use `--dist loadfile` to ensure all tests in a file execute on the same worker and maintain correct ordering. Without it, tests may fail with `KeyError` due to missing context.

### Viewing Reports

```bash
# Generate and open the Allure report
allure serve reports/allure-results
```

### Docker Compose Execution

The `docker-compose.yml` includes a full **Selenium Grid** (Hub + Chrome/Edge nodes) and a test runner service. Tests execute inside a container using the Chrome browser provided by the Selenium Grid node.

```bash
# Build and run all services (Selenium Grid + tests)
docker-compose up --build

# Run in detached mode and follow test output
docker-compose up --build -d
docker-compose logs -f tests

# Stop and clean up all containers
docker-compose down

# Rebuild only the tests service (after code changes)
docker-compose up --build tests
```

Reports are mounted to the host via volumes:
- `./reports/allure-results` — Allure raw results
- `./reports/screenshots` — Failure screenshots
- `./reports/logs` — Timestamped log files
- `./test-results` — Playwright traces

After the run completes, generate the Allure report from the host:

```bash
allure serve reports/allure-results
```

---

## Design Decisions

### 1. Project Architecture

```
nice_home_assignment/
├── src/
│   ├── config/
│   │   └── environment.py          # Dynamic config from .env (auto-cast)
│   ├── models/
│   │   ├── customer.py             # Typed dataclasses: Customer, Address, LoginCredentials
│   │   └── account.py              # Account, Transaction, AccountType enum
│   ├── pages/
│   │   ├── base_page.py            # Navigation helpers + auto-retry via __init_subclass__
│   │   ├── register_page.py        # Registration form POM
│   │   ├── login_page.py           # Login form POM
│   │   ├── accounts_overview_page.py  # Accounts table POM
│   │   ├── open_account_page.py    # New account creation POM
│   │   └── transfer_funds_page.py  # Fund transfer POM
│   ├── api/
│   │   ├── api_client.py           # requests.Session wrapper (JSON, TLS bypass)
│   │   ├── customer_api.py         # /login, /customers, registration via form POST
│   │   └── account_api.py          # /accounts, /createAccount (curl), /transfer
│   └── utils/
│       ├── data_factory.py         # Random test data generation (Faker-free)
│       ├── helpers.py              # Balance parsing, wait utilities
│       └── retry.py                # Global retry decorator for Playwright timeouts
├── tests/
│   ├── conftest.py                 # Fixtures, hooks, logging, Allure, screenshot-on-fail
│   ├── e2e/
│   │   └── test_banking_workflow.py  # Full 9-step banking flow (UI + API classes)
│   └── negative/
│       └── test_negative_scenarios.py  # 5 negative test cases (UI + API classes)
├── Dockerfile
├── docker-compose.yml              # Selenium Grid (Hub + Chrome/Edge nodes) + test runner
├── Jenkinsfile                     # CI/CD pipeline definition
├── .github/workflows/ci.yml       # GitHub Actions workflow
├── requirements.txt
├── pyproject.toml                  # pytest & Ruff configuration
└── .env.example                    # Environment variable schema
```

**Layered architecture** with strict separation of concerns:

| Layer        | Purpose                                                                      |
| ------------ | ---------------------------------------------------------------------------- |
| **Models**   | Typed dataclasses representing domain entities — no behavior, just structure |
| **Pages**    | Page Object Model encapsulating UI locators and interactions                 |
| **API**      | `requests`-based REST clients for backend validation                         |
| **Utils**    | Stateless helper functions (data generation, parsing, retry decorator)       |
| **Config**   | Dynamic attribute-based access to environment variables with auto-casting    |
| **Fixtures** | pytest/Playwright fixture composition wiring everything together             |

Tests read like specifications and contain zero locator strings or HTTP calls directly.

### 2. Dual-Layer Testing Strategy (UI + API)

The framework deliberately mixes UI and API interactions within the same test flow:

- **UI** for user-facing actions (register, login, transfer, logout) — validates the real user experience.
- **API** (`requests`) for data retrieval and verification (customer ID, balances) — faster and more reliable for assertions.
- **curl** subprocess for account creation — as explicitly required by the assignment.
- **API registration** (`requests` form POST) for non-UI test setup — faster and avoids unnecessary UI coupling.

This hybrid approach catches both rendering issues and data-layer bugs.

### 3. Page Object Model (POM)

Each page extends `BasePage`, which provides:

- Navigation helpers with automatic `domcontentloaded` waits
- **Global retry mechanism** via `__init_subclass__` — every public method on every POM subclass is automatically wrapped with a retry decorator that catches `playwright.TimeoutError` and retries configurable times (default 3) with a delay (default 1s)
- Selectors as class-level constants — easy to update when the DOM changes without modifying test logic

### 4. Shared Context for E2E Workflows

Within each E2E test class, a class-scoped `shared_context` dict passes data between ordered tests (e.g., customer ID, account IDs). Each test also includes **data recovery logic**: if run independently (without prior tests populating the context), it provisions the required data itself via API calls, ensuring every test can pass in isolation.

### 5. Allure Reporting

- Per-test **log slices** attached as text (named after the log file)
- **`shared_context` snapshot** attached as JSON to each test
- **Full-page screenshots** captured and attached on test failure
- Results directory is configurable via `ALLURE_RESULTS_DIR` environment variable

### 6. Dynamic Configuration

`EnvironmentConfig` uses `__getattr__` to read any environment variable on demand:

```python
ENV.base_url      # reads BASE_URL
ENV.headless      # reads HEADLESS → auto-cast to bool
ENV.retry_count   # reads RETRY_COUNT → auto-cast to int
```

No class updates needed when adding new variables — just add them to `.env`.

---

## Tradeoffs

| Decision                       | Benefit                                                                            | Cost                                                                                   |
| ------------------------------ | ---------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| **Sequential E2E tests**       | Tests the full flow as a real user would; catches integration issues between steps | Slower than isolated unit tests; a mid-step failure blocks downstream assertions. Use `--dist loadfile` with `pytest-xdist` to parallelize across files while keeping intra-file order |
| **`requests` for API**         | Lightweight, well-known, synchronous — matches Playwright sync mode                | Doesn't share Playwright's cookie jar; API calls are independent sessions              |
| **curl via subprocess**        | Meets the assignment requirement verbatim                                          | Platform-dependent (curl must be installed); harder to assert HTTP status codes        |
| **Session-scoped API client**  | One HTTP session reused across tests for efficiency                                | Must be careful with session state between test classes                                |
| **`pytest-playwright` plugin** | Automatic browser/page lifecycle, tracing support                                  | Couples the framework to pytest (not a real drawback for most teams)                   |
| **Random test data**           | Each run is independent — no stale-data collisions                                 | Non-deterministic; if a test fails, you need the logs to reproduce the exact data used |
| **Global retry on POMs**       | Handles transient Playwright timeouts without per-call boilerplate                 | Masks genuine slowness; may slow failure detection by retry count × delay              |
| **Allure over pytest-html**    | Rich interactive reports with attachments, steps, history                           | Requires Allure CLI to view; heavier than a single HTML file                           |

---

## Assumptions

1. **ParaBank is available**: The public instance at `parabank.parasoft.com` is up. The DB may be periodically reset — each test run registers a fresh user so this is not a problem.
2. **One initial account per user**: When a user registers, ParaBank auto-creates one savings/checking account. The E2E test relies on this for the "get existing account" step.
3. **curl is installed**: The assignment requires creating an account via curl command. The framework shells out to `curl` — it must be available in `PATH`.
4. **Transfer amounts are small**: We transfer $5–$50 to avoid overdraft issues on the default initial balance.
5. **Chromium-only**: Tests target Chromium. Multi-browser can be enabled by adding projects to `pyproject.toml` / `conftest.py`.

---

## Environment Variables

All configuration is read from `.env` (or exported shell variables). See `.env.example` for the full schema:

| Variable             | Description                        | Default in `.env.example`               |
| -------------------- | ---------------------------------- | --------------------------------------- |
| `BASE_URL`           | ParaBank web UI root URL           | `https://parabank.parasoft.com/parabank` |
| `API_BASE_URL`       | ParaBank REST API root URL         | `.../parabank/services/bank`             |
| `HEADLESS`           | Run browser headless               | `true`                                   |
| `SLOW_MO`            | Milliseconds to slow Playwright    | `0`                                      |
| `TIMEOUT`            | Default Playwright timeout (ms)    | `30000`                                  |
| `RETRY_COUNT`        | POM method retry attempts          | `3`                                      |
| `RETRY_DELAY`        | Seconds between retries            | `1.0`                                    |
| `SCREENSHOT_DIR`     | Directory for failure screenshots  | `reports/screenshots`                    |
| `ALLURE_RESULTS_DIR` | Allure raw results directory       | `reports/allure-results`                 |
| `LOG_DIR`            | Directory for timestamped log files| `reports/logs`                           |

---

## Infrastructure Considerations

### Project Architecture

The framework follows a **layered architecture** separating test logic from infrastructure:

- **Source layer** (`src/`) contains zero test logic — only reusable building blocks (pages, API clients, models, config).
- **Test layer** (`tests/`) contains only test scenarios, composed from source-layer fixtures.
- A new test requires only a new file in `tests/` using existing page objects and API clients.
- Adding a new page/endpoint means adding one file in `src/pages/` or `src/api/` — existing tests are unaffected.

This ensures the framework scales linearly: 10 tests or 1,000 tests have the same architectural footprint.

### Configuration Management

- **Environment variables** via `.env` files, loaded by `python-dotenv`.
- A dynamic `EnvironmentConfig` class reads variables on attribute access with automatic type casting — no class modifications needed for new variables.
- Multiple environments (dev, staging, prod) are supported by swapping `.env` files or passing env vars at runtime.
- Sensitive data stays in `.env` which is `.gitignore`d; `.env.example` documents the schema.
- In CI, environment variables are injected directly — no files needed.

### Reporting & Debugging

- **Allure Report** with per-test log slices, shared context snapshots, and failure screenshots attached as rich artifacts.
- **Timestamped log files** in `reports/logs/` with structured `[timestamp][logger][level]` format for post-mortem analysis.
- **Full-page screenshots** auto-captured on test failure and attached to the Allure report.
- In CI, reports and traces are uploaded as **build artifacts** with configurable retention.
- Verbose pytest output and structured assertions give clear failure messages pinpointing exactly which step and value failed.

### CI Implementation

**Jenkins Pipeline** (`Jenkinsfile`):

1. Parameterized for environment selection (dev/staging/production).
2. Installs dependencies and Playwright browsers.
3. Runs negative tests first, then E2E tests.
4. On success, builds and pushes a Docker image to the configured registry.
5. Publishes Allure report and archives all reports.

For larger teams, this extends naturally to:

- **Matrix builds** across Python versions or browser engines.
- **Sharding** via `pytest-xdist` for parallel execution.
- **Scheduled nightly runs** for regression.
- **Slack/Teams notifications** on failure via CI integrations.

### Dockerization

The `Dockerfile` uses `python:3.11-bookworm` as the base image with Playwright and Chromium installed via `playwright install --with-deps chromium`. Dependencies are installed using `uv` for faster builds.

- **Reproducible**: identical environment locally and in CI — no "works on my machine" issues.
- **docker-compose** includes a full **Selenium Grid** (Hub + Chrome/Edge nodes). The `SE_NODE_GRID_URL` setting on each node enables CDP WebSocket routing through the Hub, allowing Playwright to connect to remote browsers via the grid.
- When `SELENIUM_REMOTE_URL` is set in the `tests` service, Playwright uses the Selenium Grid's Chrome browser. Without it, Playwright uses its bundled Chromium.
- `reports/` and `test-results/` volumes are mounted to the host so artifacts (Allure results, screenshots, logs) are accessible after the run.
- For teams with internal registries, the image can be pushed and reused across pipelines.
- Environment variables are injected at `docker-compose` level, making it easy to point at different target environments.

### How to Scale

1. **More tests**: Add files under `tests/`. Page objects and API clients are already reusable.
2. **More pages**: Add a class in `src/pages/` extending `BasePage` — the retry mechanism is applied automatically.
3. **Parallel execution**: Use `pytest-xdist` with `pytest -n auto --dist loadfile`. The `loadfile` strategy keeps tests from the same file on the same worker, preserving sequential `shared_context` flows while parallelizing across files. In Docker, update the `CMD` in the Dockerfile to include `-n auto --dist loadfile`.
4. **Cross-browser**: Add Firefox/WebKit projects in the Playwright config, or use the Selenium Grid in `docker-compose.yml` which already includes Chrome and Edge nodes.
5. **Data-driven tests**: Use `@pytest.mark.parametrize` with the data factory.
6. **Multiple environments**: Swap `.env` files or use `ENV=staging pytest` to switch targets.
7. **Visual regression**: Add `pytest-playwright-visual` for screenshot comparison.
8. **API contract testing**: Validate response JSON against schemas using `jsonschema` or Pydantic.
