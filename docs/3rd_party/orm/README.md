# ORMs

Object-relational mappers (ORMs) are libraries that provide a high-level abstraction of the database, allowing you to work with the database using Python objects.

### SQLAlchemy
SQLAlchemy stands out for its efficiency by providing a versatile and performant solution for database interactions. Its dual capabilities of high-level ORM and low-level SQL expression language, coupled with features like connection pooling and robust transaction management, streamline database operations, offering developers flexibility, readability, and optimal performance.

### Peewee
Peewee is appreciated for its simplicity and lightweight design, offering an easy-to-use and expressive ORM for Python. It excels in rapid development scenarios, providing a straightforward interface for interacting with databases while maintaining a small footprint.

### Psycopg2 - Adapter
Psycopg is a PostgreSQL adapter for Python, allowing Python applications to interact with PostgreSQL databases.


## Usage

### SQLAlchemy

```python
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

engine = create_engine("sqlite://", echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    address = relationship('Address', uselist=False, back_populates='user')

class Address(Base):
    __tablename__ = 'addresses'
    id = Column(Integer, primary_key=True)
    state = Column(String(50))
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates='address')

# This assumes that the tables are already created
users = session.query(User, Address).join(Address).filter(Address.state == 'CA').all()
for user in users:
    print(user.name, user.address.state)
```

### Peewee

```python
from peewee import SqliteDatabase, Model, CharField, IntegerField, ForeignKeyField

db = SqliteDatabase(":memory:")
db.connect()

class User(Model):
    name = CharField(max_length=50)

class Address(Model):
    email = CharField(max_length=50)
    state = CharField(max_length=50)
    user = ForeignKeyField(User, unique=True, backref='address')

# This assumes that the tables are already created
users = User.select().join(Address).where(Address.state == 'CA')
for user in users:
    print(user.name, user.address.state)
```


### Peewee - Postgresql connection via Psycopg

```python
from peewee import Model, PostgresqlDatabase, CharField

db = PostgresqlDatabase('my_database', user='postgres')

# Define a Peewee model
class User(Model):
    name = CharField()

    class Meta:
        database = db

db.connect()
db.create_tables([User])
```

> AI/LLM's are quite good with `orms`.  
> 👉 Try asking [ReMark](https://chat.robocorp.com)

###### Various [snippets](snippets)

- [Create, update, delete with SQLAlchemy](snippets/sqlalchemy/crud_operations.py)
- [Create, update, delete with Peewee](snippets/peewee/crud_operations.py)

## Links and references

### SQLAlchemy
- [PyPI](https://pypi.org/project/SQLAlchemy/)
- [Documentation](https://docs.sqlalchemy.org/en/20/)

### Peewee
- [PyPI](https://pypi.org/project/peewee/)
- [Documentation](https://docs.peewee-orm.com/en/latest/)

### Psycopg2
- [PyPI](https://pypi.org/project/psycopg2/)
- [Documentation](https://www.psycopg.org/docs/)
