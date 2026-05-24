![Python](https://img.shields.io/badge/Python-90%25-brightgreen.svg)
![HTML](https://img.shields.io/badge/HTML-10%25-yellow.svg)
![Contributors](https://img.shields.io/badge/contributors-2-orange.svg)

# Documentation for V1 MVC Framework

## Introduction

The **V1 MVC Framework** was developed as a personal project to help understand the **Model-View-Controller (MVC)** architecture by building a small-scale version. The primary goal was to explore the processes involved in structuring an MVC-based application, including routing, request handling, data validation, transactions, and rendering views. This framework serves as a hands-on learning tool to deepen understanding of how MVC components interact.

### Why This Framework?
- **Hands-on MVC Understanding:** Built to explore how small-scale MVC applications work.
- **Lightweight and Modular:** Each component is independent, making it easy to extend.
- **Practical Learning:** Focuses on applying theoretical MVC concepts in a structured manner.

This documentation details the core components of the framework and demonstrates how to build a simple web application using it.

---

## Getting Started

### Prerequisites
- Python 3.9 or higher

### 1. Clone the repository

```bash
git clone https://github.com/olugbeminiyi2000/mvc-framework.git
cd mvc-framework
```

### 2. Create a virtual environment

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (Command Prompt):**
```bash
python -m venv venv
venv\Scripts\activate
```

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

> You should see `(venv)` appear at the start of your terminal prompt once the environment is active.

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

This installs:
- **watchdog** — powers hot reload (server restarts automatically when you edit a `.py` file)
- **pytest** — for running the test suite

### 4. Start the server

```bash
python -m servers.v1_runserver
```

The server starts at `http://127.0.0.1:8080`.

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

## 2. Building a Web App — Tasks API Example

The framework gives you the structure. **You define the Model, View, and Controller** to suit whatever you are building. The example below is a Tasks API that demonstrates all five supported HTTP methods: `GET`, `POST`, `PUT`, `PATCH`, and `DELETE`.

Every project lives inside the `projects/` directory and follows this layout:

```
projects/
└── tasks/
    ├── __init__.py
    ├── model.py
    ├── controller.py
    ├── view.py
    └── router.py
```

---

### Step 1: Define the Model
The model wraps `V1Model` and gives your project its own data file so it does not conflict with other projects.

```python
# projects/tasks/model.py

from models.v1_Model import V1Model

def get_model():
    return V1Model(file_path="tasks_model.json")
```

---

### Step 2: Define the Controller
Each action method receives the parsed request body as `**kwargs` and returns a response dict that the view will render.

```python
# projects/tasks/controller.py

from controllers.v1_Controller import V1AbstractController
from projects.tasks.model import get_model


class TaskController(V1AbstractController):
    def __init__(self):
        pass

    def list_tasks(self, **kwargs):
        db = get_model()
        tasks = db.get_key_value("tasks") or []
        return {"tasks": tasks, "count": len(tasks)}

    def create_task(self, **kwargs):
        title = kwargs.get("title")
        if not title:
            return {"error": "title is required"}

        db = get_model()
        tasks = db.get_key_value("tasks") or []

        new_id = max((t["id"] for t in tasks), default=0) + 1
        task = {
            "id": new_id,
            "title": title,
            "description": kwargs.get("description", ""),
            "status": kwargs.get("status", "pending"),
            "priority": kwargs.get("priority", "low"),
        }

        tasks.append(task)
        if new_id == 1:
            db.add_key_value("tasks", tasks)
        else:
            db.update_key_value(tasks=tasks)

        return {"message": f"Task '{title}' created", "task": task}

    def update_task(self, **kwargs):
        task_id = kwargs.get("id")
        if not task_id:
            return {"error": "id is required"}

        required = ["title", "description", "status", "priority"]
        missing = [f for f in required if f not in kwargs]
        if missing:
            return {"error": f"PUT requires all fields: {missing}"}

        db = get_model()
        tasks = db.get_key_value("tasks") or []

        for i, task in enumerate(tasks):
            if str(task["id"]) == str(task_id):
                tasks[i] = {
                    "id": task["id"],
                    "title": kwargs["title"],
                    "description": kwargs["description"],
                    "status": kwargs["status"],
                    "priority": kwargs["priority"],
                }
                db.update_key_value(tasks=tasks)
                return {"message": "Task fully updated", "task": tasks[i]}

        return {"error": f"Task with id {task_id} not found"}

    def patch_task(self, **kwargs):
        task_id = kwargs.get("id")
        if not task_id:
            return {"error": "id is required"}

        db = get_model()
        tasks = db.get_key_value("tasks") or []

        for i, task in enumerate(tasks):
            if str(task["id"]) == str(task_id):
                for field in ["title", "description", "status", "priority"]:
                    if field in kwargs:
                        tasks[i][field] = kwargs[field]
                db.update_key_value(tasks=tasks)
                return {"message": "Task partially updated", "task": tasks[i]}

        return {"error": f"Task with id {task_id} not found"}

    def delete_task(self, **kwargs):
        task_id = kwargs.get("id")
        if not task_id:
            return {"error": "id is required"}

        db = get_model()
        tasks = db.get_key_value("tasks") or []
        updated = [t for t in tasks if str(t["id"]) != str(task_id)]

        if len(updated) == len(tasks):
            return {"error": f"Task with id {task_id} not found"}

        db.update_key_value(tasks=updated)
        return {"message": f"Task {task_id} deleted"}
```

---

### Step 3: Define the View
Because this is a JSON API, one view class handles every route. It receives the controller response as `controller_response` in `kwargs` and serialises it.

```python
# projects/tasks/view.py

from views.v1_View import V1BaseView


class TaskJsonView(V1BaseView):
    content_type = V1BaseView.CONTENT_TYPES["JSON"]

    def __init__(self):
        pass

    def render(self, **kwargs):
        return self.render_json(kwargs.get("controller_response") or {})
```

> For HTML responses, inherit from `V1BaseView`, set `content_type` to `CONTENT_TYPES["HTML"]`, and call `self.render_template("template_name.html", data)` instead.

---

### Step 4: Register the Routes
Each route maps a URL + HTTP method to one controller action and one view. Because the router stores one method per path, each HTTP method gets its own explicit path.

```python
# projects/tasks/router.py

from projects.tasks.controller import TaskController
from projects.tasks.view import TaskJsonView
from routers.v1_Router import V1Router

route = V1Router()
route.add_route("/tasks",        TaskController, "list_tasks",  TaskJsonView, "GET")
route.add_route("/tasks/create", TaskController, "create_task", TaskJsonView, "POST")
route.add_route("/tasks/update", TaskController, "update_task", TaskJsonView, "PUT")
route.add_route("/tasks/patch",  TaskController, "patch_task",  TaskJsonView, "PATCH")
route.add_route("/tasks/delete", TaskController, "delete_task", TaskJsonView, "DELETE")
```

---

### Step 5: Register the Routes into the Router State
Run this once to save your routes to `router_state.pkl` so the server can load them:

```bash
python -m projects.tasks.router
```

---

### Step 6: Start the Server

```bash
python -m servers.v1_runserver
```

The server starts at `http://127.0.0.1:8080` with hot reload enabled — it automatically restarts when any `.py` file changes.

---

### Step 7: Test All Five Methods with curl

**GET** — list all tasks:
```bash
curl http://localhost:8080/tasks
```

**POST** — create a task (JSON body):
```bash
curl -X POST http://localhost:8080/tasks/create \
  -H "Content-Type: application/json" \
  -d '{"title": "Build MVC framework", "description": "Implement router, controller, view", "status": "in-progress", "priority": "high"}'
```

**PUT** — full replace (all fields required):
```bash
curl -X PUT http://localhost:8080/tasks/update \
  -H "Content-Type: application/json" \
  -d '{"id": 1, "title": "Build MVC framework", "description": "All layers done", "status": "done", "priority": "high"}'
```

**PATCH** — partial update (only the fields you want to change):
```bash
curl -X PATCH http://localhost:8080/tasks/patch \
  -H "Content-Type: application/json" \
  -d '{"id": 2, "status": "in-progress"}'
```

**DELETE** — remove by id:
```bash
curl -X DELETE http://localhost:8080/tasks/delete \
  -H "Content-Type: application/json" \
  -d '{"id": 1}'
```

> The request parser auto-detects `Content-Type`. The same routes also accept `multipart/form-data` (HTML forms with file uploads) and `application/x-www-form-urlencoded` (standard HTML forms) — the controller receives the fields as `**kwargs` either way.

---

## Conclusion

The **V1 MVC Framework** was built as a learning project to explore MVC principles by developing a fully functional small-scale framework from scratch — no external web frameworks, raw sockets, custom template engine, and a full validation and transaction layer. It covers essential features like **routing, transactions, request handling, and views** while maintaining simplicity.

### Understanding the Flow

Using the Tasks API as the example:

1. **Client sends a request** → `POST /tasks/create` with a JSON body.
2. **Request parser** reads the socket, extracts the method, path, and body into a dict.
3. **Router matches the path and method** → calls `TaskController.create_task(**body)`.
4. **Controller processes logic** → saves to the model → returns `{"message": "...", "task": {...}}`.
5. **Router passes the response** to `TaskJsonView.render(controller_response=...)`.
6. **View serialises the response** to JSON and returns it.
7. **The rendered response is sent** back to the client.

If a **view does not return anything**, no content will be displayed.

This flow ensures a **clear separation of concerns** between routing, controller logic, and rendering views.