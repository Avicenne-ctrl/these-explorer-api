import pandas as pd
import numpy as np
from typing import Union, List, Dict, Tuple
from rank_bm25 import BM25Okapi

# libraries HuggingFace, LangChain, Faiss
from langchain_huggingface import HuggingFaceEmbeddings
import sys
sys.path.append('..')
import scripts.get_vector_store as get_vector_store




def get_bm25_similar_paragraphs(query: Union[str, List[str]],
                                paragraphs: List[str],
                                nb_results: int = 5):# -> List[Tuple[str, float]]:
    """
    Get similar paragraphs based on the query using the BM25 model.

    Args:
    ----------
    query: Union[str, List[str]]
        The query string to search for.

    paragraphs: List[str]
        A list of paragraphs to search within.

    nb_results: int
        The number of similar paragraphs to return. Default is 5.

    sanity_check: bool
        Whether to check if the test names are in the dictionary. Default is True.

    Returns:
    -------
    List[Tuple[str, float]]
        A list of tuples with the matched paragraphs and their similarity scores.

    Examples:
    --------
    >>> get_bm25_similar_paragraphs("This is a test sentence", ["This is a test sentence", "This is another test sentence"], nb_results=1)
    [('This is a test sentence', 0, 1.0)]
    """
    query = query.split()

    bm25 = BM25Okapi(paragraphs)
    bm25_scores = bm25.get_scores(query)

    similar_paragraphs = [(paragraphs[idx], idx, score) for \
                           idx, score in enumerate(bm25_scores)]


    return sorted(similar_paragraphs, key=lambda x: x[2], reverse=True)[:nb_results]

def get_hugging_face_similar_paragraphs(query: Union[str, List[str]],
                                        paragraphs: List[str],
                                        filter,
                                        model_path : str,
                                        vector_store_path: str,
                                        nb_results: int = 5
                                        ):# -> List[Tuple[str, float]]:
    """
        Get similar paragraphs based on the query using the HuggingFaceTransformer and
        Faiss as vector stores. Note that we don't need to tokenize sequences

        Parameters:
        ----------
        query: Union[str, List[str]]
            The query string to search for.

        paragraphs: List[str]
            A list of paragraphs to search within.

        name_vector_store: str
            name of the vector store, either requirement (faiss_index_req_desc) or test description (faiss_index_test_desc)

        nb_results: int
            The number of similar paragraphs to return. Default is 5.

        sanity_check: bool
            Whether to check if the test names are in the dictionary. Default is True.

        Returns:
        -------
        List[Tuple[str, float]]
            A list of tuples with the matched paragraphs and their similarity scores.

        Examples:
        --------
        >>> get_hugging_face_similar_paragraphs("This is a test sentence", ["This is a test sentence", "This is another test sentence"], "faiss_index_req_desc",
                                        nb_results=1)
        [('This is a test sentence', 0, 1.0)]

    """
    
    #load local vector stores
    embeddings = HuggingFaceEmbeddings(model_name= model_path)
    db = get_vector_store.load_vector_store(vector_store_path, embeddings)

    result_docs = db.similarity_search(query, len(paragraphs), filter=filter)

    return result_docs[:nb_results]


def get_similar_paragraphs(query: str,                     
                             paragraphs: Union[Dict[str, str], 
                                                    pd.DataFrame, 
                                                    List[Dict[str, str]], 
                                                    List[pd.DataFrame]],
                             filter,
                             model: str,
                             vector_store_path: str,
                             nb_similar_req: Union[str, int] = 1): #-> Dict[str, str]:

    nb_similar_paragraph = len(paragraphs) if (isinstance(nb_similar_req, str) and nb_similar_req.upper() in ['ALL', 'MAX']) else nb_similar_req

    if model == 'BM25':
        matching_descriptions = get_bm25_similar_paragraphs(query, paragraphs, 
                                                            nb_similar_paragraph)
        
    elif model == 'all-MiniLM-L6-v2':
        matching_descriptions = get_hugging_face_similar_paragraphs(query, paragraphs, filter, "all-MiniLM-L6-v2", vector_store_path, 
                                                                    nb_similar_paragraph)

    else:
        print("------------------\nERROR \n--------------------\nplease enter a valid model name")
        print("BM25 or AllMini")
        return None

    return matching_descriptions

