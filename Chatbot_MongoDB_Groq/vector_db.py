from nomic import embed
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os
from langchain.vectorstores import MongoDBAtlasVectorSearch
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

# Load the nomic embedding model
embedding_model = SentenceTransformer("nomic-ai/nomic-embed-text-v1", trust_remote_code=True)

def get_embedding(text):
    """Generates vector embeddings for the given text."""
    embedding = embedding_model.encode(text)
    return embedding.tolist()

def vector_db(docs):
    client = MongoClient(MONGO_URI)

    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return None

    DB_NAME = 'ChatBot_DataBeez'
    db = client[DB_NAME]

    COLLECTION_NAME = 'chat_platform'
    collection = db[COLLECTION_NAME]

    ATLAS_VECTOR_SEARCH_INDEX_NAME = "vector_index"

    texts = [doc.page_content for doc in docs]

    try:
        # Generate embeddings using the nomic model
        embeddings = [get_embedding(text) for text in texts]

        docs_with_embeddings = []
        for doc, embed in zip(docs, embeddings):
            doc_with_embed = doc.copy()
            doc_with_embed.metadata["vector"] = embed  
            docs_with_embeddings.append(doc_with_embed)

        for doc_with_embed in docs_with_embeddings:
            collection.insert_one(doc_with_embed.metadata)

        retriever = MongoDBAtlasVectorSearch.from_documents(
            documents=docs_with_embeddings, 
            embedding=embedding_model, 
            collection=collection,
            index_name=ATLAS_VECTOR_SEARCH_INDEX_NAME
        ).as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3}
        )

        return retriever

    except Exception as e:
        print(f"Error in vector_db processing: {e}")
        return None





        # template = """Answer the question: {question} based only on the following context:
        # context: {context}
        # """
        # prompt = PromptTemplate.from_template(template = template,
        #                         input_varaibles = ["context", "question"])
        # output_parser = StrOutputParser()
        # model = ChatOpenAI(openai_api_key=key_param.openai_api_key, 
        #             model_name = 'gpt-3.5-turbo',
        #             temperature=0)

        # def format_docs(docs):
        #     return "\n\n".join(doc.page_content for doc in docs)