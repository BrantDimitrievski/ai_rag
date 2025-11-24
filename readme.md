1. Docs → Parsed text

Put all your fake RCN docs in workspace/.

Use unstructured.io to:

Read each file,

Extract clean text + metadata (ship type, date, classification),

Save into a small DB (e.g. SQLite) → one row per doc.

2. Parsed text → Vectors (for search)

Take the text from each row.

Split into chunks (e.g. 500–1000 characters).

Use an embedding model (e.g. BGE / OpenAI embeddings) to turn each chunk into a vector.

Store vectors + metadata in a vector database (Qdrant / Milvus / pgvector).

3. Question → Retrieved chunks

User asks a question.

Embed the question with the same embedding model.

Search in the vector DB → get top-k relevant chunks (with their doc info).

4. Retrieved chunks → Answer (AI tool)

Build a prompt for Llama 70B:

System message (“you are an RCN assistant…”),

The retrieved chunks as context,

The user’s question.

Llama 70B generates an answer using only that context.

Optional: wrap this in a small API or web UI (textbox + answer + sources).

That’s it:
Folder → parse → embed → vector DB → retrieve → Llama answer.