from projects.docs.controller import DocsController
from projects.docs.view import DocsView
from routers.v1_Router import V1Router

route = V1Router()
route.add_route("/docs", DocsController, "show", DocsView, "GET")
