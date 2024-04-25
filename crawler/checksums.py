from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from utils.download import download
from utils import get_logger, get_urlhash, normalize
import shelve
import os
import hashlib
import threading

lock = threading.RLock()

class Checksums:
  def __init__(self, config, restart):
    self.config = config
    self.userAgent = config.user_agent
    self.logger = get_logger("Checksums", "Checksums")

    self._checksums = set()

    # save file stuff down here
    if not os.path.exists(self.config.checksums_save_file) and not restart:
        # Save file does not exist, but request to load save.
        self.logger.info(
            f"Did not find save file {self.config.checksums_save_file}, "
            f"recreating from seed.")
    elif os.path.exists(self.config.checksums_save_file) and restart:
        # Save file does exists, but request to start from seed.
        self.logger.info(
            f"Found save file {self.config.checksums_save_file}, deleting it.")
        os.remove(self.config.checksums_save_file)

    # Load existing save file, or create one if it does not exist.
    self.save = shelve.open(self.config.checksums_save_file)

    if not restart:
      self._parse_save_file()
  
  def _parse_save_file(self):
    '''
    Updates self._checksums with the set stored in the shelve. self._checksums will be used in all
    corresonding methods to access the set.
    '''

    self._checksums = self.save
    self.logger.info(
            f"Found {len(self.save)} checksums saved.")
  
  def compute_checksum(response):
    '''
    Computes the checksum of the given document passed in as url by using a SHA-256 hash on
    the content of the url. Saves it to SAVE
    '''
    
    try:
        # Create a new SHA-256 hash object
        sha256_hash = hashlib.sha256()

        # Update the hash object with the bytes of the content
        sha256_hash.update(response.raw_response.content)

        # Return the HEX digest of the hash object
        return sha256_hash.hexdigest()

    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return None
  
  def is_exact_duplicate(checksum):
    '''
    Uses checksum to determine if the computed checksum has been encountered before. If so, it is an
    exact duplicate and should be skipped. If it isn't, add it to SAVE. Due to the way shelves work,
    we must manually reassign the set to update it.
    '''
    
    with lock:
        if 'checksums' not in SAVE:
            SAVE['checksums'] = set()
        
        saved_checksums = SAVE['checksums']

        if checksum not in saved_checksums:
            saved_checksums.add(checksum)
            SAVE['checksums'] = saved_checksums
            SAVE.sync()
            return False
        
        return True

if __name__ == "__main__":
  pass