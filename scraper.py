import re
from crawler.robots import Robots
from urllib.parse import urlparse
from urllib.parse import urljoin
from bs4 import BeautifulSoup


def scraper(url, resp, robot: Robots):
    # Checks if a url is xml. If it is an xml it assumes it is a sitemap and scrapes it for all the links.
    sitemaps = robot.parse_sitemap(resp)

    # If it finds any urls after parsing the url, it will return only the valid links
    if sitemaps:
        # Iterate through the list of links in site map and only return links thatt are valid and met the requirements
        return [link for link in sitemaps if is_valid(link, robot)]

    links = extract_next_links(url, resp)

    # Res is created by iterating through links and determining if it's valid through is_valid
    # and appends the links found in robots.txt
    res = [link for link in links if is_valid(link, robot)] + robot.sitemaps(resp.url)

    return res


def extract_next_links(url, resp):

    # Detect and avoid dead URLs that return a 200 status but no data (click here to see what the different HTTP status codes meanLinks to an external site.)
    hyperlink_list = []

    # If the response returns status 200, but there is no raw response or content it will just return a blank list.
    if resp.status == 200 and (resp.raw_response is None or not resp.raw_response.content):
        return hyperlink_list

    # If the response returns status 204 (No Content) or status greater than 400 (for invalid url)
    if resp.status == 204 or resp.status >= 400:
        return hyperlink_list

    # If the response is a 300, meaning it is a redirect, it will find the new
    if resp.status >= 300:
        # Redirect Page will have a "Location" headers where the redirect URL located
        if "Location" in resp.raw_response.headers:
            # Return that redirect link by joining the the subdomain in Location with the parent URL
            return [urljoin(resp.url, resp.headers["Location"])]

    soup = BeautifulSoup(resp.raw_response.content, "html.parser", from_encoding="utf-8")

    # finds all the anchor tags and href links and turns them all into absolute urls
    all_links = soup.find_all("a")
    for link in all_links:
        href = link.get("href")
        if href:
            if is_relative(href):
                href = urljoin(url, href)
            hyperlink_list.append(href)
    return hyperlink_list


def is_relative(url):
    """
    returns whether or not the url is a relative url
    """
    return not urlparse(url).netloc


def is_valid(url, robot: Robots):
    # Decide whether to crawl this url or not.
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        # Obtain a parsed version of the url to easily access it's individual components
        parsed = urlparse(url)

        # Check if the scheme isn't http or https. If it isn't, the url isn't valid
        if parsed.scheme not in set(["http", "https"]):
            return False

        # Check the netloc of the parsed url to obtain the authority. Split by . to easily
        # access the individual components
        domain = parsed.netloc
        dotlist = domain.split(".")

        # Check if the last 3 domain labels are within the set. If they aren't within the set,
        # the url isn't valid.
        if not ".".join(dotlist[-3:]) in set(
            [
                ".ics.uci.edu",
                ".cs.uci.edu",
                ".informatics.uci.edu",
                ".stat.uci.edu",
                "ics.uci.edu",
                "cs.uci.edu",
                "informatics.uci.edu",
                "stat.uci.edu",
            ]
        ):
            return False

        # Our reddit upvote system for the code
        """
        upvote:  1, 1
        downvote: 10
       
        """

        # Check that the user object can fetch the url. If not, the url isn't valid.
        if not robot.can_fetch(url):
            return False

        # Checks to ensure that the file extension isn't disallowed. If it is, the url isn't valid.
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf|war"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso|ppsx"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$",
            parsed.path.lower(),
        )

    except TypeError:
        print("TypeError for ", parsed)
        raise


if __name__ == "__main__":
    # print(compute_checksum('https://ics.uci.edu/2016/04/27/press-release-uc-irvine-launches-executive-masters-program-in-human-computer-interaction-design/'))
    # print(compute_checksum('https://ics.uci.edu/2016/04/27/press-release-uc-irvine-launches-executive-masters-program-in-human-computer-interaction-design/'))
    # print(compute_checksum('https://cs.ics.uci.edu/'))
    print(is_valid("https://wics.ics.uci.edu/wp-content/uploads/2021/04/Screenshot-586.png"))
