from utils import get_logger
from utils.tokenizer import tokenize_url_content
import shelve
import os
# May not need
import threading

class Max:
  def __init__(self, config, restart):
    self.config = config
    self.userAgent = config.user_agent
    self.logger = get_logger("Max", "Max")
    self.curr_max: dict[str, str | int] = {}
    self.lock = threading.RLock()

    # save file stuff down here
    if not os.path.exists(self.config.max_save_file) and not restart:
        # Save file does not exist, but request to load save.
        self.logger.info(
            f"Did not find save file {self.config.max_save_file}, "
            f"recreating from seed.")
    elif os.path.exists(self.config.max_save_file) and restart:
        # Save file does exists, but request to start from seed.
        self.logger.info(
            f"Found save file {self.config.max_save_file}, deleting it.")
        os.remove(self.config.max_save_file)

    # Load existing save file, or create one if it does not exist.
    self.save = shelve.open(self.config.max_save_file)

    if not restart:
      self._parse_save_file()
    else:
      self.save['url'] = 'None'
      self.save['max_words'] = 0
      self.curr_max = self.save
  
  def _parse_save_file(self):
    '''
    Updates self.curr_max with the set stored in the shelve. self.curr_max will be used in all
    corresonding methods to access the dictionary.
    '''

    self.curr_max = self.save
    self.logger.info(
            f"Current max detected - URL: {self.curr_max['url']}, Max words: {self.curr_max['max_words']}")

  def found_new_max(self, url, resp):
    '''
    Takes the url and the resp object and finds the number of words in the page, excluding HTML markup using
    the tokenize_url_content util. Updates the self.curr_max attribute and the corresponding shelve
    when a new max has been found.
    '''

    word_count = len(tokenize_url_content(resp))

    with self.lock:
      if word_count > self.curr_max['max_words']:
          self.curr_max['url'] = url
          self.curr_max['max_words'] = word_count
          self.logger.info(f"Updated max words - New URL: {self.curr_max['url']}, New max words: {self.curr_max['max_words']}")
      
          self.save = self.curr_max
          self.save.sync()
          return True
    
    return False
  
  def __del__(self):
    self.save.close()

if __name__ == "__main__":
  pass