import re


class Config(object):
    """
    This class defines all the config parameters used in the program.
    """
    def __init__(self, config):
        self.user_agent = config["IDENTIFICATION"]["USERAGENT"].strip()
        print(self.user_agent)
        assert self.user_agent != "DEFAULT AGENT", "Set useragent in config.ini"
        assert re.match(
            r"^[a-zA-Z0-9_ ,]+$", self.user_agent
        ), "User agent should not have any special characters outside '_', ',' and 'space'"
        self.threads_count = int(config["LOCAL PROPERTIES"]["THREADCOUNT"])
        self.save_file = config["LOCAL PROPERTIES"]["SAVE"]
        self.robot_save_file = config["LOCAL PROPERTIES"]["ROBOTSAVE"]
        self.simhash_save_file = config["LOCAL PROPERTIES"]["SIMHASHSAVE"]
        self.max_save_file = config["LOCAL PROPERTIES"]["MAXSAVE"]
        self.token_save_file = config["LOCAL PROPERTIES"]["TOKENSAVE"]
        self.skip_save_file = config["LOCAL PROPERTIES"]["SKIPSAVE"]

        self.host = config["CONNECTION"]["HOST"]
        self.port = int(config["CONNECTION"]["PORT"])

        self.seed_urls = config["CRAWLER"]["SEEDURL"].split(",")
        self.max_file_size = int(config["CRAWLER"]["MAXFILESIZE"])
        self.time_delay = float(config["CRAWLER"]["POLITENESS"])
        self.low_information_value = int(config["CRAWLER"]["LOWINFORMATIONVALUE"])
        self.similarity_threshold = float(config["CRAWLER"]["SIMILARITYTHRESHOLD"])

        self.cache_server = None
