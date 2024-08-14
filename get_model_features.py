from Chatbot_MongoDB_Groq.load import load_text
from Chatbot_MongoDB_Groq.vector_db import vector_db
from Chatbot_MongoDB_Groq.process import process_documents

def get_retriever(file_path):
    try:
        data = load_text(file_path)
        docs = process_documents(data)
        retriever = vector_db(docs=docs)
        
        if retriever is None:
            raise ValueError("Retriever could not be initialized due to an error.")
        
        return retriever

    except Exception as e:
        print(f"Error in get_retriever: {e}")
        return None
