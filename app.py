from flask import Flask, render_template, request, send_file, redirect, url_for
import pandas as pd
import sys
sys.path.append('..')
import scripts.utilities_database as utilities_database
import scripts.get_url_theses_selenium as get_url_theses_selenium
import scripts.search_engine as search_engine
import scripts.RAG as RAG

import configparser

# Lire le fichier de configuration
config = configparser.ConfigParser()
config.read('./scripts/config.ini')

MODEL_EMBEDDING                  = config["DEFAULT"]['MODEL_EMBEDDING']
VECTOR_STORE_PATH                = config["DEFAULT"]['VECTOR_STORE_PATH']
EXCEL_QUERY_STORE_PATH           = config["DEFAULT"]['EXCEL_QUERY_STORE_PATH']
EXCEL_TEMPORARY_QUERY_STORE_PATH = config["DEFAULT"]['EXCEL_TEMPORARY_QUERY_STORE_PATH']
PORT_SERVER                      = config["DEFAULT"]['PORT_SERVER']
API_KEY                          = config["MISTRAL"]["API_KEY"]


app = Flask(__name__)
app.config['SECRET_KEY'] = "secret_key"

@app.route("/")
@app.route('/', methods=['GET', 'POST'])
def index():
    
    if request.method == 'POST':
        
        query     = request.form.get('user_query')
        url_query = get_url_theses_selenium.get_url_request(query)
        df_theses = pd.read_excel(EXCEL_QUERY_STORE_PATH)
        
        if not utilities_database.query_already_exist(df_theses, url_query):
            print("updating the database because new request")
            df_theses = utilities_database.update_database(df_theses, query)
        else:
            print("url query found in excel because request already done")
            
        df_request = df_theses[df_theses["url_query"] == url_query]
        df_request.to_excel(EXCEL_TEMPORARY_QUERY_STORE_PATH, index= False)
        
            
        return redirect(url_for("resultats"))
    return render_template('index.html')


@app.route('/resultats', methods=['GET', 'POST'])
def resultats():
    df_output = pd.read_excel(EXCEL_TEMPORARY_QUERY_STORE_PATH)
    
    # check API TOKEN
    is_token_mistral = False if API_KEY == "None" else True
    
    response_rag = "No Mistral token API provided in ./scripts/config.ini" if API_KEY == "None" else "API Mistral ready No request yet"
        
    
    if request.method == "POST":
        query = request.form.get('user_query')
        mistral_query = request.form.get('mistral_query')
        
        results = search_engine.get_similar_paragraphs(query, 
                                                       df_output["content"].tolist(),
                                                       {}, # filter on similar paragraphs if needed
                                                       MODEL_EMBEDDING,
                                                       VECTOR_STORE_PATH,
                                                       10)
        
        context = RAG.document_into_context(results)
        
        list_url_similar = [res.metadata["url_these"] for res in results] # look for the specific url corresponding to the similar these
        df_deep_search = df_output[df_output["url_these"].isin(list_url_similar)]
        
        if mistral_query and is_token_mistral:
            response_rag = RAG.call_mistral_rag(context=context, prompt= f"quels articles se réfèrent le plus à la requête : '{mistral_query}'")
        
        return render_template('resultats.html',PORT_SERVER = f"http://127.0.0.1:{PORT_SERVER}", mistral_answer= response_rag, data= df_deep_search.to_dict(orient = "records"))
        
    return render_template('resultats.html', PORT_SERVER = f"http://127.0.0.1:{PORT_SERVER}", mistral_answer= response_rag , data= df_output.to_dict(orient = "records"))



if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=PORT_SERVER, threaded=False)


