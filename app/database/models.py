
from sqlalchemy import Column, Integer, String, create_engine, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

Base = declarative_base()
engine = create_engine("sqlite:///weather.db")
SessionLocal = sessionmaker(bind=engine)

class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    city = Column(String, nullable=False)
    last_sent = Column(DateTime, default=datetime.utcnow)

class History(Base):
    __tablename__ = "history"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    city = Column(String, nullable=False)
    query_type = Column(String, nullable=False)  # 'forecast' or 'details'
    response = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

class Favorite(Base):
    __tablename__ = "favorites"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    city = Column(String, nullable=False)
