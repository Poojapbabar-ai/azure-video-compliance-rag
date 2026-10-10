import os 
import logging
import glob
from dotenv import load_dotenv
load_dotenv(override=True)
from typing import Dict, Any


from langchain_community.document_loaders import PyPDFLoader, UnstructuredFileLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter  

#azure components
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import AzureSearch

#set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

logger = logging.getLogger("brand-gurardian")

index_name = os.getenv('AZURE_SEARCH_INDEX_NAME')

def index_docs():
    '''
    Reads the PDFs, chunks them and upload to Azure Search 
    '''
    #current_paths, we look for the data folder
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_folder = os.path.join(current_dir,"../../backend/data")


    #check env variables
   # Check environment variables
    logger.info("="*60)
    logger.info("Environment Configuration Check: ")
    logger.info(f"AZURE_OPENAI_ENDPOINT : {os.getenv('AZURE_OPENAI_ENDPOINT')}")
    logger.info(f"AZURE_OPENAI_API_VERSION : {os.getenv('AZURE_OPENAI_API_VERSION')}")
    logger.info(f"Embedding Deployment : {os.getenv('AZURE_OPENAI_EMBEDDING_DEPLOYMENT', 'text-embedding-3-smal')}")
    logger.info(f"AZURE_SEARCH_ENDPOINT : {os.getenv('AZURE_SEARCH_ENDPOINT')}")
    logger.info(f"AZURE_SEARCH_INDEX_NAME : {os.getenv('AZURE_SEARCH_INDEX_NAME')}")
    logger.info("="*60)


    required_vars =[
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_API_KEY",
        "AZURE_SEARCH_ENDPOINT",
        "AZURE_SEARCH_API_KEY",
        "AZURE_SEARCH_INDEX_NAME"
    ]

    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"Missing required environment variables : {missing_vars}")
        logger.isEnabledFor("Please ensure your .env file and all variables are set")
        return 

    #initialize the embedding model : turns text into vectors
    try:
        logger.info("Initialize the AZURE OPENAI Embeddings...")
        openai_base_url = f"{os.getenv('AZURE_OPENAI_ENDPOINT', '').rstrip('/')}/openai/v1"
        embeddings = OpenAIEmbeddings(
            model=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-small-2"),
            base_url=openai_base_url,
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        )
        logger.info("Embedding model Initialized")
    except Exception as e:
        logger.error(f"Failed to initialize embeddings : {e}")
        logger.error("Please verify your azure OPENAI Deployement name and endpoint")


    #initialize the Azure Search: 
    try:
        logger.info("Initialize the AZURE Embeddings...")
        vector_store = AzureSearch(
            azure_search_endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
            azure_search_key=os.getenv("AZURE_SEARCH_API_KEY"),
            index_name=index_name,
            embedding_function=embeddings.embed_query,
        )

        
        logger.info(f"Vector search Initialized for index {index_name}")
    except Exception as e:
        logger.error(f"Failed to initialize Azure Search : {e}")
        logger.error("Please verify your azure SEARCH end point,API KEY, and index name")
        return

    # Find the pdf files

    pdf_files = glob.glob(os.path.join(data_folder,"*.pdf"))
    if not pdf_files:
        logger.warning(f"NO PDFs Found in {data_folder}.Please add files")
    logger.info(f"Found {len(pdf_files)} PDF to process: {[os.path.basename(f) for f in pdf_files]}")

    all_splits = []

    #process the pdf
    for pdf_path in pdf_files:
        try:
            logger.info(f"Loading {os.path.basename(pdf_path)}........")
            loader = PyPDFLoader(pdf_path)
            raw_docs = loader.load()

            #chunking the strategy 
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size  = 1000,
                chunk_overlap = 200
            )
            splits = text_splitter.split_documents(raw_docs)
            for split in splits:
                split.metadata["source"] = os.path.basename(pdf_path)

            all_splits.extend(splits)
            logger.info(f"Split into {len(splits)} chunks")  


        except Exception as e:
            logger.error(f"Failed to process {pdf_path} : {e}")


        # Upload to azure 
        if all_splits:
            logger.info(f"Uplaoding {len(all_splits)} chunks to Azure AI Search Index '{index_name}' ")
            try:
                #azure search accepts batches automatically  via this method 
                vector_store.add_documents(documents=all_splits)
                logger.info("="*60)
                logger.info("Indexing is completed knowledge Base is Ready ")
                logger.info(f"Total chunks indexed :{len(all_splits)}")
                logger.info("="*60)

            except Exception as e:
                logger.error("Failed to upload the documents to Azure search :{e}")
                logger.error("Please check the Azure Search COnfiguration  and try again")
        else:
            logger.warning("No documents  were processed.")



if __name__ == "__main__":   
    index_docs()

  
