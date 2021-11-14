from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer, String, FLOAT, DATE
from sqlalchemy.orm import relationship

from db.base_class import Base

if TYPE_CHECKING:
    from .user import User  # noqa: F401


class Item(Base):
    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, index=True)
    type = Column(String, index=True)
    description = Column(String, index=True)
    price = Column(FLOAT)
    quantity = Column(Integer)
    qaod = Column(DATE)
    logo = Column(String, default="")
    background = Column(String, default="")
    headerText = Column(String, default="")
    headerColor = Column(String, default="")
    subHeaderText = Column(String, default="")
    owner_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"))
    owner = relationship("User", back_populates="items")
