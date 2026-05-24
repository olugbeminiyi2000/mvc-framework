from routers.v1_Router import V1Router
from servers.v1_HttpServer import start_http_server, stop_http_server
import os
import signal
import sys
import time
# pyrefly: ignore [missing-import]
from watchdog.observers import Observer
# pyrefly: ignore [missing-import]
from watchdog.events import FileSystemEventHandler
import threading

# Ensure the router_state.pkl path is absolute for consistency
router_state_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'router_state.pkl')

# Global variables for server management
server_thread = None
server_running = False

class ServerReloader(FileSystemEventHandler):
    def __init__(self):
        self.last_reload = 0
        self.reload_cooldown = 2  # Minimum seconds between reloads

    def on_modified(self, event):
        print(f"[V1_RUNSERVER_DEBUG] on_modified triggered for: {event.src_path}, is_directory: {event.is_directory}")
        if event.is_directory:
            return
        
        # Only reload on Python file changes
        if not event.src_path.endswith('.py'):
            print(f"[V1_RUNSERVER_DEBUG] Skipping non-Python file: {event.src_path}")
            return

        current_time = time.time()
        if current_time - self.last_reload < self.reload_cooldown:
            print(f"[V1_RUNSERVER_DEBUG] Skipping reload due to cooldown for: {event.src_path}")
            return

        print(f"\n[V1_RUNSERVER] Detected change in {event.src_path}")
        print("[V1_RUNSERVER] Hot reloading server...")
        self.last_reload = current_time
        restart_server()

def server_thread_function():
    """Function to run the server in a separate thread."""
    global server_running
    try:
        print(f"[V1_RUNSERVER] Initializing V1Router with file: {router_state_path}")
        route_router = V1Router(file_path=router_state_path)
        print(f"[V1_RUNSERVER] Router instance created. Registered routes: {route_router.routes.keys()}")
        print("[V1_RUNSERVER] Starting HTTP server...")
        start_http_server(route_router)
    except Exception as e:
        print(f"[V1_RUNSERVER] Server thread error: {e}")
    finally:
        server_running = False

def start_server():
    """Start the server in a separate thread."""
    global server_thread, server_running
    if server_thread and server_thread.is_alive():
        print("[V1_RUNSERVER] Server is already running")
        return

    server_running = True
    server_thread = threading.Thread(target=server_thread_function)
    server_thread.daemon = True  # Make thread daemon so it exits when main thread exits
    server_thread.start()

def restart_server():
    """Restart the server by stopping the current instance and starting a new one."""
    global server_running
    print("[V1_RUNSERVER] Restarting server...")
    stop_http_server()
    time.sleep(1)  # Give a small delay to ensure clean shutdown
    start_server()

def signal_handler(signum, frame):
    """Handle termination signals."""
    print("\n[V1_RUNSERVER] Received termination signal. Shutting down server...")
    stop_http_server()
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C
signal.signal(signal.SIGTERM, signal_handler)  # Termination signal

if __name__ == "__main__":
    # Start the server
    start_server()

    # Set up file watching
    event_handler = ServerReloader()
    observer = Observer()
    
    # Watch the entire project directory
    project_root = os.path.dirname(os.path.dirname(__file__))
    print(f"[V1_RUNSERVER_DEBUG] Watchdog watching directory: {project_root}")
    observer.schedule(event_handler, project_root, recursive=True)
    observer.start()

    print("\n[V1_RUNSERVER] Hot reload enabled. Server will automatically restart when Python files change.")
    print("  - Ctrl+C: Stop server")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        observer.join()