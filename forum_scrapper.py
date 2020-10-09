import time

from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from scrapper import Scrapper


class ForumScrapper(Scrapper):

    def __init__(self):
        super().__init__('https://forum.minerva.kgi.edu')
        print('Logging you in')
        self.login()

    def login(self):
        parent_window = self.driver.current_window_handle
        time.sleep(1)
        google_sign_in_button = self.wait_for('//*[@id="app"]/div/div/div[2]/div/div/div/div/button', one_as_list=False)
        google_sign_in_button.click()
        wait = WebDriverWait(self.driver, 5)
        wait.until(ec.number_of_windows_to_be(2))

        username, password = self.login_info()

        s1 = self.driver.window_handles
        for next_tab in s1:
            if not parent_window.lower() == next_tab.lower():
                self.driver.switch_to.window(next_tab)
                print("Working on Google Login Box")
                email_elem = self.wait_for('//*[@id="identifierId"]', one_as_list=False)
                email_elem.send_keys(username)
                # Click the next button
                self.wait_for('//*[@id="identifierNext"]/div/button', one_as_list=False).click()
                print('Email entered')
                password_elem = self.wait_for('//*[@id="password"]/div[1]/div/div[1]/input', one_as_list=False)
                password_elem.send_keys(password)
                self.wait_for('//*[ @ id = "passwordNext"]/div/button', one_as_list=False).click()
                print('Password entered')

                print('Logged in')