import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import scripts.check_utilities as check_utilities
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium.webdriver.chrome.options import Options
import configparser
import tqdm

# Lire le fichier de configuration
config = configparser.ConfigParser()
config.read('./scripts/config.ini')

DRIVER_PATH_GOOGLE = config["DRIVER"]["DRIVER_PATH_GOOGLE"]



BALISE_PARENT_THESE_TITLE     = 'div[data-v-d290f8ce]'
BALISE_TITLE                  = "h1[data-v-d290f8ce]"
BALISE_PARENT_THESE_RESUME    = 'div[data-v-35e8592d]'
BALISE_RESUME                 = "p[data-v-35e8592d]"
BALISE_PARENT_METADATA        = "div[data-v-c8bc896e]"
BALISE_METADATA               = "tr[data-v-276fb210]"

driver_path = Service(DRIVER_PATH_GOOGLE)

options = Options()
options.add_argument("--disable-extensions")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--headless")
#service = Service(driver_path, log_path="chromedriver.log")



def get_list_balise_metadata(driver: Service, parent_balise: str, child_balise: str):
    """
        get the parent div which contain sub div with relevant info

        Args:
        -------
            driver (str): 
                the google driver to the web site
                
            parent_balise (str):
                name of the parent div balise : div[name_div_class]
                
            child_balise (str):
                name of the balise we want to extract info : type_object[name_balise]

        Returns:
        --------
            selenium object: 
                list of info for all the child_balise in parent_balise
                
    """
    try:
        parent_elem = driver.find_element(By.CSS_SELECTOR, parent_balise)
        child_elem = parent_elem.find_elements(By.CSS_SELECTOR, child_balise)
        return child_elem
    except:
        print(f"{parent_balise} not found")
        return None

def get_balise_metadata(driver: Service, parent_balise: str, child_balise: str):
    """
        get the parent div which contain sub div with relevant info

        Args:
        -------
            driver (str): 
                the google driver to the web site
                
            parent_balise (str):
                name of the parent div balise : div[name_div_class]
                
            child_balise (str):
                name of the balise we want to extract info : type_object[name_balise]

        Returns:
        --------
            selenium object: 
                info for the one child_balise in parent_balise
                
    """
    try:
        parent_elem = driver.find_element(By.CSS_SELECTOR, parent_balise)
        child_elem = parent_elem.find_element(By.CSS_SELECTOR, child_balise)
        return child_elem
    except:
        print(f"{parent_balise} not found")
        return None
        
    
    
def get_metadata_dict(driver_these: str):
    """_summary_

    Args:
        driver_these (str): _description_

    Returns:
        _type_: _description_
    """
    dict_metadata = {}
    
    elements = get_list_balise_metadata(driver_these, BALISE_PARENT_METADATA, BALISE_METADATA)
    
    if elements:
        for element in elements:
            try:
                element_splited      = element.text.split(":")
                tag                  = element_splited[0]
                name                 = element_splited[1]
                dict_metadata[tag]   = name
            except:
                print("no metadata")
            
        return dict_metadata
    else:
        return {}


def get_metadata_theses(url_these: str, driver_these: Service):
    """
        get the title of a these given its url

        Args:
        -------
            url_these (str):
                the url thses
                
            driver_theses (Service): 
                the driver to connect to the url 

        Returns:
        --------
            str: 
                title of the these
    """
    
    check_utilities.check_correct_url(url_these)
    # init driver with new url
    driver_these.get(url_these)
    
    dict_metadata = get_metadata_dict(driver_these) 
    
    # get title
    content       = get_balise_metadata(driver_these, BALISE_PARENT_THESE_RESUME, BALISE_RESUME)
    title         = get_balise_metadata(driver_these, BALISE_PARENT_THESE_TITLE, BALISE_TITLE)
    
    if content:
        dict_metadata["content"]  = content.text 
    else:
        dict_metadata["content"]  =  "Missing Value"
        
    if title:
        dict_metadata["title"]    = title.text
    else:
        dict_metadata["title"]    = "Missing Value"
        
    return pd.DataFrame([dict_metadata])
    
    
def get_all_metadata_thesis(list_url_these: list):
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
    
    driver_path = Service(DRIVER_PATH_GOOGLE)
    driver_these = webdriver.Chrome(service=driver_path, options=options)

    metadata = pd.DataFrame()
    for url in tqdm.tqdm(list_url_these):  
        metadata_aux = get_metadata_theses(url, driver_these)
                
        if metadata_aux is not None:
            metadata = pd.concat([metadata, metadata_aux])
    driver_these.quit()
        
    return metadata.reset_index(drop=True)
    

    
'''def get_all_metadata_theses(list_url_these: str):
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
    metadata = pd.DataFrame()
    for url in tqdm.tqdm(list_url_these):  
        title, resume = get_metadata_theses(url)
        list_url.append(url)
        list_title.append(title)
        list_resume.append(resume)
    return list_url, list_title, list_resume
    '''
