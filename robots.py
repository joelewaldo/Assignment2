from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse

class Robots:
  def __init__(self, userAgent: str = "*"):
    self.userAgent = userAgent

    self._robots: dict[str, RobotFileParser] = {}

  def can_fetch(self, url) -> bool:
    self._addSite(url)
    baseUrl = self._getBaseUrl(url)
    
    robot = self._robots[baseUrl]
    return robot.can_fetch(self.userAgent, url)

  def sitemaps(self, url) -> list[str]:
    self._addSite(url)
    baseUrl = self._getBaseUrl(url)
    
    robot = self._robots[baseUrl]
    
    sitemaps = robot.site_maps()
    
    if sitemaps:
      return sitemaps
    return []
  
  def _getBaseUrl(self, url):
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"

  def _addSite(self, url):
    baseUrl = self._getBaseUrl(url)

    if not baseUrl in self._robots:
      self._checkRobot(baseUrl)

  def _checkRobot(self, url):
    robotParser = RobotFileParser(url=f"{url}/robots.txt")
    robotParser.read()

    self._robots[url] = robotParser

if __name__ == "__main__":
  dummy_url = "https://docs.python.org/3/library/urllib.robotparser.html"

  robot = Robots()
  print(robot.can_fetch(dummy_url))
  print(robot.sitemaps(dummy_url))