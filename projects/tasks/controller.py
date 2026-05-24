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
                allowed = ["title", "description", "status", "priority"]
                for field in allowed:
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

        original_count = len(tasks)
        tasks = [t for t in tasks if str(t["id"]) != str(task_id)]

        if len(tasks) == original_count:
            return {"error": f"Task with id {task_id} not found"}

        db.update_key_value(tasks=tasks)
        return {"message": f"Task {task_id} deleted"}
