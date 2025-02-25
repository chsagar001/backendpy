from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Post, Like, User
from auth import get_current_user
from schemas import LikeResponse

router = APIRouter(prefix="", tags=["Likes"])

@router.post("/posts/{post_id}", response_model=LikeResponse)
def like_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    existing_like = db.query(Like).filter(
        Like.user_id == current_user.id,
        Like.post_id == post_id
    ).first()
    if existing_like:
        raise HTTPException(status_code=400, detail="You already liked this post")
    
    db_like = Like(
        user_id=current_user.id,
        post_id=post_id
    )
    db.add(db_like)
    db.commit()
    db.refresh(db_like)
    return db_like

@router.delete("/posts/{post_id}")
def unlike_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    like = db.query(Like).filter(
        Like.user_id == current_user.id,
        Like.post_id == post_id
    ).first()
    if not like:
        raise HTTPException(status_code=404, detail="Like not found")

    db.delete(like)
    db.commit()
    return {"message": "Post unliked successfully"}