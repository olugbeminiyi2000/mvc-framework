from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from flask_socketio import SocketIO
import os
import json
import subprocess
import signal
import psutil
from typing import Dict, List, Optional
import threading
import queue
import logging
import importlib.util
import requests
import sys
import pickle

# Global list to store all logs
flask_app_logs: List[str] = []

class FlaskLogHandler(logging.Handler):
    def emit(self, record):
        flask_app_logs.append(self.format(record))

# Ensure the mvc-framework root is in sys.path for module imports
mvc_framework_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if mvc_framework_root not in sys.path:
    sys.path.insert(0, mvc_framework_root)

from routers.v1_Router import V1Router # Import V1Router class

app = Flask(__name__)
# Configure CORS to allow requests from React development server
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})
socketio = SocketIO(app, cors_allowed_origins="http://localhost:3000")

# Configure Flask logging to capture all output
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# Clear existing handlers to prevent duplicate output, then add custom handler
for handler in list(logger.handlers):
    logger.removeHandler(handler)
for handler in list(app.logger.handlers):
    app.logger.removeHandler(handler)

app.logger.addHandler(FlaskLogHandler())
logger.addHandler(FlaskLogHandler())

# Optionally, also capture stdout/stderr to Flask's logger
class StreamToLogger(object):
    """Fake file-like stream object that redirects writes to a logger instance."""
    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            if line.strip(): # Avoid logging empty lines
                self.logger.log(self.log_level, line.rstrip())

    def flush(self):
        pass

sys.stdout = StreamToLogger(logger, logging.INFO)
sys.stderr = StreamToLogger(logger, logging.ERROR)

global_mvc_server_process: Optional[Dict] = None
# global_mvc_log_queue: Optional[queue.Queue] = None # This will be removed as logs are now global

@app.route('/')
def serve():
    """Serve the React application."""
    # This is no longer needed as React app is served separately
    return jsonify({'message': 'Flask server is running'})

@app.route('/<path:path>')
def static_proxy(path):
    """Serve static files."""
    # This is no longer needed as React app is served separately
    return jsonify({'message': 'Flask server is running'})

def get_webapp_path(name: str) -> str:
    """Get the absolute path to a webapp directory."""
    return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'projects', name)

def get_webapp_files(name: str) -> Dict[str, List[Dict]]:
    """Get all files in a webapp directory."""
    webapp_path = get_webapp_path(name)
    if not os.path.exists(webapp_path):
        return {'models': [], 'views': [], 'controllers': [], 'router': None, 'init': None}

    files = {
        'models': [],
        'views': [],
        'controllers': [],
        'router': None,
        'init': None
    }

    for root, _, filenames in os.walk(webapp_path):
        for filename in filenames:
            if filename.endswith('.py'):
                file_path = os.path.join(root, filename)
                rel_path = os.path.relpath(file_path, webapp_path)

                if rel_path == 'model.py':
                    file_info = {'name': filename, 'path': rel_path, 'type': 'model'}
                    files['models'].append(file_info)
                elif rel_path == 'view.py':
                    file_info = {'name': filename, 'path': rel_path, 'type': 'view'}
                    files['views'].append(file_info)
                elif rel_path == 'controller.py':
                    file_info = {'name': filename, 'path': rel_path, 'type': 'controller'}
                    files['controllers'].append(file_info)
                elif rel_path == 'router.py':
                    file_info = {'name': filename, 'path': rel_path, 'type': 'router'}
                    files['router'] = file_info
                elif rel_path == '__init__.py':
                    file_info = {'name': filename, 'path': rel_path, 'type': 'init'}
                    files['init'] = file_info

    return files

