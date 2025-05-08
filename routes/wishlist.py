from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import WishlistItem, User
from auth import get_current_user
from schemas import WishlistItemResponse, WishlistItemCreate, WishlistItemUpdate, PaginationResponse
from utils.pagination import pagination_params

router = APIRouter(prefix="", tags=["Wishlist"])

@router.post("/", response_model=WishlistItemResponse)
def create_wishlist_item(
    item: WishlistItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_item = WishlistItem(**item.dict(), user_id=current_user.id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return WishlistItemResponse.from_orm(db_item)

@router.get("/", response_model=PaginationResponse)
def get_wishlist_items(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    params: dict = Depends(pagination_params)
):
    query = db.query(WishlistItem).filter(WishlistItem.user_id == current_user.id)
    if params['search']:
        search = f"%{params['search']}%"
        query = query.filter(WishlistItem.product_name.ilike(search) | WishlistItem.notes.ilike(search))
    total = query.count()
    items = query.offset((params['page'] - 1) * params['page_size'])\
                 .limit(params['page_size'])\
                 .all()
    items_response = [WishlistItemResponse.from_orm(item) for item in items]
    return {
        "items": items_response,
        "total": total,
        "page": params['page'],
        "page_size": params['page_size'],
        "total_pages": (total + params['page_size'] - 1) // params['page_size']
    }

@router.get("/{item_id}", response_model=WishlistItemResponse)
def get_wishlist_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    item = db.query(WishlistItem).filter(
        WishlistItem.id == item_id,
        WishlistItem.user_id == current_user.id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Wishlist item not found")
    return WishlistItemResponse.from_orm(item)

@router.put("/{item_id}", response_model=WishlistItemResponse)
def update_wishlist_item(
    item_id: int,
    updates: WishlistItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    item = db.query(WishlistItem).filter(
        WishlistItem.id == item_id,
        WishlistItem.user_id == current_user.id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Wishlist item not found")
    for key, value in updates.dict(exclude_unset=True).items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return WishlistItemResponse.from_orm(item)

@router.delete("/{item_id}")
def delete_wishlist_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    item = db.query(WishlistItem).filter(
        WishlistItem.id == item_id,
        WishlistItem.user_id == current_user.id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Wishlist item not found")
    db.delete(item)
    db.commit()
    return {"message": "Wishlist item deleted"}
