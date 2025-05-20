from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import text

from routes import auth, users, posts, comments, likes, orders, wishlist, reactions
from database import engine, Base, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="E-commerce API- Kubernetes DeploymentV7",
    description="API for user authentication, users, posts, orders, and wishlist management.",
)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(posts.router, prefix="/posts", tags=["Posts"])
app.include_router(comments.router, prefix="/comments", tags=["Comments"])
app.include_router(likes.router, prefix="/likes", tags=["Likes"])
app.include_router(orders.router, prefix="/orders", tags=["Orders"])
app.include_router(wishlist.router, prefix="/wishlist", tags=["Wishlist"])
app.include_router(reactions.router, prefix="/reactions", tags=["Reactions"])


@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the E-commerce API- Kubernetes DeploymentV7"}

@app.get("/test-db", tags=["Health Check"])
def test_db_connection(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"message": "Connected to PostgreSQL"}
    except Exception as e:
        return {"error": str(e)}



# from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, Query
# from http import HTTPStatus
# from fastapi.security import OAuth2PasswordRequestForm
# from sqlalchemy.orm import Session
# from database import get_db, engine, Base
# from sqlalchemy.sql import text
# import models
# from models import Order, User, UserRole, OrderStatus
# from typing import Optional, List
# from schemas import (
#     MediaCreate,
#     MediaResponse,
#     LikeResponse,
#     CommentCreate,
#     CommentResponse,
#     PaginationParams,
#     PaginationResponse,
#     WishlistItemCreate,
#     WishlistItemUpdate,
#     WishlistItemResponse,
#     UserProfileBase,
#     UserProfileUpdate,
#     UserProfileResponse,
#     ProfilePictureResponse,
#     UserCreate,
#     Token,
#     ForgotPasswordRequest,
#     ResetPasswordRequest,
#     ResetPasswordReq,
#     PostCreate,
#     PostResponse,
#     OrderCreate,
#     OrderUpdateStatus,
#     OrderResponse
# )
# from auth import authenticate_user, get_password_hash, create_access_token, get_current_user, get_admin_user, SECRET_KEY, ALGORITHM
# from datetime import timedelta, datetime
# from sqlalchemy.exc import IntegrityError
# from email_utils import send_email, generate_password_reset_token, generate_otp
# import secrets
# import jwt
# import os
# import uuid
# from fastapi.staticfiles import StaticFiles
# from sqlalchemy import func

# # ---------- Database Setup ----------
# Base.metadata.create_all(bind=engine)
# app = FastAPI()

# # ---------- Static Files Setup ----------
# BASE_STATIC_DIR = r"C:\Users\Sagar\Desktop\static"
# PROFILE_PIC_DIR = os.path.join(BASE_STATIC_DIR, "profile_pics")
# MEDIA_DIR = os.path.join(BASE_STATIC_DIR, "media")

# os.makedirs(PROFILE_PIC_DIR, exist_ok=True)
# os.makedirs(MEDIA_DIR, exist_ok=True)

# # ---------- Dependency for Pagination ----------
# def pagination_params(
#     page: int = Query(1, gt=0),
#     page_size: int = Query(10, gt=0, le=100),
#     search: Optional[str] = None
# ) -> dict:
#     return {"page": page, "page_size": page_size, "search": search}

# ---------- Endpoints ----------



# @app.post("/register/")
# def register_user(user: UserCreate, db: Session = Depends(get_db)):
#     existing_user = db.query(models.User).filter(
#         models.User.email == user.email,
#         models.User.is_deleted == False
#     ).first()
#     if existing_user:
#         raise HTTPException(status_code=400, detail="Email Already registered")
#     hashed_password = get_password_hash(user.password)
#     new_user = models.User(
#         name=user.name,
#         email=user.email, 
#         hashed_password=hashed_password, 
#         age=user.age, 
#         role=user.role.value.lower(),
#         is_deleted=False
#     )
#     db.add(new_user)
#     try:
#         db.commit()
#     except IntegrityError:
#         db.rollback()
#         raise HTTPException(status_code=400, detail="Email already registered")
#     db.refresh(new_user)
#     return {"message": "User Registered Successfully", "role": new_user.role}

