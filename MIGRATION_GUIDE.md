# Migration Guide: Selenium to Playwright

This guide helps you migrate existing Selenium-based tests to Playwright in the PyAutoPytest framework.

## Overview

The PyAutoPytest framework has been migrated from Selenium to Playwright for better reliability, performance, and cross-browser support. This guide covers what changed and how to update your tests.

## What Changed

### 1. Dependencies

**Before (Selenium):**
```txt
selenium==4.16.0
webdriver-manager==4.0.1
```

**After (Playwright):**
```txt
playwright>=1.35.0
pytest-playwright>=0.5.2
```

### 2. Installation

**Before:**
```bash
pip install -r requirements.txt
```

**After:**
```bash
pip install -r requirements.txt
python -m playwright install --with-deps
```

### 3. Test Class Structure

**Before (BaseTest):**
```python
from infra.base.base_test import BaseTest
from projects.inspection_portal.pages.login_page import LoginPage

class TestLogin(BaseTest):
    def test_login(self):
        self.navigate_to("/login")
        login_page = LoginPage(self.driver)
        login_page.login("user", "pass")
        assert "dashboard" in self.driver.current_url
```

**After (pytest-playwright fixtures):**
```python
import pytest
from projects.inspection_portal.pages.login_page import LoginPage

@pytest.mark.ui
@pytest.mark.web
class TestLogin:
    def test_login(self, navigate_to, framework_page):
        navigate_to("/login")
        login_page = LoginPage(framework_page)
        login_page.login("user", "pass")
        assert "dashboard" in framework_page.url
```

### 4. Page Object Locators

**Before (Selenium By locators):**
```python
from selenium.webdriver.common.by import By
from infra.base.base_page import BasePage

class LoginPage(BasePage):
    USERNAME_INPUT = (By.ID, "username")
    PASSWORD_INPUT = (By.ID, "password")
    
    def __init__(self, driver):
        super().__init__(driver)
```

**After (Playwright selectors):**
```python
from playwright.sync_api import Page
from infra.base.base_page import BasePage

class LoginPage(BasePage):
    USERNAME_INPUT = "#username"  # CSS selector
    PASSWORD_INPUT = "#password"
    
    def __init__(self, page: Page):
        super().__init__(page)
```

### 5. Element Interactions

**Before (Selenium):**
```python
# In page object
self.type_text(self.USERNAME_INPUT, username)
self.click(self.LOGIN_BUTTON)
text = self.get_text(self.WELCOME_MSG)
visible = self.is_element_visible(self.ERROR_MSG)
```

**After (Playwright):**
```python
# In page object - same method names!
self.fill(self.USERNAME_INPUT, username)  # or type_text still works
self.click(self.LOGIN_BUTTON)
text = self.get_text(self.WELCOME_MSG)
visible = self.is_visible(self.ERROR_MSG)
```

## Selector Migration

Playwright uses CSS selectors, XPath, and other locator strategies. Convert Selenium locators as follows:

| Selenium Locator | Playwright Selector |
|-----------------|---------------------|
| `(By.ID, "username")` | `"#username"` |
| `(By.CLASS_NAME, "error")` | `".error"` |
| `(By.NAME, "search")` | `"[name='search']"` |
| `(By.TAG_NAME, "button")` | `"button"` |
| `(By.CSS_SELECTOR, "div > p")` | `"div > p"` |
| `(By.XPATH, "//button[@id='submit']")` | `"//button[@id='submit']"` |

## Common Patterns

### Pattern 1: Direct Page API Usage

If you prefer not using page objects:

```python
def test_search(framework_page):
    framework_page.goto("https://example.com")
    framework_page.fill("#search", "test query")
    framework_page.click("button[type='submit']")
    assert framework_page.locator(".result").count() > 0
```

### Pattern 2: Using navigate_to Helper

```python
def test_with_helper(navigate_to, framework_page):
    navigate_to("/login")  # Relative to base_url from config
    framework_page.fill("#username", "user")
    framework_page.click("#login")
```

### Pattern 3: Page Object Pattern

```python
def test_with_page_object(navigate_to, framework_page):
    navigate_to("/login")
    login_page = LoginPage(framework_page)
    login_page.login("user", "password")
    assert login_page.is_dashboard_loaded()
```

## Configuration Changes

### Environment Variables

Add to your `.env` file:

```env
ENV=dev
BROWSER=chrome
BROWSER_HEADLESS=true  # New: controls headless mode
```

### Browser Selection

Playwright supports multiple browsers through `--browser` flag:

```bash
# Run with Chromium (default)
pytest test-automation/tests/ui/

# Run with Firefox
pytest test-automation/tests/ui/ --browser firefox

# Run with WebKit (Safari)
pytest test-automation/tests/ui/ --browser webkit

# Run with all browsers
pytest test-automation/tests/ui/ --browser chromium --browser firefox --browser webkit
```

## Playwright-Specific Features

### Auto-Waiting

Playwright automatically waits for elements to be actionable:

```python
# No need for explicit waits in most cases
framework_page.click("#button")  # Waits automatically until clickable
```

### Multiple Contexts

```python
def test_multi_user(context):
    # Create separate contexts for different users
    page1 = context.new_page()
    page2 = context.new_page()
    
    page1.goto("https://app.com")
    page2.goto("https://app.com")
```

### Screenshots and Videos

Playwright can capture screenshots and videos automatically:

```bash
# Enable video recording
pytest --video on

# Enable screenshots on failure (enabled by default)
pytest --screenshot on
```

## Deprecation Warnings

The following modules are deprecated but kept for compatibility:

- `infra.base.base_test.BaseTest` - Use pytest-playwright fixtures instead
- `infra.core.driver_factory` - Playwright manages browsers automatically
- `infra.core.driver_manager` - Not needed with pytest-playwright

You'll see deprecation warnings if you use these. Migrate your tests to remove warnings.

## Troubleshooting

### Issue: Tests not collecting

**Solution:** Ensure you have pytest-playwright installed:
```bash
pip install pytest-playwright
```

### Issue: Browsers not found

**Solution:** Install Playwright browsers:
```bash
python -m playwright install --with-deps
```

### Issue: Tests timing out

**Solution:** Increase default timeout in conftest.py or per-test:
```python
def test_slow_page(framework_page):
    framework_page.set_default_timeout(60000)  # 60 seconds
    framework_page.goto("https://slow-site.com")
```

### Issue: Element not found

**Solution:** Verify your selector with Playwright Inspector:
```bash
playwright codegen https://your-site.com
```

## Best Practices

1. **Use CSS Selectors**: Playwright's CSS selector engine is fast and reliable
2. **Avoid Sleeping**: Use `page.wait_for_selector()` instead of `time.sleep()`
3. **Leverage Auto-Waiting**: Playwright waits automatically, don't add unnecessary waits
4. **Use Locator API**: For dynamic elements, use `page.locator()` which auto-retries
5. **Enable Tracing**: In CI, enable trace for debugging failed tests

## Additional Resources

- [Playwright Python Docs](https://playwright.dev/python/docs/intro)
- [pytest-playwright Documentation](https://playwright.dev/python/docs/test-runners)
- [Playwright Selectors Guide](https://playwright.dev/python/docs/selectors)
- [Migration from Selenium](https://playwright.dev/python/docs/selenium)

## Need Help?

If you encounter issues during migration:

1. Check the example tests in `test-automation/tests/ui/web/`
2. Review the updated page objects in `test-automation/projects/inspection_portal/pages/`
3. Consult the Playwright documentation
4. Open an issue on GitHub

Happy testing with Playwright! 🎭
