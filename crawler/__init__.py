from utils import get_logger
from crawler.frontier import Frontier
from crawler.worker import Worker
from crawler.checksums import Checksums
from crawler.robots import Robots
from crawler.politeness import Politeness
from crawler.simhash import SimHash

class Crawler(object):
    def __init__(self, config, restart, frontier_factory=Frontier, worker_factory=Worker, robots_factory=Robots, politeness_factory=Politeness, simhash_factory=SimHash, checksums_factory=Checksums):
        self.config = config
        self.logger = get_logger("CRAWLER")
        self.robot = robots_factory(config, restart)
        self.frontier = frontier_factory(config, restart, self.robot)
        self.workers = list()
        self.worker_factory = worker_factory
        self.checksums = checksums_factory(config, restart)
        self.politeness = politeness_factory(self.robot)
        self.simhash = simhash_factory(config, restart)

    def start_async(self):
        self.workers = [
            self.worker_factory(worker_id, self.config, self.frontier, self.politeness, self.robot, self.simhash, self.checksums)
            for worker_id in range(self.config.threads_count)]
        for worker in self.workers:
            worker.start()

    def start(self):
        self.start_async()
        self.join()

    def join(self):
        for worker in self.workers:
            worker.join()
