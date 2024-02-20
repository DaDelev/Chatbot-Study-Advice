from langchain.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())


class StudyChatBot:


    def __init__(self) -> None:
        self.vector_db = Chroma(
            persist_directory='storage_scaled_w_metadata_2',
            embedding_function=OpenAIEmbeddings()
            )
        
        self.chain = ConversationalRetrievalChain.from_llm(
        llm=ChatOpenAI(model='gpt-3.5-turbo', temperature=0),
        retriever=self.vector_db.as_retriever(search_kwargs={'k': 5}),
        return_source_documents=True
        # combine_docs_chain_kwargs={"prompt": custom_prompt}
        )

        self.chat_history = []


    def query(self, question:str) -> str:
        result = self.chain.invoke({'question': question, 'chat_history': self.chat_history})
        self.chat_history.append((question, result['answer']))
        return result
