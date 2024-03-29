from typing import Any

from fastapi import APIRouter, Depends
from pydantic.networks import EmailStr

import models
import schemas
from api import deps
from core.celery_app import celery_app
from schemas.objectKey import ObjectKey
from utils import send_test_email
from aws_utils import create_presigned_post, create_presigned_url

from core.config import settings

router = APIRouter()


@router.post("/test-celery/", response_model=schemas.Msg, status_code=201)
def test_celery(
    msg: schemas.Msg,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Test Celery worker.
    """
    celery_app.send_task("app.worker.test_celery", args=[msg.msg])
    return {"msg": "Word received"}


@router.post("/test-email/", response_model=schemas.Msg, status_code=201)
def test_email(
    email_to: EmailStr,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Test emails.
    """
    send_test_email(email_to=email_to)
    return {"msg": "Test email sent"}


@router.post("/upload-presigned-link")
def test_aws(
    obj: ObjectKey,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    return create_presigned_post(settings.AWS_S3_BUCKET_NAME, obj.object_key)


@router.post("/download-presigned-link")
def test_aws(
    obj: ObjectKey,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    return create_presigned_url(settings.AWS_S3_BUCKET_NAME, obj.object_key)
