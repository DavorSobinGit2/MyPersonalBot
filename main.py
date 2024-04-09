# Import Libraries
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pywhatkit
import time
import random


def GET_TIME():
    CURRENT_TIME = time.localtime()
    # Extract the hour and minutes
    return CURRENT_TIME.tm_hour, CURRENT_TIME.tm_min


class PersonalInfo:
    def __init__(self, email: str = "John.Doe@gmail.com", password: str = "JohnsPassword123!"):
        self.__email = email
        self.__password = password

    def get_email(self):
        return self.__email

    def get_pass(self):
        return self.__password


class LinkedInBot:
    def __init__(self, url="https://www.linkedin.com/"):
        self.LOGIN_ID = ["session_key",
                         "session_password"]
        self.SEARCH_KEYS = {"University": None,
                            "Degree": None}
        self.LINKS = None
        self.url = url
        self.service = Service(executable_path="chromedriver.exe")
        self.driver = webdriver.Chrome(service=self.service)
        self.page_number = 1

    def update_url(self, new_url):
        self.url = new_url

    def add_search_key(self, key, value):
        if key in list(self.SEARCH_KEYS):
            self.SEARCH_KEYS[key] = value
        else:
            print("Error, key does not exist!")

    def start_session(self):
        driver = self.driver
        driver.get(self.url)
        driver.maximize_window()

    def user_login(self, email, password):
        driver = self.driver
        # Get the bot to find the "email" box where it will enter the email
        input_email = driver.find_element(By.ID, self.LOGIN_ID[0])
        input_email.clear()
        input_email.send_keys(email)
        time.sleep(random.randint(5, 10))  # Mimics Human responses
        # Get the bot to find the "password" box where it will enter the password
        input_password = driver.find_element(By.ID, self.LOGIN_ID[1])
        input_password.send_keys(password + Keys.ENTER)
        time.sleep(random.randint(5, 10))

    def get_search(self):
        driver = self.driver
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "search-global-typeahead__input"))
        )
        input_search = driver.find_element(By.CLASS_NAME, "search-global-typeahead__input")
        if self.SEARCH_KEYS["University"] is not None and self.SEARCH_KEYS["Degree"] is not None:
            input_search.send_keys(f"{self.SEARCH_KEYS['University']} {self.SEARCH_KEYS['Degree']}" + Keys.ENTER)
            time.sleep(random.randint(5, 10))
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "See all people results"))
        )
        # Once the search has been entered we want to find the button "see all people results" then we get the
        # bot to click on it
        foo = driver.find_element(By.PARTIAL_LINK_TEXT, "See all people results")
        foo.click()
        time.sleep(random.randint(5, 10))

    def retrieve_links(self):
        driver = self.driver
        links = []
        elements = driver.find_elements(By.CLASS_NAME, 'app-aware-link ')
        for element in elements:
            if element.get_attribute('href') is not None:
                if element.get_attribute('href') in links:
                    continue
                else:
                    links.append(element.get_attribute('href'))
        self.LINKS = links[7:]

    def print_all_links(self):
        all_links = self.LINKS
        for link in all_links:
            print(link)

    def access_person(self):
        links = self.LINKS
        driver = self.driver
        for link in links:
            try:
                driver.get(link)
                time.sleep(random.randint(5, 10))
            except Exception as e:
                print(f'Error processing {link}: {e}')
        time.sleep(random.randint(2, 5))

    def next_page(self):
        next_page_num = self.page_number + 1
        driver = self.driver
        x_path = f"//button[span='{next_page_num}']"
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, x_path))
            )
            submit = driver.find_element(By.XPATH, x_path)
            time.sleep(random.randint(2, 5))
            submit.click()
        except Exception as e:
            print(f"Error: {e}")

    def end_session(self):
        time.sleep(random.randint(5, 10))
        self.driver.quit()

    def captcha_checker(self):
        """
        Checks to see if a captcha has been detected, if it has then we will notify ourselves that we need to complete
        it in order to proceed with the operations. Otherwise if there isn't a captcha we will just proceed to the
        operations of searching and scraping
        """
        message = "Let's do a quick security check"
        driver = self.driver
        curr_h, curr_m = GET_TIME() # Current hour and minutes (local time) - this is used in our pywhatkit method

        try:
            element = driver.find_element(By.XPATH, '/html/body/div/main/h1') # fetches the h1 header text
            element_text = element.text
            if element_text == message:
                pywhatkit.sendwhatmsg(phone_no="ADD NUMBER HERE",
                                      message="Captcha Detected. Go ahead and complete it to continue operations.",
                                      time_hour=curr_h,
                                      time_min=curr_m + 3,
                                      wait_time=45)
                self.handle_captcha_resolution()
            else:
                print("No captcha detected. Continuing with normal operations...")
                self.continue_process()

        except Exception as e:
            # If the element is not found, it likely means no captcha is present
            print("Proceeding with normal operations. Reason:", e)
            self.continue_process()

    def handle_captcha_resolution(self):
        """
        Waits to see if the captcha has been solved, checking periodically if the URL has
        changed. If we reach the max attempts then we will break out of the program
        """
        captcha_url = self.driver.current_url
        max_attempts = 10
        attempt = 0
        while attempt < max_attempts:
            if self.check_url_change(captcha_url):
                print("Captcha resolved. Continuing operation...")
                self.continue_process()
                break
            else:
                print("Captcha still active. Waiting before next check...")
                time.sleep(60)
                attempt += 1
        if attempt == max_attempts:
            print("Failed to resolved captcha in allocated attempts.")
            self.driver.quit()

    def check_url_change(self, original_url):
        """
        Mainly to see if the captcha url has changed, in which case if it has changed then we return False
        if it didn't change then we proceed with the check once again
        """
        current_url = self.driver.current_url
        return current_url != original_url

    def continue_process(self):
        """
        Will continue to do the operations needed after the captcha has been completed, or if there isn't one
        then we just proceed as usual
        :return:
        """
        try:
            self.get_search()
            self.retrieve_links()
            self.print_all_links()
            self.access_person()
            self.next_page()
            self.end_session()

        except Exception as e:
            print(f"Error: {e}")
            self.captcha_checker()


def main():
    # EXAMPLE: TEST
    try:
        NEW_USER = PersonalInfo(email="ADD EMAIL HERE", password="ADD PASSWORD HERE")
        NEW_BOT = LinkedInBot()
        NEW_BOT.add_search_key("University", "The University of Texas at Austin")
        NEW_BOT.add_search_key("Degree", "Kinesiology")
        NEW_BOT.start_session()
        NEW_BOT.user_login(NEW_USER.get_email(), NEW_USER.get_pass())
        NEW_BOT.captcha_checker()

    except Exception as e:
        print(f"Error: {e}")
        NEW_BOT.end_session()


if __name__ == "__main__":
    main()
