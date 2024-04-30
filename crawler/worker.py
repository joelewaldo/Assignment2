from threading import Thread

from inspect import getsource
from utils.download import download, prep_download
from utils import get_logger
from utils.tokenizer import get_word_count_from_response
import scraper
import time


class Worker(Thread):
    def __init__(self, worker_id, config, frontier, politeness, robot, simhash, token, m_max, skip):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        self.politeness = politeness
        self.robot = robot
        self.simhash = simhash
        self.max = m_max
        self.token = token
        self.skip = skip
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

            # requests for the headers of the page first. if the headers show that the file content is above a certain threshold, then we will skip.
            if not prep_download(tbd_url, self.config, self.logger):
                self.skip.add_url(tbd_url)
                self.frontier.mark_url_complete(tbd_url)
                continue

            # downloads the page
            resp = download(tbd_url, self.config, self.logger)

            # Checks if the page has a resp and resp.raw_response. If they don't have this, then page is blank so we skip the url.
            if not (resp and resp.raw_response):
                self.logger.info(f"Skipping {tbd_url}. Page is empty.")
                self.skip.add_url(tbd_url)
                self.frontier.mark_url_complete(tbd_url)
                continue

            # Another check for content length after we have grabbed the content. If the file content is above a certain threshold then we will
            # skip the url.
            if (
                resp.raw_response.headers
                and resp.raw_response.headers.get("content-length")
                and float(resp.raw_response.headers.get("content-length"))
                > self.config.max_file_size * 1048576
            ):
                self.logger.info(
                    f"Skipping {tbd_url}. File size threshold exceeded {self.config.max_file_size * 1048576} with {float(resp.raw_response.headers.get('content-length'))}"
                )
                self.skip.add_url(tbd_url)
                self.frontier.mark_url_complete(tbd_url)
                continue

            # Checks the number of words a url has. If it is above a certain threshold, then we will skip the url.
            if (
                not self.robot.url_ends_with_xml(tbd_url)
                and get_word_count_from_response(resp)
                and get_word_count_from_response(resp) < self.config.low_information_value
            ):
                self.logger.info(
                    f"Skipping {tbd_url}. Page has less than {self.config.low_information_value} words."
                )
                self.skip.add_url(tbd_url)
                self.frontier.mark_url_complete(tbd_url)
                continue

            # Checks the simhash of the page. If it detects the page as similar to another one we already have, it will skip.
            if not self.robot.url_ends_with_xml(tbd_url) and self.simhash.check_page_is_similar(
                resp
            ):
                self.logger.info(f"Skipping {tbd_url}. Content is too similar.")
                self.skip.add_url(tbd_url)
                self.frontier.mark_url_complete(tbd_url)
                continue

            # Tracks the number of words in a certain page. If a new max is found we will log it.
            if self.max.found_new_max(tbd_url, resp):
                self.logger.info(f"Found new max. Now storing: {tbd_url}")

            # Computes the token frequencies of the url and saves it in the token save file.
            self.token.analyze_response(resp)

            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}."
            )
            scraped_urls = scraper.scraper(tbd_url, resp, self.robot)
            for scraped_url in scraped_urls:
                self.frontier.add_url(scraped_url)
            self.frontier.mark_url_complete(tbd_url)
