from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import jwt

from database import get_db
from utils.pagination import pagination_params
import models
from models import User
from email_utils import send_email, generate_password_reset_token, generate_otp
from schemas import ForgotPasswordRequest, ResetPasswordRequest, ResetPasswordReq
from auth import authenticate_user, get_password_hash, create_access_token, get_current_user, get_admin_user, SECRET_KEY, ALGORITHM


router = APIRouter(prefix="", tags=["Authentication"])


@router.post("/forgot-password/")
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == request.email, models.User.is_deleted == False).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    reset_token = generate_password_reset_token(user.email)
    user.reset_token = reset_token
    user.reset_token_expires = datetime.utcnow() + timedelta(minutes=15)
    db.commit()
    reset_link = f"http://localhost:8000/reset-password?token={reset_token}"
    email_body = f"""
    <p>You requested a password reset. Click the link below to reset your password:</p>
    <p><a href="{reset_link}">Reset Password</a></p>
    <p>This link will expire in 15 minutes.</p>
    """
    send_email(user.email, "Password Reset Request", email_body)
    return {"message": "Password reset email sent"}

@router.post("/forgot-password-otp/")
def forgot_password_otp(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == request.email, models.User.is_deleted == False).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    otp = generate_otp()
    user.otp_code = otp
    user.otp_expires_at = datetime.utcnow() + timedelta(minutes=10)
    db.commit()
    email_body = f"""
    <p>Your password reset OTP is: <strong>{otp}</strong></p>
    <p>This OTP is valid for 10 minutes.</p>
    """
    send_email(user.email, "Password Reset OTP", email_body)
    return {"message": "OTP sent to your email"}

@router.post("/reset-password/")
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(request.token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=400, detail="Invalid Token")
        if datetime.utcnow() > datetime.fromtimestamp(payload["exp"]):
            raise HTTPException(status_code=400, detail="Token has expired")
        user = db.query(models.User).filter(models.User.email == email, models.User.is_deleted == False).first()
        if not user or user.reset_token != request.token:
            raise HTTPException(status_code=400, detail="Invalid token")
        user.hashed_password = get_password_hash(request.new_password)
        user.reset_token = None
        user.reset_token_expires = None
        db.commit()
        return {"message": "Password reset successfully"}
    except jwt.PyJWTError:
        raise HTTPException(status_code=400, detail="Invalid token")

@router.post("/reset-password-otp/")
def reset_password_otp(request: ResetPasswordReq, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == request.email, models.User.is_deleted == False).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.otp_code != request.otp or user.otp_expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    user.hashed_password = get_password_hash(request.new_password)
    user.otp_code = None
    user.otp_expires_at = None
    db.commit()
    return {"message": "Password reset successfully"}