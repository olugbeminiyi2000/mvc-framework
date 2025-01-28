from routers.v1_Router import V1Router
from servers.v1_HttpServer import start_http_server

route_router = V1Router()
start_http_server(route_router)