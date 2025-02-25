from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from models import UserRole, OrderStatus

class MediaBase(BaseModel):
    file_url: str
    file_type: str

class MediaCreate(MediaBase):
    pass

class MediaResponse(MediaBase):
    id: int
    post_id: int

    class Config:
        from_attributes = True

class LikeResponse(BaseModel):
    id: int
    user_id: int
    post_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    pass

class CommentResponse(CommentBase):
    id: int
    user_id: int
    post_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class PaginationParams(BaseModel):
    page: int = 1
    page_size: int = 10

class PaginationResponse(BaseModel):
    items: list
    total: int
    page: int
    page_size: int
    total_pages: int

class WishlistItemCreate(BaseModel):
    product_name: str
    notes: Optional[str] = None
    quantity: Optional[int] = 1

class WishlistItemUpdate(BaseModel):
    product_name: Optional[str] = None
    notes: Optional[str] = None
    quantity: Optional[int] = None

class WishlistItemResponse(WishlistItemCreate):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class UserProfileBase(BaseModel):
    bio: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    social_links: Optional[dict] = None
    language: Optional[str] = "en"
    theme_preference: Optional[str] = "light"

class UserProfileUpdate(UserProfileBase):
    pass

class UserProfileResponse(UserProfileBase):
    profile_picture: Optional[str]
    preferences: Optional[dict]

class ProfilePictureResponse(BaseModel):
    message: str
    profile_picture: str

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    age: int
    role: UserRole

class Token(BaseModel):
    access_token: str
    token_type: str

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class ResetPasswordReq(BaseModel):
    email: str
    otp: str
    new_password: str

class PostBase(BaseModel):
    title: str
    content: str

class PostCreate(PostBase):
    pass

class PostResponse(PostBase):
    id: int
    user_id: int
    like_count: int
    comment_count: int
    created_at: datetime
    media_attachments: List[MediaResponse]

    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    product_name: str
    amount: int
    status: OrderStatus = OrderStatus.pending
    estimated_delivery_time: Optional[datetime] = None

class OrderCreate(OrderBase):
    pass

class OrderUpdateStatus(BaseModel):
    status: OrderStatus

class OrderResponse(OrderBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True