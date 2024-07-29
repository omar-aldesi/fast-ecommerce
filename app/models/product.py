from sqlalchemy import Column, Integer, Table, String, Float, DateTime, ForeignKey, Boolean, JSON, Date
from sqlalchemy.orm import relationship
from app.db import Base

from datetime import datetime, timedelta

product_variation_option_association = Table(
    'product_variation_option_association',
    Base.metadata,
    Column('product_variation_id', Integer, ForeignKey('product_variations.id')),
    Column('variation_option_id', Integer, ForeignKey('variation_options.id'))
)

product_addons_association = Table(
    'product_addons_association',
    Base.metadata,
    Column('product_id', Integer, ForeignKey('products.id')),
    Column('addon_id', Integer, ForeignKey('addons.id'))
)


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, index=True, unique=True)
    price = Column(Float)
    image = Column(String)
    description = Column(String)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime)

    tags = Column(JSON)

    is_active = Column(Boolean, default=True)

    stock_type = Column(String, default="fixed")
    stock_daily = Column(Integer, default=0)
    stock = Column(Integer, default=0)

    last_daily_stock_update = Column(Date, default=datetime.now)

    discount_type = Column(String, default="fixed")
    discount_value = Column(Float, default=0.0)

    total_sales = Column(Integer, default=0)
    is_visible = Column(Boolean, default=True)

    category_id = Column(Integer, ForeignKey("categories.id"))
    category = relationship("Category", back_populates="products")

    subcategory_id = Column(Integer, ForeignKey("subcategories.id"))
    subcategory = relationship("SubCategory", back_populates="products")

    branch_id = Column(Integer, ForeignKey("branches.id"))
    branch = relationship("Branch", back_populates="products")

    addons = relationship(
        "Addon",
        secondary=product_addons_association,
        backref="products",
        lazy="joined"
    )
    variations = relationship("ProductVariation", back_populates="product", lazy="joined")
    reviews = relationship("ProductReview", backref="product")


class ProductVariation(Base):
    __tablename__ = "product_variations"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    type = Column(String)
    min_selections = Column(Integer, default=1)
    max_selections = Column(Integer, default=1)
    required = Column(Boolean, default=False)

    product_id = Column(Integer, ForeignKey("products.id"))
    product = relationship("Product", back_populates="variations")
    options = relationship(
        "VariationOption",
        secondary=product_variation_option_association,
        back_populates="variations",
        lazy="joined"
    )


class VariationOption(Base):
    __tablename__ = "variation_options"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    price = Column(Float)

    variations = relationship(
        "ProductVariation",
        secondary=product_variation_option_association,
        back_populates="options"
    )


class Addon(Base):
    __tablename__ = "addons"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    price = Column(Float)
    tax = Column(Float)

    product_id = Column(Integer, ForeignKey("products.id"))


class ProductReview(Base):
    __tablename__ = "product_reviews"

    id = Column(Integer, primary_key=True, index=True)
    rating = Column(Integer)
    comment = Column(String)

    product_id = Column(Integer, ForeignKey("products.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime)