# @app.post("/login/", response_model=Token)
# def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
#     user = authenticate_user(db, form_data.username, form_data.password)
#     if not user:
#         raise HTTPException(status_code=401, detail="Invalid email or password")
#     access_token = create_access_token(
#         data={"sub": user.id, "role": user.role},
#         expires_delta=timedelta(minutes=30)
#     )
#     return {"access_token": access_token, "token_type": "bearer"}

# @app.get("/users/me/")
# def read_users_me(current_user: models.User = Depends(get_current_user)):
#     return {
#         "id": current_user.id,
#         "name": current_user.name,
#         "email": current_user.email,
#         "age": current_user.age,
#         "profile_picture": current_user.profile_picture,
#         "role": current_user.role
#     }

# @app.get("/users/", response_model=PaginationResponse)
# def get_all_users(
#     db: Session = Depends(get_db), 
#     current_user: models.User = Depends(get_current_user),
#     params: dict = Depends(pagination_params)
# ):
#     query = db.query(models.User).filter(models.User.is_deleted == False)
#     if params['search']:
#         search = f"%{params['search']}%"
#         query = query.filter(models.User.name.ilike(search) | models.User.email.ilike(search))
#     total = query.count()
#     users = query.offset((params['page'] - 1) * params['page_size'])\
#                  .limit(params['page_size'])\
#                  .all()
#     # Convert users to a list of dictionaries (or use a Pydantic schema)
#     items = [{"id": u.id, "name": u.name, "email": u.email} for u in users]
#     return {
#         "items": items,
#         "total": total,
#         "page": params['page'],
#         "page_size": params['page_size'],
#         "total_pages": (total + params['page_size'] - 1) // params['page_size']
#     }

# @app.get("/admin/users/", dependencies=[Depends(get_admin_user)], response_model=PaginationResponse)
# def get_all_users_admin(
#     db: Session = Depends(get_db),
#     params: dict = Depends(pagination_params)
# ):
#     query = db.query(models.User)
#     if params['search']:
#         search = f"%{params['search']}%"
#         query = query.filter(models.User.name.ilike(search) | models.User.email.ilike(search))
#     total = query.count()
#     users = query.offset((params['page'] - 1) * params['page_size'])\
#                  .limit(params['page_size'])\
#                  .all()
#     items = [{
#             "id": u.id,
#             "name": u.name,
#             "email": u.email,
#             "role": u.role,
#             "is_deleted": u.is_deleted,
#             "deleted_at": u.deleted_at
#         } for u in users]
#     return {
#         "items": items,
#         "total": total,
#         "page": params['page'],
#         "page_size": params['page_size'],
#         "total_pages": (total + params['page_size'] - 1) // params['page_size']
#     }

# @app.delete("/admin/users/{user_id}/soft", dependencies=[Depends(get_admin_user)])
# def soft_delete_user(user_id: int, db: Session = Depends(get_db)):
#     user = db.query(models.User).filter(models.User.id == user_id).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     if user.is_deleted:
#         raise HTTPException(status_code=400, detail="User already soft-deleted")
#     user.is_deleted = True
#     user.deleted_at = datetime.utcnow()
#     db.commit()
#     return {"message": "User soft-deleted successfully"}

# @app.delete("/admin/users/{user_id}/hard", dependencies=[Depends(get_admin_user)])
# def hard_delete_user(user_id: int, db: Session = Depends(get_db)):
#     user = db.query(models.User).filter(models.User.id == user_id).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     db.delete(user)
#     db.commit()
#     return {"message": "User hard-deleted successfully"}

# @app.post("/forgot-password/")
# def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
#     user = db.query(models.User).filter(models.User.email == request.email, models.User.is_deleted == False).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     reset_token = generate_password_reset_token(user.email)
#     user.reset_token = reset_token
#     user.reset_token_expires = datetime.utcnow() + timedelta(minutes=15)
#     db.commit()
#     reset_link = f"http://localhost:8000/reset-password?token={reset_token}"
#     email_body = f"""
#     <p>You requested a password reset. Click the link below to reset your password:</p>
#     <p><a href="{reset_link}">Reset Password</a></p>
#     <p>This link will expire in 15 minutes.</p>
#     """
#     send_email(user.email, "Password Reset Request", email_body)
#     return {"message": "Password reset email sent"}

