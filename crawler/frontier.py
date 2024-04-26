import os
import shelve

from threading import Thread, RLock
from queue import Queue, Empty

from utils import get_logger, get_urlhash, normalize
from scraper import is_valid


class Frontier(object):
    def __init__(self, config, restart, robot):
        self.logger = get_logger("FRONTIER")
        self.config = config
        self.to_be_downloaded = Queue()
        self.robot = robot
        self.lock = RLock()

        if not os.path.exists(self.config.save_file) and not restart:
            # Save file does not exist, but request to load save.
            self.logger.info(
                f"Did not find save file {self.config.save_file}, " f"starting from seed."
            )
        elif os.path.exists(self.config.save_file) and restart:
            # Save file does exists, but request to start from seed.
            self.logger.info(f"Found save file {self.config.save_file}, deleting it.")
            os.remove(self.config.save_file)
        # Load existing save file, or create one if it does not exist.
        self.save = shelve.open(self.config.save_file)
        if restart:
            for url in self.config.seed_urls:
                self.add_url(url)
        else:
            # Set the frontier state with contents of save file.
            self._parse_save_file()
            if not self.save:
                for url in self.config.seed_urls:
                    self.add_url(url)

    def _parse_save_file(self):
        """This function can be overridden for alternate saving techniques."""
        total_count = len(self.save)
        tbd_count = 0
        print("CHECK THIS length of self.save: ", len(self.save))
        for url, completed in self.save.values():
            print("CHECK THIS url: ", url, "CHECK IF COMPLETED completed: ", completed)
            if not completed and is_valid(url, self.robot):
                self.to_be_downloaded.put(url)
                tbd_count += 1
        self.logger.info(
            f"Found {tbd_count} urls to be downloaded from {total_count} " f"total urls discovered."
        )

    def get_tbd_url(self):
        try:
            url = self.to_be_downloaded.get()
            return url
        except Empty:
            return None

    def add_url(self, url):
        with self.lock:
            url = normalize(url)
            urlhash = get_urlhash(url)
            if urlhash not in self.save:
                self.save[urlhash] = (url, False)
                # "saves" to save file
                self.save.sync()
                self.to_be_downloaded.put(url)

    def mark_url_complete(self, url):
        with self.lock:
            self.to_be_downloaded.task_done()
            urlhash = get_urlhash(url)
            if urlhash not in self.save:
                # This should not happen.
                self.logger.error(f"Completed url {url}, but have not seen it before.")

            self.save[urlhash] = (url, True)
            self.save.sync()

    def __del__(self):
        self.save.close()
