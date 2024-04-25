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
        if currentWord:
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