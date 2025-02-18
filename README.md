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

### 1.1 **Controllers (`v1_controller.py`)**
The `V1AbstractController` class enforces a structured approach to controllers while allowing flexibility in defining CRUD operations.

#### How It Works
- All controllers **inherit** from `V1AbstractController` and must implement `__init__`.
- A controller method processes input and **returns a response** as a `string: kwargs`, which is passed to the view.

#### Example:
```python
from controllers.v1_Controller import V1AbstractController

class HelloController(V1AbstractController):
    def __init__(self):
        pass
    
    def hello(self, **kwargs):
        return "Hello, World!"
```

---

### 1.2 **Logging (`v1_logging.py`)**
The logging module provides structured logs for debugging and monitoring.

#### Features:
- Captures **errors, warnings, and informational logs**.
- Logs are stored in `error.log`, `info.log`, and `warning.log` files.

---

### 1.3 **Transaction Management (`v1_transaction.py`)**
Handles atomic data operations to maintain integrity.

#### Features:
- **Begin, commit, and rollback transactions**.
- **Ensures data consistency** when multiple operations are performed.

---

### 1.4 **Validation (`v1_validation.py`)**
Provides input validation for key-value pairs.

#### Features:
- Ensures **keys and values** conform to specific rules.
- Validates **emails, phone numbers, and URLs**.

---

### 1.5 **Routing (`v1_router.py`)**
Maps URLs to controllers and views dynamically.

#### How It Works
- The router connects **an incoming request** to a specific **controller action**.
- The controller's response is **passed as a `kwarg`** to the assigned view.

#### Example:
```python
router = V1Router()
router.add_route("/hello", HelloController, "hello", HelloView)
```

---

### 1.6 **View Layer (`v1_view.py`)**
Handles rendering JSON and HTML templates.

#### How It Works
- Views **inherit** from `V1BaseView` and must implement `__init__`.
- The **controller response** is received as a `kwarg` and processed.
- The view **must return a response**, or no content will be displayed.

#### Example:
```python
from views.v1_View import V1BaseView

class HelloView(V1BaseView):
    def __init__(self):
        pass
    
    def render(self, controller_response):
        return f"<h1>{controller_response}</h1>"
```

---

### 1.7 **HTTP Server (`v1_httpserver.py`)**
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
class HelloController(V1AbstractController):
    def __init__(self):
        pass
    
    def hello(self, **kwargs):
        return "Hello, World!"
```

### Step 2: Define a View
Create a view that handles rendering the response.
```python
class HelloView(V1BaseView):
    def __init__(self):
        pass
    
    def render(self, controller_response):
        return f"<h1>{controller_response}</h1>"
```

### Step 3: Register the Route
Define the route in the `v1_router.py` file.
```python
router = V1Router()
router.add_route("/hello", HelloController, "hello", HelloView)
```

### Step 4: Start the Server
Run the following command to start the server:
```
python -m servers.v1_runserver
```

### Step 5: Register the Routes
Before starting the server, ensure you run the file responsible for registering routes:
```
python path/to/your/route_registration_file.py
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




# Note to run tests for each compartment
```bash
    echo "" > v1_model.json
    pytest models/tests/ routers/tests/
```
