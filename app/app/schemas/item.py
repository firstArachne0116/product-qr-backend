from typing import Optional
from datetime import date
from pydantic import BaseModel


# Shared properties
class ItemBase(BaseModel):
    sku: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[int] = None
    qaod: Optional[str] = None #quantity at-of date
    logo: Optional[str] = None
    background: Optional[str] = None
    headerText: Optional[str] = None
    headerColor: Optional[str] = None
    subHeaderText: Optional[str] = None

# Properties to receive on item creation
class ItemCreate(ItemBase):
    sku: str
    type: str
    price: float
    quantity: int
    qaod: str

# Properties to receive on item update
class ItemUpdate(ItemBase):
    pass


# Properties shared by models stored in DB
class ItemInDBBase(ItemBase):
    id: int
    sku: str
    type: str
    price: float
    quantity: int
    qaod: str
    owner_id: int

    class Config:
        orm_mode = True


# Properties to return to client
class Item(ItemInDBBase):
    qaod: date
    pass


# Properties properties stored in DB
class ItemInDB(ItemInDBBase):
    pass
