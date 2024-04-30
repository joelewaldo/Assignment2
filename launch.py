from configparser import ConfigParser
from argparse import ArgumentParser

from utils.server_registration import get_cache_server
from utils.config import Config
from crawler import Crawler


def main(config_file, restart):
    """
    Defines the main function, taking in the config file and restart as parameters.
    """

    cparser = ConfigParser()
    cparser.read(config_file)
    config = Config(cparser)
    # Registers the program with the cache server
    config.cache_server = get_cache_server(config, restart)
    # Define the crawler using Crawler class by passing config file and restart
    crawler = Crawler(config, restart)
    # Call start method in Crawler class
    crawler.start()


if __name__ == "__main__":
    # When the program runs it takes the restart parameter and config file from the command line.
    parser = ArgumentParser()
    # set restart default to true if we want to start running from the seeds otherwise run from save file
    parser.add_argument("--restart", action="store_true", default=False)
    parser.add_argument("--config_file", type=str, default="config.ini")
    args = parser.parse_args()
    main(args.config_file, args.restart)
