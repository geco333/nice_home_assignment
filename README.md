# ParaBank Playwright Automation Framework

A production-ready automation framework that validates core banking workflows on [ParaBank](https://parabank.parasoft.com/parabank) using **Python Playwright** for UI testing and **requests** for backend API testing.

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
# Run all tests
pytest

# Run only the E2E banking workflow
pytest tests/e2e/ -m e2e

# Run only negative tests
pytest tests/negative/ -m negative

# Run headed (visible browser)
HEADLESS=false pytest

# Run with verbose output
pytest -v

# Open HTML report after run
open reports/report.html      # Mac
start reports/report.html     # Windows
```

### Docker Execution

```bash
# Build and run with docker-compose
docker-compose up --build

# Reports are mounted to ./reports on the host
```

---

## Design Decisions

### 1. Project Architecture

```
nice_home_assignment/
├── src/
│   ├── config/
│   │   └── environment.py          # Centralized config from .env
│   ├── models/
│   │   ├── customer.py             # Typed dataclasses for Customer, Address
│   │   └── account.py              # Account, Transaction, AccountType
│   ├── pages/
│   │   ├── base_page.py            # Shared navigation & assertion helpers
│   │   ├── register_page.py        # Registration form POM
│   │   ├── login_page.py           # Login form POM
│   │   ├── accounts_overview_page.py
│   │   ├── open_account_page.py
│   │   └── transfer_funds_page.py
│   ├── api/
│   │   ├── api_client.py           # requests.Session wrapper
│   │   ├── customer_api.py         # /login, /customers endpoints
│   │   └── account_api.py          # /accounts, /createAccount (curl), /transfer
│   └── utils/
│       ├── data_factory.py         # Random test data generation
│       └── helpers.py              # Balance parsing, wait utilities
├── tests/
│   ├── conftest.py                 # Shared fixtures (page objects + API clients)
│   ├── e2e/
│   │   └── test_banking_workflow.py  # Full 9-step banking flow
│   └── negative/
│       └── test_negative_scenarios.py  # 5 negative test cases
├── conftest.py                     # Root conftest for browser config
├── Dockerfile
├── docker-compose.yml
├── .github/workflows/ci.yml
├── requirements.txt
├── pyproject.toml
└── .env.example
```

**Layered architecture** with strict separation of concerns:


| Layer        | Purpose                                                                      |
| ------------ | ---------------------------------------------------------------------------- |
| **Models**   | Typed dataclasses representing domain entities — no behavior, just structure |
| **Pages**    | Page Object Model encapsulating UI locators and interactions                 |
| **API**      | `requests`-based REST clients for backend validation                         |
| **Utils**    | Stateless helper functions (data generation, parsing)                        |
| **Config**   | Single source of truth for environment variables                             |
| **Fixtures** | pytest/Playwright fixture composition wiring everything together             |


This means tests read like specifications and contain zero locator strings or HTTP calls directly.

### 2. Dual-Layer Testing Strategy (UI + API)

The framework deliberately mixes UI and API interactions within the same test flow:

- **UI** for user-facing actions (register, login, transfer, logout) — validates the real user experience.
- **API** (`requests`) for data retrieval and verification (customer ID, balances) — faster and more reliable for assertions.
- **curl** subprocess for account creation — as explicitly required by the assignment.

This hybrid approach catches both rendering issues and data-layer bugs.

### 3. Page Object Model (POM)

Each page extends `BasePage`, which provides:

- Navigation helpers with automatic `domcontentloaded` waits
- Text extraction and visibility assertion methods
- Consistent patterns that scale as more pages are added

Locators are class-level constants — easy to update when the DOM changes without modifying test logic.

---

## Tradeoffs


| Decision                       | Benefit                                                                            | Cost                                                                                   |
| ------------------------------ | ---------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| **Single sequential E2E test** | Tests the full flow as a real user would; catches integration issues between steps | Slower than isolated unit tests; a mid-step failure blocks downstream assertions       |
| `**requests` library for API** | Lightweight, well-known, synchronous — matches Playwright sync mode                | Doesn't share Playwright's cookie jar; API calls are independent sessions              |
| **curl via subprocess**        | Meets the assignment requirement verbatim                                          | Platform-dependent (curl must be installed); harder to assert HTTP status codes        |
| **Session-scoped API client**  | One HTTP session reused across tests for efficiency                                | Must be careful with session state between test classes                                |
| `**pytest-playwright` plugin** | Automatic browser/page lifecycle, screenshot-on-failure, tracing                   | Couples the framework to pytest (not a real drawback for most teams)                   |
| **Random test data**           | Each run is independent — no stale-data collisions                                 | Non-deterministic; if a test fails, you need the logs to reproduce the exact data used |


---

## Assumptions

1. **ParaBank is available**: The public instance at `parabank.parasoft.com` is up. The DB may be periodically reset — each test run registers a fresh user so this is not a problem.
2. **One initial account per user**: When a user registers, ParaBank auto-creates one savings/checking account. The E2E test relies on this for the "get existing account" step.
3. **curl is installed**: The assignment requires creating an account via curl command. The framework shells out to `curl` — it must be available in `PATH`.
4. **Transfer amounts are small**: We transfer $5–$50 to avoid overdraft issues on the default initial balance.
5. **Chromium-only**: Tests target Chromium. Multi-browser can be enabled by adding projects to `pyproject.toml` / `conftest.py`.

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
- A single `EnvironmentConfig` frozen dataclass is the only place that reads `os.getenv`.
- Multiple environments (dev, staging, prod) are supported by swapping `.env` files or passing env vars at runtime.
- Sensitive data (if any) stays in `.env` which is `.gitignore`d; `.env.example` documents the schema.
- In CI, environment variables are injected directly — no files needed.

### Reporting & Debugging

- **pytest-html** generates a self-contained HTML report after every run.
- **Playwright traces** are captured on first retry (`trace: on-first-retry`), providing a full timeline of network calls, DOM snapshots, and console logs.
- **Screenshots** are auto-captured on failure.
- **Video recording** is retained on failure for visual debugging.
- In CI, reports and traces are uploaded as **GitHub Actions artifacts** with 14-day retention.
- Verbose pytest output (`-v`) and structured assertions give clear failure messages pinpointing exactly which step and value failed.

### CI Implementation

The GitHub Actions workflow (`.github/workflows/ci.yml`):

1. Triggers on push/PR to `main`.
2. Sets up Python 3.11 and installs dependencies + Playwright browsers.
3. Runs the full test suite with environment variables injected.
4. Uploads HTML reports and test artifacts regardless of pass/fail.
5. 30-minute timeout prevents runaway jobs.

For larger teams, this extends naturally to:

- **Matrix builds** across Python versions or browser engines.
- **Sharding** via `pytest-xdist` for parallel execution.
- **Scheduled nightly runs** for regression.
- **Slack/Teams notifications** on failure via GitHub Actions integrations.

### Dockerization

The `Dockerfile` uses Microsoft's official `playwright/python` image which includes all browser dependencies pre-installed:

- **Reproducible**: identical environment locally and in CI — no "works on my machine" issues.
- **docker-compose** mounts `reports/` and `test-results/` volumes so artifacts are accessible on the host.
- For teams with internal registries, the image can be pushed and reused across pipelines.
- Environment variables are injected at `docker-compose` level, making it easy to point at different target environments.

### How to Scale

1. **More tests**: Add files under `tests/`. Page objects and API clients are already reusable.
2. **More pages**: Add a class in `src/pages/` extending `BasePage` and a fixture in `conftest.py`.
3. **Parallel execution**: Enable `pytest-xdist` with `pytest -n auto`. Each worker gets its own browser context and registers its own user, so tests are isolated.
4. **Cross-browser**: Add Firefox/WebKit projects in the Playwright config.
5. **Data-driven tests**: Use `@pytest.mark.parametrize` with the data factory.
6. **Multiple environments**: Swap `.env` files or use `ENV=staging pytest` to switch targets.
7. **Visual regression**: Add `pytest-playwright-visual` for screenshot comparison.
8. **API contract testing**: Validate response JSON against schemas using `jsonschema` or Pydantic.

