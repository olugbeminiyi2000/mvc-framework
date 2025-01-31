from controllers.v1_Controller import V1AbstractController
from models.v1_Model import V1Model
from typing import Dict

class ProductController(V1AbstractController):
    def __init__(self):
        pass

    def product_list(self, **kwargs: Dict):
        if not kwargs:
            return None
        return None
    
    def product_create_get(self, **kwargs: Dict):
        if not kwargs:
            return None
        return None
    
    def product_create_post(self, **kwargs: Dict):
        print(kwargs)
        database = V1Model()
        product_list = database.get_key_value("product_list")
        if product_list is None:
            pass
        pass