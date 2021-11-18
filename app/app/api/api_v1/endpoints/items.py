import io
import qrcode
import qrcode.image.svg

from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

import crud
import models
import schemas
from api import deps
from aws_utils import create_presigned_url, delete_s3_object
from core.config import settings

router = APIRouter()


@router.get("/", response_model=List[schemas.Item])
def read_items(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    # limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve items.
    """
    if crud.user.is_superuser(current_user):
        items = crud.item.get_multi(
            db,
            skip=skip,
            # limit=limit
        )
    else:
        items = crud.item.get_multi_by_owner(
            db=db,
            owner_id=current_user.id,
            skip=skip,
            # limit=limit
        )
    return items


@router.post("/", response_model=schemas.Item)
def create_item(
    *,
    db: Session = Depends(deps.get_db),
    item_in: schemas.ItemCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new item.
    """
    item = crud.item.create_with_owner(db=db, obj_in=item_in, owner_id=current_user.id)
    return item


@router.delete("/")
def delete_item(
    *,
    db: Session = Depends(deps.get_db),
    ids: list[int],
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete multiple items.
    """
    items = crud.item.get_multi_by_ids(db=db, ids=ids)
    if len(items) != len(ids):
        raise HTTPException(status_code=404, detail="Item(s) not found")
    items = list(filter(lambda x: x.owner_id == current_user.id, items))
    if not crud.user.is_superuser(current_user) and len(items) != len(ids):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    result = crud.item.remove_multi(db=db, ids=ids)
    return result


@router.post("/upload", response_model=List[schemas.Item])
def upload_items(
    file: UploadFile = File(...),
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    items = crud.item.import_from_sheet(db=db, file=file, owner_id=current_user.id)
    return items


@router.get("/hash/{hash}")
def get_item_by_hash(
    *,
    db: Session = Depends(deps.get_db),
    hash: str,
) -> Any:
    """
    Get Item By Hash
    """
    print(hash)
    item = crud.item.get_by_hash(db=db, hash=hash)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    assets = crud.asset.get_multi_by_item(db=db, item_id=item.id)
    if len(item.logo) > 0:
        item.logo = create_presigned_url(
                settings.AWS_S3_BUCKET_NAME, str(item.id) + '-logo-' + item.logo)
    for asset in assets:
        if asset.type == 'video' or asset.type == 'doc':
            asset.presigned_link = create_presigned_url(
                settings.AWS_S3_BUCKET_NAME, str(item.id) + '-' + str(asset.id) + '-' + asset.link)
    return {"item": item, "assets": assets}


@router.put("/{id}", response_model=schemas.Item)
def update_item(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    item_in: schemas.ItemUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an item.
    """
    item = crud.item.get(db=db, id=id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not crud.user.is_superuser(current_user) and (item.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    item = crud.item.update(db=db, db_obj=item, obj_in=item_in)
    return item


@router.get("/{id}", response_model=schemas.Item)
def read_item(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get item by ID.
    """
    item = crud.item.get(db=db, id=id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not crud.user.is_superuser(current_user) and (item.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return item


@router.delete("/file")
def delete_file(
    *,
    db: Session = Depends(deps.get_db),
    obj: schemas.ObjectKey,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a file.
    """
    id = int(obj.object_key.split('-')[0])
    item = crud.item.get(db=db, id=id)
    if not item:
        raise HTTPException(status_code=403, detail="Item not found")
    if not crud.user.is_superuser(current_user) and (item.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return delete_s3_object(settings.AWS_S3_BUCKET_NAME, obj.object_key)


@router.delete("/{id}", response_model=schemas.Item)
def delete_item(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an item.
    """
    item = crud.item.get(db=db, id=id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not crud.user.is_superuser(current_user) and (item.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    item = crud.item.remove(db=db, id=id)
    return item


@router.get("/{id}/assets", response_model=List[schemas.Asset], tags=["assets"])
def get_item_assets(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    get all assets belong to an item
    """
    item = crud.item.get(db=db, id=id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not crud.user.is_superuser(current_user) and (item.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    assets = crud.asset.get_multi_by_item(db=db, item_id=id)
    return assets


@router.post("/{id}/assets", response_model=schemas.Asset, tags=["assets"])
def create_asset(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    obj_in: schemas.AssetCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new asset.
    """
    item = crud.item.get(db=db, id=id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not crud.user.is_superuser(current_user) and (item.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    asset = crud.asset.create_with_item(db=db, obj_in=obj_in, item_id=id)
    return asset


@router.get("/{id}/qrcode", response_model=str)
def get_item_qrcode(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Generate QR Code
    """
    item = crud.item.get(db=db, id=id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not crud.user.is_superuser(current_user) and (item.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    qr = qrcode.QRCode()
    qr.add_data(settings.MENU_APP_BASE_URL + '/' + item.hash)
    img = qr.make_image(image_factory=qrcode.image.svg.SvgFragmentImage)
    file_like = io.BytesIO()
    img.save(file_like)
    file_like.seek(0)
    return file_like.read()


@router.post("/{id}/refreshHash", response_model=schemas.Item)
def refresh_item_hash(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Refresh Item Hash
    """
    item = crud.item.get(db=db, id=id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not crud.user.is_superuser(current_user) and (item.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    item = crud.item.refresh_hash(db=db, db_obj=item)
    return item
