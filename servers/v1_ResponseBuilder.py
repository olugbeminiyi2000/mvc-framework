def construct_http_response(status_code, body):
    """
    Constructs a full HTTP response.

    Args:
        status_code (int): The HTTP status code (e.g., 200, 404).
        body (str): The response body.
        content_type (str): The content type of the response.

    Returns:
        str: The formatted HTTP response.
    """
    response = (
        f"HTTP/1.1 {status_code} OK\r\n"
        f"Content-Length: {len(body)}\r\n"
        f"\r\n"
        f"{body}"
    )
    return response


def http_404_response():
    """Returns a 404 Not Found response."""
    body = "<h1>404 Not Found</h1><p>The requested resource was not found.</p>"
    return construct_http_response(404, body)


def http_500_response():
    """Returns a 500 Internal Server Error response."""
    body = "<h1>500 Internal Server Error</h1><p>Something went wrong.</p>"
    return construct_http_response(500, body)
