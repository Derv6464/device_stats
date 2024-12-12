from sqlalchemy import create_engine, String, Column, Float, ForeignKey, Integer, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()
metadata = Base.metadata

class Device(Base):
    __tablename__ = 'devices'
    name = Column(String, nullable=False)
    id = Column(String, primary_key=True, nullable=False)

class Metric_Type(Base):
    __tablename__ = 'metric_type'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    unit = Column(String, nullable=False)

class Times(Base):
    __tablename__ = 'times'
    id = Column(Integer, primary_key=True, autoincrement=True)
    samples_utc = Column(Integer, nullable=False)
    sent_utc = Column(Integer, nullable=False)
    received_utc = Column(Integer, nullable=False)
    samples_min = Column(Integer, nullable=False)
    sent_min = Column(Integer, nullable=False)
    received_min = Column(Integer, nullable=False)

class Metric(Base):
    __tablename__ = 'metrics'
    metric_id = Column(ForeignKey('metric_type.id'), primary_key=True, nullable=False)
    device_id = Column(ForeignKey('devices.id'), primary_key=True, nullable=False)
    time_id = Column(ForeignKey('times.id'), primary_key=True, nullable=False)
    value = Column(Float, nullable=False)

    device = relationship('Device')
    metric_type = relationship('Metric_Type')
    time = relationship('Times')
