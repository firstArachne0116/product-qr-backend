from pydantic import BaseModel


# Shared properties
class ObjectKey(BaseModel):
    object_key: str