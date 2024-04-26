import os
import shelve
from bs4 import BeautifulSoup
from utils import get_logger
from threading import RLock

stop_words = {
    'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', "aren't", 'as', 'at',
    'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by',
    "can't", 'cannot', 'could', "couldn't", 'did', "didn't", 'do', 'does', "doesn't", 'doing', "don't", 'down',
    'during', 'each', 'few', 'for', 'from', 'further',
    'had', "hadn't", 'has', "hasn't", 'have', "haven't", 'having', 'he', "he'd", "he'll", "he's", 'her',
    "here's", 'hers', 'herself', 'him', 'himself', 'his', 'how', "how's",
    'i', "i'd", "i'll", "i'm", "i've", 'if', 'in', 'into', 'is', "isn't", 'it', "it's", 'its', 'itself', "let's",
    'me', 'more', 'most', "mustn't", 'my', 'myself',
    'no', 'nor', 'not', 'of', 'off', 'on', 'once', 'only', 'or', 'other', 'ought', 'our', 'ours', 'ourselves', 'out',
    'over', 'own', 'same', "shan't", 'she', "she'd", "she'll", "she's", 'should', "shouldn't", 'so', 'some', 'such',
    'than', 'that', "that's", 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there', "there's", 'these',
    'they', "they'd", "they'll", "they're", "they've", 'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up',
    'very', 'was', "wasn't", 'we', "we'd", "we'll", "we're", "we've", 'were', "weren't", 'what', "what's", 'when',
    "when's", 'where', "where's", 'which', 'while', 'who', "who's", 'whom', 'why', "why's", 'with', "won't", 'would',
    "wouldn't", 'you', "you'd", "you'll", "you're", "you've", 'your', 'yours', 'yourself', 'yourselves'
}



class Token:
    def __init__(self, config, restart):
        self.logger = get_logger("Token", "Token")
        self.config = config
        self.counter: dict[str, int] = {}
        self.lock = RLock
        
        if not os.path.exists(self.config.token_save_file) and not restart:
            # Save file does not exist, but request to load save.
            self.logger.info(
                f"Did not find save file {self.config.token_save_file}, "
                f"starting from seed.")
        elif os.path.exists(self.config.token_save_file) and restart:
            # Save file does exists, but request to start from seed.
            self.logger.info(
                f"Found save file {self.config.token_save_file}, deleting it.")
            os.remove(self.config.token_save_file)
        # Load existing save file, or create one if it does not exist.
        self.save = shelve.open(self.config.token_save_file)
        if not restart:
            self.counter = self.save

    def analyze_response(self, resp):
        with self.lock:
            try:
                res = self._tokenize_url_content(resp)
                self._computeWordFrequencies(res)
                self.logger.info(
                    f"Successfully computed word frequencies url: {resp.url}."
                )     
            except Exception as e:
                self.logger.error(
                    f"Something went wrong with this url: {resp.url}. -- Error: {e}")
        
        
    def _isAlnum(self, character: str) -> bool:
        """
        Check if a character is alphanumeric.
        
        Parameters:
        - character: str: Character to be checked.
        
        Returns:
        - bool: True if the character is alphanumeric, otherwise False.
        """
        try:
            character = character.lower()
            return (ord('a') <= ord(character) <= ord('z')) or (ord('0') <= ord(character) <= ord('9'))
        except:
            return False
        

    def _tokenize_url_content(self, response) -> list[str]:
        """
        Parse the HTML content of a response object and tokenize it.
        
        Parameters:
        - response: Response: Response object from HTTP request.
        
        Returns:
        - list[str]: List of tokens (alphanumeric sequences) from the content.
        """
        tokens = []
        currentWord = ""
        
        try:
            soup = BeautifulSoup(response.raw_response.text, 'html.parser')
            text = soup.get_text()
            for character in text:
                if self._isAlnum(character):
                    currentWord += character.lower()
                else:
                    if currentWord and not (currentWord in stop_words):
                        tokens.append(currentWord)
                        currentWord = ""
            if currentWord and not (currentWord in stop_words):
                tokens.append(currentWord)
                
        except Exception as e:
            print(f"An unexpected error occurred while processing the text: {e}")
            return []
        
        return tokens

    def _computeWordFrequencies(self, tokenList: list[str]):
        """
        Compute the frequency of each token.
        
        Parameters:
        - tokenList: list[str]: List of tokens.
        
        Returns:
        - dict[str, int]: Dictionary mapping each token to its frequency count.
        """
        with self.lock:
            try:
                for token in tokenList:
                    if token in self.counter:
                        self.counter[token] += 1
                        self.save[token] += 1
                    else:
                        self.counter[token] = 1
                        self.save[token] = 1
                    self.save.sync()
            except Exception as e:
                print(f"An unexpected error occurred while updating save file: {e}")
        
    def __del__(self):
        self.save.close()