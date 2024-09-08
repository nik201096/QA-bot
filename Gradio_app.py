import gradio as gr
import os
from main import process_files_from_source
from utils.RAG import rag_system, add_document
from utils.file_utils import  read_pdf, read_docx, read_txt, extract_text_from_image

os.environ["GRADIO_ANALYTICS_ENABLED"] = "False"

def process_links(input_links):
    links = input_links.split(',')
    output = ""
    
    for url in links:
        files = process_files_from_source(url.strip())
        if files:
            for file_bytes, file_name in files:
                if file_name.endswith('.pdf'):
                    output += read_pdf(file_bytes)
                elif file_name.endswith('.docx'):
                    output += read_docx(file_bytes)
                elif file_name.endswith('.txt'):
                    output += read_txt(file_bytes)
                elif file_name.endswith(('.jpeg', '.png', '.jpg')):
                    output += extract_text_from_image(file_bytes)
                output += "\n" + "-"*50 + "\n"
        else:
            return f"Failed to process files from {url}"
    
    add_document(text=output)
    print(output)
    return "Document added successfully. You can now ask questions related to the document."

def answer_query(query):
    response = rag_system(query)
    return response

# Create Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("## Document Processing and Q&A System")

    with gr.Tab("Document Processing"):
        input_links = gr.Textbox(label="Enter file paths or URLs (comma-separated)")
        process_button = gr.Button("Process Files")
        process_output = gr.Textbox(label="Output")
        
        process_button.click(process_links, inputs=input_links, outputs=process_output)

    with gr.Tab("Query"):
        query_input = gr.Textbox(label="Ask a question")
        query_button = gr.Button("Get Answer")
        query_output = gr.Textbox(label="Answer")

        query_button.click(answer_query, inputs=query_input, outputs=query_output)

# Launch the interface
if __name__ == '__main__':
    demo.launch(share=True)
