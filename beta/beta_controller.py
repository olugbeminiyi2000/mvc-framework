from controllers.v1_Controller import V1AbstractController
from typing import Dict

class ProductController(V1AbstractController):
    def __init__(self):
        pass

    def product_list(self, **kwargs: Dict):
        if not kwargs:
            return None
        return None