# @app.post("/forgot-password-otp/")
# def forgot_password_otp(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
#     user = db.query(models.User).filter(models.User.email == request.email, models.User.is_deleted == False).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     otp = generate_otp()
#     user.otp_code = otp
#     user.otp_expires_at = datetime.utcnow() + timedelta(minutes=10)
#     db.commit()
#     email_body = f"""
#     <p>Your password reset OTP is: <strong>{otp}</strong></p>
#     <p>This OTP is valid for 10 minutes.</p>
#     """
#     send_email(user.email, "Password Reset OTP", email_body)
#     return {"message": "OTP sent to your email"}

# @app.post("/reset-password/")
# def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
#     try:
#         payload = jwt.decode(request.token, SECRET_KEY, algorithms=[ALGORITHM])
#         email = payload.get("sub")
#         if not email:
#             raise HTTPException(status_code=400, detail="Invalid Token")
#         if datetime.utcnow() > datetime.fromtimestamp(payload["exp"]):
#             raise HTTPException(status_code=400, detail="Token has expired")
#         user = db.query(models.User).filter(models.User.email == email, models.User.is_deleted == False).first()
#         if not user or user.reset_token != request.token:
#             raise HTTPException(status_code=400, detail="Invalid token")
#         user.hashed_password = get_password_hash(request.new_password)
#         user.reset_token = None
#         user.reset_token_expires = None
#         db.commit()
#         return {"message": "Password reset successfully"}
#     except jwt.PyJWTError:
#         raise HTTPException(status_code=400, detail="Invalid token")

# @app.post("/reset-password-otp/")
# def reset_password_otp(request: ResetPasswordReq, db: Session = Depends(get_db)):
#     user = db.query(models.User).filter(models.User.email == request.email, models.User.is_deleted == False).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     if user.otp_code != request.otp or user.otp_expires_at < datetime.utcnow():
#         raise HTTPException(status_code=400, detail="Invalid or expired OTP")
#     user.hashed_password = get_password_hash(request.new_password)
#     user.otp_code = None
#     user.otp_expires_at = None
#     db.commit()
#     return {"message": "Password reset successfully"}

# @app.put("/users/me/profile", response_model=UserProfileResponse)
# async def update_profile(
#     profile_data: UserProfileUpdate,
#     current_user: models.User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     update_data = profile_data.dict(exclude_unset=True)
#     for field in update_data:
#         setattr(current_user, field, update_data[field])
#     db.commit()
#     db.refresh(current_user)
#     return current_user

# @app.post("/users/me/profile-picture", response_model=ProfilePictureResponse)
# async def upload_profile_picture(
#     file: UploadFile = File(...),
#     current_user: models.User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     allowed_types = ["image/jpeg", "image/png", "image/gif"]
#     if file.content_type not in allowed_types:
#         raise HTTPException(400, "Invalid file type. Allowed types: JPEG, PNG, GIF")
#     file_ext = file.filename.split(".")[-1]
#     filename = f"{uuid.uuid4()}.{file_ext}"
#     file_path = os.path.join(PROFILE_PIC_DIR, filename)
#     with open(file_path, "wb") as buffer:
#         content = await file.read()
#         buffer.write(content)
#     current_user.profile_picture = f"/static/profile_pics/{filename}"
#     db.commit()
#     return {
#         "message": "Profile picture updated successfully",
#         "profile_picture": current_user.profile_picture
#     }

# @app.get("/current/users/me/profile", response_model=UserProfileResponse)
# def get_user_profile(current_user: models.User = Depends(get_current_user)):
#     return current_user

# @app.post("/users/me/posts/", response_model=PostResponse)
# def create_post(
#     post: PostCreate,
#     current_user: models.User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     db_post = models.Post(**post.dict(), user_id=current_user.id)
#     db.add(db_post)
#     db.commit()
#     db.refresh(db_post)
#     return PostResponse(
#         id=db_post.id,
#         title=db_post.title,
#         content=db_post.content,
#         user_id=db_post.user_id,
#         created_at=db_post.created_at,
#         like_count=0,
#         comment_count=0,
#         media_attachments=db_post.media_attachments if db_post.media_attachments else []
#     )


