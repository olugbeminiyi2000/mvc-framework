import os
from typing import Dict, Union

def save_uploaded_file(file_info: Dict[str, Union[str, bytes]]) -> str:
    """
    Saves an uploaded file to a subdirectory based on its extension.

    Args:
        file_info (dict): A dictionary containing 'filename', 'content_type', and 'data'.

    Returns:
        str: The path of the saved file.
    """
    upload_base_dir = "static/uploads" 
    os.makedirs(upload_base_dir, exist_ok=True)

    filename = file_info['filename']
    file_extension = os.path.splitext(filename)[1][1:].lower()

    folder_name = file_extension if file_extension else 'others'
    upload_dir = os.path.join(upload_base_dir, folder_name)

    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, filename)

    with open(file_path, 'wb') as f:
        f.write(file_info['data'])

    return file_path


def handle_file_uploads(body: Dict[str, Union[str, bytes]]) -> None:
    """
    Handles the processing of uploaded files from the request body.

    Args:
        body (dict): The parsed request body containing form data.
        upload_directory (str): The fixed directory where files should be saved.
    """
    for key, value in body.items():
        if isinstance(value, dict) and 'data' in value:
            saved_file_path = save_uploaded_file(value)
            del body[key]["data"]
            print(f"File saved at: {saved_file_path}")
