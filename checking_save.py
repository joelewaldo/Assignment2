import shelve
import os
from utils.config import Config
from configparser import ConfigParser
from argparse import ArgumentParser
from collections import defaultdict
from urllib.parse import urlparse, urlunparse


class SaveChecker:
    def __init__(self, frontier_save_file, max_save_file, token_save_file, skip_save_file):
        self.frontier_save_file = frontier_save_file
        self.max_save_file = max_save_file
        self.token_save_file = token_save_file
        self.skip_save_file = skip_save_file

        if not os.path.exists(self.frontier_save_file):
            # Save file does not exist, but request to load save.
            print("frontier_save_file does not exist")
            self.frontier_save = None

        else:  # Load existing save file, or create one if it does not exist.
            self.frontier_save = shelve.open(self.frontier_save_file)

        if not os.path.exists(self.max_save_file):
            # Save file does not exist, but request to load save.
            print("max_save_file does not exist")
            self.max_save = None

        else:  # Load existing save file, or create one if it does not exist.
            self.max_save = shelve.open(self.max_save_file)

        if not os.path.exists(self.token_save_file):
            # Save file does not exist, but request to load save.
            print("token_save_file does not exist")
            self.token_save = None

        else:  # Load existing save file, or create one if it does not exist.
            self.token_save = shelve.open(self.token_save_file)

        if not os.path.exists(self.skip_save_file):
            # Save file does not exist, but request to load save.
            print("skip_save_file does not exist")
            self.skip_save = None

        else:  # Load existing save file, or create one if it does not exist.
            self.skip_save = shelve.open(self.skip_save_file)

    def longest_page(self) -> tuple[str, str]:
        return (self.max_save["url"], self.max_save["max_words"])

    def common_words(self):
        # Sorting the dictionary by value and storing it as a list of tuples (key, value)
        mostFrequent = sorted(self.token_save.items(), key=lambda x: x[1], reverse=True)

        # If the dictionary has 50 or fewer items, return them all
        if len(mostFrequent) <= 50:
            return dict(mostFrequent)  # Convert list of tuples back to dictionary for consistency
        else:
            # Return the first 50 elements as a dictionary
            return dict(mostFrequent[:50])

    def _normalize_url(self, url):
        """Normalize a URL by removing the fragment part"""
        parsed_url = urlparse(url)
        return urlunparse(parsed_url._replace(fragment=""))

    def unique_pages(self):
        unique_urls = set()
        urls = [url_tuple[0] for url_tuple in self.frontier_save.values()]

        for url in urls:
            if not url in self.skip_save['skipped']:
                normalized_url = self._normalize_url(url)
                unique_urls.add(normalized_url)
        return len(unique_urls)

    def count_subdomains(self):
        subdomains = defaultdict(set)
        urls = [url_tuple[0] for url_tuple in self.frontier_save.values()]

        for url in urls:
            parsed_url = urlparse(url)
            if parsed_url.netloc == "ics.uci.edu" or parsed_url.netloc.endswith(".ics.uci.edu"):
                # Extract the subdomain part and normalize to lowercase
                subdomain = parsed_url.netloc.lower().strip()
                # Use a set for the path to ensure uniqueness
                subdomains[subdomain].add(parsed_url.path)

        # Prepare the output
        results = []
        for subdomain, paths in sorted(subdomains.items()):
            results.append(f"{subdomain}, {len(paths)}")

        return results

    def generate_answer(self):
        with open("Answer.txt", "w") as file:
            file.write("Question 1: \n")
            question_1 = self.unique_pages()
            file.write(f"     There are {question_1} unique pages.\n")
            file.write("Question 2: \n")
            question_2 = self.longest_page()
            file.write(f"     Longest page url is {question_2[0]} with {question_2[1]} words.\n")
            file.write("Question 3: \n")
            question_3 = self.common_words()
            for token, freq in question_3.items():
                file.write(f"     <{token}> -> <{freq}>\n")
            file.write("Question 4: \n")
            question_4 = self.count_subdomains()
            for domain in question_4:
                file.write(f"     {domain}\n")

    def __del__(self):
        self.frontier_save.close()
        self.max_save.close()
        self.token_save.close()


def main(config: Config):
    checker = SaveChecker(config.save_file, config.max_save_file, config.token_save_file)
    checker.generate_answer()


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--config_file", type=str, default="config.ini")
    args = parser.parse_args()

    config_file = args.config_file

    cparser = ConfigParser()
    cparser.read(config_file)
    config = Config(cparser)

    main(config)
