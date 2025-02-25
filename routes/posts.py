import os
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import case
from sqlalchemy.sql import func
from database import get_db
from models import Post, Media, Like, Comment
from auth import get_current_user
from schemas import PostCreate, PostResponse, PaginationResponse, MediaResponse, ReactionType
from utils.pagination import pagination_params
import models

BASE_STATIC_DIR = r"C:\Users\Sagar\Desktop\static"
MEDIA_DIR = os.path.join(BASE_STATIC_DIR, "media")
os.makedirs(MEDIA_DIR, exist_ok=True)

router = APIRouter(prefix="", tags=["Posts"])

@router.post("/", response_model=PostResponse)
def create_post(
    post: PostCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_post = models.Post(**post.dict(), user_id=current_user.id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return PostResponse(
        id=db_post.id,
        title=db_post.title,
        content=db_post.content,
        user_id=db_post.user_id,
        created_at=db_post.created_at,
        like_count=0,
        comment_count=0,
        media_attachments=db_post.media_attachments if db_post.media_attachments else []
    )

@router.post("/{post_id}/media/", response_model=List[MediaResponse])
async def upload_media(
    post_id: int,
    files: List[UploadFile] = File(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    post = db.query(models.Post).filter(
        models.Post.id == post_id,
        models.Post.user_id == current_user.id
    ).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    media_responses = []
    for file in files:
        file_type = file.content_type.split("/")[0]
        if file_type not in ["image", "video", "audio"]:
            raise HTTPException(status_code=400, detail=f"Invalid file type: {file.content_type}")
        
        file_ext = file.filename.split(".")[-1]
        filename = f"{uuid.uuid4()}.{file_ext}"
        file_path = os.path.join(MEDIA_DIR, filename)
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        db_media = models.Media(
            file_url=f"/static/media/{filename}",
            file_type=file_type,
            post_id=post_id
        )
        db.add(db_media)
        db.commit()
        db.refresh(db_media)
        
        media_responses.append(db_media)
    
    return media_responses

@router.get("/", response_model=PaginationResponse)
def get_user_posts(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
    params: dict = Depends(pagination_params)
):
    query = db.query(models.Post,
        func.count(models.Like.id).label("like_count"),
        func.count(models.Comment.id).label("comment_count")
    ).outerjoin(models.Like, models.Like.post_id == models.Post.id)\
    .outerjoin(models.Comment, models.Comment.post_id == models.Post.id)\
    .group_by(models.Post.id)\
    .filter(models.Post.user_id == current_user.id)

    if params['search']:
        search = f"%{params['search']}%"
        query = query.filter(models.Post.title.ilike(search) | models.Post.content.ilike(search))
    total = query.count()
    posts = query.offset((params['page'] - 1) * params['page_size'])\
                 .limit(params['page_size'])\
                 .all()
    posts_response = []
    for post, like_count, comment_count in posts:
        media_attachments = db.query(models.Media).filter(models.Media.post_id == post.id).all()
        
        posts_response.append(
            PostResponse(
                id=post.id,
                title=post.title,
                content=post.content,
                user_id=post.user_id,
                created_at=post.created_at,
                like_count=like_count,
                comment_count=comment_count,
                media_attachments=media_attachments
            )
        )
    return {
        "items": posts_response,
        "total": total,
        "page": params['page'],
        "page_size": params['page_size'],
        "total_pages": (total + params['page_size'] - 1) // params['page_size']
    }

@router.get("/{post_id}", response_model=PostResponse)
def get_post(
    post_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    post_with_counts = db.query(
        models.Post,
        func.sum(case((models.Reaction.reaction_type == ReactionType.LIKE, 1), else_=0)).label("like_count"),
        func.sum(case((models.Reaction.reaction_type == ReactionType.LOVE, 1), else_=0)).label("love_count"),
        func.sum(case((models.Reaction.reaction_type == ReactionType.HAHA, 1), else_=0)).label("haha_count"),
        func.sum(case((models.Reaction.reaction_type == ReactionType.WOW, 1), else_=0)).label("wow_count"),
        func.sum(case((models.Reaction.reaction_type == ReactionType.SAD, 1), else_=0)).label("sad_count"),
        func.sum(case((models.Reaction.reaction_type == ReactionType.ANGRY, 1), else_=0)).label("angry_count"),
        func.count(models.Comment.id).label("comment_count")
    ).outerjoin(models.Reaction, models.Reaction.post_id == models.Post.id)\
     .outerjoin(models.Comment, models.Comment.post_id == models.Post.id)\
     .group_by(models.Post.id)\
     .filter(models.Post.id == post_id)\
     .first()
    
    if not post_with_counts:
        raise HTTPException(status_code=404, detail="Post not found")

    post_data, like_count, love_count, haha_count, wow_count, sad_count, angry_count, comment_count = post_with_counts
    return PostResponse(
        id=post_data.id,
        title=post_data.title,
        content=post_data.content,
        user_id=post_data.user_id,
        created_at=post_data.created_at,
        like_count=like_count,
        love_count=love_count,
        haha_count=haha_count,
        wow_count=wow_count,
        sad_count=sad_count,
        angry_count=angry_count,
        comment_count=comment_count,
        media_attachments=post_data.media_attachments
    )

@router.put("/{post_id}", response_model=PostResponse)
def update_post(
    post_id: int,
    post_update: PostCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    post = db.query(models.Post).filter(
        models.Post.id == post_id,
        models.Post.user_id == current_user.id
    ).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    for key, value in post_update.dict().items():
        setattr(post, key, value)
    
    db.commit()
    db.refresh(post)

    post_with_counts = db.query(
        models.Post,
        func.count(models.Like.id).label("like_count"),
        func.count(models.Comment.id).label("comment_count")
    ).outerjoin(models.Like, models.Like.post_id == models.Post.id)\
     .outerjoin(models.Comment, models.Comment.post_id == models.Post.id)\
     .group_by(models.Post.id)\
     .filter(models.Post.id == post_id)\
     .first()
    
    if not post_with_counts:
        raise HTTPException(status_code=404, detail="Post not found")

    post_data, like_count, comment_count = post_with_counts

    return PostResponse(
        id=post_data.id,
        title=post_data.title,
        content=post_data.content,
        user_id=post_data.user_id,
        created_at=post_data.created_at,
        like_count=like_count,
        comment_count=comment_count,
        media_attachments=post_data.media_attachments
    )

@router.delete("/{post_id}")
def delete_post(
    post_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    post = db.query(models.Post).filter(
        models.Post.id == post_id,
        models.Post.user_id == current_user.id).first()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    db.delete(post)
    db.commit()
    return {"message": "Post deleted successfully"}