def get_routes(name: str) -> List[Dict]:
    """Get all registered routes for a webapp."""
    webapp_path = get_webapp_path(name)
    router_path = os.path.join(webapp_path, 'router.py')
    
    if not os.path.exists(router_path):
        logger.warning(f"Router file not found for {name}: {router_path}") # Debug print
        return []

    try:
        # Add the root of the MVC framework to sys.path temporarily
        mvc_framework_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        if mvc_framework_root not in sys.path:
            sys.path.insert(0, mvc_framework_root)
        
        # Dynamically load the router module
        router_spec = importlib.util.spec_from_file_location("webapp_router", router_path)
        router_module = importlib.util.module_from_spec(router_spec) # type: ignore
        router_spec.loader.exec_module(router_module) # type: ignore

        # Find the V1Router instance in the loaded module
        router_instance = None
        for attr_name in dir(router_module):
            attr = getattr(router_module, attr_name)
            if isinstance(attr, type) and attr.__name__ == 'V1Router':
                # If it's the class itself, try to find an instance
                for inst_name in dir(router_module):
                    inst = getattr(router_module, inst_name)
                    if isinstance(inst, attr):
                        router_instance = inst
                        break
            elif isinstance(attr, object) and hasattr(attr, 'routes'): # A more general check for the router instance
                router_instance = attr
                break

        if not router_instance:
            logger.error(f"No V1Router instance found in router.py for {name}")
            return []

        # Debug: Check the routes loaded by the V1Router instance
        logger.info(f"[APP.PY:get_routes] Router instance routes for {name}: {router_instance.routes.keys()}")

        routes = []
        for path, (controller, action, view, method) in router_instance.routes.items(): # type: ignore
            # Filter routes by webapp_name based on controller/view module path
            # Assuming module names are like 'projects.webapp_name.controller'
            controller_module = controller.__module__
            if controller_module.startswith(f'projects.{name}.'):
                routes.append({
                    'path': path,
                    'method': method,  # Use the actual method from the router
                    'controller': controller.__name__,
                    'action': action,
                    'view': view.__name__
                })
        return routes
    except Exception as e:
        logger.error(f"Error getting routes for {name}: {e}")
        return []
    finally:
        # Clean up sys.path to prevent conflicts
        if mvc_framework_root in sys.path:
            sys.path.remove(mvc_framework_root)

def start_server(name: str) -> Optional[int]:
    """Start the MVC server."""
    global global_mvc_server_process

    if global_mvc_server_process and psutil.pid_exists(global_mvc_server_process['pid']):
        logger.info(f"MVC server is already running with PID {global_mvc_server_process['pid']}.")
        return global_mvc_server_process['pid']

    mvc_framework_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    if not os.path.exists(os.path.join(mvc_framework_root, 'servers', 'v1_runserver.py')):
        logger.error(f"Cannot find v1_runserver.py at {os.path.join(mvc_framework_root, 'servers', 'v1_runserver.py')}")
        return None

    try:
        logger.info("Attempting to start MVC server...")
        process = subprocess.Popen(
            ['python', '-u', '-m', 'servers.v1_runserver'], # Use -u for unbuffered output
            cwd=mvc_framework_root,
            stdout=subprocess.PIPE, # Re-enable stdout capture
            stderr=subprocess.STDOUT, # Re-enable stderr capture
            text=True,
            bufsize=1 # Line-buffered output
        )

        # Re-introduce log reading thread to pipe subprocess stdout to Flask logs
        def read_subprocess_logs():
            logger.info("Subprocess log reading thread started.")
            for line in iter(process.stdout.readline, ''):
                if line:
                    # Append subprocess output directly to Flask's global log list
                    flask_app_logs.append(f"[MVC_SERVER_SUBPROCESS] {line.strip()}")
            process.stdout.close()
            logger.info("Subprocess log reading thread finished.")

        threading.Thread(target=read_subprocess_logs, daemon=True).start()

        global_mvc_server_process = {
            'pid': process.pid,
            'process': process
        }
        logger.info(f"MVC server started with PID: {process.pid} from {mvc_framework_root}")
        return process.pid
    except Exception as e:
        logger.error(f"Error starting MVC server: {e}")
        global_mvc_server_process = None # Clear state on failure
        return None

def stop_server(name: str) -> bool: # 'name' parameter will be ignored for global server
    """Stop the MVC server."""
    global global_mvc_server_process

    logger.info(f"[stop_server] Called. Current global_mvc_server_process: {global_mvc_server_process}")

    if not global_mvc_server_process or not psutil.pid_exists(global_mvc_server_process['pid']):
        logger.info("MVC server is not running or already stopped. No process to stop.")
        global_mvc_server_process = None
        return False

    try:
        process = global_mvc_server_process['process']
        pid = global_mvc_server_process['pid']
        logger.info(f"[stop_server] Attempting to stop MVC server with PID {pid}...")
        process.terminate()
        try:
            process.wait(timeout=5)
            logger.info(f"[stop_server] MVC server with PID {pid} terminated gracefully.")
        except subprocess.TimeoutExpired:
            logger.warning(f"[stop_server] MVC server with PID {pid} did not terminate gracefully. Attempting to kill...")
            process.kill()
            process.wait(timeout=5)
            logger.info(f"[stop_server] MVC server with PID {pid} killed.")
        
        global_mvc_server_process = None
        logger.info(f"[stop_server] Global MVC server process state cleared for PID {pid}.")
        return True
    except Exception as e:
        logger.error(f"[stop_server] Error stopping MVC server with PID {global_mvc_server_process.get('pid', 'N/A')}: {e}")
        return False

