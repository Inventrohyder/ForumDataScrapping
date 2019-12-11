from getpass import getpass  # For getting the User's password
from selenium import webdriver  # Gives access to the driver
from selenium.webdriver.support.ui import WebDriverWait  # Allows the driver to pause
from selenium.webdriver.support import expected_conditions as ec  # Make driver get conditions
from selenium.webdriver.common.by import By  # Get methods of identifying elements
import selenium.common.exceptions as exceptions  # The exceptions module of Selenium
import json  # For reading credentials file


class Scrapper:
    def __init__(self, url, driver=webdriver.Safari, credentials_file_name='.credentials.json'):
        print('Opening Browser')
        self.driver = driver()
        print('Browser opened')
        self.credentials_file_name = credentials_file_name
        print('Navigating to', url)
        self.driver.get(url)
        print(url, 'navigated successfully')

    def __del__(self):
        print('Closing Browser')
        self.driver.quit()
        print('Browser closed')

    def wait_for(self, text, delay=10, by=By.XPATH, check_again_limit=3, one_as_list=True):
        check = 0
        try:
            elements = WebDriverWait(self.driver, delay).until(ec.presence_of_all_elements_located((by, text)))
        except exceptions.TimeoutException:
            if check < check_again_limit:
                elements = WebDriverWait(self.driver, delay).until(ec.presence_of_all_elements_located((by, text)))
            else:
                return None
            check += 1
        if len(elements) == 0:
            return None
        elif len(elements) == 1:
            if one_as_list:
                return self.driver.find_elements(by, text)
            else:
                return elements[0]
        return elements

    # Logging in function
    def login_info(self):
        try:
            # Try to open the file in read mode
            # if it doesn't exist it throws an exception
            with open(self.credentials_file_name) as credentials_file:
                credentials = json.load(credentials_file)
                user_name = credentials['user']
                user_pass = credentials['password']
        except FileNotFoundError:
            with open(self.credentials_file_name, 'w+') as credentials_file:
                # For sure the file had nothing, therefore
                user_name = str(input("Username: "))
                user_pass = getpass()
                json.dump(
                    {'user': user_name,
                     'password': user_pass
                     },
                    credentials_file
                )

        return user_name, user_pass


class ForumScrapper(Scrapper):

    def __init__(self):
        super().__init__('https://seminar.minerva.kgi.edu')
        print('Logging you in')
        self.login()

    def login(self):
        parent_window = self.driver.current_window_handle
        google_sign_in_button = self.wait_for('//*[@id="js-google-sign-in"]', one_as_list=False)
        google_sign_in_button.click()
        wait = WebDriverWait(self.driver,5)
        wait.until(ec.number_of_windows_to_be(2))

        username, password = self.login_info()

        s1 = self.driver.window_handles
        for next_tab in s1:
            if not parent_window.toLower() == next_tab.toLower():
                self.driver.switch_to.window(next_tab)
                print("Working on Google Login Box")
                email_elem = self.wait_for('//*[@id="identifierId"]', one_as_list=False)
                email_elem.send_keys(username)
                email_elem.submit()
                print('Email entered')
                password_elem = self.wait_for('//*[@id="password"]/div[1]/div/div[1]/input', one_as_list=False)
                password_elem.send_keys(password)
                password_elem.submit()
                print('Password entered')

                print('Logged in')


def main():
    forum_scrapper = ForumScrapper()
    print('Working')


if __name__ == '__main__': main()
