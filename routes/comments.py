from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Post, Comment, User
from auth import get_current_user
from schemas import CommentCreate, CommentResponse

router = APIRouter(prefix="", tags=["Comments"])

@router.post("/posts/{post_id}", response_model=CommentResponse)
def create_comment(
    post_id: int,
    comment: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    db_comment = Comment(
        content=comment.content,
        user_id=current_user.id,
        post_id=post_id
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

@router.get("/posts/{post_id}", response_model=list[CommentResponse])
def get_comments(
    post_id: int,
    db: Session = Depends(get_db)
):
    comments = db.query(Comment).filter(Comment.post_id == post_id).all()
    return comments
