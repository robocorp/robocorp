from typing import Optional

from peewee import CharField, IntegerField, Model, SqliteDatabase

# Define the database and create a connection
db = SqliteDatabase(":memory:")


# Define a simple model class
class User(Model):
    name = CharField(max_length=50)
    age = IntegerField()

    class Meta:
        database = db


db.connect()
db.create_tables([User])


def add_user(name: str, age: int) -> User:
    return User.create(name=name, age=age)


def update_user(user_id: int, new_name: str, new_age: str) -> None:
    user = User.get_by_id(user_id)
    user.name = new_name
    user.age = new_age
    user.save()


def delete_user(user_id: int) -> None:
    user = User.get_by_id(user_id)
    user.delete_instance()


def get_user(user_id: int) -> Optional[User]:
    return User.get_or_none(User.id == user_id)