# @app.post("/posts/{post_id}/media/", response_model=List[MediaResponse])
# async def upload_media(
#     post_id: int,
#     files: List[UploadFile] = File(...),
#     current_user: models.User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     post = db.query(models.Post).filter(
#         models.Post.id == post_id,
#         models.Post.user_id == current_user.id
#     ).first()
#     if not post:
#         raise HTTPException(status_code=404, detail="Post not found")
    
#     media_responses = []
#     for file in files:
#         file_type = file.content_type.split("/")[0]
#         if file_type not in ["image", "video", "audio"]:
#             raise HTTPException(status_code=400, detail=f"Invalid file type: {file.content_type}")
        
#         file_ext = file.filename.split(".")[-1]
#         filename = f"{uuid.uuid4()}.{file_ext}"
#         file_path = os.path.join(MEDIA_DIR, filename)
        
#         with open(file_path, "wb") as buffer:
#             content = await file.read()
#             buffer.write(content)
        
#         db_media = models.Media(
#             file_url=f"/static/media/{filename}",
#             file_type=file_type,
#             post_id=post_id
#         )
#         db.add(db_media)
#         db.commit()
#         db.refresh(db_media)
        
#         media_responses.append(db_media)
    
#     return media_responses


# @app.get("/users/me/posts/", response_model=PaginationResponse)
# def get_user_posts(
#     current_user: models.User = Depends(get_current_user),
#     db: Session = Depends(get_db),
#     params: dict = Depends(pagination_params)
# ):
#     query = db.query(models.Post,
#         func.count(models.Like.id).label("like_count"),
#         func.count(models.Comment.id).label("comment_count")
#     ).outerjoin(models.Like, models.Like.post_id == models.Post.id)\
#     .outerjoin(models.Comment, models.Comment.post_id == models.Post.id)\
#     .group_by(models.Post.id)\
#     .filter(models.Post.user_id == current_user.id)

#     if params['search']:
#         search = f"%{params['search']}%"
#         query = query.filter(models.Post.title.ilike(search) | models.Post.content.ilike(search))
#     total = query.count()
#     posts = query.offset((params['page'] - 1) * params['page_size'])\
#                  .limit(params['page_size'])\
#                  .all()
#     posts_response = []
#     for post, like_count, comment_count in posts:
#         media_attachments = db.query(models.Media).filter(models.Media.post_id == post.id).all()
        
#         posts_response.append(
#             PostResponse(
#                 id=post.id,
#                 title=post.title,
#                 content=post.content,
#                 user_id=post.user_id,
#                 created_at=post.created_at,
#                 like_count=like_count,
#                 comment_count=comment_count,
#                 media_attachments=media_attachments
#             )
#         )
#     return {
#         "items": posts_response,
#         "total": total,
#         "page": params['page'],
#         "page_size": params['page_size'],
#         "total_pages": (total + params['page_size'] - 1) // params['page_size']
#     }


# @app.get("/users/me/posts/{post_id}", response_model=PostResponse)
# def get_post(
#     post_id: int,
#     current_user: models.User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     post = db.query(
#         models.Post,
#         func.count(models.Like.id).label("like_count"),
#         func.count(models.Comment.id).label("comment_count")
#     ).outerjoin(models.Like, models.Like.post_id == models.Post.id)\
#      .outerjoin(models.Comment, models.Comment.post_id == models.Post.id)\
#      .group_by(models.Post.id)\
#      .filter(models.Post.id == post_id, models.Post.user_id == current_user.id)\
#      .first()
    
#     if not post:
#         raise HTTPException(status_code=404, detail="Post not found")
    
#     post_data, like_count, comment_count = post
#     return PostResponse(
#         id=post_data.id,
#         title=post_data.title,
#         content=post_data.content,
#         user_id=post_data.user_id,
#         created_at=post_data.created_at,
#         like_count=like_count,
#         comment_count=comment_count
#     )


# @app.put("/users/me/posts/{post_id}", response_model=PostResponse)
# def update_post(
#     post_id: int,
#     post_update: PostCreate,
#     current_user: models.User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     post = db.query(models.Post).filter(
#         models.Post.id == post_id,
#         models.Post.user_id == current_user.id
#     ).first()
#     if not post:
#         raise HTTPException(status_code=404, detail="Post not found")

#     for key, value in post_update.dict().items():
#         setattr(post, key, value)
    
