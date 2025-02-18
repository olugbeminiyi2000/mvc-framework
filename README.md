

## 2. Building a Simple Web App

### Step 1: Define a Controller
Create a controller that processes user requests.
```python
# File - webapp.hello_controller.py

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
# File - webapp.hello_view.py

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
# File - webapp.hello_router.py

from webapp.beta_view import HelloView
from webapp.hello_controller import HelloController
from routers.v1_Router import V1Router
router = V1Router()
router.add_route("/hello", HelloController, "hello", HelloView)

```

### Step 4: Register the Routes
Before starting the server, ensure you run the file responsible for registering routes:
```
python hello_router.py
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




# Note to run tests for each compartment
```bash
    echo "" > v1_model.json
    pytest models/tests/ routers/tests/
```
