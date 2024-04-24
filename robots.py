from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from utils.download import download
from utils import get_logger

class Robots:
  def __init__(self, config):
    self.config = config
    self.userAgent = config.user_agent
    self.logger = get_logger("Robots", "Robots")

    self._robots: dict[str, RobotFileParser] = {}

  def can_fetch(self, url) -> bool:
    """Determine if the user agent can fetch the specified URL."""
    self._addSite(url)
    baseUrl = self._getBaseUrl(url)

    if baseUrl in self._robots:
      robot = self._robots[baseUrl]
      return robot.can_fetch(self.userAgent, url)
    return True
  
  def crawl_delay(self, url) -> float:
    """
    Returns the crawl delay for a specific url. If robots.txt does not exist,
    it will return 0.
    """
    self._addSite(url)
    baseUrl = self._getBaseUrl(url)

    if baseUrl in self._robots:
      robot = self._robots[baseUrl]
      delay = robot.crawl_delay(self.userAgent)
      if delay:
        return delay
    return 0

  def sitemaps(self, url) -> list[str]:
    """Retrieve list of sitemap URLs declared in the robots.txt."""
    self._addSite(url)
    baseUrl = self._getBaseUrl(url)
    
    if baseUrl in self._robots:
      robot = self._robots[baseUrl]
      sitemaps = robot.site_maps()
      if sitemaps:
        return sitemaps
    return []

  def parse_sitemap(self, xml_content) -> list[str]:
    """Parses a sitemap and returns a list of URLs associated with it."""
    soup = BeautifulSoup(xml_content, 'xml')
    urls = soup.find_all('loc') 
    return [url.text for url in urls]
  
  def _getBaseUrl(self, url):
    """Extract the base URL from the given URL."""
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"

  def _addSite(self, url):
    """Add site to robots dictionary if it's not already present."""
    baseUrl = self._getBaseUrl(url)

    if not baseUrl in self._robots:
      self._checkRobot(baseUrl)

  def _checkRobot(self, url):
    """Read and parse the robots.txt for the specified base URL, ignoring SSL verification when neccessary."""
    # todo: add more error handling here
    robot_url = f"{url}/robots.txt"

    res = download(robot_url, self.config, logger=self.logger)

    if not res or not res.raw_response:
      self.logger.error(f"Failed to download robots.txt from {robot_url}.")
      return
    
    self.logger.info(
                f"Downloaded {robot_url}, status <{res.status}>, "
                f"using cache {self.config.cache_server}.")
    
    robotParser = RobotFileParser()
    robotParser.parse(res.raw_response.text.splitlines())
    self._robots[url] = robotParser

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