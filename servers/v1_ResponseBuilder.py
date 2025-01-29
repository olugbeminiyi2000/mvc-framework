def construct_http_response(status_code: int, body: bytes, content_type: str = "text/html") -> bytes:
    """
    Constructs a full HTTP response for both text and binary data.

    Args:
        status_code (int): The HTTP status code (e.g., 200, 404).
        body (bytes): The response body (can be binary).
        content_type (str): The content type of the response.

    Returns:
        bytes: The formatted HTTP response.
    """
    status_messages = {200: "OK", 404: "Not Found", 500: "Internal Server Error"}
    status_message = status_messages.get(status_code, "Unknown Status")

    headers = (
        f"HTTP/1.1 {status_code} {status_message}\r\n"
        f"Content-Type: {content_type}\r\n"
        f"Content-Length: {len(body)}\r\n"
        "Connection: close\r\n\r\n"
    ).encode("utf-8")  # Convert headers to bytes

    return headers + body  # Append headers and binary body



def http_404_response():
    """Returns a 404 Not Found response."""
    body = "<h1>404 Not Found</h1><p>The requested resource was not found.</p>"
    return construct_http_response(404, body)


def http_500_response():
    """Returns a 500 Internal Server Error response."""
    body = "<h1>500 Internal Server Error</h1><p>Something went wrong.</p>"
    return construct_http_response(500, body)
