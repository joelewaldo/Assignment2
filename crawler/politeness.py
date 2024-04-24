from threading import RLock
import time
from crawler.robots import Robots

class Politeness:
  def __init__(self, robot: Robots):
    self.robot = robot
    self.delay = robot.config.time_delay
    self.last_request = time.time() - self.delay
    self.lock = RLock()

  def wait_polite(self, url):
    with self.lock:
      now = time.time()
      elapsed = now - self.last_request

      delay = self.delay
      if self.robot.url_exists(url):
        delay = max(self.robot.crawl_delay(url), delay)
      
      if elapsed < delay:
        time.sleep(delay - elapsed)

      self.last_request = time.time()