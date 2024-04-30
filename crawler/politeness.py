from threading import RLock
import time
from crawler.robots import Robots


class Politeness:
    """
    This class manages the Politeness for urls, ensuring that each thread respects the politeness values. For each url, the class will track
    the last time the page with the base url was accessed. If it was accessed recently, it will sleep the thread and it will be able to then
    make the request after the wait. However, if it was not accessed recently, the thread will be able to access the content without any wait.
    """

    def __init__(self, robot: Robots):
        self.robot = robot
        self.delay = robot.config.time_delay
        self.last_request: dict[str, float] = {}
        self.lock = RLock()

    def wait_polite(self, url):
        """
        Each thread will call this function. This function will ensure that politeness is ensured for the base url by saving the last access time and
        sleeping the thread if it was accessed recently.

        Parameters:
        - url: The url of the page to be checked

        Returns:
        None
        """
        baseUrl = self.robot._getBaseUrl(url)
        with self.lock:
            now = time.time()
            elapsed = now - self.last_request.get(baseUrl, now - self.delay)

            delay = self.delay
            if self.robot.url_exists(url):
                delay = max(self.robot.crawl_delay(url), delay)

            if elapsed < delay:
                time.sleep(delay - elapsed)

            self.last_request[baseUrl] = time.time()
