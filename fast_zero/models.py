from datetime import datetime

from slqalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import registry


table_registry = registry()


@table_registry.mapped_as_dataclass
class User:
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str]
    password: Mapped[str]
    email: Mapped[str]
    created_at: Mapped[datetime]
