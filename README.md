# PyAutoPytest

A Python-based test automation framework using Pytest, Selenium, and Requests for comprehensive UI and API testing.

## Features

- **Multi-layer architecture**: Separated infrastructure, base classes, helpers, and project-specific code
- **Multiple test types**: Support for UI (web), API, and mobile testing (mobile in progress)
- **Environment configuration**: YAML-based config files for different environments (dev, staging, prod)
- **Page Object Model**: Clean page object implementation for maintainable UI tests
- **API testing**: Requests-based API client with session management
- **Test data generation**: Faker integration for generating realistic test data
- **Pytest integration**: Full pytest features including markers, fixtures, and parallel execution

## Project Structure

```
test-automation/
├── infra/                      # Core infrastructure
│   ├── core/                   # Core components
│   │   ├── config_manager.py   # YAML configuration loader
│   │   ├── driver_factory.py   # WebDriver factory
│   │   ├── driver_manager.py   # Driver lifecycle manager
│   │   ├── driver_bundle.py    # Driver container
│   │   └── test_context.py     # Test context dataclass
│   ├── base/                   # Base classes
│   │   ├── base_test.py        # Base test class
│   │   ├── base_page.py        # Base page object
│   │   ├── base_api.py         # Base API client
│   │   └── base_mobile_page.py # Base mobile page (TODO)
│   ├── helpers/                # Helper utilities
│   │   ├── web_helper.py       # Web interaction helpers
│   │   ├── api_helper.py       # API request helpers
│   │   └── mobile_helper.py    # Mobile helpers (TODO)
│   ├── utils/                  # Utility modules
│   │   ├── logger.py           # Logging configuration
│   │   ├── wait_helper.py      # WebDriver wait utilities
│   │   └── data_generator.py   # Test data generation
│   └── config/                 # Environment configs
│       ├── dev.yaml
│       ├── staging.yaml
│       └── prod.yaml
├── projects/                   # Project-specific code
│   └── inspection_portal/
│       ├── config.py           # Project configuration
│       ├── pages/              # Page objects
│       │   ├── login_page.py
│       │   └── dashboard_page.py
│       ├── api/                # API clients
│       │   └── auth_api.py
│       └── models/             # Data models
│           └── inspection.py
└── tests/                      # Test cases
    ├── ui/                     # UI tests
    │   └── web/
    │       └── inspection_portal/
    │           └── test_login.py
    ├── api/                    # API tests
    │   └── inspection_portal/
    │       └── test_auth_api.py
    └── mobile/                 # Mobile tests (TODO)
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Khalilassi/PyAutoPytest.git
cd PyAutoPytest
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment configuration:
```bash
cp .env.example .env
# Edit .env with your settings
```

## Configuration

### Environment Variables

Configure the test environment by creating a `.env` file:

```env
ENV=dev          # Environment: dev, staging, or prod
BROWSER=chrome   # Browser: chrome or firefox
```

### Environment-Specific Configs

Edit YAML files in `test-automation/infra/config/` to configure environment-specific settings:

- `dev.yaml`: Development environment
- `staging.yaml`: Staging environment  
- `prod.yaml`: Production environment

**Configuration keys:**
- `base_url`: Application base URL
- `browser`: Default browser (chrome/firefox)
- `implicit_wait`: Implicit wait timeout (seconds)
- `explicit_wait`: Explicit wait timeout (seconds)
- `headless`: Run browser in headless mode (true/false)
- `window_size`: Browser window size (e.g., "1920x1080")

## Running Tests

### Run all tests:
```bash
pytest
```

### Run specific test types:
```bash
# UI tests only
pytest -m ui

# API tests only
pytest -m api

# Web tests only
pytest -m web
```

### Run specific test file:
```bash
pytest test-automation/tests/ui/web/inspection_portal/test_login.py
```

### Run tests in parallel:
```bash
pytest -n auto
```

### Run with HTML report:
```bash
pytest --html=report.html --self-contained-html
```

## Writing Tests

### UI Test Example

```python
from infra.base.base_test import BaseTest
from projects.inspection_portal.pages.login_page import LoginPage

class TestLogin(BaseTest):
    def test_login(self):
        # Navigate to page
        self.navigate_to("/login")
        
        # Use page object
        login_page = LoginPage(self.driver)
        login_page.login("username", "password")
        
        # Assert
        assert "dashboard" in self.driver.current_url
```

### API Test Example

```python
import pytest
from projects.inspection_portal.api.auth_api import AuthApi

class TestAuthApi:
    @pytest.fixture
    def auth_api(self):
        return AuthApi("https://api.example.com")
    
    def test_login(self, auth_api):
        response = auth_api.login("username", "password")
        assert "token" in response
```

## Creating New Page Objects

1. Inherit from `BasePage`
2. Define locators as class attributes
3. Implement page-specific methods

```python
from selenium.webdriver.common.by import By
from infra.base.base_page import BasePage

class MyPage(BasePage):
    # Define locators
    BUTTON = (By.ID, "my-button")
    
    def click_button(self):
        self.click(self.BUTTON)
```

## TODO Items

The following items need to be completed for production use:

### Infrastructure
- [ ] Add Appium integration for mobile testing
- [ ] Implement screenshot capture on test failure
- [ ] Add video recording for test runs
- [ ] Set up CI/CD integration examples

### Projects
- [ ] **Update page object selectors**: Replace placeholder selectors with actual application selectors
- [ ] **Add real test credentials**: Use proper test accounts (DO NOT commit real credentials)
- [ ] **Update API endpoints**: Match actual API endpoint paths and payloads
- [ ] **Complete mobile page implementations**: Add Appium-based mobile page objects

### Tests
- [ ] Add more comprehensive test scenarios
- [ ] Implement data-driven testing examples
- [ ] Add visual regression testing
- [ ] Create smoke test suite

## Security Notes

⚠️ **IMPORTANT**: This repository contains only placeholder values for demonstration purposes.

**Before using in production:**
1. Replace all placeholder URLs, credentials, and selectors with real values
2. Use environment variables or secure vaults for sensitive data
3. Never commit credentials, tokens, or secrets to version control
4. Use the `.env` file (already gitignored) for local configuration
5. Configure proper secrets management in your CI/CD pipeline

## Browser Support

- ✅ Chrome (using ChromeDriver via webdriver-manager)
- ✅ Firefox (using GeckoDriver via webdriver-manager)
- 🔄 Safari (TODO)
- 🔄 Edge (TODO)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add/update tests
5. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

For issues and questions, please open an issue on GitHub.

---

**Happy Testing! 🚀**
