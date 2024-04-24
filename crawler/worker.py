from threading import Thread

from inspect import getsource
from utils.download import download
from utils import get_logger
import scraper
import time


class Worker(Thread):
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
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

            # respects repective site's robots.txt, if doesn't exist uses default politeness delay
            delay = self.config.time_delay
            if self.frontier.robot.url_exists(tbd_url):
                delay = self.frontier.robot.crawl_delay(tbd_url)
            # moved time.sleep here; should work the same
            time.sleep(delay)

            resp = download(tbd_url, self.config, self.logger)
            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}.")
            scraped_urls = scraper.scraper(tbd_url, resp, self.frontier.robot)
            for scraped_url in scraped_urls:
                self.frontier.add_url(scraped_url)
            self.frontier.mark_url_complete(tbd_url)