def get_server_status(name: str) -> Dict: # 'name' parameter will be ignored for global server
    """Get MVC server status."""
    global global_mvc_server_process, flask_app_logs

    logger.info(f"Checking server status. Process state: {global_mvc_server_process}")

    # Always return current logs from flask_app_logs
    current_logs = list(flask_app_logs)

    if not global_mvc_server_process:
        logger.info("No global MVC server process recorded.")
        return {
            'isRunning': False,
            'logs': current_logs
        }

    try:
        process = global_mvc_server_process['process']
        if process.poll() is not None:  # Process has terminated
            logger.warning(f"MVC server process (PID {global_mvc_server_process['pid']}) has terminated. Clearing state.")
            global_mvc_server_process = None
            return {
                'isRunning': False,
                'logs': current_logs + ["Server process terminated unexpectedly."]
            }

        # Process is running
        return {
            'isRunning': True,
            'pid': global_mvc_server_process['pid'],
            'port': 8080, # MVC server runs on 8080 as per README
            'logs': current_logs
        }
    except psutil.NoSuchProcess:
        logger.warning(f"MVC server process (PID {global_mvc_server_process['pid']}) no longer exists. Clearing state.")
        global_mvc_server_process = None
        return {
            'isRunning': False,
            'logs': current_logs + ["Server process not found or crashed."]
        }
    except Exception as e:
        logger.error(f"Error getting MVC server status: {e}")
        return {
            'isRunning': False,
            'logs': current_logs + [f"Error retrieving status: {e}"]
        }

@app.route('/api/webapps', methods=['GET'])
def get_webapps():
    """Get all webapps."""
    projects_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'projects')
    if not os.path.exists(projects_dir):
        return jsonify([])

    webapps = []
    for name in os.listdir(projects_dir):
        if os.path.isdir(os.path.join(projects_dir, name)):
            files = get_webapp_files(name)
            webapps.append({
                'name': name,
                'path': os.path.join('projects', name),
                **files
            })

    return jsonify(webapps)

@app.route('/api/webapps', methods=['POST'])
def create_webapp():
    """Create a new webapp."""
    data = request.get_json()
    name = data.get('name')
    
    if not name:
        return jsonify({'error': 'Name is required'}), 400

    webapp_path = get_webapp_path(name)
    if os.path.exists(webapp_path):
        return jsonify({'error': 'Webapp already exists'}), 400

    try:
        # Create webapp directory
        os.makedirs(webapp_path)

        # Create empty __init__.py, model.py, view.py, controller.py, router.py
        with open(os.path.join(webapp_path, '__init__.py'), 'w') as f:
            pass
        with open(os.path.join(webapp_path, 'model.py'), 'w') as f:
            f.write("# Define your models here\n")
        with open(os.path.join(webapp_path, 'view.py'), 'w') as f:
            f.write("# Define your views here\n")
        with open(os.path.join(webapp_path, 'controller.py'), 'w') as f:
            f.write("# Define your controllers here\n")
        with open(os.path.join(webapp_path, 'router.py'), 'w') as f:
            f.write("# Define your routes here\n")

        return jsonify({
            'name': name,
            'path': os.path.join('projects', name),
            'models': [{'name': 'model.py', 'path': 'model.py', 'type': 'model'}],
            'views': [{'name': 'view.py', 'path': 'view.py', 'type': 'view'}],
            'controllers': [{'name': 'controller.py', 'path': 'controller.py', 'type': 'controller'}],
            'router': {'name': 'router.py', 'path': 'router.py', 'type': 'router'},
            'init': {'name': '__init__.py', 'path': '__init__.py', 'type': 'init'}
        })
    except Exception as e:
        logger.error(f"Error creating webapp {name}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/files/content', methods=['GET'])
def get_file_content():
    """Get file content."""
    path = request.args.get('path')
    webapp_name = request.args.get('webapp')

    if not path or not webapp_name:
        return jsonify({'error': 'File path and webapp name are required'}), 400

    webapp_path = get_webapp_path(webapp_name)
    full_file_path = os.path.join(webapp_path, path)

    if not os.path.exists(full_file_path):
        return jsonify({'error': 'File not found'}), 404

    try:
        with open(full_file_path, 'r') as f:
            content = f.read()
        return jsonify(content)
    except Exception as e:
        logger.error(f"Error reading file {full_file_path}: {e}")
        return jsonify({'error': f'Error reading file: {e}'}), 500

@app.route('/api/files/content', methods=['POST'])
def save_file_content():
    """Save file content."""
    data = request.get_json()
    path = data.get('path')
    content = data.get('content')
    webapp_name = data.get('webapp') # Assuming webapp name is also sent for saving

    if not path or content is None or not webapp_name:
        return jsonify({'error': 'File path, content, and webapp name are required'}), 400

    webapp_path = get_webapp_path(webapp_name)
    full_file_path = os.path.join(webapp_path, path)

    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(full_file_path), exist_ok=True)
        with open(full_file_path, 'w') as f:
            f.write(content)
        return jsonify({'message': 'File saved successfully'})
    except Exception as e:
        logger.error(f"Error saving file {full_file_path}: {e}")
        return jsonify({'error': f'Error saving file: {e}'}), 500

