# PyAutoPytest Test Automation Framework

A comprehensive test automation framework built with Python and Pytest for web, API, and mobile testing.

## 🚀 Features

- **Multi-Platform Testing**: Support for Web (Selenium), API (Requests), and Mobile (Appium)
- **Modular Architecture**: Clean separation of concerns with infra, projects, and tests
- **Configuration Management**: Environment-specific YAML configurations (dev, staging, prod)
- **Page Object Model**: Structured page/screen objects for maintainable test code
- **Facade Pattern**: Simplified high-level test interfaces
- **Parallel Execution**: Run tests in parallel with pytest-xdist
- **Rich Reporting**: HTML reports and Allure integration
- **Flexible Test Organization**: Markers for smoke, regression, integration, and project-specific tests

## 📁 Project Structure

```
test-automation/
├── infra/              # Core framework infrastructure
│   ├── core/          # Driver management, configuration, test context
│   ├── base/          # Base classes for tests, pages, and API
│   ├── helpers/       # Helper utilities for web, API, mobile
│   ├── facades/       # High-level test facades
│   ├── utils/         # Logger, wait helpers, data generators
│   └── config/        # Environment configurations (YAML)
│
├── projects/          # Project-specific implementations
│   ├── inspection_portal/
│   ├── facility_portal/
│   ├── inspector_mobile/
│   └── balag_tegary/
│
├── tests/            # Test cases
│   ├── api/         # API tests
│   ├── ui/          # UI tests (web and mobile)
│   └── integration/ # Integration tests
│
├── pytest.ini        # Pytest configuration
├── requirements.txt  # Python dependencies
└── .env.example     # Environment variables template
```

## 🛠️ Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd test-automation
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## 🧪 Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test Categories
```bash
# API tests only
pytest -m api

# Web UI tests only
pytest -m web

# Mobile tests only
pytest -m mobile

# Smoke tests
pytest -m smoke

# Specific project tests
pytest -m inspection_portal
```

### Run Tests by Path
```bash
# All API tests
pytest tests/api/

# Specific project tests
pytest tests/ui/web/inspection_portal/

# Single test file
pytest tests/api/inspection_portal/test_auth_api.py
```

### Parallel Execution
```bash
pytest -n auto
```

### Generate HTML Report
```bash
pytest --html=report.html --self-contained-html
```

## 🔧 Configuration

### Environment Selection
Set the `TEST_ENV` variable in `.env` file:
- `dev` - Development environment
- `staging` - Staging environment
- `prod` - Production environment

### YAML Configurations
Environment-specific configurations are located in `infra/config/`:
- `dev.yaml` - Development settings
- `staging.yaml` - Staging settings
- `prod.yaml` - Production settings

## 📝 Writing Tests

### API Test Example
```python
import pytest
from projects.inspection_portal.api.auth_api import AuthAPI

class TestAuthAPI:
    def test_login_success(self):
        auth_api = AuthAPI()
        response = auth_api.login("user@example.com", "password")
        assert response.status_code == 200
```

### Web UI Test Example
```python
import pytest
from projects.inspection_portal.pages.login_page import LoginPage

class TestLogin:
    def test_login_success(self, driver):
        login_page = LoginPage(driver)
        login_page.navigate()
        login_page.login("user@example.com", "password")
        assert login_page.is_logged_in()
```

## 🧩 Framework Components

### Infra Layer
- **core**: Driver management and configuration
- **base**: Base classes for inheritance
- **helpers**: Utility functions
- **facades**: Simplified high-level interfaces
- **utils**: Logging, waiting, data generation

### Projects Layer
- Project-specific page objects, API clients, and models
- Each project has its own configuration

### Tests Layer
- Organized by test type (API, UI, integration)
- Further organized by project

## 📊 Test Markers

- `@pytest.mark.smoke` - Quick smoke tests
- `@pytest.mark.regression` - Full regression suite
- `@pytest.mark.api` - API tests
- `@pytest.mark.ui` - UI tests
- `@pytest.mark.web` - Web UI tests
- `@pytest.mark.mobile` - Mobile tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.slow` - Long-running tests

## 🤝 Contributing

1. Follow the existing project structure
2. Write tests for new features
3. Ensure all tests pass before submitting
4. Follow PEP 8 style guidelines

## 📄 License

[Add your license information here]

## 📧 Contact

[Add contact information here]
