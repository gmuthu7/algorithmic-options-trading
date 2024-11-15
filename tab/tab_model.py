from pydantic import BaseModel
from redis_om import JsonModel


class TabModelPydantic(BaseModel):
    # pk = <id>
    id: str
    name: str
    stock: str
    expiry: str


class TabModel(TabModelPydantic, JsonModel):
    # pk = <id>
    pass
