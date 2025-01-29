from routers.v1_Router import V1Router
from servers.v1_RequestParser import parse_http_request
from servers.v1_ResponseBuilder import construct_http_response, http_404_response, http_500_response
import socket
import os
from pathlib import Path
from typing import Type, Optional, Tuple

server_socket: Optional[socket.socket] = None
server_running: bool = False


def get_content_type(file_path: str) -> str:
    """Returns the appropriate Content-Type based on the file extension."""
    ext = Path(file_path).suffix
    return {
        ".html": "text/html",
        ".css": "text/css",
        ".js": "application/javascript",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".svg": "image/svg+xml",
        ".ico": "image/x-icon",
        ".mp4": "video/mp4",
        ".webm": "video/webm",
    }.get(ext, "application/octet-stream")  # Default binary data type

def serve_static_file(file_path: str) -> Tuple[bytes, str, int]:
    """Reads and returns static file contents in binary mode."""
    file_path = os.path.join(file_path.lstrip("/"))

    if os.path.exists(file_path) and os.path.isfile(file_path):
        try:
            with open(file_path, "rb") as file:  # Read in binary mode
                file_data = file.read()
            content_type = get_content_type(file_path)
            return file_data, content_type, 200
        except Exception as e:
            print(f"Error reading static file {file_path}: {e}")
            return b"Internal Server Error", "text/plain", 500
    else:
        return b"File Not Found", "text/plain", 404


def run_server(router: Type[V1Router], host: str = "127.0.0.1", port: int = 8080) -> None:
    """Runs the HTTP server, handling requests and responding accordingly."""
    global server_socket, server_running
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((host, port))
        server_socket.listen(5)
        server_running = True

        print(f"Server started at http://{host}:{port} (Press CTRL+C to stop)")

        while server_running:
            client_socket, client_address = server_socket.accept()
            print(f"Connection from {client_address}")

            with client_socket:
                try:
                    request_data = client_socket.recv(1024).decode("utf-8", errors="ignore")
                    method, path, body = parse_http_request(request_data)

                    # Handle static file requests
                    if path.startswith("/static/"):
                        file_data, content_type, status_code = serve_static_file(path)
                        response = construct_http_response(status_code, file_data, content_type)
                    else:
                        try:
                            response_body = router.route(path, method=method, **body)
                            
                            # Ensure response body is bytes
                            if isinstance(response_body, str):
                                response_body = response_body.encode("utf-8")
                            
                            response = construct_http_response(200, response_body, "text/html")
                        except ValueError:
                            print(f"Resource {path} not found.")
                            response = http_404_response()
                        except Exception as e:
                            print(f"Internal server error: {e}")
                            response = http_500_response()

                except Exception as e:
                    print(f"Failed to process request: {e}")
                    response = http_500_response()

                client_socket.sendall(response)  # Send as raw bytes

    except KeyboardInterrupt:
        print("\nShutting down server...")
    except Exception as e:
        print(f"Server error: {e}")
    finally:
        server_socket.close()


def start_http_server(router: Type[V1Router], host: str = "127.0.0.1", port: int = 8080) -> None:
    """Starts the HTTP server and allows graceful shutdown with KeyboardInterrupt."""
    run_server(router, host, port)
