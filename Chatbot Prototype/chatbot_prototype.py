from langchain_community.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.prompts import PromptTemplate

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())


class StudyChatBot:


    def __init__(self, study_program) -> None:
        
        self.vector_db = Chroma(
            persist_directory='storage_scaled_w_metadata',
            embedding_function=OpenAIEmbeddings()
            )
        
        print('loaded documents: ', len(self.vector_db.get()['documents']))

        template = """
Use the following pieces of context to answer the question at the end.

Execute these steps:
1 - always answer in the language the question was given in
2 - read the context, do not use information outside of the context to answer the question
3 - if the answer is not provided in the given context, say where more information can possibly be found
4 - answer the question

------------------------
Context: {context}

Question: I am studying the {study_program}. {question}

"""        
        custom_prompt = PromptTemplate.from_template(template)
        
        self.chain = ConversationalRetrievalChain.from_llm(
        llm=ChatOpenAI(model='gpt-3.5-turbo', temperature=0),
        retriever=self.vector_db.as_retriever(search_kwargs={'k': 5}),
        return_source_documents=True,
        combine_docs_chain_kwargs={"prompt": custom_prompt.partial(study_program=study_program)}
        )

        self.chat_history = []


    def query(self, question:str) -> str:
        result = self.chain.invoke({'question': question, 'chat_history': self.chat_history})
        self.chat_history.append((question, result['answer']))
        return result
