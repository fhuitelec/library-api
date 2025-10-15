"""Root package of library_api."""

import datetime
import uuid

from pydantic import BaseModel


class Book(BaseModel):
    """Book model."""

    id: uuid.UUID
    human_id: str  # EDITOR-TITLE-ID, eg. ALI-FEELGOOD-001
    issue: int
    isbn: str
    title: str
    title: str
    author: str
    publisher: str
    publish_date: datetime.datetime


# uuid.uuid7() -> passer à Python 3.14 -> https://docs.python.org/3/library/uuid.html#uuid.uuid7
# Primary key indexation en UUIDv7
# Constraint on human_id + copy: https://stackoverflow.com/a/14221810
