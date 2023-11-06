from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    create_engine,
    Date,
    Time,
    DateTime,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker


engine = create_engine("'postgresql://postdb:postdb616@localhost:5432/taskdb'")
Session = sessionmaker(bind=engine)


def get_db():
    """To get the session to be active and to close after the db operation."""
    session = Session()
    try:
        yield session
    finally:
        session.close()


base = declarative_base()


class User_det(base):
    __tablename__ = "user_det"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    password = Column(String)
    tok = relationship("Token", back_populates="user_det")
    tasks = relationship("Task", back_populates="user_dets")


class Token(base):
    __tablename__ = "token"
    id = Column(Integer, primary_key=True)
    accesstype = Column(String)
    user_id = Column(Integer, ForeignKey("user_det.id"))
    user_det = relationship("User_det", back_populates="tok")


class Task(base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_name = Column(String)
    task_date = Column(Date)
    task_time = Column(Time(timezone=True))
    priority = Column(String)
    created_time = Column(DateTime)
    is_complete = Column(String)
    user_id = Column(Integer, ForeignKey("user_det.id"))
    user_dets = relationship("User_det", back_populates="tasks")


class RevokedToken(Base):
    __tablename__ = "revoked_tokens"
    token = Column(String, primary_key=True)
