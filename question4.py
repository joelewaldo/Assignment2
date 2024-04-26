import re
from collections import defaultdict
from urllib.parse import urlparse

log_file_path = "./Logs/Worker.log"

with open("./Logs/Worker.log", "r") as file:
    log_data = file.read()

subdomains_dict = defaultdict(set)

regex = re.compile(r"https?://[^\s,]+")

for line in log_data.splitlines():
    urls = regex.findall(line)
    for url in urls:
        parsed_url = urlparse(url)
        if ".ics.uci.edu" in parsed_url.netloc or parsed_url.netloc == "ics.uci.edu":
            # www.abc.com
            subdomain = parsed_url.netloc
            # /abc/path
            path = parsed_url.path
            subdomains_dict[subdomain].add(path)

res = []
for key, value in sorted(subdomains_dict.items()):
    res.append(f"http://{key}, {len(value)}")

for i in res:
    print(i)
