from fastapi import UploadFile
import pandas, io
from typing import List

from fastapi.encoders import jsonable_encoder
from pandas._libs.tslibs import NaT
from sqlalchemy.orm import Session

from crud.base import CRUDBase
from models.asset import Asset
from schemas.asset import AssetCreate, AssetUpdate


class CRUDAsset(CRUDBase[Asset, AssetCreate, AssetUpdate]):
    def create_with_item(
        self, db: Session, *, obj_in: AssetCreate, item_id: int
    ) -> Asset:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data, item_id=item_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        db_obj.order = float(db_obj.id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_item(
        self,
        db: Session,
        *,
        item_id: int,
        skip: int = 0,
        # limit: int = 100
    ) -> List[Asset]:
        return (
            db.query(self.model)
            .filter(Asset.item_id == item_id)
            .offset(skip)
            # .limit(limit)
            .all()
        )

asset = CRUDAsset(Asset)
