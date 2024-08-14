import os
from get_model_features import get_retriever
from Chatbot_MongoDB_Groq.prompt import prompt
from Chatbot_MongoDB_Groq.model import llm
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema import output_parser
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

class ChatBot:
    
    def __init__(self, file_path):
        try:
            self.retriever_callable = get_retriever(file_path)
            if self.retriever_callable is None:
                raise ValueError("Retriever initialization failed.")

            self.documents = self.retriever_callable({"question": ""})
            self.retrieval_chain = (
                {"context": self.retriever_callable, "question": RunnablePassthrough()}
                | prompt
                | llm 
                | output_parser()
            )

            MONGO_URI = os.getenv("MONGO_URI")
            self.client = MongoClient(MONGO_URI)
            self.db = self.client["ChatBot_DataBeez"]
            self.collection_embeddings = self.db["chat_platform"]
            self.collection_conversations = self.db["conversations"]
            self.embeddings_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

        except Exception as e:
            print(f"Error during initialization: {e}")
            raise

    def retrieve_similar_embeddings(self, query):
        query_embedding = self.embeddings_model.encode([query])[0]

        pipeline = [
            {
                "$project": {
                    "document_id": 1,
                    "text": 1,
                    "embedding": 1,
                    "similarity": {
                        "$let": {
                            "vars": {
                                "query_embedding": query_embedding.tolist()
                            },
                            "in": {
                                "$dotProduct": [
                                    "$embedding", "$$query_embedding"
                                ]
                            }
                        }
                    }
                }
            },
            {
                "$sort": {"similarity": -1}
            },
            {
                "$limit": 3
            }
        ]

        similar_docs = list(self.collection_embeddings.aggregate(pipeline))
        return similar_docs

    def chat(self, question):
        similar_docs = self.retrieve_similar_embeddings(question)
        context = "\n".join([doc["text"] for doc in similar_docs])

        response = self.retrieval_chain.invoke({"context": context, "question": question})
        self.save_conversation(question, response)
        return response

    def save_conversation(self, question, response):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        conversation = {
            "timestamp": timestamp,
            "user_question": question,
            "bot_response": response
        }
        self.collection_conversations.insert_one(conversation)

        print("Conversation enregistrée dans MongoDB")

