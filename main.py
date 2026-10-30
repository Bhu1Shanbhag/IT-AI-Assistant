import os
import sys
import io
import shutil
import tempfile
import pandas as pd

from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from agent import SmalltalkAgent, RetrieverAgent, ValidatoryAgent

# Load Environment Variables
load_dotenv()

# 🔹 Azure Config
AZURE_ENDPOINT = os.getenv("AOAI_CHAT_ENDPOINT")
API_KEY = os.getenv("AOAI_CHAT_KEY")
API_VERSION = os.getenv("AOAI_API_VERSION_GPT")
EMBEDDING_DEPLOYMENT = os.getenv("AOAI_EMBEDDING_DEPLOYMENT")
CHAT_DEPLOYMENT = os.getenv("AOAI_CHAT_DEPLOYMENT")

# Configuration
EXCEL_PATH = "test_excel 1.xlsx"
DB_DIRECTORY = "vector_db"

# 🔹 Initialize Models
embeddings = AzureOpenAIEmbeddings(
    azure_endpoint=AZURE_ENDPOINT,
    api_key=API_KEY,
    azure_deployment=EMBEDDING_DEPLOYMENT,
    openai_api_version=API_VERSION
)

llm = AzureChatOpenAI(
    azure_endpoint=AZURE_ENDPOINT,
    api_key=API_KEY,
    azure_deployment=CHAT_DEPLOYMENT,
    openai_api_version=API_VERSION
)

def create_and_store_article(row_data, vector_store):
    sno = row_data.get('SNo.', 'N/A')
    title = row_data.get('Title', 'N/A')
    description = row_data.get('Description', 'N/A')
    resolution = row_data.get('Resolution with steps', 'N/A')


    template = """
    You are an expert technical writer. Create a professional knowledge base article.
    Strictly include: Sno, Title, Description, Resolution of Steps.

    Data:
    Sno: {sno}
    Title: {title}
    Description: {description}
    Resolution: {resolution}
    """
    
    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm
    
    print(f"--- Processing Row {sno} ---")
    response = chain.invoke({"sno": sno, "title": title, "description": description, "resolution": resolution})
    
    doc = Document(
        page_content=response.content,
        metadata={"sno": str(sno)}
    )

    vector_store.add_documents([doc])
    print(f"Stored: {title}\n")

class RetrieverWrapper:
    """Wrapper for the vector store to provide a clean retrieval interface."""
    def __init__(self, vector_store):
        self.vector_store = vector_store

    def get_relevant_documents(self, query):
        print(f"[RetrieverWrapper] Searching for: '{query}'")
        return self.vector_store.similarity_search(query, k=5)

def retrieve_articles(query, vector_store):
    """Legacy retriever function (kept for compatibility)."""
    wrapper = RetrieverWrapper(vector_store)
    results = wrapper.get_relevant_documents(query)
    return results[0].page_content if results else "No results."

def handle_query(query, vector_store, llm):
    """Orchestrates agents using the Validatory agent as a master selector."""
    # 1. Initialize Wrapper
    retriever_wrapper = RetrieverWrapper(vector_store)
    
    # 2. Initialize the 3 core agents
    smalltalk_agent = SmalltalkAgent(llm)
    retriever_agent = RetrieverAgent(retriever_wrapper, llm)
    validatory_agent = ValidatoryAgent(llm)
    
    # 3. Let the validatory agent orchestrate the choice and execution
    return validatory_agent.orchestrate(query, smalltalk_agent, retriever_agent)

def load_excel_safely(file_path):
    """Reads Excel file, handling PermissionError if file is open in another app."""
    try:
        return pd.read_excel(file_path)
    except PermissionError:
        print(f"Warning: {file_path} is locked. Creating a temporary copy to read...")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            tmp_path = tmp.name
        
        shutil.copy2(file_path, tmp_path)
        df = pd.read_excel(tmp_path)
        os.remove(tmp_path)
        return df

# 🔹 Global Initialization
vector_store = Chroma(
    persist_directory=DB_DIRECTORY,
    embedding_function=embeddings
)

def main():
    # Process Rows ONLY IF DB IS EMPTY
    existing_docs = vector_store.get()
    if not existing_docs['ids']:
        print("Vector DB is empty. Processing Excel data...")
        df = load_excel_safely(EXCEL_PATH)
        for index, row in df.iterrows():
            create_and_store_article(row.to_dict(), vector_store)
    else:
        print(f"Vector DB already exists with {len(existing_docs['ids'])} documents. Skipping data processing.")


if __name__ == "__main__":
    main()
