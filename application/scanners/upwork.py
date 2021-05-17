from application.entities.upwork.profile import Address, Certificate, Contact, Education, Experience, Language
from application.utils import check_auth_and_wait_load_delay
from application.entities.upwork.page_scans import (
    ContactInfoData,
    FullScanProfile,
    MainPageData,
    ProfilePageData,
)
import datetime
import time
from application.validators import clean_scan_data
from application.constants import MAX_RAND, MIN_RAND
from application.exceptions import (
    CaptchaException,
    ElementTookTooLongToLoad,
    IncompleteUserAuthInformation,
    LoginNotCompleted,
)
from application.scanners.base_scanner import BaseScanner
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    StaleElementReferenceException,
    TimeoutException,
    NoSuchElementException,
)
from bs4 import BeautifulSoup
import os
import logging


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
            unpack=False,
        )
        profile.set_preference("security.fileuri.strict_origin_policy", False)
        profile.update_preferences()

        # Setup Desired Capabilities
        capabilities = webdriver.DesiredCapabilities.FIREFOX
        capabilities["marionette"] = True
        firefox = webdriver.Firefox(
            executable_path=self.drivers_path + "geckodriver",
            options=options,
            capabilities=capabilities,
            firefox_profile=profile,
        )
        # sets up a timeout for the requests.
        firefox.implicitly_wait(30)
        return firefox

    @property
    def base_url(self):
        return "https://www.upwork.com/"

    @property
    def drivers_path(self):
        return os.path.dirname(os.path.abspath(__file__)) + "/../drivers/"
    
    @property
    def parse(self):
        return BeautifulSoup(self.firefox.page_source, features="html.parser")

    def login(self):
        """Log into the upwork platform"""
        login_url = self.base_url + "ab/account-security/login"
        user_info = self.settings["user_auth"]

        # Fetching Login URL
        self.firefox.get(login_url)
        wait = WebDriverWait(self.firefox, 10)
        self.firefox.maximize_window()

        # Checking RECaptcha
        element = self.firefox.find_elements_by_xpath(
            "/html/body/section/div[3]/div/p[1]"
        )

        if element:
            raise CaptchaException("Login failed, retriable exception.")

        try:
            wait.until(EC.element_to_be_clickable((By.ID, "login_username")))
        except TimeoutException:
            logging.warning(
                "%s[login] Platform seems to be slow at the moment", self.baselog
            )  # noqa
            raise ElementTookTooLongToLoad(
                "Platform seems to be slow at the moment, retriable exception"
            )
        try:
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

            logging.info(
                "%s[login] user (%s) logged in!", self.baselog, user_info["username"]
            )
        except StaleElementReferenceException as exc:
            logging.warning(
                "%s[login] weird behavior from element, task will retry, error %s",
                self.baselog,
                repr(exc),
            )
            raise ElementTookTooLongToLoad()

        self.logged_in = True
        self.user["username"] = user_info["username"]

        return True

    @check_auth_and_wait_load_delay
    def scan_main_page(self, close_driver=False):
        logging.info(
            "%s[scan_main_page] started parsing and saving content from main page",
            self.baselog,
        )
        try:
            profile_visibility = self.firefox.find_element_by_xpath(
                "/html/body/div[2]/div/div[2]/div/div[6]/div[3]/div/fe-profile-completeness/div/div[3]/fe-profile-visibility/div/div/div/div/div/div/div[2]/small"
            ).text

            hours = self.firefox.find_element_by_xpath(
                "/html/body/div[2]/div/div[2]/div/div[6]/div[3]/div/fe-profile-completeness/div/div[4]/div/div[2]/small/span"
            ).text

            profile_completion = self.firefox.find_element_by_xpath(
                "/html/body/div[2]/div/div[2]/div/div[6]/div[3]/div/fe-profile-completeness/div/div[5]/div/div/div/span/span"
            ).text

            proposals = self.firefox.find_element_by_xpath(
                "/html/body/div[2]/div/div[2]/div/div[6]/div[3]/div/fe-fwh-proposal-stats/div/ul/li/a"
            ).text

            # Fetches the <ul> element
            list_of_categories = self.firefox.find_element_by_xpath(
                "/html/body/div[2]/div/div[2]/div/div[6]/div[1]/div[3]/fe-fwh-my-categories/div/div/ul"
            )

        except NoSuchElementException as exc:
            logging.warning(
                "%s[scan_main_page] could not find certificate information, error %s",
                self.baselog,
                repr(exc),
            )
            raise

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
            "categories": categories,
        }
        cleaned_data = clean_scan_data(MainPageData, raw_data)

        if close_driver:
            logging.info("%s[scan_main_page] closing driver")
            self.firefox.quit()

        self.user["main_page_data"] = cleaned_data
        return cleaned_data

    @check_auth_and_wait_load_delay
    def scan_profile_page(self, close_driver=False):
        logging.info("%s[scan_profile_page] starting task to scan profile page", self.baselog)

        logging.info("%s[scan_profile_page] clicking on the profile link", self.baselog)
        self.firefox.find_element_by_xpath(
            "/html/body/div[2]/div/div[2]/div/div[6]/div[3]/div/fe-profile-completeness/div/div[2]/a"
        ).click()

        # Wait for the profile page to load
        time.sleep(10)

        try:
            # Fetches basic info
            full_name = self.firefox.find_element_by_xpath(
                "/html/body/div[1]/div/span/div/div/main/div[2]/div[2]/div[2]/div/div[1]/div[1]/section[1]/div/div[1]/div[1]/div/div[2]/div/div[1]/h1"
            ).text
            city = self.firefox.find_element_by_xpath(
                "/html/body/div[1]/div/span/div/div/main/div[2]/div[2]/div[2]/div/div[1]/div[1]/section[1]/div/div[1]/div[1]/div/div[2]/div/div[2]/div[1]/span[2]"
            ).text
            country = self.firefox.find_element_by_xpath(
                "/html/body/div[1]/div/span/div/div/main/div[2]/div[2]/div[2]/div/div[1]/div[1]/section[1]/div/div[1]/div[1]/div/div[2]/div/div[2]/div[1]/span[4]"
            ).text
            price_per_hour = self.firefox.find_element_by_xpath(
                "/html/body/div[1]/div/span/div/div/main/div[2]/div[2]/div[2]/div/div[1]/div[1]/section[2]/div[2]/section[1]/div[1]/div/div[2]/div[1]/h3/span/span[1]"
            ).text

            profile_description = self.firefox.find_element_by_xpath(
                "/html/body/div[1]/div/span/div/div/main/div[2]/div[2]/div[2]/div/div[1]/div[1]/section[2]/div[2]/section[1]/div[2]/div[1]/div[2]/span"
            ).text.replace("\n", ", ")

            job_title = self.firefox.find_element_by_xpath(
                "/html/body/div[1]/div/span/div/div/main/div[2]/div[2]/div[2]/div/div[1]/div[1]/section[2]/div[2]/section[1]/div[1]/div/div[1]/h2"
            ).text

            picture_url = self.firefox.find_element_by_xpath(
                "/html/body/div[1]/div/span/div/div/main/div[2]/div[2]/div[2]/div/div[1]/div[1]/section[1]/div/div[1]/div[1]/div/div[1]/div/div/img"
            ).get_attribute("src")

            # Build a profile dict to store the scanned information
            profile = {
                "full_name": full_name,
                "picture_url": picture_url,
                "city": city,
                "country": country,
                "job_title": job_title,
                "professional_experiences": [],
                "languages": [],
                "education": [],
                "price_per_hour": price_per_hour,
                "profile_description": profile_description,
                "certificates": [],
            }

            logging.info(
                "%s[scan_profile_page] first profile dict was built, %s", self.baselog, repr(profile)
            )

            # Fetches the <ul> element
            employment_history_list = self.firefox.find_element_by_xpath(
                "/html/body/div[1]/div/span/div/div/main/div[2]/div[2]/div[2]/div/div[1]/div[9]/section/div/ul"
            )

            # Iterates over all <li>
            for element in employment_history_list.find_elements_by_tag_name("li"):
                professional_experience = dict()

                role = element.find_element_by_class_name("my-0").text
                professional_experience["role"] = role

                period = element.find_element_by_class_name("text-muted").text
                professional_experience["period"] = period

                try:
                    # optional field
                    comment = element.find_element_by_tag_name("span").text
                    professional_experience["comment"] = comment
                except NoSuchElementException:
                    logging.info(
                        "%s user have no comments on professional experience (%s)",
                        self.baselog,
                        role,
                    )
                    professional_experience["comment"] = None
                    pass

                profile["professional_experiences"].append(clean_scan_data(Experience, professional_experience))

            # Languages
            list_of_languages = self.firefox.find_element_by_xpath(
                "/html/body/div[1]/div/span/div/div/main/div[2]/div[2]/div[2]/div/div[1]/div[1]/section[2]/div[1]/aside/section[4]/div[3]/ul"
            )

            for element in list_of_languages.find_elements_by_tag_name("li"):
                lang_info = dict()

                lang = (
                    element.find_element_by_tag_name("strong")
                    .text.replace(": ", "")
                    .strip()
                )
                lang_info["language"] = lang

                profiency = element.find_element_by_tag_name("span").text
                lang_info["profiency"] = profiency

                profile["languages"].append(clean_scan_data(Language, lang_info))

            # Education
            education_info = self.firefox.find_element_by_xpath(
                "/html/body/div[1]/div/span/div/div/main/div[2]/div[2]/div[2]/div/div[1]/div[1]/section[2]/div[1]/aside/section[4]/div[5]/ul"
            )
            for element in education_info.find_elements_by_tag_name("li"):
                education_info = dict()

                title = element.find_element_by_tag_name("h5").text
                education_info["title"] = title

                divs = element.find_elements_by_tag_name("div")
                if divs:
                    # There is one div without any class nor identifier, so we need to get
                    # all divs inside <li> and get the middle one, its the field we want to scan
                    field = divs[1].text
                    education_info["field"] = field

                period = element.find_element_by_class_name("text-muted").text
                education_info["period"] = period
                profile["education"].append(clean_scan_data(Education, education_info))

            certificates = self.firefox.find_elements_by_xpath(
                "//div[@data-testid='certificate-wrapper']"
            )
            for element in certificates:
                certificate = dict()
                try:
                    certificate["title"] = (
                        element.find_element_by_class_name("col")
                        .find_element_by_tag_name("h5")
                        .find_element_by_tag_name("span")
                        .text
                    )

                    certificate["description"] = (
                        element.find_element_by_class_name("col")
                        .find_element_by_tag_name("p")
                        .find_element_by_tag_name("span")
                        .text
                    )

                    profile["certificates"].append(clean_scan_data(Certificate, certificate))
                except NoSuchElementException as exc:
                    logging.warning(
                        "%s[scan_profile_page] could not find certificate information, error %s",
                        self.baselog,
                        repr(exc),
                    )
                    raise

            logging.info(
                "%s[scan_profile_page] profile dict was fully built, %s", self.baselog, repr(profile)
            )

            cleaned_data = clean_scan_data(ProfilePageData, profile)

            if close_driver:
                logging.info("%s[scan_profile_page] closing driver")
                self.firefox.quit()

            self.user["profile_page_data"] = cleaned_data
            return cleaned_data

        except Exception:
            logging.exception("%s[scan_profile_page] error while selecting profile items")
            raise

    @check_auth_and_wait_load_delay
    def scan_contact_info(self, close_driver=False):
        logging.info("%s[scan_contact_info] starting task to scan contact info page", self.baselog)

        if self.firefox.title.lower() != "my job feed":
            logging.info("%s[scan_contact_info] go back to home screen", self.baselog)
            self.firefox.find_element_by_class_name(
                "container"
            ).find_element_by_tag_name("a").click()
            time.sleep(10)

        logging.info(
            "%s[scan_contact_info] clicking on the menu bar to open the menu",
            self.baselog,
        )
        self.firefox.find_element_by_xpath(
            "/html/body/div[2]/div/nav/div/div/div/nav/ul/li[8]/button"
        ).click()

        time.sleep(3)

        logging.info(
            "%s[scan_contact_info] clicking on the settings option in the menu",
            self.baselog,
        )
        self.firefox.find_element_by_xpath(
            "/html/body/div[2]/div/nav/div/div/div/nav/ul/li[8]/ul/li[3]/ul/li[1]/a"
        ).click()

        # loading time
        time.sleep(15)

        logging.info(
            "%s[scan_contact_info] started parsing and saving content from contact info page",
            self.baselog,
        )

        if self.firefox.title.lower() == "device authorization":
            self.bypass_device_authentication()

        logging.info(
            "%s[scan_contact_info] clicking on the edit button to fetch the email info",
            self.baselog,
        )
        self.firefox.find_element_by_xpath(
            "/html/body/div[1]/div/div/div/div/main/div[2]/div[2]/div[2]/main/div[1]/header/button"
        ).click()

        self.wait_between(MIN_RAND, MAX_RAND)

        email = self.firefox.find_element_by_xpath(
            "/html/body/div[1]/div/div/div/div/main/div[2]/div[2]/div[2]/main/div[1]/section/div[1]/div[3]/input"
        ).get_attribute("value")

        logging.info(
            "%s[scan_contact_info] clicking on the edit button to fetch the location info",
            self.baselog,
        )
        self.firefox.find_element_by_xpath(
            "/html/body/div[1]/div/div/div/div/main/div[2]/div[2]/div[2]/main/div[3]/header/button"
        ).click()

        self.wait_between(MIN_RAND, MAX_RAND)

        timezone = self.firefox.find_element_by_xpath(
            "/html/body/div[1]/div/div/div/div/main/div[2]/div[2]/div[2]/main/div[3]/section/div[2]/div[1]/div/button/div/span"
        ).text

        street = self.firefox.find_element_by_xpath(
            "/html/body/div[1]/div/div/div/div/main/div[2]/div[2]/div[2]/main/div[3]/section/div[2]/div[2]/div[2]/div[1]/input"
        ).get_attribute("value")

        street_complement = self.firefox.find_element_by_xpath(
            "/html/body/div[1]/div/div/div/div/main/div[2]/div[2]/div[2]/main/div[3]/section/div[2]/div[2]/div[2]/div[2]/div/div/input"
        ).get_attribute("value")

        zipcode = self.firefox.find_element_by_xpath(
            "/html/body/div[1]/div/div/div/div/main/div[2]/div[2]/div[2]/main/div[3]/section/div[2]/div[2]/div[2]/div[4]/div/div/input"
        ).get_attribute("value")

        phone_number = self.firefox.find_element_by_xpath(
            "/html/body/div[1]/div/div/div/div/main/div[2]/div[2]/div[2]/main/div[3]/section/div[2]/div[3]/div/div/input"
        ).get_attribute("value")

        try:
            country_code = (
                self.firefox.find_element_by_xpath(
                    "/html/body/div[1]/div/div/div/div/main/div[2]/div[2]/div[2]/main/div[3]/section/div[2]/div[3]/div/div"
                )
                .find_element_by_tag_name("span")
                .text.split(" ")[1]
            )
        except IndexError:
            country_code = None
            pass

        contact_info = {
            "email": email,
            "timezone": timezone,
            "street": street,
            "street_complement": street_complement,
            "zipcode": zipcode,
            "phone_number": phone_number,
            "country_code": country_code,
        }
        logging.info(
            "%s[scan_contact_info] contact_info dict was fully built, %s", self.baselog, repr(contact_info)
        )
        cleaned_data = clean_scan_data(ContactInfoData, contact_info)
        self.user["contact_info_page"] = cleaned_data

        if close_driver:
            logging.info("%s[scan_contact_info] closing driver")
            self.firefox.quit()

        return cleaned_data

    def bypass_device_authentication(self):
        logging.info(
            "%s[bypass_device_authentication] Device Authorization screen has appeared",
            self.baselog,
        )
        user_info = self.settings["user_auth"]
        secret_answer = user_info.get("answer")

        if not secret_answer:
            logging.warning(
                "%s[bypass_device_authentication] could not complete scan due lack of user authentication info SECRET ANSWER, user (%s)",
                self.baselog,
                user_info.get("username"),
            )
            raise IncompleteUserAuthInformation()

        answer_input = self.firefox.find_element_by_id("deviceAuth_answer")
        self.wait_between(MIN_RAND, MAX_RAND)

        logging.info(
            "%s[bypass_device_authentication] entering user secret phrase", self.baselog
        )
        answer_input.send_keys(secret_answer + Keys.ENTER)

        time.sleep(5)

    def build_full_scan_data(self):
        """Groups data from all scans to build a full scan.

        Must be used after the flow was fully executed, it
        expects all data from page scans to be already cleaned."""
        try:
            contact_info = self.user["contact_info_page"]
            profile_page_data = self.user["profile_page_data"]
            main_page_data = self.user["main_page_data"]

            address = {
                "city": profile_page_data.pop("city"),
                "country": profile_page_data.pop("country"),
                "street": contact_info.pop("street"),
                "street_complement": contact_info.pop("street_complement"),
                "zipcode": contact_info.pop("zipcode"),
                "timezone": contact_info.pop("timezone"),
            }
            contact = {
                "email": contact_info.pop("email"),
                "phone_number": contact_info.pop("phone_number"),
            }
            
            input = {
                **contact_info,
                **profile_page_data,
                **main_page_data,
                "address": clean_scan_data(Address, address),
                "contact": clean_scan_data(Contact, contact),
                "created_at": str(datetime.datetime.utcnow()),
            }

            return clean_scan_data(FullScanProfile, input)
        except KeyError as exc:
            logging.exception(
                "%s[build_full_scan_data] cannot build full scan data, missing scan refers to %s", exc
            )
            raise
