import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import scripts.check_utilities as check_utilities
import configparser
import lxml
import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
# Lire le fichier de configuration
config = configparser.ConfigParser()
config.read('./scripts/config.ini')

BALISE_TITLE_THESE_BS         = config["BEAUTIFUL_SOUP"]["BALISE_TITLE_THESE_BS"]
TYPE_BALISE_TITLE_THESE_BS    = config["BEAUTIFUL_SOUP"]["TYPE_BALISE_TITLE_THESE_BS"]
BALISE_RESUME_THESE_BS        = config["BEAUTIFUL_SOUP"]["BALISE_RESUME_THESE_BS"]
TYPE_BALISE_RESUME_THESE_BS   = config["BEAUTIFUL_SOUP"]["TYPE_BALISE_RESUME_THESE_BS"]
BALISE_METADATA_THESE_BS      = config["BEAUTIFUL_SOUP"]["BALISE_METADATA_THESE_BS"]
TYPE_BALISE_METADATA_THESE_BS = config["BEAUTIFUL_SOUP"]["TYPE_BALISE_METADATA_THESE_BS"]

def get_metadata_theses_bs(url_these: str):
    """
        get the title of a these given its url

        Args:
        -------
            url_these (str):
                the url thses
                
            driver_path (str): 
                path to the google driver 
                
            options (str):
                options for the google driver

        Returns:
        --------
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
        title_element = soup.find(TYPE_BALISE_TITLE_THESE_BS, {BALISE_TITLE_THESE_BS: True})
        title = title_element.text if title_element else "Missing value"
        
        # Find the resume element, check if it's found, and extract text if present
        resume_element = soup.find(TYPE_BALISE_RESUME_THESE_BS, {BALISE_RESUME_THESE_BS: True})
        resume = resume_element.text if resume_element else "Missing value"
        
        # other metadata
        dict_infos = {}
        for i in soup.find_all(TYPE_BALISE_METADATA_THESE_BS, {BALISE_METADATA_THESE_BS: True}):
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
        -------
            list_url_these (List(str)):
                the url thses list

        Returns:
        --------
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
        -------
            list_url_these (List(str)):
                the url thses list

        Returns:
        --------
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
    


### get metadata by using selenium :
### issue : to long and crashes almost all the time
'''
BALISE_PARENT_THESE_TITLE     = 'div[data-v-d290f8ce]'
BALISE_TITLE                  = "h1[data-v-d290f8ce]"
BALISE_PARENT_THESE_RESUME    = 'div[data-v-35e8592d]'
BALISE_RESUME                 = "p[data-v-35e8592d]"



def get_balise_resume(driver: str):
    """
        get the parent div which contain sub div with relevant info

        Args:
        -------
            driver (str): 
                the google driver to the web site

        Returns:
        --------
            selenium object: 
                info of the parent balise with child balise
    """
    return WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, BALISE_PARENT_THESE_RESUME))).find_element(By.CSS_SELECTOR, BALISE_RESUME)
    


def get_balise_title(driver: str):
    """
        get the parent div which contain sub div with relevant info

        Args:
        -------
            driver (str): 
                the google driver to the web site

        Returns:
        --------
            selenium object: 
                info of the parent balise with child balise
    """
    return WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, BALISE_PARENT_THESE_TITLE))).find_element(By.CSS_SELECTOR, BALISE_TITLE)
    


def get_metadata_theses(url_these: str):
    """
        get the title of a these given its url

        Args:
        -------
            url_these (str):
                the url thses
                
            driver_path (str): 
                path to the google driver 
                
            options (str):
                options for the google driver

        Returns:
        --------
            str: 
                title of the these
    """
    # init driver with new url
    driver_theses = get_url_theses_selenium.init_chrome_driver(url_these)
    # get title
    title         = get_balise_title(driver_theses).text
    # get resume
    resume        = get_balise_resume(driver_theses).text
    
    # quit driver
    driver_theses.quit()
    return title, resume
    
def get_all_metadata_theses(list_url_these: str):
    """
        get the title of theses given a list of url

        Args:
        -------
            list_url_these (List(str)):
                the url thses list
                
            driver_path (str): 
                path to the google driver 
                
            options (str):
                options for the google driver

        Returns:
        --------
            str: 
                title of the these
                
        Example:
        --------
            >>> get_title_theses([url_1, url_2, url_3])
            >>> [title_1, title_2, title_3]
            >>> if not found for url_3 :
            >>> [title_1, title_2, None]
    """
    list_url     = []
    list_title   = []
    list_resume  = []
    for url in tqdm(list_url_these):  
        title, resume = get_metadata_theses(url)
        list_url.append(url)
        list_title.append(title)
        list_resume.append(resume)
    return list_url, list_title, list_resume
    
def get_info_theses(url_query: str):
    

    try:
        # get url article corresponding query
        theses_url = get_url_theses_selenium.get_all_url_theses(url_query)
        print("found url")
        
        # for each url get the title and the resume of the article
        list_url, list_title, list_resume = get_all_metadata_theses(theses_url)
        
        return list_url, list_title, list_resume, url_query
        
    except Exception as e:
        print("Erreur :", e)'''


