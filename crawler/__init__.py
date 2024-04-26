from utils import get_logger
from crawler.frontier import Frontier
from crawler.worker import Worker
from crawler.robots import Robots
from crawler.politeness import Politeness
from crawler.simhash import SimHash
from crawler.find_max import FindMax
from crawler.common_token import Token

class Crawler(object):
    def __init__(self, config, restart, frontier_factory=Frontier, worker_factory=Worker, robots_factory=Robots, politeness_factory=Politeness, simhash_factory=SimHash, token_factory=Token, max_factory=FindMax):
        self.config = config
        self.logger = get_logger("CRAWLER")
        self.robot = robots_factory(config, restart)
        self.frontier = frontier_factory(config, restart, self.robot)
        self.workers = list()
        self.worker_factory = worker_factory
        self.politeness = politeness_factory(self.robot)
        self.simhash = simhash_factory(config, restart)
        self.token = token_factory(config, restart)
        self.max= max_factory(config, restart)

    def start_async(self):
        self.workers = [
            self.worker_factory(worker_id, self.config, self.frontier, self.politeness, self.robot, self.simhash, self.token, self.max)
            for worker_id in range(self.config.threads_count)]
        for worker in self.workers:
            worker.start()

    def start(self):
        self.start_async()
        self.join()

    def join(self):
        for worker in self.workers:
            worker.join()
