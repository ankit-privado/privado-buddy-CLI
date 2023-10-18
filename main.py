from urllib.parse import urlparse
from flask import Flask
from flask import Flask, request, jsonify
import sys
import os
import requests
import subprocess
from langchain.document_loaders import JSONLoader
from langchain.vectorstores import Chroma
from langchain.embeddings import GPT4AllEmbeddings
from langchain import PromptTemplate
from langchain.llms import Ollama
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pathlib import Path
app = Flask(__name__)

class SuppressStdout:
    def __enter__(self):
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout
        sys.stderr = self._original_stderr


def is_valid_url(url):
    print(url,"iiiiiiiiii")
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

    
@app.route('/api/upload-json', methods=['POST'])

def upload_json():
    global json_path, qa_chain
    try:
        json_data = request.get_json()
        json_path = json_data.get('json_path')
        print(json_path,"pppppp")
        if not json_path:
            return jsonify({'error': 'No JSON file path or URL provided'})
        print(is_valid_url(json_path), "uuuuuuu")
        if is_valid_url(json_path):
            response = requests.get(json_path)
            if response.status_code == 200:
                content = response.text
                with open("downloaded_json.json", "w") as f:
                    f.write(content)
                json_path = "downloaded_json.json"
                with open('downloaded.json', 'wb') as file:
                    file.write(json_file)
                os.chdir("/Users/adititripathi/Desktop/ollama")
                ollama_command = "ollama serve"
                subprocess.Popen(ollama_command, shell=True)
                print("Ollama is running")
                qa_chain = initialize_chatbot_model('downloaded.json')
                return jsonify({'message': 'Chatbot model and server started successfully'})
        elif os.path.isfile(json_path):
            with open(json_path, 'r') as file:
                content = file.read()
            print("yeyeyeyyey")
            os.chdir("/Users/adititripathi/Desktop/ollama")
            ollama_command = "ollama serve"
            subprocess.Popen(ollama_command, shell=True)
            print("Ollama is running")
            qa_chain = initialize_chatbot_model(json_path)

            return jsonify({'message': 'Chatbot model and server started successfully'})
        else:
            return jsonify({'error': 'JSON file does not exist at the provided path'})
    except Exception as e:
        return jsonify({'error': str(e)})









# Route for chatbot interactions
@app.route('/api/chatbot', methods=['POST'])
def chatbot():
    try:
        json_data = request.get_json()
        user_query = json_data.get('query')

        if not qa_chain:
            return jsonify({'answer': 'Chatbot not initialized'})

        response = generate_response_using_model(qa_chain, user_query)

        return jsonify({'answer': response})
    except Exception as e:
        return jsonify({'error': str(e)})
    
    
def initialize_chatbot_model(json_path):
    loader = JSONLoader(file_path=json_path, jq_schema='.', text_content=False)
    data = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
    all_splits = text_splitter.split_documents(data)

    with SuppressStdout():
        vectorstore = Chroma.from_documents(documents=all_splits, embedding=GPT4AllEmbeddings())

    template = """Use the following pieces of context to answer the question at the end. 
    If you don't know the answer, just say that you don't know, don't try to make up an answer. 
    Use three sentences maximum and keep the answer as concise as possible. 
    {context}
    Question: {question}
    Helpful Answer:"""
    QA_CHAIN_PROMPT = PromptTemplate(
        input_variables=["context", "question"],
        template=template,
    )

    llm = Ollama(base_url='http://localhost:11434', model="llama2", callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]))
    qa_chain = RetrievalQA.from_chain_type(
        llm,
        retriever=vectorstore.as_retriever(),
        chain_type_kwargs={"prompt": QA_CHAIN_PROMPT},
    )

    return qa_chain

def generate_response_using_model(qa_chain, user_query):
    try:
        result = qa_chain({"query": user_query})
        response = result.get('result', 'No answer available')
        return response
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    print("oooo")
    app.run(host='0.0.0.0', port=3000)