#     db.commit()
#     db.refresh(post)
#     return post


# @app.delete("/users/me/posts/{post_id}")
# def delete_post(
#     post_id: int,
#     current_user: models.User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     post = db.query(models.Post).filter(
#         models.Post.id == post_id,
#         models.Post.user_id == current_user.id).first()
    
#     if not post:
#         raise HTTPException(status_code=404, detail="Post not found")

#     db.delete(post)
#     db.commit()
#     return{"message": "Post deleted successfully"}


# @app.post("/posts/{post_id}/comments", response_model=CommentResponse)
# def create_comment(
#     post_id: int,
#     comment: CommentCreate,
#     current_user: models.User = Depends(get_current_user),
#     db:Session = Depends(get_db)
# ):
#     post = db.query(models.Post).filter(models.Post.id == post_id).first()
#     if not post:
#         raise HTTPException(status_code=404, detail="Post not found")

#     db_comment = models.Comment(
#         content=comment.content,
#         user_id=current_user.id,
#         post_id=post_id
#     )
#     db.add(db_comment)
#     db.commit()
#     db.refresh(db_comment)
#     return db_comment

# @app.get("/posts/{post_id}/comments", response_model=list[CommentResponse])
# def get_comments(
#     post_id: int,
#     db: Session = Depends(get_db)
# ):
#     comments=db.query(models.Comment).filter(models.Comment.post_id == post_id).all()
#     return comments

# @app.post("/posts/{post_id}/like", response_model=LikeResponse)
# def like_post(
#     post_id:int,
#     current_user: models.User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     post = db.query(models.Post).filter(models.Post.id == post_id).first()
#     if not post:
#         raise HTTPException(status_code=404, detail="Post not found")

#     existing_like = db.query(models.Like).filter(
#         models.Like.user_id == current_user.id,
#         models.Like.post_id == post_id
#     ).first()
#     if existing_like:
#         raise HTTPException(status_code=400, detail="You already liked this post")
    
#     db_like = models.Like(
#         user_id=current_user.id,
#         post_id=post_id
#     )
#     db.add(db_like)
#     db.commit()
#     db.refresh(db_like)
#     return db_like

# @app.delete("/posts/{post_id}/like")
# def unlike_post(
#     post_id: int,
#     current_user: models.User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     like = db.query(models.Like).filter(
#         models.Like.user_id == current_user.id,
#         models.Like.post_id == post_id
#     ).first()
#     if not like:
#         raise HTTPException(status_code=404, detail="Like not found")

#     db.delete(like)
#     db.commit()
#     return {"message" : "Post unliked successfully"}


