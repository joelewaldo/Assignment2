from urllib.parse import urlparse
from threading import RLock
import os
import shelve
from utils import get_logger, get_urlhash, normalize


class Skip:
    """
    This class keeps track of all the pages that are skipped and saves it all in a save file.
    """

    def __init__(self, config, restart):
        self.logger = get_logger("Skip", "Skip")
        self.config = config
        self.lock = RLock()
        self.skip_set: dict[str, str] = {}

        if not os.path.exists(self.config.skip_save_file) and not restart:
            # Save file does not exist, but request to load save.
            self.logger.info(
                f"Did not find save file {self.config.skip_save_file}, " f"starting from seed."
            )
        elif os.path.exists(self.config.skip_save_file) and restart:
            # Save file does exists, but request to start from seed.
            self.logger.info(f"Found save file {self.config.skip_save_file}, deleting it.")
            os.remove(self.config.skip_save_file)
        # Load existing save file, or create one if it does not exist.
        self.save = shelve.open(self.config.skip_save_file)

        if not restart:
            self._parse_save_file()

    def _parse_save_file(self):
        self.skip_set = self.save
        self.logger.info(f"Found {len(self.skip_set)} skipped urls in the save file.")

    def add_url(self, url):
        """
        When there is a url to be skipped, it will first get the hash of the url and check if that hash already exists within our saves. If it does not,
        it will add it to the dictionary of urls that we skip. Then the save files are synced.
        """
        hashed_url = self._getHashUrl(url)
        with self.lock:
            if hashed_url not in self.save:
                self.save[hashed_url] = url
                self.skip_set[hashed_url] = url
                # "saves" to save file
                self.save.sync()

                self.logger.info(
                    f"Skipping {url}. There are now {len(self.skip_set)} skipped urls in the save file."
                )

    def _getHashUrl(self, url):
        """Gets the url hash for a certain url."""
        url = normalize(url)
        return get_urlhash(url)

    def __del__(self):
        self.save.close()
