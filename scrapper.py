import json
from getpass import getpass

from selenium import webdriver
from selenium.common import exceptions as exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

import logging

logger = logging.getLogger("Forum Scrapper")


class Scrapper:
    def __init__(self, url, credentials_file_name='.credentials.json'):
        logger.info('Opening Browser')
        self.driver = webdriver.Chrome("./chromedriver")
        logger.info('Browser opened')
        self.credentials_file_name = credentials_file_name
        logger.info(f'Navigating to {url}')
        self.driver.get(url)
        logger.info(f'{url} navigated successfully')

    def __del__(self):
        logger.info('Closing Browser')
        self.driver.quit()
        logger.info('Browser closed')

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

    def login_info(self):
        """
        Gets the user's log in information from the command line
        or from a file.
        The first use of the command line creates a file and saves
        the information for faster runtimes in the future.
        :return: a tuple consisting of the user_name, password
        """
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
