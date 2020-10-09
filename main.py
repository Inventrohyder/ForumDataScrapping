import time

from forum_scrapper import ForumScrapper
import logging


def setup_logging():
    logger = logging.getLogger("Forum Scrapper")
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler('forum_scrapper.log')
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    # add the handlers to logger
    logger.addHandler(ch)
    logger.addHandler(fh)


def main():
    setup_logging()
    forum_scrapper = ForumScrapper()
    # forum_scrapper.setup_hc_links()
    forum_scrapper.setup_scores_file()
    time.sleep(10)


if __name__ == '__main__': main()
