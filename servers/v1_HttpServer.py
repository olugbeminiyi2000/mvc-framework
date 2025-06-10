import os
from pathlib import Path
import re
from routers.v1_Router import V1Router
from servers.v1_RequestParser import parse_http_request
from servers.v1_ResponseBuilder import construct_http_response, http_404_response, http_500_response
from servers.v1_UploadToServer import handle_file_uploads
import socket
import signal
from typing import Type, Optional, Tuple

server_socket: Optional[socket.socket] = None
server_running: bool = False

def stop_http_server():
    """Stop the HTTP server gracefully."""
    global server_running, server_socket
    print("[HTTP_SERVER] Stopping server...", flush=True)
    server_running = False
    if server_socket:
        try:
            server_socket.close()
            print("[HTTP_SERVER] Server socket closed.", flush=True)
        except Exception as e:
            print(f"[HTTP_SERVER] Error closing server socket: {e}", flush=True)
        finally:
            server_socket = None

def signal_handler(signum, frame):
    """Handle termination signals."""
    print("\n[HTTP_SERVER] Received termination signal. Shutting down server...", flush=True)
    stop_http_server()

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C
signal.signal(signal.SIGTERM, signal_handler)  # Termination signal

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
            print(f"Error reading static file {file_path}: {e}", flush=True)
            return b"Internal Server Error", "text/plain", 500
    else:
        return b"File Not Found", "text/plain", 404


def read_full_request(client_socket: socket.socket) -> str:
    """Reads the full HTTP request from the client socket."""
    request_data = b""
    
    # Read headers first
    while True:
        chunk = client_socket.recv(1024)
        if not chunk:
            break
        request_data += chunk
        
        # Check for end of headers
        if b"\r\n\r\n" in request_data:
            break

    # Decode headers and extract Content-Length
    headers, _, body = request_data.partition(b"\r\n\r\n")
    headers_str = headers.decode("utf-8", errors="ignore")
    
    # Extract Content-Length
    content_length_match = re.search(r"Content-Length: (\d+)", headers_str)
    content_length = int(content_length_match.group(1)) if content_length_match else 0
    
    # Read remaining body based on Content-Length
    while len(body) < content_length:
        chunk = client_socket.recv(content_length - len(body))
        if not chunk:
            break
        body += chunk

    return (headers + b"\r\n\r\n" + body).decode("utf-8", errors="ignore")


def run_server(router: Type[V1Router], host: str = "127.0.0.1", port: int = 8080) -> None:
    """Runs the HTTP server, handling requests and responding accordingly."""
    global server_socket, server_running
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow reuse of the address
        server_socket.bind((host, port))
        server_socket.listen(5)
        server_socket.settimeout(1)  # Set a 1-second timeout for accept()
        server_running = True

        print(f"[HTTP_SERVER] Server started at http://{host}:{port} (Press CTRL+C to stop)", flush=True)

        while server_running:
            try:
                client_socket, client_address = server_socket.accept()
                print(f"[HTTP_SERVER] Connection from {client_address}", flush=True)

                with client_socket:
                    try:
                        # Read full request data
                        request_data = read_full_request(client_socket)
                        if not request_data:  # Skip empty requests
                            continue
                            
                        method, path, body = parse_http_request(request_data)
                        
                        # Skip requests with empty method or path
                        if not method or not path:
                            continue

                        print(f"[HTTP_SERVER] Received request: Method={method}, Path={path}, Body={body.keys()}", flush=True) # Debug print

                        # Handle file uploads and delete the raw byte
                        handle_file_uploads(body)
                        
                        # Handle static file requests
                        if path.startswith("/static/"):
                            file_data, content_type, status_code = serve_static_file(path)
                            response = construct_http_response(status_code, file_data, content_type)
                        else:
                            try:
                                # Pass the method to the router.route method
                                response_body_str, response_content_type = router.route(path, method=method, **body)
                                print(f"[HTTP_SERVER] Route successful for Path={path}, Method={method}, Content-Type={response_content_type}", flush=True) # Debug print

                                # Ensure response body is bytes
                                if isinstance(response_body_str, str):
                                    response_body = response_body_str.encode("utf-8")
                                else:
                                    response_body = response_body_str # Already bytes if from a file for example

                                response = construct_http_response(200, response_body, response_content_type)
                            except ValueError as ve:
                                print(f"[HTTP_SERVER] Route error (ValueError): {ve}", flush=True) # Debug print
                                response = http_404_response()
                            except Exception as e:
                                print(f"[HTTP_SERVER] Internal server error during routing: {e}", flush=True) # Debug print
                                response = http_500_response()

                    except Exception as e:
                        print(f"[HTTP_SERVER] Failed to process request: {e}", flush=True) # Debug print
                        response = http_500_response()

                    client_socket.sendall(response)  # Send as raw bytes
            except socket.timeout:
                # This is expected due to the non-blocking socket
                continue
            except Exception as e:
                if server_running:  # Only print error if we're still supposed to be running
                    print(f"[HTTP_SERVER] Error accepting connection: {e}", flush=True)
                continue

    except KeyboardInterrupt:
        print("\n[HTTP_SERVER] Shutting down server...")
        stop_http_server()
    except Exception as e:
        print(f"[HTTP_SERVER] Server error: {e}", flush=True)
        stop_http_server()


def start_http_server(router: Type[V1Router], host: str = "127.0.0.1", port: int = 8080) -> None:
    """Starts the HTTP server and allows graceful shutdown with KeyboardInterrupt."""
    run_server(router, host, port)
