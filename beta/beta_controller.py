from controllers.v1_Controller import V1AbstractController
from models.v1_Model import V1Model
from typing import Dict, Any

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
        database: V1Model = V1Model()
        product_list: list[dict[str, Any]] | None = database.get_key_value("product_list")
        if product_list is None:
            product_list = []
            product_list.append(kwargs)
            database.add_key_value("product_list", product_list)
        else:
            product_list.append(kwargs)
            database.update_key_value(product_list=product_list)
        message = "new product {} added sucessfully".format(kwargs.get("name"))
        return {"message": message}