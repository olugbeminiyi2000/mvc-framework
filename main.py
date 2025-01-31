from urllib.parse import parse_qs
from typing import Tuple, Dict


def parse_http_request(request_data: str) -> Tuple[str, str, Dict[str, str]]:
    """
    Parses the raw HTTP request into its components.

    Args:
        request_data (str): The raw HTTP request string.

    Returns:
        Tuple[str, str, Dict[str, str]]: (method, path, body), where:
            - method (str): The HTTP method (e.g., "GET", "POST").
            - path (str): The requested path (e.g., "/some-route").
            - body (Dict[str, str]): Parsed form data (for POST or PUT requests).
    """
    lines = request_data.split("\r\n")
    method, path, _ = lines[0].split()
    headers: Dict[str, str] = {}

    # Collect headers
    i = 1
    while lines[i]:
        key, value = lines[i].split(": ", 1)
        headers[key] = value
        i += 1

    # Collect body (if applicable)
    body: Dict[str, str] = {}
    if method in {"POST", "PUT", "PATCH", "DELETE"}:
        raw_body = lines[-1]
        body = {k: v[0] for k, v in parse_qs(raw_body).items()}  # Parse form data into a dictionary

    return method, path, body
