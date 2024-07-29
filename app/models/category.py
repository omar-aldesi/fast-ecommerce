from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean
from app.db import Base

from sqlalchemy.orm import relationship


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    priority = Column(Integer)
    is_active = Column(Boolean, default=True)
    banner_image = Column(String)
    image = Column(String)
    products = relationship("Product", back_populates="category")
    subcategories = relationship("SubCategory", back_populates="category", lazy="joined")


class SubCategory(Base):
    __tablename__ = "subcategories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    is_active = Column(Boolean, default=True)
    category_id = Column(Integer, ForeignKey("categories.id"))
    category = relationship("Category", back_populates="subcategories")
    products = relationship("Product", back_populates="subcategory")
