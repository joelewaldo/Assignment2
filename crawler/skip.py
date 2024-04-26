from utils import get_logger
from threading import RLock
import os
import shelve


class Skip:
    def __init__(self, config, restart):
        self.logger = get_logger("Skip", "Skip")
        self.config = config
        self.lock = RLock()
        self.skip_set: dict[str, set] = {}

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
        else:
            self.save["skipped"] = set()
            self.skip_set = self.save

    def _parse_save_file(self):
        self.skip_set = self.save
        self.logger.info(
            f"Found {len(self.skip_set)} skipped urls in the save file."
        )

    def add_url(self, url):
        with self.lock:
            if url not in self.save["skipped"]:
                self.save["skipped"].add(url)
                self.skip_set["skipped"].add(url)
                # "saves" to save file
                self.save.sync()

                self.logger.info(
                    f"Skipping {url}. There are now {len(self.skip_set)} skipped urls in the save file."
                )

    def __del__(self):
        self.save.close()