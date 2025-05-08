from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from http import HTTPStatus
from typing import Optional

from database import get_db
from models import Order, User, UserRole, OrderStatus
from auth import get_current_user
from schemas import OrderResponse, OrderCreate, OrderUpdateStatus, PaginationResponse
from utils.pagination import pagination_params
import models

router = APIRouter(prefix="", tags=["Orders"])

@router.post("/users/me/", response_model=OrderResponse)
def create_order(
    order: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_order = Order(
        product_name=order.product_name,
        amount=order.amount,
        user_id=current_user.id,
        status=order.status if order.status else OrderStatus.pending,
        estimated_delivery_time=order.estimated_delivery_time or None
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return OrderResponse.from_orm(db_order)

@router.get("/users/me/", response_model=PaginationResponse)
def get_user_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    params: dict = Depends(pagination_params),
    status: Optional[OrderStatus] = None
):
    query = db.query(Order).filter(Order.user_id == current_user.id)
    if params['search']:
        search = f"%{params['search']}%"
        query = query.filter(Order.product_name.ilike(search))
    if status:
        query = query.filter(Order.status == status)

    total = query.count()
    orders = query.offset((params['page'] - 1) * params['page_size'])\
                  .limit(params['page_size'])\
                  .all()
    orders_response = [OrderResponse.from_orm(order) for order in orders]
    return {
        "items": orders_response,
        "total": total,
        "page": params['page'],
        "page_size": params['page_size'],
        "total_pages": (total + params['page_size'] - 1) // params['page_size']
    }

@router.patch("/users/me/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    order_update: OrderUpdateStatus,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    
    db_order = db.query(Order).filter(
        Order.id == order_id, Order.user_id == current_user.id
    ).first()

    if not db_order:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Order not found"
        )

    if order_update.status not in OrderStatus.__members__.values():
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Invalid order status"
        )

    db_order.status = order_update.status

    if order_update.status == OrderStatus.processing:
        db_order.estimated_delivery_time = datetime.utcnow() + timedelta(days=2)
    elif order_update.status == OrderStatus.in_packaging:
        db_order.estimated_delivery_time = datetime.utcnow() + timedelta(days=1)
    elif order_update.status == OrderStatus.out_for_delivery:
        db_order.estimated_delivery_time = datetime.utcnow() + timedelta(hours=5)
    elif order_update.status in [OrderStatus.delivered, OrderStatus.cancelled]:
        db_order.estimated_delivery_time = None

    db.commit()
    db.refresh(db_order)

    return OrderResponse.from_orm(db_order)