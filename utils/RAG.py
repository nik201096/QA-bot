import chromadb
from dotenv import load_dotenv
import os
import openai

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
clients = openai.OpenAI()

# Initialize ChromaDB client and create an in-memory collection
db = chromadb.Client()
collection = db.create_collection("Test")

def add_document(text):
    collection.add(ids="default", documents=text)

def retrieve_documents(query, top_k=3):
    results = collection.query(query_texts=[query], n_results=top_k)
    return results

def gpt_chat(text):
    system_prompt = (
        "You are a helpful and informative AI assistant. "
        "Given a query and relevant context, provide a concise and comprehensive response in 200 words."
    )

    response = clients.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text},
        ],
        temperature=0.01,
        presence_penalty=0.5,
        seed=123,
    )
    return response.choices[0].message.content

def rag_system(query):
    doc_text = retrieve_documents(query, top_k=3)

    if not doc_text:
        return "Document not found."

    input_text = f"Context:\n{doc_text}\n\nQuery:\n{query}"
    response = gpt_chat(input_text)
    return response

def handle_user_interactions():
    print("Please upload the document.")
    document_text = input("Enter the document text: ").strip()
    add_document(document_text)
    print("Document added successfully. You can now ask questions related to the document.")

    while True:
        query = input("Enter your query: ").strip()
        response = rag_system(query)
        print(f"Response: {response}")



if __name__ == "__main__":
    handle_user_interactions()
