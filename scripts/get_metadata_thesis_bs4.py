import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import scripts.check_utilities as check_utilities
import configparser
import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
# Lire le fichier de configuration
config = configparser.ConfigParser()
config.read('./scripts/config.ini')

TAG_TITLE_THESE_BS         = config["BEAUTIFUL_SOUP"]["TAG_TITLE_THESE_BS"]
TYPE_TAG_TITLE_THESE_BS    = config["BEAUTIFUL_SOUP"]["TYPE_TAG_TITLE_THESE_BS"]
TAG_RESUME_THESE_BS        = config["BEAUTIFUL_SOUP"]["TAG_RESUME_THESE_BS"]
TYPE_TAG_RESUME_THESE_BS   = config["BEAUTIFUL_SOUP"]["TYPE_TAG_RESUME_THESE_BS"]
TAG_METADATA_THESE_BS      = config["BEAUTIFUL_SOUP"]["TAG_METADATA_THESE_BS"]
TYPE_TAG_METADATA_THESE_BS = config["BEAUTIFUL_SOUP"]["TYPE_TAG_METADATA_THESE_BS"]

def get_metadata_theses_bs(url_these: str):
    """
        get the title of a these given its url

        Args:
            url_these (str):
                the url thses
                
            driver_path (str): 
                path to the google driver 
                
            options (str):
                options for the google driver

        Returns:
            pd.Dataframe: 
                ddataframe of metadata and associated value
                
        Raise:
        -------
            - check_utilities.check_correct_url(url_these) : if the url is in the correct format
    """
    check_utilities.check_correct_url(url_these) # url check
    
    response = requests.get(url_these)
    #soup     = BeautifulSoup(response.text, 'html.parser')
    soup     = BeautifulSoup(response.text, 'lxml')

    if soup:  # Check if the soup object is not None
        # Find the title element, check if it's found, and extract text if present
        title_element = soup.find(TYPE_TAG_TITLE_THESE_BS, {TAG_TITLE_THESE_BS: True})
        title = title_element.text if title_element else "Missing value"
        
        # Find the resume element, check if it's found, and extract text if present
        resume_element = soup.find(TYPE_TAG_RESUME_THESE_BS, {TAG_RESUME_THESE_BS: True})
        resume = resume_element.text if resume_element else "Missing value"
        
        # other metadata
        dict_infos = {}
        for i in soup.find_all(TYPE_TAG_METADATA_THESE_BS, {TAG_METADATA_THESE_BS: True}):
            infos = i.text.split(":") if i else "Missing value"
            dict_infos[infos[0].replace("\xa0", "")] = infos[-1].replace("\xa0", "")
        
        dict_infos["title"] = title
        dict_infos["content"] = resume
        dict_infos["url_these"] = url_these
        
        return pd.DataFrame([dict_infos])
    
    return None
    
def get_all_metadata_theses_bs(list_url_these: list):
    """
        get metadata of theses given a list of url

        Args:
            list_url_these (List(str)):
                the url thses list

        Returns:
            pd.DataFrame: 
                dataframe of metadata which each line correspond to a these
                
        Example:
        --------
            >>> get_title_theses([url_1, url_2, url_3])
        >>> pd.DataFrame()
            
        Raise:
        ------
            - if the input is not a list
            
    """
    
    if not isinstance(list_url_these, list):
        raise TypeError(f"The inut must be a list of url link, recieved : {type(list_url_these).__name__}")
    
    metadata = pd.DataFrame()
    for url in tqdm.tqdm(list_url_these):  
        metadata_aux = get_metadata_theses_bs(url)
                
        if metadata_aux is not None:
            metadata = pd.concat([metadata, metadata_aux])
        
    return metadata.reset_index(drop=True)

def get_all_metadata_theses_bs_parallelized(list_url_these: list):
    """
        get metadata of theses given a list of url

        Args:
            list_url_these (List(str)):
                the url thses list

        Returns:
            pd.DataFrame: 
                dataframe of metadata which each line correspond to a these
                
        Example:
        --------
            >>> get_title_theses([url_1, url_2, url_3])
            >>> pd.DataFrame()
            
        Raise:
        ------
            - if the input is not a list
            
    """
    
    if not isinstance(list_url_these, list):
        raise TypeError(f"The inut must be a list of url link, recieved : {type(list_url_these).__name__}")
    
    metadata = pd.DataFrame()
    
    
    # parallelize metadata extraction
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(get_metadata_theses_bs, url) for url in tqdm.tqdm(list_url_these)]
        print("futures")
        for future in tqdm.tqdm(as_completed(futures)):
            if future.result() is not None:
                metadata = pd.concat([metadata, future.result()])
        
    return metadata.reset_index(drop=True)
    


