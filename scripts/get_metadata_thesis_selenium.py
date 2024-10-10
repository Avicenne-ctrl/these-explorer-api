import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import scripts.check_utilities as check_utilities
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium.webdriver.chrome.options import Options
import configparser
import tqdm

# Read config.ini
config = configparser.ConfigParser()
config.read('./scripts/config.ini')

# import config var
DRIVER_PATH_GOOGLE = config["DRIVER"]["DRIVER_PATH_GOOGLE"]

# TAG name for metadata extraction
TAG_PARENT_THESE_TITLE     = 'div[data-v-d290f8ce]'
TAG_TITLE                  = "h1[data-v-d290f8ce]"
TAG_PARENT_THESE_RESUME    = 'div[data-v-35e8592d]'
TAG_RESUME                 = "p[data-v-35e8592d]"
TAG_PARENT_METADATA        = "div[data-v-c8bc896e]"
TAG_METADATA               = "tr[data-v-276fb210]"

# init chrome driver
driver_path = Service(DRIVER_PATH_GOOGLE)

options = Options()
options.add_argument("--disable-extensions")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--headless")

# python functiond

def get_list_tag_metadata(driver: Service, parent_tag: str, child_tag: str):
    """
        get the parent div which contain sub div with relevant info

        Args:
            driver (str): 
                the google driver to the web site
                
            parent_tag (str):
                name of the parent div tag : div[name_div_class]
                
            child_tag (str):
                name of the tag we want to extract info : type_object[name_tag]

        Returns:
            selenium object: 
                list of info for all the child_tag in parent_tag
                
        Raise:
        -------
            - check if something has been extract
            - error du to bad internet connection
 
    """
    try:
        parent_elem = driver.find_element(By.CSS_SELECTOR, parent_tag)
        child_elem = parent_elem.find_elements(By.CSS_SELECTOR, child_tag)
        return child_elem
    except:
        print(f"{parent_tag} not found")
        return None

def get_tag_metadata(driver: Service, parent_tag: str, child_tag: str):
    """
        get the parent div which contain sub div with relevant info

        Args:
            driver (str): 
                the google driver to the web site
                
            parent_tag (str):
                name of the parent div tag : div[name_div_class]
                
            child_tag (str):
                name of the tag we want to extract info : type_object[name_tag]

        Returns:
            selenium object (selenium): 
                info for the one child_tag in parent_tag
                
        Raise:
        -----
            - check if something has been extract
            - error du to bad internet connection     
               
        Example:
            >>> get_tag_metadata(driver_goole, 
                                    parent_tag = "div[data-v-c8bc896e]", 
                                    child_tag = "tr[data-v-276fb210]")
                                    
    """
    try:
        parent_elem = driver.find_element(By.CSS_SELECTOR, parent_tag)
        child_elem = parent_elem.find_element(By.CSS_SELECTOR, child_tag)
        return child_elem
    except:
        print(f"{parent_tag} not found")
        return None
        
    
    
def get_metadata_dict(driver_these: str):
    """Gather thesis metadata by reading metadata_tag

    Args:
        driver_these (str): _description_

    Returns:
        _type_: _description_
    """
    dict_metadata = {}
    
    elements = get_list_tag_metadata(driver_these, TAG_PARENT_METADATA, TAG_METADATA)
    
    if elements:
        for element in elements:
            try:
                element_splited      = element.text.split(":")
                tag                  = element_splited[0].strip()
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
    content       = get_tag_metadata(driver_these, TAG_PARENT_THESE_RESUME, TAG_RESUME)
    title         = get_tag_metadata(driver_these, TAG_PARENT_THESE_TITLE, TAG_TITLE)
    
    try: # avoid crash if bad connection
        dict_metadata["content"]  = content.text 
    except:
        dict_metadata["content"]  =  "Missing Value"
        
    try: # avoid crash if bad connection
        dict_metadata["title"]    = title.text
    except:
        dict_metadata["title"]    = "Missing Value"
        
    dict_metadata["url_these"]    = url_these
    
        
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
