import re
from crawler.robots import Robots
from crawler.checksums import Checksums
from urllib.parse import urlparse
from urllib.parse import urljoin
from bs4 import BeautifulSoup

# May not need these
import hashlib
import threading

def scraper(url, resp, robot: Robots, checksums: Checksums):
    # print("++++++++ (Scraper.py) url: HERE", url)
    # print("++++++++(Scraper.py) resp: HERE", resp)

    # checking for any sitemap links
    sitemaps = robot.parse_sitemap(resp)
    if sitemaps:
        return sitemaps

    links = extract_next_links(url, resp)
    checksum = checksums.compute_checksum(resp)
    res = [link for link in links if is_valid(link, robot) and not checksums.is_exact_duplicate(checksum)] + robot.sitemaps(resp.url)

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

    # max retries: 5 for status and errors then return empty list

    # Detect and avoid dead URLs that return a 200 status but no data (click here to see what the different HTTP status codes meanLinks to an external site.)
    hyperlink_list = []


    if resp.status == 200 and (resp.raw_response is None or not resp.raw_response.content):
        return hyperlink_list
    
    if resp.status == 204 or resp.status >= 400:
        return hyperlink_list
    
    if resp.status >=300:
        if "Location" in resp.raw_response.headers:
            return [urljoin(resp.url, resp.headers['Location'])]

    soup = BeautifulSoup(resp.raw_response.content, 'html.parser', from_encoding='utf-8')
    # doesn't get all the links in the page, might need to use robots.txt and sitemaps
    
    all_links = soup.find_all('a')
    for i, link in enumerate(all_links):
        hyperlink_list.append(link.get('href'))

    return hyperlink_list

def is_valid(url, robot: Robots):
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

        if not robot.can_fetch(url):
            return False
        
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf|war"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso|ppsx"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise

# def compute_checksum(response):
#     '''
#     Computes the checksum of the given document passed in as url by using a SHA-256 hash on
#     the content of the url. Saves it to SAVE
#     '''
    
#     try:
#         # Create a new SHA-256 hash object
#         sha256_hash = hashlib.sha256()

#         # Update the hash object with the bytes of the content
#         sha256_hash.update(response.raw_response.content)

#         # Return the HEX digest of the hash object
#         return sha256_hash.hexdigest()

#     except requests.RequestException as e:
#         print(f"An error occurred: {e}")
#         return None

# def is_exact_duplicate(checksum):
#     '''
#     Uses checksum to determine if the computed checksum has been encountered before. If so, it is an
#     exact duplicate and should be skipped. If it isn't, add it to SAVE. Due to the way shelves work,
#     we must manually reassign the set to update it.
#     '''
    
#     with lock:
#         if 'checksums' not in SAVE:
#             SAVE['checksums'] = set()
        
#         saved_checksums = SAVE['checksums']

#         if checksum not in saved_checksums:
#             saved_checksums.add(checksum)
#             SAVE['checksums'] = saved_checksums
#             SAVE.sync()
#             return False
        
#         return True

if __name__ == "__main__":
    print(compute_checksum('https://ics.uci.edu/2016/04/27/press-release-uc-irvine-launches-executive-masters-program-in-human-computer-interaction-design/'))
    print(compute_checksum('https://ics.uci.edu/2016/04/27/press-release-uc-irvine-launches-executive-masters-program-in-human-computer-interaction-design/'))
    print(compute_checksum('https://cs.ics.uci.edu/'))
    print(is_valid("https://gitlab-cs142a-s23.ics.uci.edu/users/sign_in"))
