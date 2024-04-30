from utils.tokenizer import tokenize_url_content, computeWordFrequencies
from utils import get_logger
from threading import RLock
import os
import shelve
import hashlib


class SimHash:
    """
    This class will manage all the sim hashes for each url. If the page has not been accessed yet, the class will compute the respective sim hash and
    save it in the save file. When we want to compare the similarity of a page,  we will iterate through all the hashes saved and if the similarity is
    above a certain threshold, it will return True for being similar and False for being unsimilar.
    """

    def __init__(self, config, restart):
        """
        initializes the simhash save files storing urls as keys and their hashes as values
        """
        self.logger = get_logger("Simhash", "Simhash")
        self.config = config
        self.lock = RLock()
        self.hashes: dict[str, str] = {}

        if not os.path.exists(self.config.simhash_save_file) and not restart:
            # Save file does not exist, but request to load save.
            self.logger.info(
                f"Did not find save file {self.config.simhash_save_file}, " f"starting from seed."
            )
        elif os.path.exists(self.config.simhash_save_file) and restart:
            # Save file does exists, but request to start from seed.
            self.logger.info(f"Found save file {self.config.simhash_save_file}, deleting it.")
            os.remove(self.config.simhash_save_file)
        # Load existing save file, or create one if it does not exist.
        self.save = shelve.open(self.config.simhash_save_file)
        if not restart:
            self.hashes = self.save

    def check_page_is_similar(self, response):
        """
        this function looks through all the hashes and tries to determine if there is a page that is above our similarity threshold
        if so --> return true for similarity
        else --> return false
        """

        # tokenizes the page
        page_hash = self._tokenize(response)

        # hashes the page based off tokens
        page_hash = self._hashify(page_hash)
        resp_url = response.url

        # only one thread can work with simhash at a time this prevents any errors of synchronization from happening
        with self.lock:

            # if there are hashes currently continue
            if self.hashes:
                for url, saved_hash in self.hashes.items():
                    # compare the current pagehash with the other hashes in the simhash save file
                    # if there it passes the similarity threshold then return true
                    if (
                        self._compare_hashes(page_hash, saved_hash)
                        >= self.config.similarity_threshold
                    ):
                        self.logger.info(
                            f"{resp_url} IS SIMILAR TO {url} WITH PERCENTAGE: {self._compare_hashes(page_hash, saved_hash)}"
                        )
                        return True

                # since the hashes are not similar we will return false and store the page with its hash
                self.hashes[resp_url] = page_hash
                self.save[resp_url] = page_hash
                self.logger.info(f"SimHash of {resp_url} is --> {page_hash}")
                self.save.sync()
                return False
            # this will get run when there is currently nothing in the save file since the hashes are not similar
            # we will return false and store the page with its hash
            self.hashes[resp_url] = page_hash
            self.save[resp_url] = page_hash
            self.logger.info(f"SimHash of {resp_url} is --> {page_hash}")

            self.save.sync()
        return False

    def _tokenize(self, response):
        """
        tokenizes the url and store the word frequencies in a dictionary
        and return the dictionary
        """
        tokens = tokenize_url_content(response)
        token_frequencies = computeWordFrequencies(tokens)
        return token_frequencies

    def _hashify(self, token_freq_dict):
        """
        returns the hash of the current page based of the tokens dictionary
        """
        try:
            # intiializes the vector with 256 0's as bits
            vector = [0] * 256
            for token, freq in token_freq_dict.items():
                # turns the token "word" into a hash by encoding the token first
                # and then converts the encodign into a sha256 hash
                # and then gets the hexadecimal representation of it and turning it into an integer and storing it
                hash_hex = int(hashlib.sha256(token.encode("utf-8")).hexdigest(), 16)
                for i in range(256):
                    # this checks each bit in the current hash, if it's a 1 then we add update the vector by incrementing
                    # the ith value by 1
                    # this is done by shifting the bit by i times
                    bit = (hash_hex >> i) & 1
                    vector[i] += freq if bit == 1 else -freq

            # checks the position of each vector if the vector[i] is positive
            # then we add 1 to the simhash and we shift left
            # we are ultimately building the simhash for the page and return it at the end
            simhash = 0
            for pos, count in enumerate(vector):
                if count > 0:
                    simhash |= 1 << pos

            simhash_hash = f"{simhash:064x}"

            return simhash_hash

        except Exception as e:
            self.logger.error("Failed to compute hash: " + str(e))

    def _compare_hashes(self, hash1, hash2):
        # XOR operator counting the bits that are the same and turning it into a zero
        hash1 = int(hash1, 16)
        hash2 = int(hash2, 16)
        diff = hash1 ^ hash2

        # inverting the bits making the 1 represent the bits that are the same
        same_bits = ~diff

        # using mask because the invert operator could add extra leading 1s past the original bit length
        bit_length = 256
        mask = (1 << bit_length) - 1

        # removes potential extra leading bits
        same_bits = mask & same_bits

        return bin(same_bits).count("1") / bit_length

    def __del__(self):
        self.save.close()


if __name__ == "__main__":
    pass
    # token1 = tokenize_from_file("../test1.txt")
    # token2 = tokenize_from_file("../test2.txt")

    # token_frequencies1 = computeWordFrequencies(token1)
    # token_frequencies2 = computeWordFrequencies(token2)

    # hash1 = hashify(token_frequencies1)
    # hash2 = hashify(token_frequencies2)

    # similarity = compare_hashes(hash1, hash2)

    # print("similariryt", similarity)
