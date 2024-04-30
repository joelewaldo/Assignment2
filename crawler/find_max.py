from utils import get_logger
from utils.tokenizer import tokenize_url_content, get_word_count_from_response
import shelve
import os

import threading


class FindMax:
    def __init__(self, config, restart):
        # Initialize an instance of the config file and userAgent obtained from arguments
        self.config = config
        self.userAgent = config.user_agent

        # Initialize a a new instance of a logger for FindMax
        self.logger = get_logger("Max", "Max")

        # Initialize curr_max which is a dictionary that stores the url containing the max words
        # in the key 'url' and the count of the max words stored in the key 'max_words'
        self.curr_max: dict[str, str | int] = {}

        # Initialize an instance of an RLock to handle concurrent access of shelves
        self.lock = threading.RLock()

        # save file stuff down here
        if not os.path.exists(self.config.max_save_file) and not restart:
            # Save file does not exist, but request to load save.
            self.logger.info(
                f"Did not find save file {self.config.max_save_file}, " f"recreating from seed."
            )
        elif os.path.exists(self.config.max_save_file) and restart:
            # Save file does exists, but request to start from seed.
            self.logger.info(f"Found save file {self.config.max_save_file}, deleting it.")
            os.remove(self.config.max_save_file)

        # Load existing save file, or create one if it does not exist.
        self.save = shelve.open(self.config.max_save_file)

        # If we are not restarting the crawler, call _parse_save_file to load self.curr_max
        # with the data stored in our shelve and resume from there.
        if not restart:
            self._parse_save_file()

        # Otherwise, initialize the key-value pairs in the dictionary and update self.curr_max
        else:
            self.save["url"] = "None"
            self.save["max_words"] = 0
            self.curr_max = self.save

    def _parse_save_file(self):
        """
        Updates self.curr_max with the set stored in the shelve. self.curr_max will be used in all
        corresonding methods to access the dictionary.
        """

        # Set self.curr_max to the instance stored in self.save
        self.curr_max = self.save

        # Log that we have found a save instance and are loading it
        self.logger.info(
            f"Current max detected - URL: {self.curr_max['url']}, Max words: {self.curr_max['max_words']}"
        )

    def found_new_max(self, url, resp):
        """
        Takes the url and the resp object and finds the number of words in the page, excluding HTML markup using
        the tokenize_url_content util. Updates the self.curr_max attribute and the corresponding shelve
        when a new max has been found. These maxes are then saved in the max save file.
        """

        # Obtain the amount of words stored in the response
        word_count = get_word_count_from_response(resp)

        # If there were no words in the response, return False
        if not word_count:
            return False

        # Using self.lock to ensure that concurrent shelve access is properly handled
        # for multi-threaded crawls
        with self.lock:
            # If our current word_count is over the current max word count, update both the url
            # and the stored max words in self.curr_max
            if word_count > self.curr_max["max_words"]:
                self.curr_max["url"] = url
                self.curr_max["max_words"] = word_count

                # Log that we have a found new url with a new max
                self.logger.info(
                    f"Updated max words - New URL: {self.curr_max['url']}, New max words: {self.curr_max['max_words']}"
                )

                # Update the shelve and sync it
                self.save = self.curr_max
                self.save.sync()
                return True

        return False

    def __del__(self):
        # Close the save file when the destructor is called to clean up
        self.save.close()


if __name__ == "__main__":
    pass
