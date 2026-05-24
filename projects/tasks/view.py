from views.v1_View import V1BaseView


class TaskJsonView(V1BaseView):
    content_type = V1BaseView.CONTENT_TYPES["JSON"]

    def __init__(self):
        pass

    def render(self, **kwargs):
        return self.render_json(kwargs.get("controller_response") or {})
