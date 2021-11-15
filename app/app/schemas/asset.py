from typing import Optional
from datetime import date
from pydantic import BaseModel


# Shared properties
class AssetBase(BaseModel):
    type: Optional[str] = None
    title: Optional[str] = None
    order: Optional[int] = None
    link: Optional[str] = None
    background: Optional[str] = None

# Properties to receive on item creation
class AssetCreate(AssetBase):
    type: str
    title: str
    link: str
    background: str

# Properties to receive on item update
class AssetUpdate(AssetBase):
    pass


# Properties shared by models stored in DB
class AssetInDBBase(AssetBase):
    id: int
    type: str
    title: str
    order: int
    link: str
    item_id: int
    background: str

    class Config:
        orm_mode = True


# Properties to return to client
class Asset(AssetInDBBase):
    pass


# Properties properties stored in DB
class AssetInDB(AssetInDBBase):
    pass
