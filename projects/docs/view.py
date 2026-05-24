from views.v1_View import V1BaseView


class DocsView(V1BaseView):
    content_type = V1BaseView.CONTENT_TYPES["HTML"]

    def __init__(self):
        pass

    def render(self, **kwargs):
        return self.render_template("docs.html", {})
