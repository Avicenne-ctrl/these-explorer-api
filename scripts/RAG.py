import os
from mistralai import Mistral
from langchain_core.documents import Document
import configparser

# Lire le fichier de configuration
config = configparser.ConfigParser()
config.read('./scripts/config.ini')

API_KEY       = config["MISTRAL"]["API_KEY"]
MISTRAL_MODEL = config["MISTRAL"]["MISTRAL_MODEL"]

client = Mistral(api_key=API_KEY)

def call_mistral_rag(context:str, prompt: str, client:str = client):
    
    message       = [{
                        "role": "system",
                        "content": f"{context}",
                    },
                    {
                        "role": "user",
                        "content": f"{prompt}",
                    },
                        ]
    
    print("LLM is thinking...")
    chat_response = client.chat.complete(
                                        model= MISTRAL_MODEL,
                                        messages = message )
    
    print(chat_response.choices[0].message.content)
    
    return chat_response.choices[0].message.content

def document_into_context(documents: Document):
    
    created_context = ""
    for i, doc in enumerate(documents):
        title   = doc.metadata["title"]
        content = doc.page_content
        url     = doc.metadata["url_these"]
        
        doc_context = (f" - Title : " + title +
                       f" - content : " + content + 
                       f" url a ne pas afficher dans ta réponse" + url +"\n\n")
        
        created_context += doc_context
        
    created_context += "utilise cette syntaxe lorsque tu affiche un titre d'article <a href= url target='_blank'>title</a>, avec une petite explication de pourquoi cette article est le plus similaire"
        
    return created_context
        