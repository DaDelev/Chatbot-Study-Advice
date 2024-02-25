import os
from functools import partial
from langchain.document_loaders import UnstructuredHTMLLoader, UnstructuredPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.chains.combine_documents import collapse_docs, split_list_of_docs
from langchain.chat_models import ChatOpenAI
from langchain.document_transformers.openai_functions import create_metadata_tagger
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain.schema import Document, StrOutputParser
from langchain_core.prompts import format_document
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
import time

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

# config for metadata generation prompt and schema
from config import config

# dircetory with the scraped documents
doc_directory = ""

# directory to persist vector db
vectordb_dir = ""   

llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0125")

metadata_prompt = ChatPromptTemplate.from_template(config["metadata"]["metadata_prompt"])

schema = config["metadata"]["metadata_schema"]

document_transformer = create_metadata_tagger(metadata_schema=schema, llm=llm, prompt=metadata_prompt)

# Prompt and method for converting Document -> str.
document_prompt = PromptTemplate.from_template("{page_content}")
partial_format_document = partial(format_document, prompt=document_prompt)

# A text splitter that recursively splits a document into multiple chunks until
# the maximum chunck size is below a predefined value (without overlap).
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 16000,
    chunk_overlap  = 0,
    length_function = llm.get_num_tokens,
    is_separator_regex = False,
)

def load_documents(doc_directory: str) -> list:
    documents = []
    for file in os.listdir(doc_directory):
        # load pdf files
        if file.endswith('.pdf'):
            pdf_path = f'./{doc_directory}/' + file
            print(f'Loading {pdf_path}')
            loader = UnstructuredPDFLoader(pdf_path)
            documents.extend(loader.load())
            # load html files
        elif file.endswith('.html'):
            doc_path = f'./{doc_directory}/' + file
            print(f'Loading {doc_path}')
            loader = UnstructuredHTMLLoader(doc_path)
            documents.extend(loader.load())
    return documents


def clean_documents(documents: list) -> list:
    # clean text from tab characters "\t"
    for d in documents:
        d.page_content = d.page_content.replace("\t", "")
    return documents

def get_num_tokens_single_doc(doc):
    return llm.get_num_tokens(partial_format_document(doc))

def format_docs(docs):
    return "\n\n".join(partial_format_document(doc) for doc in docs)

def get_num_tokens(docs):
    return llm.get_num_tokens(format_docs(docs))

def collapse(docs, config, token_max=16000):
    collapse_ct = 1
    while get_num_tokens(docs) > token_max:
        config["run_name"] = f"Collapse {collapse_ct}"
        invoke = partial(collapse_chain.invoke, config=config)
        split_docs = split_list_of_docs(docs, get_num_tokens, token_max)
        docs = [collapse_docs(_docs, invoke) for _docs in split_docs]
        collapse_ct += 1
    return docs

def get_metadata(docs, metadata_tagger, summarizer, llm, max_tokens):
    document_prompt = PromptTemplate.from_template("{page_content}")
    partial_format_document = partial(format_document, prompt=document_prompt)
    docs_transformed = []
    for i, doc in enumerate(docs):
        print(f"Processing document {i}/{len(docs)-1}")
        # directly apply metadata tagger if number of tokens is below threshold
        if llm.get_num_tokens(partial_format_document(doc)) <= max_tokens:
            print(f"\tApply metadata tagger...")
            doc_w_metadata = metadata_tagger.transform_documents([doc])[0]
            docs_transformed.append(doc_w_metadata)
        # otherwise, summarize document first to get metadata
        else:
            print(f"\tSummarize document...")
            
            # sleep if rate limit on tokens per minutes is reached
            try:
                summary = summarizer.invoke([doc])
            except:
                time.sleep(15)
            
            summary_doc = Document(page_content=summary, metadata=doc.metadata)
            print(f"\tApply metadata tagger...")
            summary_w_metadata = metadata_tagger.transform_documents([summary_doc])[0]
            doc_w_metadata = Document(page_content=doc.page_content, metadata=summary_w_metadata.metadata)
            docs_transformed.append(doc_w_metadata)
    print("done!")
    return docs_transformed

# build chains

# The chain we'll apply to each individual document.
# Returns a summary of the document.
map_chain = (
    {"context": partial_format_document}
    | PromptTemplate.from_template("Summarize this content:\n\n{context}")
    | llm
    | StrOutputParser()
)

# A wrapper chain to keep the original Document metadata
map_as_doc_chain = (
    RunnableParallel({"doc": RunnablePassthrough(), "content": map_chain})
    | (lambda x: Document(page_content=x["content"], metadata=x["doc"].metadata))
).with_config(run_name="Summarize (return doc)")

# The chain we'll repeatedly apply to collapse subsets of the documents
# into a consolidate document until the total token size of our
# documents is below some max size.
collapse_chain = (
    {"context": format_docs}
    | PromptTemplate.from_template("Collapse this content:\n\n{context}")
    | llm
    | StrOutputParser()
)

# The chain we'll use to combine our individual document summaries
# (or summaries over subset of documents if we had to collapse the map results)
# into a final summary.
reduce_chain = (
    {"context": format_docs}
    | PromptTemplate.from_template("Combine these summaries:\n\n{context}")
    | llm
    | StrOutputParser()
).with_config(run_name="Reduce")

# The final full chain for summarizing documents
map_reduce_summarizer = (text_splitter.split_documents | map_as_doc_chain.map() | collapse | reduce_chain).with_config(
    run_name="Map reduce"
)

def create_text_chunks(docs):
    # split documents into text chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunked_documents = text_splitter.split_documents(docs)

    # integrate metadata into text chunks
    for d in chunked_documents:
        d.page_content = f"""Study Program: {d.metadata['study_program']}
    Short Description: {d.metadata['short_description']}
    Content: {d.page_content}
    ------------------------
    """
    return chunked_documents

def create_vector_db(docs, vectordb_dir):
    # create chroma vector db with OpenAIEmbeddings
    vectordb = Chroma.from_documents(
    docs,
    embedding=OpenAIEmbeddings(),
    persist_directory=f'./{vectordb_dir}'
    )
    vectordb.persist()
    
    
if __name__ == '__main__':
    
    # load and clean documents
    documents = clean_documents(load_documents(doc_directory=doc_directory))

    # generate metadata for documents
    documents_w_metadata = get_metadata(
        documents,  
        metadata_tagger=document_transformer, 
        summarizer=map_reduce_summarizer, 
        llm=llm, max_tokens=16000)
    
    #create text chunks of documents
    chunked_documents = create_text_chunks(documents_w_metadata)

    # embedd and persist text chunks in chroma vector storage
    create_vector_db(chunked_documents, vectordb_dir)

