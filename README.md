# Documentation for V1 MVC Framework

## Introduction

The **V1 MVC Framework** was developed as a personal project to help understand the **Model-View-Controller (MVC)** architecture by building a small-scale version. The primary goal was to explore the processes involved in structuring an MVC-based application, including routing, request handling, data validation, transactions, and rendering views. This framework serves as a hands-on learning tool to deepen understanding of how MVC components interact.

### Why This Framework?
- **Hands-on MVC Understanding:** Built to explore how small-scale MVC applications work.
- **Lightweight and Modular:** Each component is independent, making it easy to extend.
- **Practical Learning:** Focuses on applying theoretical MVC concepts in a structured manner.

This documentation details the core components of the framework and demonstrates how to build a simple web application using it.

---

## 1. Framework Components

### 1.1 **Controllers (`v1_Controller.py`)**
The `V1AbstractController` class enforces a structured approach to controllers while allowing flexibility in defining CRUD operations.

#### How It Works
- All controllers **inherit** from `V1AbstractController` and must implement `__init__`.
- A controller method processes the data received from the body(**kwargs**) of the request and **returns a response**, which is passed to the view, as a kwargs `controller_response=response`.

---

### 1.2 **Logging (`v1_Logging.py`)**
The logging module provides structured logs for debugging and monitoring.

#### Features:
- Captures **errors, warnings, and informational logs**.
- Logs are stored in `error.log`, `info.log`, and `warning.log` files.

---

### 1.3 **Transaction Management (`v1_Transaction.py`)**
Handles atomic data operations to maintain integrity.

#### Features:
- **Begin, commit, and rollback transactions**.
- **Ensures data consistency** when multiple operations are performed.

---

### 1.4 **Validation (`v1_Validation.py`)**
Provides input validation for key-value pairs.

#### Features:
- Ensures **keys and values** conform to specific rules.
- Validates **emails, phone numbers, and URLs**.

---

### 1.5 **Model (`v1_Model.py`)**
Manages application data and enforces validation rules.

#### Features:
- **CRUD operations** for structured data storage.
- **Persistent storage** using JSON.
- **Custom validation rules** for flexible data integrity enforcement.

---

### 1.6 **Routing (`v1_Router.py`)**
Maps URLs to controllers and views dynamically.

#### How It Works
- The router connects **an incoming request** to a specific **controller action**.
- The controller's response is **passed as a `kwarg`** to the assigned view.

---

### 1.7 **View Layer (`v1_View.py`)**
Handles rendering JSON and HTML templates.

#### How It Works
- Views **inherit** from `V1BaseView` and must implement `__init__`.
- The **controller response** is received as a `kwarg` and processed.
- The view **must return a response**, or no content will be displayed.

---

### 1.8 **HTTP Request Parsing (`v1_RequestParser.py`)**
Extracts relevant data from incoming HTTP requests.

#### Features:
- **Parses GET and POST data**.
- **Handles file uploads**.
- **Validates headers** to ensure proper request format.

---

### 1.9 **Response Builder (`v1_ResponseBuilder.py`)**
Constructs structured HTTP responses for client requests.

#### Features:
- **Supports status codes** (`200`, `404`, `500`).
- **Handles binary and text responses**.
- **Automatically sets correct headers** for content type.

---

### 1.10 **File Upload Handling (`v1_UploadToServer.py`)**
Processes and saves uploaded files to a structured directory.

#### Features:
- **Categorizes files by extension** for organized storage.
- **Ensures secure file handling** by preventing unwanted overwrites.

---

### 1.11 **HTTP Server (`v1_HttpServer.py`)**
Acts as a lightweight web server to process requests.

#### Features:
- **Handles incoming HTTP requests**.
- **Serves static files** (CSS, JS, images).
- **Routes requests to the appropriate controller**.

---

## 2. Building a Simple Web App

### Step 1: Define a Controller
Create a controller that processes user requests.
```python
# File - webapp_name.hello_controller.py

from controllers.v1_Controller import V1AbstractController

class HelloController(V1AbstractController):
    def __init__(self):
        pass
    
    def hello(self, **kwargs):
        return "Hello, World!"
```

### Step 2: Define a View
Create a view that handles rendering the response.
```python
# File - webapp_name.hello_view.py

from views.v1_View import V1BaseView

class HelloView(V1BaseView):
    def __init__(self):
        pass
    
    def render(self, **kwargs):
        message = kwargs["controller_response"]
        return f"<h1>{message}</h1>"
```

### Step 3: Register the Route
Define the route in the `v1_router.py` file.
```python
# File - webapp_name.hello_router.py

from webapp_name.beta_view import HelloView
from webapp_name.hello_controller import HelloController
from routers.v1_Router import V1Router
router = V1Router()
router.add_route("/hello", HelloController, "hello", HelloView)

```

### Step 4: Register the Routes
Before starting the server, ensure you run the file responsible for registering routes:
```
python -m webapp_name.hello_router
```

### Step 5: Start the Server
Run the following command to start the server:
```
python -m servers.v1_runserver
```

### Step 6: Access the Web App
Run the server and visit `http://127.0.0.1:8080/hello`.

---

## Conclusion
The **V1 MVC Framework** was built as a learning project to explore MVC principles by developing a fully functional small-scale framework. It covers essential features like **routing, transactions, request handling, and views** while maintaining simplicity. This framework serves as an excellent tool for gaining hands-on experience with MVC-based development.

### Understanding the Flow
1. **Client sends a request** → `/hello`.
2. **Router matches the request** and calls `HelloController.hello()`.
3. **Controller processes logic** and returns `"Hello, World!"`.
4. **Router sends the response** to `HelloView.render()` as a `kwarg`.
5. **View processes the response** and returns `"<h1>Hello, World!</h1>"`.
6. **The rendered response is sent** to the client’s browser.

If a **view does not return anything**, no content will be displayed.

This flow ensures a **clear separation of concerns** between routing, controller logic, and rendering views.

