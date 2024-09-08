import os
import re
from utils.google_drive import authenticate_google_drive, extract_folder_id, is_file_link, list_files_in_folder, download_file_from_google_drive
from utils.dropbox import download_files_from_dropbox
from utils.onedrive import download_files_from_onedrive
from utils.sharepoint import download_files_from_sharepoint
from utils.file_utils import download_file_from_url, read_pdf, read_docx, read_txt, extract_text_from_image
from utils.RAG import rag_system, add_document

ALLOWED_EXTENSIONS = ('.pdf', '.docx', '.txt', '.jpeg', '.png', '.jpg')

def is_local_file(path):
    return os.path.isfile(path)

def is_local_directory(path):
    return os.path.isdir(path)

def read_local_file(file_path):
    _, file_extension = os.path.splitext(file_path)
    with open(file_path, 'rb') as f:
        file_bytes = f.read()
    return file_bytes, file_extension

def read_local_directory(directory_path):
    file_list = []
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.lower().endswith(ALLOWED_EXTENSIONS):
                file_path = os.path.join(root, file)
                file_bytes, file_extension = read_local_file(file_path)
                file_list.append((file_bytes, file))
    return file_list

def process_files_from_source(source_url):
    file_list = []
    try:
        if is_local_file(source_url):
            file_bytes, file_extension = read_local_file(source_url)
            file_list.append((file_bytes, source_url.split(os.sep)[-1]))
        elif is_local_directory(source_url):
            file_list = read_local_directory(source_url)
        elif 'www.dropbox.com' in source_url:
            file_list = download_files_from_dropbox(source_url)
        elif 'drive.google.com' in source_url:
            service = authenticate_google_drive()
            if is_file_link(source_url):
                file_id = re.search(r'/file/d/(.*?)/', source_url).group(1)
                file_metadata = service.files().get(fileId=file_id, fields='name').execute()
                file_name = file_metadata['name']
                file_bytes = download_file_from_google_drive(service, file_id, file_name)
                if file_bytes:
                    file_list.append((file_bytes, file_name))
            else:  # Assume it's a folder link
                folder_id = extract_folder_id(source_url)
                files = list_files_in_folder(service, folder_id)
                if files:
                    for file in files:
                        if file['name'].endswith(ALLOWED_EXTENSIONS):
                            file_bytes = download_file_from_google_drive(service, file['id'], file['name'])
                            file_list.append((file_bytes, file['name']))
                else:
                    print("No files found in the Google Drive folder.")
        elif 'onedrive.live.com' in source_url or '1drv.ms' in source_url:
            file_list = download_files_from_onedrive(source_url)
        elif 'sharepoint.com' in source_url:
            file_list = download_files_from_sharepoint(source_url)
        else:
            file_bytes = download_file_from_url(source_url)
            if file_bytes:
                file_list.append((file_bytes, source_url.split('/')[-1]))

    except Exception as e:
        print(f"Error processing files from {source_url}: {e}")

    return file_list


def main(link):

    output=""

    file_urls = link
    for url in file_urls:
        print(f"Processing URL: {url}")
        files = process_files_from_source(url)
        if files:
            for file_bytes, file_name in files:
                if file_name.endswith('.pdf'):
                    print(f"Content from PDF ({file_name}):")
                    output+=read_pdf(file_bytes)
                elif file_name.endswith('.docx'):
                    print(f"Content from DOCX ({file_name}):")
                    output+=read_docx(file_bytes)
                elif file_name.endswith('.txt'):
                    print(f"Content from TXT ({file_name}):")
                    output+=read_txt(file_bytes)
                elif file_name.endswith(('.jpeg', '.png', '.jpg')):
                    print(f"Content from Image ({file_name}):")
                    output+=extract_text_from_image(file_bytes)
                output+="\n" + "-"*50 + "\n"

        else:
            print(f"Failed to process files from {url}")

    add_document(text=output)



def handle_user_interactions():
    link=input("Path : ").split(sep=",")
    main(link)
    print("Document added successfully. You can now ask questions related to the document.")

    while True:
        query = input("Question : ")
        response = rag_system(query)
        #return response
        print(response)




if __name__ == '__main__':
    handle_user_interactions()
