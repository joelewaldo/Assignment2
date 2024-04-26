from threading import Thread

from inspect import getsource
from utils.download import download, prep_download
from utils import get_logger
from utils.tokenizer import get_word_count_from_response
import scraper
import time


class Worker(Thread):
    def __init__(self, worker_id, config, frontier, politeness, robot, simhash, token, m_max):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        self.politeness = politeness
        self.robot = robot
        self.simhash = simhash
        self.max = m_max
        self.token = token
        # basic check for requests in scraper
        assert {
            getsource(scraper).find(req) for req in {"from requests import", "import requests"}
        } == {-1}, "Do not use requests in scraper.py"
        assert {
            getsource(scraper).find(req)
            for req in {"from urllib.request import", "import urllib.request"}
        } == {-1}, "Do not use urllib.request in scraper.py"
        super().__init__(daemon=True)

    def run(self):
        while True:
            tbd_url = self.frontier.get_tbd_url()
            # This checks for any next to be downloaded URLs that are obtained after we parse the existing pages
            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                print("++++++++ (worker.py) The frontier is empty and there were no tbd urls")
                break

            # politeness manager here
            self.politeness.wait_polite(tbd_url)

            ###
            # uncomment the code below during development and comment it out during production
            # temporarily here so we can catch errors
            ###

            if not prep_download(tbd_url, self.config, self.logger):
                continue

            resp = download(tbd_url, self.config, self.logger)

            if not self.robot.url_ends_with_xml(tbd_url) and self.simhash.check_page_is_similar(resp):
                self.logger.info(f"Skipping {tbd_url}. Content is too similar.")
                continue

            if not self.robot.url_ends_with_xml(tbd_url) and get_word_count_from_response(resp) and get_word_count_from_response(resp) < self.config.low_information_value:
                self.logger.info(f"Skipping {tbd_url}. Page has less than {self.config.low_information_value} words.")
                continue

            if self.max.found_new_max(tbd_url, resp):
                self.logger.info(f"Found new max. Now storing: {tbd_url}")

            self.token.analyze_response(resp)

            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}."
            )
            scraped_urls = scraper.scraper(tbd_url, resp, self.robot)
            for scraped_url in scraped_urls:
                self.frontier.add_url(scraped_url)
            self.frontier.mark_url_complete(tbd_url)