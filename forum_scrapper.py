import time

import selenium.common.exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

import pandas as pd

from scrapper import Scrapper
import logging

logger = logging.getLogger("Forum Scrapper")


class ForumScrapper(Scrapper):

    def __init__(self, forum_link: str = "https://forum.minerva.kgi.edu"):
        super().__init__(forum_link)
        logger.info('Logging you in')
        self.login()

    def login(self):
        """
        Allows the user to login via Google Login
        :return: nothing
        """
        parent_window = self.driver.current_window_handle
        time.sleep(1)
        google_sign_in_button = self.wait_for('//*[@id="app"]/div/div/div[2]/div/div/div/div/button', one_as_list=False)
        google_sign_in_button.click()
        wait = WebDriverWait(self.driver, 5)
        wait.until(ec.number_of_windows_to_be(2))

        username, password = self.login_info()

        # Switch to the Google Login window
        s1 = self.driver.window_handles
        for next_tab in s1:
            if not parent_window.lower() == next_tab.lower():
                self.driver.switch_to.window(next_tab)
                logger.info("Working on Google Login Box")
                email_elem = self.wait_for('//*[@id="identifierId"]', one_as_list=False)
                email_elem.send_keys(username)
                # Click the next button
                self.wait_for('//*[@id="identifierNext"]/div/button', one_as_list=False).click()
                logger.info('Email entered')
                password_elem = self.wait_for('//*[@id="password"]/div[1]/div/div[1]/input', one_as_list=False)
                password_elem.send_keys(password)
                self.wait_for('//*[ @ id = "passwordNext"]/div/button', one_as_list=False).click()
                logger.info('Password entered')

                logger.info('Logged in')

        # Switch back away from the Google Login Window to the Main window
        self.driver.switch_to.window(parent_window)

        # Before leaving ensure that the login was successful by
        # accessing an element present when logged in
        self.wait_for('//*[@id="header"]/div/div[1]/div/section/div[2]/div/div/div[1]/div/div/div/span')

    def setup_hc_links(self, hcs_link: str = "https://forum.minerva.kgi.edu/app/outcome-index",
                       hcs_file="hc_links.csv"):
        """
        Generate a file containing the links to the HCs
        :return: nothing
        """
        self.driver.get(hcs_link)
        links = []
        hcs = []
        hcs_elements = self.wait_for('section > div > div > ul > li > ul > li > div > span > a', by=By.CSS_SELECTOR)
        logger.info("Getting HC links")
        for hc_element in hcs_elements:
            hc_link = hc_element.get_property("href")
            hc = hc_link.split("/")[-1]
            links.append(hc_link)
            hcs.append(hc)
        df = pd.DataFrame(data=[hcs, links])
        df = df.transpose()
        df.columns = ["HC", "HC_Link"]
        df.to_csv(hcs_file)
        logger.info("Saved hc links into file")

    def setup_scores_file(self, hcs_file: str = "hc_links.csv"):
        try:
            # Try to open the file in read mode
            # if it doesn't exist it throws an exception
            open(hcs_file)
        except FileNotFoundError:
            logger.error("HCS file not found")
            self.setup_hc_links(hcs_file=hcs_file)
        finally:
            df = pd.read_csv(hcs_file)
            self.__get_scores(hc_df=df)

    def __get_scores(self, hc_df: pd.DataFrame, scores_file: str = "./.data/scores.csv"):
        """
        Navigates through each HC link and scrapes the scores
        :param hc_df: The DataFrame containing the links
        :return:
        """
        weight_elements = []
        hcs = []
        weights = []
        dates = []
        grades = []
        for hc_row in hc_df.itertuples():
            logger.info(f"Scraping HC data -> #{hc_row.HC}")
            link = hc_row.HC_Link
            self.driver.get(link)
            # Wait for the page to load
            self.wait_for('//*[@id="main-semantic-content"]/div/div/div/div/div/section[3]/div')

            # Check if the HC has been used by waiting for a TimeoutException when finding the weight data
            try:
                # Scrape the weights
                weight_elements = self.wait_for(
                    '//*[@id="main-semantic-content"]/div/div/div/div/div/section[2]/div/div[3]/table/tbody/tr/td[4]')
                for weight_element in weight_elements:
                    weights.append(weight_element.text.strip("x"))
            except selenium.common.exceptions.TimeoutException:
                logger.error(f"#{hc_row.HC} has never been graded")
                hcs.extend([hc_row.HC])
                weights.append(0)
                dates.append("Apr 1 2012")
                grades.append(0)
                continue

            # The number of weights should be equal to the number of dates and grades
            # Therefore add the same number of hcs so that a table can be made of
            # all of the variables
            hcs.extend([hc_row.HC] * len(weight_elements))

            # Scrape the dates
            date_elements = self.wait_for(
                '//*[@id="main-semantic-content"]/div/div/div/div/div/section[2]/div/div[3]/table/tbody/tr/td[5]')
            for date_element in date_elements:
                dates.append(date_element.text.strip())

            # Scrape the grades
            grade_elements = self.wait_for(
                '//*[@id="main-semantic-content"]/div/div/div/div/div/section[2]/div/div[3]/table/tbody/tr/td[6]')
            for grade_element in grade_elements:
                grades.append(grade_element.text.strip())

        df = pd.DataFrame(data=[hcs, weights, dates, grades])
        df = df.transpose()
        df.columns = ["HC", "HC_Weight", "HC_Date", "HC_Grade"]
        df.to_csv(scores_file)
        logger.info("Saved hc links into file")
