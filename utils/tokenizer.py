from bs4 import BeautifulSoup
import re


def _isAlnum(character: str) -> bool:
    """
    Check if a character is alphanumeric.

    Parameters:
    - character: str: Character to be checked.

    Returns:
    - bool: True if the character is alphanumeric, otherwise False.
    """
    try:
        character = character.lower()
        return (ord("a") <= ord(character) <= ord("z")) or (ord("0") <= ord(character) <= ord("9"))
    except:
        return False


def tokenize_url_content(response) -> list[str]:
    """
    Parse the HTML content of a response object and tokenize it.

    Parameters:
    - response: Response: Response object from HTTP request.

    Returns:
    - list[str]: List of tokens (alphanumeric sequences) from the content.
    """
    tokens = []
    currentWord = ""

    try:
        soup = BeautifulSoup(response.raw_response.text, "html.parser")
        text = soup.get_text()

        for character in text:
            if _isAlnum(character):
                currentWord += character.lower()
            else:
                if currentWord:
                    tokens.append(currentWord)
                    currentWord = ""
        if currentWord:
            tokens.append(currentWord)

    except Exception as e:
        print(f"An unexpected error occurred while processing the text: {e}")
        return []

    return tokens


def tokenize_from_file(textFilePath: str) -> list[str]:
    """
    Runtime Complexity: O(n) where n is the number of bytes in the text file.

    Reads in a text file and returns a list of tokens in that file.
    A token is a sequence of alphanumeric characters, independent of capitalization.

    :param textFilePath: Path to the text file to be read.
    :return: List of tokens in that file.
    """

    tokens = []
    currentWord = ""
    try:
        with open(textFilePath, "r", encoding="utf-8") as file:
            character = file.read(1)
            while character:
                if _isAlnum(character):
                    currentWord += character.lower()
                else:
                    if currentWord:
                        tokens.append(currentWord)
                    currentWord = ""
                character = file.read(1)
        if currentWord:
            tokens.append(currentWord)
    except FileNotFoundError:
        return []
    except NotADirectoryError:
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []
    return tokens


def computeWordFrequencies(tokenList: list[str]) -> dict[str, int]:
    """
    Compute the frequency of each token.

    Parameters:
    - tokenList: list[str]: List of tokens.

    Returns:
    - dict[str, int]: Dictionary mapping each token to its frequency count.
    """
    frequencies = {}
    for token in tokenList:
        if token in frequencies:
            frequencies[token] += 1
        else:
            frequencies[token] = 1
    return frequencies


def printWordFrequencies(frequencies: dict[str, int]) -> None:
    """
    Print word frequencies sorted by descending order of frequency.

    Parameters:
    - frequencies: dict[str, int]: Mapping of tokens to their frequencies.

    Returns:
    - None
    """
    mostFrequent = sorted(frequencies, key=lambda x: frequencies[x], reverse=True)
    for token in mostFrequent:
        print(f"<{token}> -> <{frequencies[token]}>")


def get_word_count_from_response(resp):
    """This function grabs the number of tokens found in the response parameter."""
    if resp.status == 200:
        soup = BeautifulSoup(resp.raw_response.content, "html.parser")
        text = soup.get_text()
        pattern = re.compile(r"[\w']+")
        tokens = pattern.findall(text)
        return len(tokens)
    else:
        return None


stop_words = {
    "a",
    "about",
    "above",
    "after",
    "again",
    "against",
    "all",
    "am",
    "an",
    "and",
    "any",
    "are",
    "aren't",
    "as",
    "at",
    "be",
    "because",
    "been",
    "before",
    "being",
    "below",
    "between",
    "both",
    "but",
    "by",
    "can't",
    "cannot",
    "could",
    "couldn't",
    "did",
    "didn't",
    "do",
    "does",
    "doesn't",
    "doing",
    "don't",
    "down",
    "during",
    "each",
    "few",
    "for",
    "from",
    "further",
    "had",
    "hadn't",
    "has",
    "hasn't",
    "have",
    "haven't",
    "having",
    "he",
    "he'd",
    "he'll",
    "he's",
    "her",
    "here's",
    "hers",
    "herself",
    "him",
    "himself",
    "his",
    "how",
    "how's",
    "i",
    "i'd",
    "i'll",
    "i'm",
    "i've",
    "if",
    "in",
    "into",
    "is",
    "isn't",
    "it",
    "it's",
    "its",
    "itself",
    "let's",
    "me",
    "more",
    "most",
    "mustn't",
    "my",
    "myself",
    "no",
    "nor",
    "not",
    "of",
    "off",
    "on",
    "once",
    "only",
    "or",
    "other",
    "ought",
    "our",
    "ours",
    "ourselves",
    "out",
    "over",
    "own",
    "same",
    "shan't",
    "she",
    "she'd",
    "she'll",
    "she's",
    "should",
    "shouldn't",
    "so",
    "some",
    "such",
    "than",
    "that",
    "that's",
    "the",
    "their",
    "theirs",
    "them",
    "themselves",
    "then",
    "there",
    "there's",
    "these",
    "they",
    "they'd",
    "they'll",
    "they're",
    "they've",
    "this",
    "those",
    "through",
    "to",
    "too",
    "under",
    "until",
    "up",
    "very",
    "was",
    "wasn't",
    "we",
    "we'd",
    "we'll",
    "we're",
    "we've",
    "were",
    "weren't",
    "what",
    "what's",
    "when",
    "when's",
    "where",
    "where's",
    "which",
    "while",
    "who",
    "who's",
    "whom",
    "why",
    "why's",
    "with",
    "won't",
    "would",
    "wouldn't",
    "you",
    "you'd",
    "you'll",
    "you're",
    "you've",
    "your",
    "yours",
    "yourself",
    "yourselves",
}
