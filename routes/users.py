import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi.security import OAuth2PasswordRequestForm

from database import get_db
import models
from models import User
from auth import (
    get_password_hash,
    authenticate_user,
    create_access_token,
    get_current_user,
    get_admin_user,
)
from utils.pagination import pagination_params
from schemas import (
    UserCreate,
    PaginationResponse,
    Token,
    UserProfileUpdate,
    UserProfileResponse,
    ProfilePictureResponse,
)


router = APIRouter(prefix="", tags=["Users"])


BASE_STATIC_DIR = os.path.join(os.getcwd(), "static")
PROFILE_PIC_DIR = os.path.join(BASE_STATIC_DIR, "profile_pics")
os.makedirs(PROFILE_PIC_DIR, exist_ok=True)



@router.post("/register/")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(
        models.User.email == user.email, models.User.is_deleted == False
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email Already registered")
    
    hashed_password = get_password_hash(user.password)
    new_user = models.User(
        name=user.name,
        email=user.email,
        hashed_password=hashed_password,
        age=user.age,
        role=user.role.value.lower(),
        is_deleted=False,
    )
    db.add(new_user)
    
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db.refresh(new_user)
    return {"message": "User Registered Successfully", "role": new_user.role}



@router.post("/login/", response_model=Token)
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    access_token = create_access_token(
        data={"sub": user.id, "role": user.role}, expires_delta=timedelta(minutes=30)
    )
    return {"access_token": access_token, "token_type": "bearer"}



@router.get("/me/", response_model=UserProfileResponse)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user



@router.get("/", response_model=PaginationResponse)
def get_all_users(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    params: dict = Depends(pagination_params),
):
    query = db.query(models.User).filter(models.User.is_deleted == False)
    
    if params["search"]:
        search = f"%{params['search']}%"
        query = query.filter(models.User.name.ilike(search) | models.User.email.ilike(search))
    
    total = query.count()
    users = query.offset((params["page"] - 1) * params["page_size"]).limit(params["page_size"]).all()
    
    items = [{"id": u.id, "name": u.name, "email": u.email} for u in users]
    
    return {
        "items": items,
        "total": total,
        "page": params["page"],
        "page_size": params["page_size"],
        "total_pages": (total + params["page_size"] - 1) // params["page_size"],
    }



@router.get("/admin/", dependencies=[Depends(get_admin_user)], response_model=PaginationResponse)
def get_all_users_admin(db: Session = Depends(get_db), params: dict = Depends(pagination_params)):
    query = db.query(models.User)
    
    if params["search"]:
        search = f"%{params['search']}%"
        query = query.filter(models.User.name.ilike(search) | models.User.email.ilike(search))
    
    total = query.count()
    users = query.offset((params["page"] - 1) * params["page_size"]).limit(params["page_size"]).all()
    
    items = [
        {
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "role": u.role,
            "is_deleted": u.is_deleted,
            "deleted_at": u.deleted_at,
        }
        for u in users
    ]
    
    return {
        "items": items,
        "total": total,
        "page": params["page"],
        "page_size": params["page_size"],
        "total_pages": (total + params["page_size"] - 1) // params["page_size"],
    }



@router.delete("/admin/{user_id}/soft", dependencies=[Depends(get_admin_user)])
def soft_delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.is_deleted:
        raise HTTPException(status_code=400, detail="User already soft-deleted")
    
    user.is_deleted = True
    user.deleted_at = datetime.utcnow()
    db.commit()
    return {"message": "User soft-deleted successfully"}


@router.delete("/admin/{user_id}/hard", dependencies=[Depends(get_admin_user)])
def hard_delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    return {"message": "User hard-deleted successfully"}


@router.put("/me/profile", response_model=UserProfileResponse)
async def update_profile(
    profile_data: UserProfileUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    update_data = profile_data.dict(exclude_unset=True)
    
    for field in update_data:
        setattr(current_user, field, update_data[field])
    
    db.commit()
    db.refresh(current_user)
    return current_user

@router.post("/me/profile-picture", response_model=ProfilePictureResponse)
async def upload_profile_picture(
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    allowed_types = ["image/jpeg", "image/png", "image/gif"]
    if file.content_type not in allowed_types:
        raise HTTPException(400, "Invalid file type. Allowed types: JPEG, PNG, GIF")

    file_ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{file_ext}"
    file_path = os.path.join(PROFILE_PIC_DIR, filename)

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    current_user.profile_picture = f"/static/profile_pics/{filename}"
    db.commit()

    return {"message": "Profile picture updated successfully", "profile_picture": current_user.profile_picture}


@router.get("/profile", response_model=UserProfileResponse)
def get_user_profile(current_user: User = Depends(get_current_user)):
    return current_user