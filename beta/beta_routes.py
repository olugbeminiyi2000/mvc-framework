from beta.beta_controller import ProductController
from beta.beta_view import ProductListView
from routers.v1_Router import V1Router

route = V1Router()
route.add_route("/product/list", ProductController, "product_list", ProductListView)
