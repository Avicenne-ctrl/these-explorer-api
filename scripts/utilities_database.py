import pandas as pd
import os
from langchain_community.vectorstores import FAISS
import sys
sys.path.append('../..')
sys.path.append('..')
import scripts.get_vector_store as get_vector_store
import scripts.get_url_theses_selenium as get_url_theses_selenium
import scripts.get_metadata_theses_beautiful_soup as get_metadata_theses_beautiful_soup
from langchain_huggingface import HuggingFaceEmbeddings
import configparser

# Lire le fichier de configuration
config = configparser.ConfigParser()
config.read('./scripts/config.ini')

MODEL_EMBEDDING   = config["DEFAULT"]["MODEL_EMBEDDING"]

EMBEDDING = HuggingFaceEmbeddings(model_name= MODEL_EMBEDDING)
COLUMN_URL_QUERY = "url_query"


def condense_content(text, num_words=10):
    """Condense the content in order to reduce the space in the html page

        Args:
            text (str): 
                the content text
                
            num_words (int, optional): 
                the length we want to split the text. Defaults to 10.

        Returns:
            str: the condensed text
            
        Raise:
        ----
            - text is nit string
            - num_words is not int
    """
    
    if not isinstance(text, str):
        raise TypeError(f"the text given is not in the correct format, recieved : {type(text).__name__}")
    
    if not isinstance(num_words, int):
        raise TypeError(f"the num of words given is not in the correct format, recieved : {type(num_words).__name__}")
    
    words = text.split()
    if len(words) > num_words * 2:
        return ' '.join(words[:num_words]) + ' ... ' + ' '.join(words[-num_words:])
    return text

def condense_content_metadata_df(df_metadata: pd.DataFrame):
    """Condense the content column of the given dataframe and creat a new column "content_condensed"

    Args:
        df_metadata (pd.DataFrame): _description_

    Returns:
        pd.DataFrame: the original dataframe with a content_condensed column added
        
    """
    
    if "content" not in df_metadata.columns:
        raise TypeError(f"content column not found in {df_metadata}, make sure the column's name associated to text description is called 'content'")
    
    if not isinstance(df_metadata, pd.DataFrame):
        raise TypeError(f"a dataframe is expected, recieved : {type(df_metadata).__name__}")
    
    df_metadata["content_condensed"] = [condense_content(content) for content in df_metadata["content"].to_list()]
    return df_metadata


def update_db(df, embeddings: str = EMBEDDING):
    """_summary_

    Args:
        df (_type_): _description_
        embeddings (str, optional): _description_. Defaults to EMBEDDING.
    """
    
    
    # add an index:
    df["Id"] = list(range(df.shape[0]))
    
    df_to_dict = df.to_dict(orient="list")
    
    db = get_vector_store.create_vector_store(df_to_dict, embeddings)
    
    get_vector_store.save_vector_store(db, "./static/vector_store")
    
def load_vector_store(vector_store_path: str, embeddings: str = EMBEDDING):
    """
        Load a vector store given a path and embedding
        FAISS vectore store

        Args:
            vector_store_path (str): 
                path where the vector store is
                
            embeddings (str): 
                name of the embedder, could be None for images vector store for example

        Returns:
            db : the index vector store
    """

    if os.path.exists(vector_store_path):
        return FAISS.load_local(vector_store_path, embeddings, allow_dangerous_deserialization=True)
    
    else:
        print("Error : vector store doesn't exist, make sure it is stored in stage_yann_avicenne\\Vector_stores")
        return None
    
def update_excel_query_search(df_theses: pd.DataFrame, df_metadata: pd.DataFrame, url_query: str):
    
    df_metadata[COLUMN_URL_QUERY] = [url_query]*df_metadata.shape[0]
    df_theses = pd.concat([df_theses, df_metadata])
    
    return df_theses.fillna("Missing value")


def query_already_exist(df, url_query: str):
    
    if COLUMN_URL_QUERY in df.columns:
        if url_query in df[COLUMN_URL_QUERY].tolist():
            return True
    return False


def update_database(df_theses, query: str):
    """Update the database (excle and vector store) if unseen query detescted

        Args:
            df_theses (pd.Dataframe): 
                the dataframe with saved query
                
            query (str): 
                the user query
    """
    
    list_url_theses, main_query_url= get_url_theses_selenium.get_all_url_theses(query) # get all theses url and the url query
    # if new request, we extract only info
    df_metadata = get_metadata_theses_beautiful_soup.get_all_metadata_theses_bs(list_url_theses) # list of dict with info for each url in the list
    df_metadata = condense_content_metadata_df(df_metadata)
    
    # we update the excel dataset
    df_theses = update_excel_query_search(df_theses, df_metadata, main_query_url)
    df_theses.to_excel("./static/excel/df_query.xlsx", index=False)
    
    # we update the vector store
    update_db(df_theses)
    
    return df_theses
