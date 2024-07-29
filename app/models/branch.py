from app.db import Base
from sqlalchemy import Column, String, Integer, Float, ForeignKey

from sqlalchemy.orm import relationship


class Branch(Base):
    __tablename__ = "branches"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True)
    address = Column(String)
    phone_number = Column(String)
    email = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    cover_image = Column(String)
    coverage_radius = Column(Integer)

    products = relationship("Product", back_populates="branch")
    orders = relationship("Order", back_populates="branch")
