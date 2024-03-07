# Chatbot Prototype

This prototype implementation contains a simple web interface. To run the protypes, following steps must be executed:

* A vector store with embeddings of the source documents must be created. Running the file `setup_vector_db.py` will create a vector store and embedd text chunks with generated metadata. The directory for the source documents can be adjusted in `config.py`.

* an OpenAI Key has to be defined in a `.env` file 

* to open the web interface, run the file `app.py`. This will start a flask based python server.
