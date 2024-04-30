from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from utils.download import download
from utils import get_logger, get_urlhash, normalize
from threading import RLock
import shelve
import os


class Robots:
    """
    This class will track the robots.txt for each base url. When a function like can_fetch, crawl_delay, or sitemaps is called, it will first check
    if the robots.txt file is already saved inside the dictionary. If it is not, it will then get the robots.txt for that url and save it inside the dictionary.
    The dictionary is then always synced up with the robot save file.
    """
    def __init__(self, config, restart):
        self.config = config
        self.userAgent = config.user_agent
        self.logger = get_logger("Robots", "Robots")
        self.lock = RLock()

        self._robots: dict[str, RobotFileParser | None] = {}

        # save file stuff down here
        if not os.path.exists(self.config.robot_save_file) and not restart:
            # Save file does not exist, but request to load save.
            self.logger.info(
                f"Did not find save file {self.config.robot_save_file}, " f"recreating from seed."
            )
        elif os.path.exists(self.config.robot_save_file) and restart:
            # Save file does exists, but request to start from seed.
            self.logger.info(f"Found save file {self.config.robot_save_file}, deleting it.")
            os.remove(self.config.robot_save_file)
        # Load existing save file, or create one if it does not exist.
        self.save = shelve.open(self.config.robot_save_file)

        if not restart:
            self._parse_save_file()

    def _parse_save_file(self):
        print("ROBOT: CHECK THIS length of self.save: ", len(self.save))
        self._robots = self.save
        self.logger.info(f"Found {len(self.save)} robots saved.")

    def url_exists(self, url) -> bool:
        """Checks if url exists in robots dictionary. Returns True if it does and False if not."""
        hashedUrl = self._getHashUrl(url)
        return hashedUrl in self._robots

    def can_fetch(self, url) -> bool:
        """Determine if the user agent can fetch the specified URL."""
        self._addSite(url)
        hashedUrl = self._getHashUrl(url)

        robot = self._robots[hashedUrl]
        if robot:
            return robot.can_fetch(self.userAgent, url)
        return True

    def crawl_delay(self, url) -> float:
        """
        Returns the crawl delay for a specific url. If robots.txt does not exist,
        it will return 0.
        """
        self._addSite(url)
        hashedUrl = self._getHashUrl(url)

        robot = self._robots[hashedUrl]
        if robot:
            delay = robot.crawl_delay(self.userAgent)
            if delay:
                return delay
        return 0

    def sitemaps(self, url) -> list[str]:
        """Retrieve list of sitemap URLs declared in the robots.txt."""
        self._addSite(url)
        hashedUrl = self._getHashUrl(url)

        robot = self._robots[hashedUrl]
        if robot:
            sitemaps = robot.site_maps()
            if sitemaps:
                return sitemaps
        return []

    def parse_sitemap(self, resp) -> list[str]:
        """Parses a sitemap and returns a list of URLs associated with it."""
        if resp.url.lower().endswith(".xml"):
            self.logger.info(
                f"URL: {resp.url} ends with xml.",
            )
            if resp and resp.raw_response and resp.raw_response.content:
                xml_content = resp.raw_response.content
                soup = BeautifulSoup(xml_content, "xml")
                urls = soup.find_all("loc")

                self.logger.info(f"Found {len(urls)} from {resp.url}")

                return [url.text for url in urls]
        return []

    def url_ends_with_xml(self, url) -> bool:
        if url.lower().endswith(".xml"):
            return True
        return False

    def _getBaseUrl(self, url):
        """Extract the base URL from the given URL."""
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"

    def _getHashUrl(self, url):
        baseUrl = self._getBaseUrl(url)
        robot_url = normalize(baseUrl)
        return get_urlhash(robot_url)

    def _addSite(self, url):
        """Add site to robots dictionary if it's not already present."""
        with self.lock:
            hashedUrl = self._getHashUrl(url)
            if not hashedUrl in self._robots:
                self._checkRobot(self._getBaseUrl(url))

    def _checkRobot(self, url):
        """Read and parse the robots.txt for the specified base URL, ignoring SSL verification when neccessary."""
        # todo: add more error handling here
        with self.lock:
            robot_url = f"{url}/robots.txt"

            res = download(robot_url, self.config, logger=self.logger)

            urlhash = self._getHashUrl(url)

            if not res or not res.raw_response:
                self.logger.error(f"Failed to download robots.txt from {robot_url}.")
                self.save[urlhash] = None
                self._robots[urlhash] = None
                # "saves" to save file
                self.save.sync()
                return

            self.logger.info(
                f"Downloaded {robot_url}, status <{res.status}>, "
                f"using cache {self.config.cache_server}."
            )

            robotParser = RobotFileParser()
            robotParser.parse(res.raw_response.text.splitlines())
            self._robots[urlhash] = robotParser
            self.save[urlhash] = robotParser
            # "saves" to save file
            self.save.sync()

    def __del__(self):
        self.save.close()


if __name__ == "__main__":
    from configparser import ConfigParser
    from utils.config import Config
    from utils.server_registration import get_cache_server

    config_file = "config.ini"

    cparser = ConfigParser()
    cparser.read(config_file)
    config = Config(cparser)
    config.cache_server = get_cache_server(config, True)

    dummy_url = "https://www.stat.uci.edu/wp-sitemap.xml"
    robot = Robots(config)
    print(robot.can_fetch(dummy_url))
    print(robot.sitemaps(dummy_url))
    print(robot.crawl_delay(dummy_url))
