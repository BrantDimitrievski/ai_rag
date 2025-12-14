How to run me:

1- Add files to workspace folder
2- Parsing: python -m parsing.parser
3- Chunking: python -m chunking.build_chunks
4- Creating VectorDB using Qdrant from chunks
4.1 - 
python vectorstore_qdrant.py  
5- Setup a server, install dependencies and your model of choice 
ex: 


Plan for action

1. Docs to Parsed text
Put all your fake RCN docs in workspace/.
Use unstructured.io to parse docs into JSON. Insert into an SQL lite DB. 

2. Parsed text to vector Space
How to do i split chunks? 1000 characters?
Use an embedding model to turn chunk into a vector
create vectorSpace maybe use Qdrant or pgvector

3. Choose and Setup model (probably 70B Llama)
Build a system prompt for Llama 70B:
System message (“You are an assistant to the National Defence of Canada (DND). ”), #cite all information, 
Setup UI
Embed the question with the same embedding model

Search in the vector DB, get top-k relevant chunks (with their doc info)

Llama 70B generates an answer using only that context
