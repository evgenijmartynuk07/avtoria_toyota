from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, autoincrement=True)
    car_id = Column(String, unique=True, index=True)
    link = Column(String, unique=True)
    title = Column(String)
    price = Column(String)
    odometer = Column(String)
    auction_url = Column(String, nullable=True)
    car_vin = Column(String, nullable=True, unique=True)
    location = Column(String, nullable=True)
    sold = Column(Boolean, default=False)

    photos = relationship("Photo", back_populates="car")


class Photo(Base):
    __tablename__ = "photos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    path = Column(String)
    car_id = Column(Integer, ForeignKey("cars.id"))
    car = relationship("Car", back_populates="photos")
