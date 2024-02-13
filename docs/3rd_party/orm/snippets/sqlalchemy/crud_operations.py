from sqlalchemy import Column, Integer, Sequence, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define the database engine and create a session
engine = create_engine(
    "sqlite:///:memory:", echo=True
)  # Use an in-memory SQLite database for this example
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


# Define a simple model class
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, Sequence("user_id_seq"), primary_key=True)
    name = Column(String(50))
    age = Column(Integer)


# Create the table in the database
Base.metadata.create_all(engine)


def add_user(name, age):
    new_user = User(name=name, age=age)
    session.add(new_user)
    session.commit()

    return new_user


def update_user(user_id, new_name, new_age):
    user = session.query(User).filter_by(id=user_id).first()
    user.name = new_name
    user.age = new_age
    session.commit()


def delete_user(user_id):
    user = session.query(User).filter_by(id=user_id).first()
    session.delete(user)
    session.commit()


def get_user(user_id) -> User:
    return session.query(User).filter_by(id=user_id).first()
