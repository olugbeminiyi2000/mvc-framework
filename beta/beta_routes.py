from beta.beta_controller import ProductController
from beta.beta_view import ProductListView, ProductGetView, ProductPostView
from routers.v1_Router import V1Router

route = V1Router()
route.add_route("/product/list", ProductController, "product_list", ProductListView)
route.add_route("/product/create_product", ProductController, "product_create_get", ProductGetView)
route.add_route("/product/post_product", ProductController, "product_create_post", ProductPostView)