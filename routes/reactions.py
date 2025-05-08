from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models
import schemas
from auth import get_current_user

router = APIRouter(prefix="", tags=["Reactions"])

@router.post("/posts/{post_id}/", response_model=schemas.ReactionResponse)
def add_reaction(
    post_id: int,
    reaction: schemas.ReactionCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    existing_reaction = db.query(models.Reaction).filter(
        models.Reaction.user_id == current_user.id,
        models.Reaction.post_id == post_id
    ).first()
    if existing_reaction:
        existing_reaction.reaction_type = reaction.reaction_type
    else:
        db_reaction = models.Reaction(
            user_id=current_user.id,
            post_id=post_id,
            reaction_type=reaction.reaction_type
        )
        db.add(db_reaction)
        existing_reaction = db_reaction

    db.commit()
    db.refresh(existing_reaction)
    return existing_reaction


@router.delete("/posts/{post_id}/")
def remove_reaction(
    post_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    reaction = db.query(models.Reaction).filter(
        models.Reaction.user_id == current_user.id,
        models.Reaction.post_id == post_id
    ).first()
    if not reaction:
        raise HTTPException(status_code=404, detail="Reaction not found")

    db.delete(reaction)
    db.commit()
    return {"message": "Reaction removed successfully"}