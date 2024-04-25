import re
from crawler.robots import Robots
from urllib.parse import urlparse
from urllib.parse import urljoin
from bs4 import BeautifulSoup

def scraper(url, resp, robot: Robots):
    # print("++++++++ (Scraper.py) url: HERE", url)
    # print("++++++++(Scraper.py) resp: HERE", resp)

    links = extract_next_links(url, resp, robot)
    res = [link for link in links if is_valid(link, robot)] + robot.sitemaps(resp.url)
    return res

def extract_next_links(url, resp, robot: Robots):
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
        if "Location" in resp.headers:
            return [urljoin(resp.url, resp.headers['Location'])]
    
    # checking for any sitemap links
    if resp.url.lower().endswith('.xml'):
        return robot.parse_sitemap(resp.raw_response.content)

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
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise

if __name__ == "__main__":
    print(is_valid("https://wfuckww.ics.uci.edu/about/search/index.php"))
    