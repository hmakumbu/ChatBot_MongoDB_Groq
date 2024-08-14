from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv



load_dotenv()

groq_api_ke = os.getenv("API_Key_groq")

llm = ChatGroq(temperature=0, groq_api_key=groq_api_ke, model_name="mixtral-8x7b-32768")
