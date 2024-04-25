from threading import Thread

from inspect import getsource
from utils.download import download
from utils import get_logger
import scraper
import time


class Worker(Thread):
    def __init__(self, worker_id, config, frontier, politeness, robot, simhash):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        self.politeness = politeness
        self.robot = robot
        self.simhash = simhash
        # basic check for requests in scraper
        assert {getsource(scraper).find(req) for req in {"from requests import", "import requests"}} == {-1}, "Do not use requests in scraper.py"
        assert {getsource(scraper).find(req) for req in {"from urllib.request import", "import urllib.request"}} == {-1}, "Do not use urllib.request in scraper.py"
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

            resp = download(tbd_url, self.config, self.logger)

            if resp.headers and resp.headers['content-length'] and float(resp.headers['content-length']) > self.config.max_file_size * 1048576:
                self.logger.info(f"Skipping {tbd_url}. File size threshold exceeded {self.config.max_file_size * 1048576} with {float(resp.headers['content-length'])}")
                continue

            if self.simhash.check_page_is_similar(resp):
                self.logger.info(f"Skipping {tbd_url}. Content is too similar.")
                continue

            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}.")
            scraped_urls = scraper.scraper(tbd_url, resp, self.robot)
            for scraped_url in scraped_urls:
                self.frontier.add_url(scraped_url)
            self.frontier.mark_url_complete(tbd_url)

            ###
            # uncomment the code below during production and comment it out during development
            # ignores errors and completely skips url
            ###

            # for attempt in range(self.config.max_retries):
            #     try:
            #         resp = download(tbd_url, self.config, self.logger)
            #         self.logger.info(
            #             f"Downloaded {tbd_url}, status <{resp.status}>, "
            #             f"using cache {self.config.cache_server}.")
            #         scraped_urls = scraper.scraper(tbd_url, resp, self.robot)
            #         for scraped_url in scraped_urls:
            #             self.frontier.add_url(scraped_url)
            #         self.frontier.mark_url_complete(tbd_url)
            #         break
            #     except Exception as e:
            #         self.logger.error(f"Error downloading or processing {tbd_url}: {str(e)}")
            #         if attempt < self.config.max_retries:
            #             self.logger.info(f"Retrying {tbd_url} (Attempt {attempt + 1}/{self.config.max_retries}) in {self.config.retry_time} seconds.")
            #             time.sleep(self.config.retry_time)
            #         else:
            #             self.logger.error(f"Failed to process {tbd_url} after {self.config.max_retries} attempts.")
            #             break
