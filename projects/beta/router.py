from projects.beta.controller import ProductController
from projects.beta.view import ProductListView, ProductGetView, ProductPostView
from routers.v1_Router import V1Router

route = V1Router()
route.add_route("/product/list", ProductController, "product_list", ProductListView, "GET")
route.add_route("/product/create_product", ProductController, "product_create_get", ProductGetView, "GET")
route.add_route("/product/post_product", ProductController, "product_create_post", ProductPostView, "POST")