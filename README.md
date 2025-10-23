# PyAutoPytest

A Python-based test automation framework using Pytest, Playwright, and Requests for comprehensive UI and API testing.

## Features

- **Multi-layer architecture**: Separated infrastructure, base classes, helpers, and project-specific code
- **Multiple test types**: Support for UI (web), API, and mobile testing (mobile in progress)
- **Environment configuration**: YAML-based config files for different environments (dev, staging, prod)
- **Page Object Model**: Clean page object implementation for maintainable UI tests
- **Playwright integration**: Modern browser automation with auto-waiting and multi-browser support
- **API testing**: Requests-based API client with session management
- **Test data generation**: Faker integration for generating realistic test data
- **Pytest integration**: Full pytest features including markers, fixtures, and parallel execution
- **CI/CD ready**: GitHub Actions workflow for automated testing

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

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Install Playwright browsers:
```bash
python -m playwright install --with-deps
```

> **Note**: The `--with-deps` flag installs system dependencies required by browsers. On CI/CD systems, this ensures all dependencies are available. For local development, you can use `python -m playwright install` if system dependencies are already installed.

4. Set up environment configuration:
```bash
cp .env.example .env
# Edit .env with your settings
```

## Configuration

### Environment Variables

Configure the test environment by creating a `.env` file:

```env
ENV=dev                    # Environment: dev, staging, or prod
BROWSER=chrome             # Browser: chrome, firefox, webkit (Playwright)
BROWSER_HEADLESS=true      # Run browser in headless mode (default: true)
```

> **Note**: Playwright runs in headless mode by default for efficiency in CI/CD environments. Set `BROWSER_HEADLESS=false` for local debugging with visible browser.

### Environment-Specific Configs

Edit YAML files in `test-automation/infra/config/` to configure environment-specific settings:

- `dev.yaml`: Development environment
- `staging.yaml`: Staging environment  
- `prod.yaml`: Production environment

**Configuration keys:**
- `base_url`: Application base URL
- `browser`: Default browser (chrome/firefox/webkit for Playwright)
- `implicit_wait`: Default wait timeout (seconds)
- `explicit_wait`: Explicit wait timeout (seconds)
- `headless`: Run browser in headless mode (true/false) - can be overridden by `BROWSER_HEADLESS` env var
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

### Test Architecture: Project Facades Pattern

**⭐ New Pattern (Recommended)**: Tests use high-level facades that encapsulate all page/API/mobile interactions. This keeps tests clean and maintainable by moving all action logic to project modules.

**Key Principle**: Test code should contain only:
1. High-level actions via facades (e.g., `self.web.inspection_portal.login()`)
2. Assertions
3. Test data

All interaction logic (clicks, fills, API calls, waits) lives in project facades and page objects.

### Project Facades

The framework provides three main facade types automatically attached to test class instances:

- **`self.web`**: Web UI facades (e.g., `self.web.inspection_portal`)
- **`self.api`**: API facades (e.g., `self.api.facility_portal`)
- **`self.appium`**: Mobile app facades (e.g., `self.appium.inspector_mobile`)

### UI Test Example (New Pattern)

```python
import pytest

@pytest.mark.ui
@pytest.mark.web
class TestLogin:
    """Tests automatically get self.web, self.api, self.appium from fixtures."""
    
    def test_successful_login(self, page):
        # High-level action - all page interactions hidden in facade
        self.web.inspection_portal.login('test_user', 'test_password')
        
        # Simple assertion
        assert self.web.inspection_portal.is_logged_in()
```

### API Test Example (New Pattern)

```python
import pytest

@pytest.mark.api
class TestFacilityApi:
    def test_get_facilities(self, requests_session):
        # High-level action - all HTTP logic hidden in facade
        facilities = self.api.facility_portal.get_facilities()
        
        # Simple assertion
        assert isinstance(facilities, list)
```

### Mobile Test Example (New Pattern)

```python
import pytest

@pytest.mark.mobile
class TestInspectionForm:
    def test_submit_inspection(self, appium_driver):
        # High-level action - all Appium logic hidden in facade
        result = self.appium.inspector_mobile.submit_inspection({
            'title': 'Test Inspection',
            'notes': 'Test notes'
        })
        
        # Simple assertion
        assert result['success'] is True
```

### Old Pattern (Page Objects in Tests)

The old pattern with direct page object usage in tests is still supported but not recommended:

```python
import pytest
from projects.inspection_portal.pages.login_page import LoginPage

@pytest.mark.ui
@pytest.mark.web
class TestLogin:
    def test_login(self, navigate_to, framework_page):
        navigate_to("/login")
        
        login_page = LoginPage(framework_page)
        login_page.login("username", "password")
        
        assert "dashboard" in framework_page.url
```

### Creating New Project Facades

When adding a new project, create a facade class:

```python
# projects/my_project/facade.py
from playwright.sync_api import Page
from projects.my_project.pages.home_page import HomePage

class MyProjectWebFacade:
    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url
        self.home_page = HomePage(page)
    
    def navigate_home(self) -> None:
        """Navigate to home page."""
        self.page.goto(f"{self.base_url}/home")
    
    def perform_action(self, data: dict) -> bool:
        """High-level action encapsulating multiple page interactions."""
        self.navigate_home()
        self.home_page.fill_form(data)
        self.home_page.submit()
        return self.home_page.is_success_displayed()
```

Then register it in `tests/conftest.py` in the `attach_facades` fixture.

### UI Test Example (Direct Playwright)

For simple cases, you can still use Playwright directly:

```python
import pytest

@pytest.mark.ui
@pytest.mark.web
class TestLogin:
    def test_login(self, navigate_to, framework_page):
        # Navigate to page using helper fixture
        navigate_to("/login")
        
        # Use Playwright Page API directly
        framework_page.fill("#username", "test_user")
        framework_page.fill("#password", "test_pass")
        framework_page.click("#login-button")
        
        # Assert
        assert "dashboard" in framework_page.url
```

Or using Page Objects:

```python
import pytest
from projects.inspection_portal.pages.login_page import LoginPage

@pytest.mark.ui
@pytest.mark.web
class TestLogin:
    def test_login(self, navigate_to, framework_page):
        navigate_to("/login")
        
        login_page = LoginPage(framework_page)
        login_page.login("username", "password")
        
        assert "dashboard" in framework_page.url
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
2. Define selectors as class attributes (CSS selectors or XPath)
3. Implement page-specific methods

```python
from playwright.sync_api import Page
from infra.base.base_page import BasePage

class MyPage(BasePage):
    # Define selectors (CSS, XPath, or other Playwright selectors)
    BUTTON = "#my-button"
    INPUT_FIELD = "input[name='search']"
    
    def __init__(self, page: Page):
        super().__init__(page)
    
    def click_button(self):
        self.click(self.BUTTON)
    
    def enter_search_text(self, text: str):
        self.fill(self.INPUT_FIELD, text)
```

## TODO Items

The following items need to be completed for production use:

### Infrastructure
- [x] ~~Add Selenium for browser automation~~ Migrated to Playwright
- [x] Set up CI/CD integration (GitHub Actions)
- [ ] Implement screenshot capture on test failure (partially done via pytest-playwright)
- [ ] Add video recording for test runs (available via pytest-playwright config)
- [ ] Add Appium integration for mobile testing

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

- ✅ Chromium (using Playwright)
- ✅ Firefox (using Playwright)
- ✅ WebKit/Safari (using Playwright)
- ✅ Chrome & Edge (Chromium-based, using Playwright)

Playwright provides consistent cross-browser automation with a single API.

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
