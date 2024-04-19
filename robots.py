from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse
from urllib.request import urlopen
import urllib.error
import ssl
from lxml import etree

class Robots:
  def __init__(self, userAgent: str = "*"):
    self.userAgent = userAgent

    self._robots: dict[str, RobotFileParser] = {}

  def can_fetch(self, url) -> bool:
    """Determine if the user agent can fetch the specified URL."""
    self._addSite(url)
    baseUrl = self._getBaseUrl(url)
    
    robot = self._robots[baseUrl]
    return robot.can_fetch(self.userAgent, url)

  def sitemaps(self, url) -> list[str]:
    """Retrieve list of sitemap URLs declared in the robots.txt."""
    self._addSite(url)
    baseUrl = self._getBaseUrl(url)
    
    robot = self._robots[baseUrl]
    
    sitemaps = robot.site_maps()
    
    if sitemaps:
      return sitemaps
    return []
  
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
    robot_url = f"{url}/robots.txt"
    try:
        with urlopen(robot_url) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.URLError:
        print(f"SSL Verification failed for {url}; retrying without verification (unsafe).")
        try:
            context = ssl._create_unverified_context()
            with urlopen(robot_url, context=context) as response:
                raw = response.read().decode("utf-8")
        except Exception as ex:
            print(f"Failed to retrieve robots.txt with disabled SSL verification: {ex}")
            return 

    robotParser = RobotFileParser()
    robotParser.parse(raw.splitlines())
    self._robots[url] = robotParser

  def parse_sitemap(self, xml_content) -> list[str]:
    tree = etree.fromstring(xml_content)
    urls = tree.xpath('//url/loc/text()')
    return urls

if __name__ == "__main__":
  dummy_url = "https://statconsulting.ics.uci.edu/"
  robot = Robots()
  print(robot.can_fetch(dummy_url))
  print(robot.sitemaps(dummy_url))