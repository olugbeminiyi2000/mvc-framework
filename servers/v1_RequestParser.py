import re
from typing import Tuple, Dict, Union
from urllib.parse import parse_qs

def parse_http_request(request_data: str) -> Tuple[str, str, Dict[str, Union[str, bytes]]]:
    """
    Parses an HTTP request, handling both application/x-www-form-urlencoded
    and multipart/form-data correctly.

    Args:
        request_data (str): The raw HTTP request data.

    Returns:
        Tuple[str, str, Dict[str, Union[str, bytes]]]: 
            - method (str): HTTP method (e.g., "GET", "POST").
            - path (str): The request path (e.g., "/some-route").
            - body (dict): Contains text fields (str) and file data (bytes).
    """
    try:
        # Split headers and body
        if "\r\n\r\n" not in request_data:
            raise ValueError("Malformed request, no headers found")

        headers, raw_body = request_data.split("\r\n\r\n", 1)
        header_lines = headers.split("\r\n")

        # Extract method and path
        request_line = header_lines[0].split()
        if len(request_line) < 2:
            raise ValueError("Malformed request line")

        method, path = request_line[:2]

        # Extract headers
        header_dict = {}
        for line in header_lines[1:]:
            if ": " in line:
                key, value = line.split(": ", 1)
                header_dict[key.lower()] = value.strip()

        # Initialize body dictionary
        body: Dict[str, Union[str, bytes]] = {}

        # Check for Content-Type to determine how to parse the body
        content_type = header_dict.get("content-type", "")
        
        if "multipart/form-data" in content_type:
            # Handle multipart/form-data
            boundary_match = re.search(r'boundary=([^;]+)', content_type)
            if not boundary_match:
                raise ValueError("No boundary found in Content-Type header")

            boundary = f"--{boundary_match.group(1)}"
            
            # Ensure the request ends with the correct boundary
            if not raw_body.endswith(f"{boundary}--"):
                raw_body += f"\r\n{boundary}--"

            parts = raw_body.split(boundary)
            for part in parts:
                part = part.strip()
                if not part or part == "--":  # Skip empty parts and closing boundary
                    continue

                split_index = part.find("\r\n\r\n")
                if split_index == -1:
                    continue  # Malformed part; skip

                headers_part = part[:split_index]
                body_part = part[split_index + 4:]  # Skip "\r\n\r\n"

                disposition_match = re.search(r'name="([^"]+)"(?:; filename="([^"]+)")?', headers_part)
                if not disposition_match:
                    continue  # No valid Content-Disposition; skip

                field_name, file_name = disposition_match.groups()

                if file_name:  # File upload
                    content_type_match = re.search(r'Content-Type: (.+)', headers_part)
                    file_content_type = content_type_match.group(1) if content_type_match else "application/octet-stream"
                    
                    body[field_name] = {
                        "filename": file_name,
                        "content_type": file_content_type,
                        "data": body_part.encode("utf-8")  # Use utf-8 for binary data
                    }
                else:  # Text field
                    body[field_name] = body_part.strip()

        elif "application/x-www-form-urlencoded" in content_type or not content_type:
            # Handle application/x-www-form-urlencoded or no Content-Type
            body.update({k: v[0] for k, v in parse_qs(raw_body).items()})

        else:
            raise ValueError(f"Unsupported Content-Type: {content_type}")
        return method, path, body

    except Exception as e:
        print(f"Error parsing request: {e}")
        return "", "", {}