# @app.post("/users/me/orders/", response_model=OrderResponse)
# def create_order(
#     order: OrderCreate,
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     db_order = Order(
#         product_name=order.product_name,
#         amount=order.amount,
#         user_id=current_user.id,
#         status=order.status if order.status else OrderStatus.pending,
#         estimated_delivery_time=order.estimated_delivery_time or None
#     )
#     db.add(db_order)
#     db.commit()
#     db.refresh(db_order)
#     return OrderResponse.from_orm(db_order)

# @app.get("/users/me/orders/", response_model=PaginationResponse)
# def get_user_orders(
#     current_user: models.User = Depends(get_current_user),
#     db: Session = Depends(get_db),
#     params: dict = Depends(pagination_params),
#     status: Optional[OrderStatus] = None
# ):
#     query = db.query(models.Order).filter(models.Order.user_id == current_user.id)
#     if params['search']:
#         search = f"%{params['search']}%"
#         query = query.filter(models.Order.product_name.ilike(search))
#     if status:
#         query = query.filter(Order.status == status)

#     total = query.count()
#     orders = query.offset((params['page'] - 1) * params['page_size'])\
#                   .limit(params['page_size'])\
#                   .all()
#     orders_response = [OrderResponse.from_orm(order) for order in orders]
#     return {
#         "items": orders_response,
#         "total": total,
#         "page": params['page'],
#         "page_size": params['page_size'],
#         "total_pages": (total + params['page_size'] - 1) // params['page_size']
#     }

# @app.patch("/users/me/orders/{order_id}/status", response_model=OrderResponse)
# def update_order_status(
#     order_id: int,
#     order_update: OrderUpdateStatus,
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
    
#     db_order = db.query(Order).filter(
#         Order.id == order_id, Order.user_id == current_user.id
#     ).first()

#     if not db_order:
#         raise HTTPException(
#             status_code=HTTPStatus.NOT_FOUND,
#             detail="Order not found"
#         )

#     if order_update.status not in OrderStatus:
#         raise HTTPException(
#             status_code=HTTPStatus.BAD_REQUEST,
#             detail="Invalid order status"
#         )

#     db_order.status = order_update.status

#     if order_update.status == OrderStatus.processing:
#         db_order.estimated_delivery_time = datetime.utcnow() + timedelta(days=2)
#     elif order_update.status == OrderStatus.in_packaging:
#         db_order.estimated_delivery_time = datetime.utcnow() + timedelta(days=1)
#     elif order_update.status == OrderStatus.out_for_delivery:
#         db_order.estimated_delivery_time = datetime.utcnow() + timedelta(hours=5)
#     elif order_update.status in [OrderStatus.delivered, OrderStatus.cancelled]:
#         db_order.estimated_delivery_time = None

#     db.commit()
#     db.refresh(db_order)

#     return OrderResponse.from_orm(db_order)


# @app.post("/users/me/wishlist/", response_model=WishlistItemResponse)
# def create_wishlist_item(
#     item: WishlistItemCreate,
#     current_user: models.User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     db_item = models.WishlistItem(**item.dict(), user_id=current_user.id)
#     db.add(db_item)
#     db.commit()
#     db.refresh(db_item)
#     return WishlistItemResponse.from_orm(db_item)

# @app.get("/users/me/wishlist/", response_model=PaginationResponse)
# def get_wishlist_items(
#     current_user: models.User = Depends(get_current_user),
#     db: Session = Depends(get_db),
#     params: dict = Depends(pagination_params)
# ):
#     query = db.query(models.WishlistItem).filter(models.WishlistItem.user_id == current_user.id)
#     if params['search']:
#         search = f"%{params['search']}%"
#         query = query.filter(models.WishlistItem.product_name.ilike(search) | models.WishlistItem.notes.ilike(search))
#     total = query.count()
#     items = query.offset((params['page'] - 1) * params['page_size'])\
#                  .limit(params['page_size'])\
#                  .all()
#     items_response = [WishlistItemResponse.from_orm(item) for item in items]
#     return {
#         "items": items_response,
#         "total": total,
#         "page": params['page'],
#         "page_size": params['page_size'],
#         "total_pages": (total + params['page_size'] - 1) // params['page_size']
#     }

# @app.get("/users/me/wishlist/{item_id}", response_model=WishlistItemResponse)
# def get_wishlist_item(
#     item_id: int,
#     current_user: models.User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     item = db.query(models.WishlistItem).filter(
#         models.WishlistItem.id == item_id,
#         models.WishlistItem.user_id == current_user.id
#     ).first()
#     if not item:
#         raise HTTPException(status_code=404, detail="Wishlist item not found")
#     return WishlistItemResponse.from_orm(item)

# @app.put("/users/me/wishlist/{item_id}", response_model=WishlistItemResponse)
# def update_wishlist_item(
#     item_id: int,
#     updates: WishlistItemUpdate,
#     current_user: models.User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     item = db.query(models.WishlistItem).filter(
#         models.WishlistItem.id == item_id,
#         models.WishlistItem.user_id == current_user.id
#     ).first()
#     if not item:
#         raise HTTPException(status_code=404, detail="Wishlist item not found")
#     for key, value in updates.dict(exclude_unset=True).items():
#         setattr(item, key, value)
#     db.commit()
#     db.refresh(item)
#     return WishlistItemResponse.from_orm(item)

# @app.delete("/users/me/wishlist/{item_id}")
# def delete_wishlist_item(
#     item_id: int,
#     current_user: models.User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     item = db.query(models.WishlistItem).filter(
#         models.WishlistItem.id == item_id,
#         models.WishlistItem.user_id == current_user.id
#     ).first()
#     if not item:
#         raise HTTPException(status_code=404, detail="Wishlist item not found")
#     db.delete(item)
#     db.commit()
#     return {"message": "Wishlist item deleted"}