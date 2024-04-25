import re
from robots import Robots
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import lxml
import requests
import hashlib
import threading

ROBOT = Robots()
SAVE = shelve.open(self.config.checksums_save_file)
lock = threading.RLock()

def scraper(url, resp):
    # print("++++++++ (Scraper.py) url: HERE", url)
    # print("++++++++(Scraper.py) resp: HERE", resp)

    links = extract_next_links(resp.url, resp)

    # Compute the checksum of the current document here using url/resp
    checksum = compute_checksum(resp)

     # Then we want to add the link to res only if the computed checksum isn't an exact duplicate
    res = [link for link in links if is_valid(link) and not is_exact_duplicate(checksum)] + ROBOT.sitemaps(resp.url)
    return res

def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content

    # Encountered an error related to resp.raw_response evaluating to None

    # max retries: 5 for status and errors then return empty list
    if not resp.raw_response or resp.raw_response.content:
        return []
    
    # checking for any sitemap links
    if resp.url.lower().endswith('.xml'):
        return ROBOT.parse_sitemap(resp.raw_response.content)

    soup = BeautifulSoup(resp.raw_response.content, 'html.parser', from_encoding='utf-8')
    # doesn't get all the links in the page, might need to use robots.txt and sitemaps
    
    all_links = soup.find_all('a')
    hyperlink_list = []
    for i, link in enumerate(all_links):
        hyperlink_list.append(link.get('href'))

    return hyperlink_list

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        
        if parsed.scheme not in set(["http", "https"]):
            return False

        domain = parsed.netloc
        dotlist = domain.split('.')
        if not ".".join(dotlist[-3:]) in set([".ics.uci.edu", ".cs.uci.edu", ".informatics.uci.edu", ".stat.uci.edu", "ics.uci.edu", "cs.uci.edu", "informatics.uci.edu", "stat.uci.edu"]):
            return False
        '''
        upvote:  1, 1
        downvote: 10
        
        '''

        if not ROBOT.can_fetch(url):
            return False
        
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise

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
    print(compute_checksum('https://ics.uci.edu/2016/04/27/press-release-uc-irvine-launches-executive-masters-program-in-human-computer-interaction-design/'))
    print(compute_checksum('https://ics.uci.edu/2016/04/27/press-release-uc-irvine-launches-executive-masters-program-in-human-computer-interaction-design/'))
    print(compute_checksum('https://cs.ics.uci.edu/'))
