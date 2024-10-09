from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import os
import scripts.check_utilities as check_utilities
import configparser
import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

# Lire le fichier de configuration
config = configparser.ConfigParser()
config.read('./scripts/config.ini')


# Set the path to the Chromedriver
DRIVER_PATH_GOOGLE = config["DRIVER"]["DRIVER_PATH_GOOGLE"]
PATH_THESES_HEAD   = config["DRIVER"]["PATH_THESES_HEAD"]
PATH_THESES_TAIL   = config["DRIVER"]["PATH_THESES_TAIL"]
BALISE_PARENT      = config["DRIVER"]["BALISE_PARENT"]
BALISE_HREF        = config["DRIVER"]["BALISE_HREF"]

    
if not os.path.exists(DRIVER_PATH_GOOGLE):
    raise TypeError(f"Provided driver_path_goole in ./scripts/config.ini doesn't exist, please download google driver or provide the path")
if not isinstance(DRIVER_PATH_GOOGLE, str):
    raise TypeError(f"Provided driver_path_goole in ./scripts/config.ini is not in the correct format, expected str got : {type(DRIVER_PATH_GOOGLE).__name__}")


driver_path = Service(DRIVER_PATH_GOOGLE)

options = Options()
options.add_argument("--disable-extensions")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--headless")
#service = Service(driver_path, log_path="chromedriver.log")

def init_chrome_driver(url_web_site: str, driver_path: Service = driver_path, options: Options = options):
    """
        Initialize the google driver and check if the url is correct (https...)

        Args:
            url_web_site (str): 
                the url to the website
                
            driver_path (Service, optional): 
                the path to the driver saved locally. Defaults to driver_path.
                
            options (Options, optional): 
                the options we want for the driver, ex : don't show the pop up.... Defaults to options.
                

        Returns:
            webdriver.Chrome: 
                the driver initialized
                
        Raises:
        ------
            ValueError: 
                if the url is not correct
                
        Example:
        ------------
            >>> driver_path = Service(DRIVER_PATH)
            >>> options = ....
            >>> init_chrome_driver("https://www.example.com")
    """

    # check if correct url
    check_utilities.check_correct_url(url_web_site) # url check
    
    # Initialisation du driver
    driver = webdriver.Chrome(service=driver_path, options=options)
    driver.get(url_web_site)
    return driver


def get_url_request(query: str):
    """
        Given a query, build the correct url to access the theses web site

        Args:
        ------
            query (str): 
                the user query

        Returns:
        --------
            str: 
                the correct url
    """
    
    if not isinstance(query, str):
        raise TypeError(f" The query must be a list of words, recieved : {type(query).__name__}")
    
    if len(query) == 0:
        raise TypeError(f"The query recieved is empty, no theses will be found")
    
    query = query.split()
    model_query = ""
    for i in range(len(query)-1):
        model_query += query[i] + "+"
    model_query += query[-1]
    return PATH_THESES_HEAD + model_query + PATH_THESES_TAIL

def get_parent_div(driver: webdriver.Chrome):
    """
        get the parent div which contain sub div with relevant info

        Args:
            driver (str): 
                the google driver to the web site

        Returns:
            selenium.webdriver.remote.webelement.WebElement: 
                info of the parent balise with child balise
    """
    return WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, BALISE_PARENT)))
    
def get_link_theses(div: webdriver.remote.webelement.WebElement):
    """ 
        In the sub divs get the link to the theses

        Args:
            div (selenium.webdriver.remote.webelement.WebElement): 
                parent div which contain child div of url these

        Returns:
            List[str]: 
                list of the href (link to the these)
    """
    
    url_theses = []
    links = div.find_elements(By.CSS_SELECTOR, BALISE_HREF)
        
    # Itérer sur les liens et récupérer l'attribut href
    for link in links:
        href_value = link.get_attribute('href')
        url_theses.append(href_value)
        
    return url_theses

def get_all_url_theses(query: str):
    """
        Combined function to automatically get the these url from the theses.fr website

        Args:
            url_query (str): 
                the user request

        Returns:
            List[str]: 
                list of the theses url
                
            url_query (str):
                the url path the the theses.fr website
                
        Raise:
        -----
            - if the query is not a string
            - if the query is empty or only space
            
    """
    
    if not isinstance(query, str):
        raise TypeError(f"Query given is not a string, recieved : {type(query).__name__}")
    
    if len(query.split()) == 0:
        raise TypeError(f"The query is empty")
    
    url_query = get_url_request(query) # convert query into url theses query
    
    driver = init_chrome_driver(url_query)
    
    parent_div    = get_parent_div(driver)
    child_divs = parent_div.find_elements(By.TAG_NAME, 'div')
    url_theses  = []
    
    for div in tqdm.tqdm(child_divs):
        url_aux = get_link_theses(div)
        if len(url_aux)>0:
            url_theses += url_aux
            
    driver.quit()
            
    return list(set(url_theses)), url_query

def get_all_url_theses_parallelize(query: str):
    """
        Combined function to automatically get the these url from the theses.fr website

        Args:
            url_query (str): 
                the user request

        Returns:
            List[str]: 
                list of the theses url
                
            url_query (str):
                the url path the the theses.fr website
                
        Raise:
        -----
            - if the query is not a string
            - if the query is empty or only space
            
    """
    
    if not isinstance(query, str):
        raise TypeError(f"Query given is not a string, recieved : {type(query).__name__}")
    
    if len(query.split()) == 0:
        raise TypeError(f"The query is empty")
    
    url_query = get_url_request(query) # convert query into url theses query
    
    driver = init_chrome_driver(url_query)
    
    parent_div    = get_parent_div(driver)
    child_divs = parent_div.find_elements(By.TAG_NAME, 'div')
    url_theses  = []
    
    # parallelize url extraction
    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = [executor.submit(get_link_theses, div) for div in tqdm.tqdm(child_divs)]
        print("futures")
        results = []
        for future in tqdm.tqdm(as_completed(futures)):
            if len(future.result())>0:
                results.append(future.result()[0])
            
        driver.quit()
            
    return list(set(results)), url_query





