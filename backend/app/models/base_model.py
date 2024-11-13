from app import db
from datetime import datetime, timezone
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Query


## Reference: https://blog.miguelgrinberg.com/post/implementing-the-soft-delete-pattern-with-flask-and-sqlalchemy


class SoftDeleteQuery(Query):
    def __init__(self, entities, *args, **kwargs):
        super().__init__(entities, *args, **kwargs)
        # Apply the filter by default on initialization
        self._with_deleted = False
        self = self.filter_by(is_deleted=False)

    def with_deleted(self):
        """Allow including deleted entries in the query."""
        self._with_deleted = True
        return self

    def __iter__(self):
        if not self._with_deleted:
            self = self.filter_by(is_deleted=False)
        return super().__iter__()


# NOTE: Faced the `TypeError: metaclass conflict` when tried multiple inheritance with `BaseModel` and `ABC`, to make it an abstract class.
# To resolve this issue, used __abstract__ = True to make it an abstract class and skip the creation of the table for this class.
# Reference: https://docs.sqlalchemy.org/en/13/orm/extensions/declarative/api.html#abstract


class BaseModel(db.Model):
    __abstract__ = True
    query_class = SoftDeleteQuery

    @declared_attr
    def is_deleted(cls):
        return db.Column(db.Boolean, default=False)

    @declared_attr
    def deleted_at(cls):
        return db.Column(db.DateTime, nullable=True)

    @declared_attr
    def created_at(cls):
        return db.Column(
            db.DateTime, default=datetime.now(timezone.utc), nullable=False
        )

    @declared_attr
    def updated_at(cls):
        return db.Column(
            db.DateTime,
            default=datetime.now(timezone.utc),
            onupdate=datetime.now(timezone.utc),
            nullable=False,
        )

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        db.session.commit()

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = datetime.now(timezone.utc)
        db.session.commit()

    def hard_delete(self):
        db.session.delete(self)
        db.session.commit()
