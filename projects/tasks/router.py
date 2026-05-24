from projects.tasks.controller import TaskController
from projects.tasks.view import TaskJsonView
from routers.v1_Router import V1Router

route = V1Router()
route.add_route("/tasks",        TaskController, "list_tasks",   TaskJsonView, "GET")
route.add_route("/tasks/create", TaskController, "create_task",  TaskJsonView, "POST")
route.add_route("/tasks/update", TaskController, "update_task",  TaskJsonView, "PUT")
route.add_route("/tasks/patch",  TaskController, "patch_task",   TaskJsonView, "PATCH")
route.add_route("/tasks/delete", TaskController, "delete_task",  TaskJsonView, "DELETE")
