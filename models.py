from sqlalchemy import Column, Integer, String, Enum, Boolean, DateTime, Index, JSON, Text, ForeignKey
from database import Base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY
import enum
from datetime import datetime


class ReactionType(str, enum.Enum):
    LIKE = "like"
    LOVE = "love"
    HAHA = "haha"
    WOW = "wow"
    SAD = "sad"
    ANGRY = "angry"


class OrderStatus(str, enum.Enum):
    pending = "Pending"
    processing = "Processing"
    in_packaging = "In Packaging"
    out_for_delivery = "Out for Delivery"
    delivered = "Delivered"
    cancelled = "Cancelled"


class UserRole(str, enum.Enum):
    admin = "admin"
    user = "user"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    email = Column(String(50), index=True, nullable=False)
    age = Column(Integer, nullable=True)
    hashed_password = Column(String)
    role = Column(Enum(UserRole, name="user_role_enum"), nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    #new fields for profile management
    profile_picture = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    preferences = Column(JSON, nullable=True)
    phone_number = Column(String(20), nullable=True)
    address = Column(String(255), nullable=True)
    social_links = Column(JSON, nullable=True)
    language = Column(String(10), default="en")
    theme_preference = Column(String(10), default="light")

    reset_token = Column(String, nullable=True)
    reset_token_expire = Column(DateTime, nullable=True)
    otp_code = Column(String, nullable=True)
    otp_expires_at = Column(DateTime, nullable=True)

    # Relationships
    posts = relationship("Post", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    wishlist_items = relationship("WishlistItem", back_populates="user", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="user", cascade="all, delete-orphan")
    reactions = relationship("Reaction", back_populates="user", cascade="all, delete-orphan")


# Partial unique index for email where is_deleted is False
Index('idx_user_email_unique', User.email, unique=True, postgresql_where=(User.is_deleted == False))


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="post", cascade="all, delete-orphan")
    media_attachments = relationship("Media", back_populates="post", cascade="all, delete-orphan")
    reactions = relationship("Reaction", back_populates="post", cascade="all, delete-orphan")


class OrderStatusLog(Base):
    __tablename__ = "order_status_logs"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    status = Column(String, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow)

    order = relationship("Order", back_populates="order_status_logs")



class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String(100), nullable=False)
    amount = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String, default=OrderStatus.pending)
    estimated_delivery_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="orders")
    order_status_logs = relationship("OrderStatusLog", back_populates="order")


class WishlistItem(Base):
    __tablename__ = "wishlist_items"

    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String(100), nullable=False)
    notes = Column(Text, nullable=True)
    quantity = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    user = relationship("User", back_populates="wishlist_items")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)

    user = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")

class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="likes")
    post = relationship("Post", back_populates="likes")


class Media(Base):
    __tablename__ = "media"

    id = Column(Integer, primary_key=True, index=True)
    file_url = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)

    post = relationship("Post", back_populates="media_attachments")


class Reaction(Base):
    __tablename__ = "reactions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    reaction_type = Column(Enum(ReactionType), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="reactions")
    post = relationship("Post", back_populates="reactions")