@app.route('/api/routes', methods=['GET'])
def get_routes_api():
    """Get routes for a webapp."""
    webapp = request.args.get('webapp')
    if not webapp:
        return jsonify({'error': 'Webapp name is required'}), 400

    routes = get_routes(webapp)
    return jsonify(routes)

@app.route('/api/routes/test', methods=['POST'])
def test_route():
    """Test a route by simulating an HTTP request."""
    data = request.get_json()
    logger.info(f"Received test route request: {data}") # Debug print
    webapp_name = data.get('webapp')
    req_data = data.get('request')

    if not webapp_name or not req_data:
        logger.warning(f"Missing webapp name or request data. webapp_name: {webapp_name}, req_data: {req_data}") # Debug print
        return jsonify({'error': 'Webapp name and request data are required'}), 400

    # Ensure the global MVC server is running
    if not global_mvc_server_process or not psutil.pid_exists(global_mvc_server_process['pid']):
        logger.warning("MVC framework server is not running.") # Debug print
        return jsonify({'error': 'The MVC framework server is not running. Please start it from Server Management.'}), 400

    # The path to test on the MVC framework server
    path = req_data.get('path')
    method = req_data.get('method', 'GET') # Default to GET

    # The port is always 8080 for the single MVC server
    app_port = 8080 
    full_url = f'http://localhost:{app_port}{path}'

    try:
        headers = req_data.get('headers', {})
        request_body = req_data.get('body', None)

        if request_body and not isinstance(request_body, str):
            # Assume JSON body if not string, and serialize it
            request_body = json.dumps(request_body)
            headers['Content-Type'] = 'application/json'

        # Make the actual HTTP request to the running web app
        print(full_url)
        response = requests.request(method, full_url, headers=headers, data=request_body)
        print(response)

        # Extract response data
        response_status = response.status_code
        response_headers = dict(response.headers)
        content_type = response_headers.get('Content-Type')
        
        # Try to parse response body as JSON, otherwise keep as text
        try:
            response_body_content = response.json()
        except json.JSONDecodeError:
            response_body_content = response.text
        
        # Always set view_output if the response was successful, regardless of content type
        view_output = response.text if response.ok else None

        http_response = {
            'status': response_status,
            'headers': response_headers,
            'body': response_body_content,
            'viewOutput': view_output,
            'contentType': content_type # Pass content type to frontend
        }
        return jsonify(http_response)

    except requests.exceptions.ConnectionError:
        return jsonify({'error': f'Could not connect to MVC framework server at {full_url}. Is it running and accessible?'}), 503
    except Exception as e:
        logger.error(f"Error testing route for {webapp_name} via HTTP request: {e}")
        return jsonify({'error': f'Failed to test route via HTTP: {str(e)}'}), 500

