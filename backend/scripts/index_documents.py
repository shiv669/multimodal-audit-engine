import os
import glob
import logging
from dotenv import load_dotenv
load_dotenv(override=True)

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_mistralai.embeddings import MistralEmbeddings
from langchain_community.vectorstores import FAISS

#setup logging

logging.basicConfig(
    level = logging.INFO,
    format = "%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("indexer")

def index_logs():
    '''
    read the pdf, chunk it and upload it for vector search
    '''

    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_folder = os.path.join(current_dir,"../../backend/data")


    # validate the endpoints 
    # verify environment variables are set and accessible for Mistral embeddings and LangSmith tracing
    # using an simple for loop if required variables are not there using logger log them
    required_vars = ["MISTRAL_API_KEY", "LANGSMITH_API_KEY"]
    for var in required_vars:
        if not os.getenv(var):
            logger.warning(f"Missing environment variable: {var}")
        else:
            logger.info(f" {var} is set")
    
    # validate Mistral API endpoint
    try:
        mistral_key = os.getenv("MISTRAL_API_KEY")
        if mistral_key:
            embeddings = MistralEmbeddings(api_key=mistral_key)
            logger.info("Mistral API endpoint validated and initialsed successfully")
    except Exception as e:
        logger.error(f"Failed to validate Mistral API endpoint: {str(e)}")
    
    # validate FAISS vector store setup
    try:
        vector_store = FAISS.from_documents([], embeddings)
        logger.info("FAISS vector store configured successfully")
    except Exception as e:
        logger.error(f"Failed to configure FAISS: {str(e)}") 


    #find pdf files 
    pdf_files = glob.glob(os.path.join(data_folder, "*.pdf"))
    if not pdf_files:
        logger.warning(f"no pdf files found at {data_folder}")
    logger.info(f"found {len(pdf_files)} to process: {[os.path.basename(f) for f in pdf_files]}")

    all_splits = []

    #process each pdf

    for pdf_paths in pdf_files:
        try:
            logger.info(f"loading: {os.path.basename(pdf_paths)}...")
            loader = PyPDFLoader(pdf_paths)
            raw_format = loader.load()

            #chunking startegy
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size = 1000,
                chunk_overlap = 200
            )

            splits = text_splitter.split_documents(raw_format)
            for split in splits:
                split.metadata["source"] = os.path.basename(pdf_paths)

            all_splits.extend(splits)
            logger.info(f"split into {len(splits)} chunks...")

        except Exception as e:
            logger.error(f"error at {os.path.basename(pdf_paths)} {e}")

    if all_splits:
        logger.info(f"uploading {len(all_splits)} to mistral ai embeddings")
        try:
            vector_store.add_documents(documents = all_splits)
            logger.info("="*60)
            logger.info("indexing completed knowledge base ready !")
            logger.info(f"total number of chunks indexed : {len(all_splits)}")
            logger.info("="*60)
        except Exception as e:
            logger.info(f"indexing failed due to : {e} . For assurance please check api and try again")

    else:
        logger.warning("no documents were to be found")

if __name__ == "__main__":
    index_logs()
