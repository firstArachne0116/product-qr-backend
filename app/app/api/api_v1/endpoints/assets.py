from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

import crud, models, schemas
from api import deps
from aws_utils import delete_s3_object

router = APIRouter()


@router.put("/{id}", response_model=schemas.Asset)
def update_asset(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    item_in: schemas.AssetUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an asset.
    """
    asset = crud.asset.get(db=db, id=id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    item = crud.item.get(db=db, id=asset.item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not crud.user.is_superuser(current_user) and (item.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    asset = crud.asset.update(db=db, db_obj=asset, obj_in=item_in)
    return asset


@router.get("/{id}", response_model=schemas.Asset)
def read_item(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get asset by ID.
    """
    asset = crud.asset.get(db=db, id=id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    item = crud.item.get(db=db, id=asset.item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not crud.user.is_superuser(current_user) and (item.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return asset

@router.delete("/{id}", response_model=schemas.Asset)
def delete_item(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an asset.
    """
    asset = crud.asset.get(db=db, id=id)
    if not asset:
        raise HTTPException(status_code=404, detail="Item not found")
    item = crud.item.get(db=db, id=asset.item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not crud.user.is_superuser(current_user) and (item.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    asset = crud.asset.remove(db=db, id=id)
    return asset

