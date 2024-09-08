import dropbox

ACCESS_TOKEN = "Your Access Token"
dbx = dropbox.Dropbox(ACCESS_TOKEN)
    

def download_files_from_dropbox(shared_link):
    try:
        metadata = dbx.sharing_get_shared_link_metadata(shared_link)
        if isinstance(metadata, dropbox.sharing.FolderLinkMetadata):
            # It's a folder, list the files in it
            dir_path = metadata.path_lower
            dir_list = dbx.files_list_folder(dir_path)
            file_list = []
            for entry in dir_list.entries:
                if entry.name.endswith(('.pdf', '.docx', '.txt', '.jpeg', '.png', '.jpg')):
                    file_path = entry.path_lower
                    _, response = dbx.files_download(file_path)
                    file_list.append((response.content, entry.name))
            return file_list
        elif isinstance(metadata, dropbox.sharing.FileLinkMetadata):
            # It's a file, download it
            file_path = metadata.path_lower
            _, response = dbx.files_download(file_path)
            return [(response.content, metadata.name)]
        else:
            print("Unsupported link type.")
            return []
    except dropbox.exceptions.ApiError as err:
        print(f"API Error: {err}")
        return []
    except Exception as e:
        print(f"Error: {e}")
        return []