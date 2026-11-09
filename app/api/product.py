from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import require_admin_api_key
from app.database.session import get_db
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductRead, ProductUpdate

router = APIRouter(prefix="/api/v1", tags=["Products"])


@router.get(
    "/products",
    response_model=list[ProductRead],
)
def list_products(
    db: Annotated[Session, Depends(get_db)],
    search: str | None = Query(default=None, max_length=100),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> list[Product]:
    statement = select(Product).where(Product.is_active.is_(True))

    if search and search.strip():
        term = f"%{search.strip()}%"
        statement = statement.where(
            or_(
                Product.name.ilike(term),
                Product.sku.ilike(term),
            )
        )

    statement = statement.order_by(Product.id).offset(skip).limit(limit)

    return list(db.scalars(statement).all())


@router.get(
    "/products/{product_id}",
    response_model=ProductRead,
)
def get_product(
    product_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> Product:
    product = db.get(Product, product_id)

    if product is None or not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    return product


@router.post(
    "/admin/products",
    response_model=ProductRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin_api_key)],
)
def create_product(
    payload: ProductCreate,
    db: Annotated[Session, Depends(get_db)],
) -> Product:
    product = Product(**payload.model_dump())

    db.add(product)

    try:
        db.commit()
        db.refresh(product)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="SKU already exists or product violates a database constraint",
        ) from exc

    return product


@router.put(
    "/admin/products/{product_id}",
    response_model=ProductRead,
    dependencies=[Depends(require_admin_api_key)],
)
def update_product(
    product_id: int,
    payload: ProductUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> Product:
    product = db.get(Product, product_id)

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    changes = payload.model_dump(exclude_unset=True)

    for field, value in changes.items():
        setattr(product, field, value)

    try:
        db.commit()
        db.refresh(product)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="SKU already exists or product violates a database constraint",
        ) from exc

    return product