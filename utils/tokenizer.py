from bs4 import BeautifulSoup

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
        return (ord('a') <= ord(character) <= ord('z')) or (ord('0') <= ord(character) <= ord('9'))
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
    stop_words = ['a', 's',
 'about',
 'above',
 'after',
 'again',
 'against',
 'all',
 'am',
 'an',
 'and',
 'any',
 'are',
 "aren't",
 'as',
 'at',
 'be',
 'because',
 'been',
 'before',
 'being',
 'below',
 'between',
 'both',
 'but',
 'by',
 "can't",
 'cannot',
 'could',
 "couldn't",
 'did',
 "didn't",
 'do',
 'does',
 "doesn't",
 'doing',
 "don't",
 'down',
 'during',
 'each',
 'few',
 'for',
 'from',
 'further',
 'had',
 "hadn't",
 'has',
 "hasn't",
 'have',
 "haven't",
 'having',
 'he',
 "he'd",
 "he'll",
 "he's",
 'her',
 'here',
 "here's",
 'hers',
 'herself',
 'him',
 'himself',
 'his',
 'how',
 "how's",
 'i',
 "i'd",
 "i'll",
 "i'm",
 "i've",
 'if',
 'in',
 'into',
 'is',
 "isn't",
 'it',
 "it's",
 'its',
 'itself',
 "let's",
 'me',
 'more',
 'most',
 "mustn't",
 'my',
 'myself',
 'no',
 'nor',
 'not',
 'of',
 'off',
 'on',
 'once',
 'only',
 'or',
 'other',
 'ought',
 'our',
 'ours',
 'ourselves',
 'out',
 'over',
 'own',
 'same',
 "shan't",
 'she',
 "she'd",
 "she'll",
 "she's",
 'should',
 "shouldn't",
 'so',
 'some',
 'such',
 'than',
 'that',
 "that's",
 'the',
 'their',
 'theirs',
 'them',
 'themselves',
 'then',
 'there',
 "there's",
 'these',
 'they',
 "they'd",
 "they'll",
 "they're",
 "they've",
 'this',
 'those',
 'through',
 'to',
 'too',
 'under',
 'until',
 'up',
 'very',
 'was',
 "wasn't",
 'we',
 "we'd",
 "we'll",
 "we're",
 "we've",
 'were',
 "weren't",
 'what',
 "what's",
 'when',
 "when's",
 'where',
 "where's",
 'which',
 'while',
 'who',
 "who's",
 'whom',
 'why',
 "why's",
 'with',
 "won't",
 'would',
 "wouldn't",
 'you',
 "you'd",
 "you'll",
 "you're",
 "you've",
 'your',
 'yours',
 'yourself',
 'yourselves']
    
    try:
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text()
        
        for character in text:
            if _isAlnum(character):
                currentWord += character.lower()
            else:
                if currentWord:
                    tokens.append(currentWord)
                    currentWord = ""
        if currentWord and currentWord not in stop_words:
            tokens.append(currentWord)
            
    except Exception as e:
        print(f"An unexpected error occurred while processing the text: {e}")
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
        print(f'<{token}> -> <{frequencies[token]}>')