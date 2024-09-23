import os
import logging
from playwright.sync_api import sync_playwright  # Use synchronous Playwright API
from screeninfo import get_monitors  # To get screen size information


class BrowserManager:
    def __init__(self, user_data_dir: str, headless: bool = False):
        """
        Initialize BrowserManager with Playwright and browser settings.

        Args:
            user_data_dir (str): Path to the user data directory for persistent context.
            headless (bool): Whether to run the browser in headless mode (default: False).
        """
        self.playwright = None
        self.browser = None
        self.page = None
        self.user_data_dir = user_data_dir
        self.headless = headless
        self.screen_width, self.screen_height = get_monitors()[0].width, get_monitors()[0].height

    def start_browser(self, url: str):
        """
        Start the browser using Playwright and load the page with the given URL.

        Args:
            url (str): URL of the page to load.
        """
        try:
            # Start Playwright in synchronous mode
            self.playwright = sync_playwright().start()

            # Create the user_data_dir if it doesn't exist
            if not os.path.exists(self.user_data_dir):
                os.makedirs(self.user_data_dir)

            # Launch the browser with persistent context
            self.browser = self.playwright.chromium.launch_persistent_context(
                user_data_dir=self.user_data_dir,
                headless=self.headless,
                viewport={"width": self.screen_width, "height": self.screen_height}
            )

            # Open a new page and navigate to the URL
            self.page = self.browser.new_page()
            self.page.goto(url)

            logging.info(f"Browser started and navigated to {url}")

        except Exception as e:
            logging.error(f"Failed to start the browser and navigate to the page: {e}")
            raise

    def select_element_by_xpath(self, xpath: str) -> bool:
        """
        Select an element on the page by XPath.

        Args:
            xpath (str): XPath string to select the element.

        Returns:
            bool: True if the element was found and clicked, False otherwise.
        """
        try:
            element = self.page.query_selector(xpath)
            if element:
                element.click()
                logging.info(f"Clicked element with XPath: {xpath}")
                return True
            else:
                logging.error(f"No element found with XPath: {xpath}")
                return False
        except Exception as e:
            logging.error(f"Failed to select element by XPath: {e}")
            return False

    def stop_browser(self):
        """
        Stops the browser and closes Playwright.
        """
        try:
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()

            logging.info("Browser stopped successfully.")

        except Exception as e:
            logging.error(f"Failed to stop the browser: {e}")