from routers.v1_Router import V1Router
from servers.v1_RequestParser import parse_http_request
from servers.v1_ResponseBuilder import construct_http_response, http_404_response, http_500_response
import socket


def start_http_server(router: V1Router, host: str = "127.0.0.1", port: int = 8080) -> None:
    """
    Starts the HTTP server to handle incoming requests and send responses.
    
    Args:
        router (V1Router): The router instance to handle route resolution.
        host (str): The host address for the server.
        port (int): The port number for the server.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen(5)
        print(f"Server started at http://{host}:{port}")
        
        while True:
            client_socket, client_address = server_socket.accept()
            print(f"Connection from {client_address}")
            
            with client_socket:
                try:
                    request_data: str = client_socket.recv(1024).decode("utf-8")
                    method, path, body = parse_http_request(request_data)
                    print(method, path, body)
                    
                    # Process the route
                    try:
                        response_body: str = router.route(path, method=method, **body)
                        print(response_body)
                        response: str = construct_http_response(200, response_body)
                    except ValueError:
                        response = http_404_response()
                    except Exception as e:
                        print(f"Error: {e}")
                        response = http_500_response()

                except Exception as e:
                    print(f"Failed to process request: {e}")
                    response = http_500_response()
                
                client_socket.sendall(response.encode("utf-8"))
