from urllib.parse import urlparse
import os


def check_correct_format(item, item_type):
    if not isinstance(item, item_type):
        # Affiche l'erreur en rouge
        raise Exception(f"\033[91mExpected {item_type} got {type(item)}\033[0m")
    
def check_correct_url(url_web_site: str, verbose: bool= False):
    # Parsing URL
    parsed_url = urlparse(url_web_site)
    
    if verbose:
        print(f"Result parsing : {parsed_url}")

    # scheme and netloc verification
    if not parsed_url.scheme or not parsed_url.netloc:
        raise ValueError(f"L'URL '{url_web_site}' is not correct.")
    
