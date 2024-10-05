import os
from typing import Union, List, Dict
import pandas as pd
# libraries HuggingFace, LangChain, Faiss
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document


# TOOLS FOR LANGCHAIN//FAISS

######################### useless for now
def get_transformer_path_model(model_name_path: str):
    """
        Function to automatically get the path to the transformer model folder if
        it exists

        Args:
        ----
            model_name (str):
                name of the transformer model

        Returns:
            (str): the path to the transformer model folder on the repo
    """
    if os.path.exists(model_name_path):
        return model_name_path

    else:
        print("{} doesn't exist, make sure you downloaded the model on the correct folder -> {}".format(model_name_path, model_name_path))
        return None
#########################

def create_document_paragraphs(paragraphs: dict):
    """
        In order to create a vector store we need to 
        stores our documents in a Document object understandable for
        vector store. By defaut metadata if filled with Id which are integer

        Args:
        -----
            paragraphs (Dict[str]):
                dict of documents must contains the following key : "content"
                other keys will be put in metadata

        Returns:
        -----
            documents (Document):
                Document object

        Example:
            >>> create_document_paragraphs({"content": ["sentence 1", "sentence 2"], "id_metadata" : ["id1", "id2"]})
            >>> result: [
                            Document(metadata={"id_metadata": id1}, page_content= "sentence 1"),
                            Document(metadata={"id_metadata": id2}, page_content= "sentence 1")
                        ]
    """
    documents = []

    if "content" in paragraphs.keys():
        for i in range(len(paragraphs["content"])):
            metad = {}
            for key in paragraphs.keys():
                if key != "content":
                    metad[key] = paragraphs[key][i]
                
            doc = Document(
                            page_content = paragraphs["content"][i],
                            metadata = metad
                            )


            documents.append(doc)

        return documents
    
    elif "content" not in paragraphs.keys():
        print("ERROR")
        print("--------------------------")
        print("content key not in the dict provided")
        return None
            


def create_vector_store(paragraphs: Union[Dict[str, str], 
                                            pd.DataFrame, 
                                            List[Dict[str, str]], 
                                            List[pd.DataFrame]],
                        embeddings):

    """
        We need to create vector stores and save before using because training takes
        few minutes. LangChain method here

        Args:
        -----
            paragraphs:
                dict should contain "content" key with list of text we want to vectorize
                other keys will be refered as metadata associated to text in content
                
            embeddings (Huggingface):
                the embbeding model we want from huggingface
                
        Returns:
        --------
            db (Faiss):
                the face vector store
                
        Example:
        ---------
            >>> embeddings = HuggingFaceEmbeddings(model_name= "all-MiniLM-L6-v2")
        >>> create_vector_store(paragraphs = {"content": [text1, text2, text3],
                                                  "metadata_1" : [metadata_text_1, metadata_text_2, metadata_text_3]},
                                embeddings = embeddings)
    """

    #create Document object for vector stores
    documents = create_document_paragraphs(paragraphs)

    db = FAISS.from_documents(documents, embeddings)
    
    print(f"Vector Database: {db.index.ntotal} docs")
    
    return db

def save_vector_store(db : str, path_store_db : str):
    """
        save a vector store locally given the object, its name and path to store

        Args:
        ---------
            db (str): 
                the vector store object
                
            path_store_db (str): 
                the path we want to store it
                
        Returns:
        -------
            None
    """
    
    path_vector = path_store_db 

    if not os.path.exists(path_store_db):
        print("Vector_Store folder doesn't exist")
        print("Vector_Store folder created in {}".format(path_store_db))

    elif os.path.exists(path_vector):
        print("be carefull {} already exists and is being replaced".format(path_vector))

    print("{} stored in {}".format(path_store_db, path_vector))
    db.save_local(path_vector)
    

def load_vector_store(vector_store_path: str, embeddings: str):
    """
        Load a vector store given a path and embedding
        FAISS vectore store

        Args:
        -----
            vector_store_path (str): 
                path where the vector store is
                
            embeddings (str): 
                name of the embedder, could be None for images vector store for example

        Returns:
        --------
            db : the index vector store
    """

    if os.path.exists(vector_store_path):
        return FAISS.load_local(vector_store_path, embeddings, allow_dangerous_deserialization=True)
    
    else:
        print("Error : vector store doesn't exist, make sure it is stored in stage_yann_avicenne\\Vector_stores")
        return None


def get_len_key_dict(dico: dict):
    if len(dico.keys())>0:
        list_len = []
        for cle, valeur in dico.items():
            list_len.append(len(valeur))
        return list_len
            

def create_list_metadata(metadata_dict: dict):
    """
        Given a dict of list, we create a list of dicts
        in order to create a metadata dict for each elements

        Params:
        -----------
            metadata_dict (dict): 
                the dict of list with each keys with the same length of values
                
        Returns:
        -----------
            list_dict_metadata (List[dict]):
                the list of dict for each element
                
        Example:
        -----------
            >>> create_list_meatadata(metadata_dict = {"id" : [id0, id1, id2], "label" : ["label0", "label1", "label2"]})
            >>> list_dict_metadata = [{"id": id0, "label": "label0"}, {"id": id1, "label": "label1"}, {"id": id2, "label": "label2"}]
    """
    if len(metadata_dict.keys()) > 0:
        list_dict_metadata = []
        # each key should have the same values len so we take the first
        n = get_len_key_dict(metadata_dict)
        n = n[0]
        
        for i in range(n):
            aux_dict = {}
            for key in metadata_dict.keys():
                aux_dict[key] = metadata_dict[key][i]
            list_dict_metadata.append(aux_dict)
                
        return list_dict_metadata
    


