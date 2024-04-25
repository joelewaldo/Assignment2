from utils import get_logger
from crawler.frontier import Frontier
from crawler.worker import Worker
from crawler.checksums import Checksums

class Crawler(object):
    def __init__(self, config, restart, frontier_factory=Frontier, worker_factory=Worker, checksums_factory=Checksums):
        self.config = config
        self.logger = get_logger("CRAWLER")
        self.frontier = frontier_factory(config, restart)
        self.workers = list()
        self.worker_factory = worker_factory
        self.checksums = checksums_factory(config, restart)

    def start_async(self):
        self.workers = [
            self.worker_factory(worker_id, self.config, self.frontier, self.checksums)
            for worker_id in range(self.config.threads_count)]
        for worker in self.workers:
            worker.start()

    def start(self):
        self.start_async()
        self.join()

    def join(self):
        for worker in self.workers:
            worker.join()
