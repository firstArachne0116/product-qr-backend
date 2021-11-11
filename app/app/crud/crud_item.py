from fastapi import UploadFile
import pandas, io
from typing import List

from fastapi.encoders import jsonable_encoder
from pandas._libs.tslibs import NaT
from sqlalchemy.orm import Session

from crud.base import CRUDBase
from models.item import Item
from schemas.item import ItemCreate, ItemUpdate


class CRUDItem(CRUDBase[Item, ItemCreate, ItemUpdate]):
    def create_with_owner(
        self, db: Session, *, obj_in: ItemCreate, owner_id: int
    ) -> Item:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data, owner_id=owner_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_owner(
        self,
        db: Session,
        *,
        owner_id: int,
        skip: int = 0,
        # limit: int = 100
    ) -> List[Item]:
        return (
            db.query(self.model)
            .filter(Item.owner_id == owner_id)
            .offset(skip)
            # .limit(limit)
            .all()
        )
    def get_multi_by_ids(
        self,
        db: Session,
        *,
        ids: list[int],
    ) -> List[Item]:
        return (
            db.query(self.model)
            .filter(Item.id.in_(ids))
            .all()
        )
    def import_from_sheet(
        self,
        db: Session,
        *,
        file: UploadFile,
        owner_id: int,
    ) -> List[Item]:
        df = None
        if file.filename.endswith('.csv'):
            df = pandas.read_csv(io.BytesIO(file.file.read()))
        else:
            df = pandas.read_excel(file.file.read(), engine='openpyxl')
        item_list = []
        for index, row in df[df.SKU.notnull()].iterrows():
            date = row[df.columns[5]]
            if type(date) is not str:
                date = date.strftime('%Y-%m-%d')
            price = str(row[df.columns[3]])
            if price.startswith('$'):
                price = price[1:]
            item_list.append(ItemCreate(
                sku=row[df.columns[0]],
                type=row[df.columns[1]],
                description=row[df.columns[2]],
                price=float(price),
                quantity=int(row[df.columns[4]]),
                qaod=date,
            ))
        for i in range(len(item_list)):
            item_list[i] = self.create_with_owner(db=db, obj_in=item_list[i], owner_id=owner_id)
        return item_list

item = CRUDItem(Item)
