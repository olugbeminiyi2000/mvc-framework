from views.v1_View import V1BaseView
from typing import Dict

class ProductListView(V1BaseView):
    def __init__(self):
        pass
    def render(self, **kwargs: Dict):
        if kwargs["controller_response"] is None:
            kwargs = {}
        return self.render_template("beta.html", kwargs)
    
class ProductGetView(V1BaseView):
    def __init__(self):
        pass
    def render(self, **kwargs):
        if kwargs["controller_response"] is None:
            kwargs = {}
        return self.render_template("create.html", kwargs)
    
class ProductPostView(V1BaseView):
    def __init__(self):
        pass
    def render(self, **kwargs):
        if kwargs["controller_response"] is None:
            kwargs = {}
        else:
            kwargs = kwargs["controller_response"]
        return self.render_template("create.html", kwargs)