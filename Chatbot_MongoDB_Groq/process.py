from langchain.text_splitter import  RecursiveCharacterTextSplitter
#CharacterTextSplitter,

def process_documents(documents):
    text_splitter = RecursiveCharacterTextSplitter(separators=["\n\n", "\n", ". ", " ", ""], chunk_size=300, chunk_overlap=30)
    docs = text_splitter.split_documents(documents)

    return docs
