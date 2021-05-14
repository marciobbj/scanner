import time
from application.validators import clean_scan_data
from application.entities import UpWorkMainPageData
from application.constants import MAX_RAND, MIN_RAND
from application.exceptions import CaptchaException, ElementTookTooLongToLoad, LoginNotCompleted
from application.scanners.base_scanner import BaseScanner
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s:%(name)s:%(levelname)s:%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler('./log/upwork_scraper.log'),
        logging.StreamHandler()
    ]
)


class UpWorkScanner(BaseScanner):

    baselog = "[scanners][upwork][UpWorkScanner]"

    def __init__(self, settings):
        super().__init__(settings)
        self.firefox = self.setup_firefox_driver()
        self.logged_in = False
        self.user = {}

    def setup_firefox_driver(self):
        # Setup headless option
        options = webdriver.FirefoxOptions()
        options.headless = True

        # Setup profile and install recaptcha solver extension
        profile = webdriver.FirefoxProfile()
        profile._install_extension(
            f"{self.drivers_path}/buster_captcha_solver_for_humans-0.7.2-an+fx.xpi",
            unpack=False
        )
        profile.set_preference("security.fileuri.strict_origin_policy", False)
        profile.update_preferences()

        # Setup Desired Capabilities
        capabilities = webdriver.DesiredCapabilities.FIREFOX
        capabilities['marionette'] = True

        return webdriver.Firefox(
            executable_path=self.drivers_path + "geckodriver",
            options=options,
            capabilities=capabilities,
            firefox_profile=profile
        )

    @property
    def base_url(self):
        return "https://www.upwork.com/"

    @property
    def drivers_path(self):
        return os.path.dirname(os.path.abspath(__file__)) + "/../drivers/"

    def parse(self, page_source):
        return BeautifulSoup(page_source, features="html.parser")

    def login(self, user_info):
        """Log into the upwork platform"""
        login_url = self.base_url + "ab/account-security/login"

        # Fetching Login URL
        self.firefox.get(login_url)
        wait = WebDriverWait(self.firefox, 10)
        self.firefox.maximize_window()

        # Checking RECaptcha
        element = self.firefox.find_elements_by_xpath(
            '/html/body/section/div[3]/div/p[1]')

        if element:
            raise CaptchaException("Login failed, retriable exception.")

        try:
            wait.until(
                EC.element_to_be_clickable((By.ID, "login_username"))
            )
        except TimeoutException:
            logging.warning("%s[login] Platform seems to be slow at the moment", self.baselog)  # noqa
            raise ElementTookTooLongToLoad(
                "Platform seems to be slow at the moment, retriable exception")

        # Select the Username/Email input
        user_input = self.firefox.find_element_by_id("login_username")
        user_input.send_keys(user_info["username"] + Keys.ENTER)
        logging.info("%s[login] Filled the username field", self.baselog)
        self.wait_between(MIN_RAND, MAX_RAND)

        # Select the password input
        user_input = self.firefox.find_element_by_id("login_password")
        user_input.send_keys(user_info["password"] + Keys.ENTER)
        logging.info("%s[login] Filled the password field", self.baselog)
        self.wait_between(MIN_RAND, MAX_RAND)

        logging.info("%s[login] user (%s) logged in!",
                     self.baselog, user_info["username"])

        self.logged_in = True
        self.user["username"] = user_info["username"]

        return True

    def scan_main_page(self):
        time.sleep(10)

        if self.logged_in:
            logging.info("%s started parsing and saving content from main page", self.baselog)

            profile_visibility = self.firefox.find_element_by_xpath(
                "/html/body/div[2]/div/div[2]/div/div[6]/div[3]/div/fe-profile-completeness/div/div[3]/fe-profile-visibility/div/div/div/div/div/div/div[2]/small").text

            hours = self.firefox.find_element_by_xpath(
                "/html/body/div[2]/div/div[2]/div/div[6]/div[3]/div/fe-profile-completeness/div/div[4]/div/div[2]/small/span").text

            profile_completion = self.firefox.find_element_by_xpath(
                "/html/body/div[2]/div/div[2]/div/div[6]/div[3]/div/fe-profile-completeness/div/div[5]/div/div/div/span/span").text

            proposals = self.firefox.find_element_by_xpath(
                "/html/body/div[2]/div/div[2]/div/div[6]/div[3]/div/fe-fwh-proposal-stats/div/ul/li/a").text

            # Fetches the <ul> element
            list_of_categories = self.firefox.find_element_by_xpath(
                "/html/body/div[2]/div/div[2]/div/div[6]/div[1]/div[3]/fe-fwh-my-categories/div/div/ul")
            # Iterates over all <li>
            categories = [
                ctg.text for ctg in list_of_categories.find_elements_by_tag_name("li")
            ]  # noqa

            # Removes the last one, it's the Edit button
            categories.pop()

            raw_data = {
                "username": self.user["username"],
                "profile_visibility": profile_visibility,
                "available_hours": hours,
                "profile_completion": profile_completion,
                "proposals": proposals,
                "categories": categories
            }
            cleaned_data = clean_scan_data(UpWorkMainPageData, raw_data)
            return cleaned_data
        else:
            logging.error(
                "%s cannot scan page of logged off user", self.baselog)
            raise LoginNotCompleted()