@app.route('/api/server/status', methods=['GET'])
def get_server_status_api():
    """API endpoint to get MVC server status."""
    # 'webapp_name' from frontend is currently ignored for global server
    status = get_server_status(request.args.get('webapp_name', ''))
    return jsonify(status)

@app.route('/api/server/start', methods=['POST'])
def start_server_api():
    """Start the server."""
    data = request.get_json()
    webapp = data.get('webapp')
    pid = start_server(webapp) # Call the global start function
    if not pid:
        return jsonify({'error': 'Failed to start server'}), 500
    return jsonify({'success': True, 'pid': pid})

@app.route('/api/server/stop', methods=['POST'])
def stop_server_api():
    """Stop the server."""
    data = request.get_json()
    webapp = data.get('webapp')
    if stop_server(webapp): # Call the global stop function
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Failed to stop server'}), 500

@app.route('/api/server/restart', methods=['POST'])
def restart_server_api():
    """Restart the server."""
    data = request.get_json()
    webapp = data.get('webapp')
    logger.info(f"[restart_server_api] Restart requested for webapp: {webapp}") # Debug
    logger.info(f"[restart_server_api] Calling stop_server... Current global_mvc_server_process BEFORE stop: {global_mvc_server_process}") # Debug
    stop_result = stop_server(webapp) # Call global stop
    logger.info(f"[restart_server_api] stop_server returned: {stop_result}. Current global_mvc_server_process AFTER stop: {global_mvc_server_process}") # Debug
    pid = start_server(webapp) # Call global start
    logger.info(f"[restart_server_api] start_server returned PID: {pid}") # Debug
    if not pid:
        return jsonify({'error': 'Failed to restart server'}), 500
    return jsonify({'success': True, 'pid': pid})

@app.route('/api/routes/register', methods=['POST'])
def register_webapp_routes_api():
    """Register routes for a specific webapp."""
    data = request.get_json()
    webapp_name = data.get('webapp')

    if not webapp_name:
        return jsonify({'error': 'Webapp name is required'}), 400

    mvc_framework_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    router_state_path = os.path.join(mvc_framework_root, 'router_state.pkl')
    webapp_path = os.path.join(mvc_framework_root, 'projects', webapp_name)
    webapp_router_file = os.path.join(webapp_path, 'router.py')

    if not os.path.exists(webapp_router_file):
        return jsonify({'error': f'Router file not found for webapp {webapp_name} at {webapp_router_file}'}), 404

    try:
        # Load the central V1Router instance
        central_router = V1Router(file_path=router_state_path)
        
        # Add projects directory to sys.path to allow webapp router.py to import its modules
        if mvc_framework_root not in sys.path:
            sys.path.insert(0, mvc_framework_root)

        # Dynamically load the webapp's router.py
        spec = importlib.util.spec_from_file_location(f"projects.{webapp_name}.router_module_temp", webapp_router_file)
        module = importlib.util.module_from_spec(spec) # type: ignore
        sys.modules[spec.name] = module # type: ignore
        spec.loader.exec_module(module) # type: ignore

        # Find the V1Router instance created by the webapp's router.py
        webapp_router_instance = None
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, V1Router):
                webapp_router_instance = attr
                break
        
        if not webapp_router_instance:
            raise ValueError(f"No V1Router instance found in {webapp_name}/router.py. Please ensure it instantiates V1Router.")

        # Merge routes from webapp's router into the central router
        registered_count = 0
        for path, (controller, action, view, method) in webapp_router_instance.routes.items(): # type: ignore
            try:
                # Use the add_route of the central router to ensure persistence
                central_router.add_route(path, controller, action, view, method)
                registered_count += 1
            except Exception as e:
                logger.warning(f"Could not register route {method} {path} from {webapp_name}: {e}")

        return jsonify({
            'success': True,
            'message': f'Successfully registered {registered_count} routes for {webapp_name}.',
            'registered_routes': list(central_router.routes.keys())
        })

    except Exception as e:
        logger.error(f"Error registering routes for {webapp_name}: {e}")
        return jsonify({'error': f'Failed to register routes: {str(e)}'}), 500
    finally:
        # Clean up sys.path
        if mvc_framework_root in sys.path:
            sys.path.remove(mvc_framework_root)

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000) 