from utils.tokenizer import tokenize_url_content, computeWordFrequencies
from utils import get_logger
import os
import shelve
import hashlib

class SimHash:
    def __init__(self, config, restart):
        self.logger = get_logger("Simhash", "Simhash")
        self.config = config
        self.hashes: dict[str, str] = {}
        
        if not os.path.exists(self.config.simhash_save_file) and not restart:
            # Save file does not exist, but request to load save.
            self.logger.info(
                f"Did not find save file {self.config.simhash_save_file}, "
                f"starting from seed.")
        elif os.path.exists(self.config.simhash_save_file) and restart:
            # Save file does exists, but request to start from seed.
            self.logger.info(
                f"Found save file {self.config.simhash_save_file}, deleting it.")
            os.remove(self.config.simhash_save_file)
        # Load existing save file, or create one if it does not exist.
        self.save = shelve.open(self.config.simhash_save_file)
        if not restart:
            self.hashes = self.save
            

    def check_page_is_similar(self, response):
        page_hash = self._tokenize(response)
        page_hash = self._hashify(page_hash)
        url = response.url

        if self.hashes:
            for url, saved_hash in self.hashes.items():
                if self._compare_hashes(page_hash, saved_hash) >= self.config.similarity_threshold:
                    return True
            return False
        
        self.hashes[url] = page_hash
        self.save[url] = page_hash
        self.save.sync()
        return False
            


    def _tokenize(self, response):
        tokens = tokenize_url_content(response)
        token_frequencies = computeWordFrequencies(tokens)
        return token_frequencies

    def _hashify(self, token_freq_dict):
        try:
            vector = [0] * 256
            for token, freq in token_freq_dict.items():
                hash_hex = int(hashlib.sha256(token.encode('utf-8')).hexdigest(), 16)
                for i in range(256):
                    bit = (hash_hex >> i) & 1
                    vector[i] += freq if bit == 1 else -freq
            
            simhash = 0
            for pos, count in enumerate(vector):
                if count > 0:
                    simhash |= (1 << pos)

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
        bit_length = max(hash1.bit_length(), hash2.bit_length())
        mask = (1 << bit_length) - 1

        # removes potential extra leading bits
        same_bits = mask & same_bits

        return bin(same_bits).count('1') / bit_length
     

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