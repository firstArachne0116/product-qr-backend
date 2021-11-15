from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from db.base_class import Base

if TYPE_CHECKING:
    from .item import Item


class Asset(Base):
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)
    title = Column(String)
    order = Column(Integer)
    link = Column(String)
    background = Column(String)
    item_id = Column(Integer, ForeignKey("item.id", ondelete="CASCADE"))
    item = relationship("Item", back_populates="assets")
