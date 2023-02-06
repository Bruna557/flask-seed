from sqlalchemy import Table, MetaData, Column, String, Date
from sqlalchemy.orm import registry

from users.domain import model


metadata = MetaData()

users = Table(
    "users",
    metadata,
    Column("ssn", String(255), primary_key=True),
    Column("first_name", String(255)),
    Column("last_name", String(255)),
    Column("date_of_birth", Date),
)


def start_mappers():
    mapper_reg = registry()
    users_mapper = mapper_reg.map_imperatively(model.User, users)
